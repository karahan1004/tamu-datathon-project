import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide", page_title="Ingredient Demand Forecast Viewer")

CSV_FILEPATH = "/Users/kara/tamu-datathon-project/ingredient_forecast_with_constraints.csv"
HISTORICAL_MONTHS = 6 

@st.cache_data
def load_data():
    """Loads, cleans, and pre-processes the ingredient forecast data."""
    try:
        df = pd.read_csv(CSV_FILEPATH)
        df = df.rename(columns={
            'Date' : 'ds',
            'Forecast_LBS_or_Count': 'yhat',
            'Forecasted_Usage_Original_Unit': 'yhat_raw_unit', 
            'Ingredient' : 'ingredient',
            'Monthly_Supply_Constraint': 'supply',
            'Constraint_Unit': 'unit',
            'Shortfall_Surplus': 'shortfall',
            'Action_Required': 'action_required'
        })
       
        df = df.drop(columns=['Month_Label'])

        df['ds'] = pd.to_datetime(df['ds'])

        df['period'] = df.groupby('ingredient').cumcount()
        df['period'] = df['period'].apply(lambda x: 'Historical Proxy' if x < HISTORICAL_MONTHS else 'Future Forecast')
        
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{CSV_FILEPATH}' was not found. Please ensure it is available.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        return pd.DataFrame()


def create_trend_chart(df, ingredient_name, unit):
    """Creates the interactive time series Altair chart for a single ingredient."""
    df_filtered = df[df['ingredient'] == ingredient_name].sort_values('ds')
    
    base = alt.Chart(df_filtered).encode(
        x=alt.X('ds', title='Date', axis=alt.Axis(format="%b %Y")),
        y=alt.Y('yhat', title=f'Forecasted Quantity ({unit})', scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip('ds', title='Date', format='%Y-%m-%d'),
            alt.Tooltip('yhat', title='Quantity', format=',.0f'),
            'period'
        ]
    )

    line = base.mark_line(point=True).encode(
        color=alt.Color('period', 
                        scale=alt.Scale(domain=['Historical Proxy', 'Future Forecast'], 
                                        range=['#2563eb', '#ef4444']),
                        legend=alt.Legend(title="Forecast Period")),
        strokeWidth=alt.value(3)
    )
    
    transition_df = df_filtered[df_filtered['period'] == 'Future Forecast']
    if not transition_df.empty:
        historical_end_date = df_filtered[df_filtered['period'] == 'Historical Proxy']['ds'].max()
        rule = alt.Chart(pd.DataFrame({'date': [historical_end_date]})).mark_rule(
            strokeDash=[5, 5], 
            color='#94a3b8',
            size=2
        ).encode(
            x='date'
        )
        chart = rule + line
    else:
        chart = line

    return chart.properties(
        title=f'Demand Forecast Trend: {ingredient_name} (in {unit})'
    ).interactive()

def create_constraint_chart(df, ingredient_name, unit):
    """Creates a bar chart comparing monthly supply vs. forecasted demand for future months."""
    
    df_filtered = df[(df['ingredient'] == ingredient_name) & (df['period'] == 'Future Forecast')].sort_values('ds')
    
    if df_filtered.empty:
        return None

    comparison_df = df_filtered[['ds', 'yhat', 'supply']].copy()
    comparison_df = comparison_df.melt(
        id_vars='ds', 
        value_vars=['yhat', 'supply'],
        var_name='Type', 
        value_name='Quantity'
    ).rename(columns={'ds': 'Date'})
    
    bar_chart = alt.Chart(comparison_df).mark_bar().encode(
        x=alt.X('Date', axis=alt.Axis(format="%b %Y"), title="Forecast Month"),
        column=alt.Column('Type', header=alt.Header(titleOrient="bottom", labelOrient="bottom")),
        y=alt.Y('Quantity', title=f'Quantity ({unit})'),
        color=alt.Color('Type', scale=alt.Scale(domain=['yhat', 'supply'], range=['#f97316', '#10b981']), 
                        legend=alt.Legend(title="Type", labelExpr="datum.label == 'yhat' ? 'Forecasted Demand' : 'Monthly Supply'")),
        tooltip=[
            alt.Tooltip('Date', format='%Y-%m-%d'),
            alt.Tooltip('Quantity', format=',.0f'),
            alt.Tooltip('Type', title='Metric')
        ]
    ).properties(
        title=f'Supply vs. Demand Comparison ({ingredient_name})'
    ).interactive()
    
    return bar_chart


def calculate_metrics(df_filtered):
    """Calculates key metrics for the selected ingredient."""
    if df_filtered.empty:
        return None

    historical_data = df_filtered[df_filtered['period'] == 'Historical Proxy']
    forecast_data = df_filtered[df_filtered['period'] == 'Future Forecast']
    
    metrics = {}
    
    metrics['Historical Average'] = historical_data['yhat'].mean()
    
    if not forecast_data.empty:
        last_forecast = forecast_data.iloc[-1]
        
        metrics['Last Forecast Month'] = last_forecast['ds'].strftime('%b %Y')
        metrics['Last Forecast Value'] = last_forecast['yhat']
        metrics['Current Monthly Supply'] = last_forecast['supply']
        metrics['Shortfall/Surplus'] = last_forecast['shortfall']
        metrics['Action Required'] = last_forecast['action_required']
        metrics['Unit'] = last_forecast['unit']
        

        if not historical_data.empty:
            last_historical = historical_data.iloc[-1]['yhat']
            change = ((last_forecast['yhat'] - last_historical) / last_historical) * 100
            metrics['% Change (Last Hist to Forecast End)'] = change

    return metrics


if __name__ == "__main__":
    df = load_data()

    st.title("🍜 Ingredient Demand Forecast & Constraint Analysis")
    st.markdown("Use this dashboard to check future demand for ingredients and see if your **current shipment schedule** (defined in your `MSY Data - Shipment.csv` file) is sufficient to cover it.")

    if not df.empty:
        default_ingredient = 'braised beef used (g)' if 'braised beef used (g)' in df['ingredient'].unique() else df['ingredient'].iloc[0]
        
        selected_ingredient = st.selectbox(
            "**Select Ingredient to Analyze:**", 
            df['ingredient'].unique().tolist(),
            index=df['ingredient'].unique().tolist().index(default_ingredient) if default_ingredient in df['ingredient'].unique() else 0
        )

        st.markdown("---")
        
        metrics_df = df[df['ingredient'] == selected_ingredient]
        metrics = calculate_metrics(metrics_df)
        unit = metrics.get('Unit', 'Units')

        if selected_ingredient and metrics:
            
            st.subheader(f"1. Demand Trend for {selected_ingredient}")
            st.markdown(f"Shows the monthly usage trend, standardized to **{unit}** for supply comparison.")
            trend_chart = create_trend_chart(df, selected_ingredient, unit)
            st.altair_chart(trend_chart, use_container_width=True)

            
            st.markdown("---")
            st.subheader(f"2. Inventory Constraint Summary ({metrics.get('Last Forecast Month')})")

            col1, col2, col3, col4 = st.columns(4)
        
            col1.metric(
                label="Historical Proxy Avg.", 
                value=f"{metrics.get('Historical Average', 0):,.0f} {unit}"
            )

            col2.metric(
                label=f"Current Monthly Supply ({unit})", 
                value=f"{metrics.get('Current Monthly Supply', 0):,.0f}"
            )

            col3.metric(
                label=f"Forecasted Demand ({metrics.get('Last Forecast Month')})", 
                value=f"{metrics.get('Last Forecast Value', 0):,.0f}" if metrics.get('Last Forecast Value') is not None else "N/A"
            )
            
            shortfall_value = metrics.get('Shortfall/Surplus')
            delta_color = "inverse" if shortfall_value < 0 else "normal"
            col4.metric(
                label="Shortfall / Surplus", 
                value=f"{shortfall_value:,.0f}" if shortfall_value is not None else "N/A",
                delta_color=delta_color
            )
            
            st.markdown("#### **Action Required**")
            st.markdown(f"**{metrics.get('Action Required', 'N/A')}**")

            st.markdown("---")
            st.subheader("3. Future Supply vs. Forecasted Demand")
            st.markdown("This bar chart highlights months where demand (orange) exceeds your current supply (green).")
            
            constraint_chart = create_constraint_chart(df, selected_ingredient, unit)
            if constraint_chart:
                st.altair_chart(constraint_chart, use_container_width=True)
            else:
                st.info("No future forecast data available for constraint comparison.")

            st.markdown("---")
            st.subheader("Raw Data Points")
            st.dataframe(metrics_df[['ds', 'yhat', 'supply', 'shortfall', 'action_required']].rename(
                columns={'ds': 'Date', 'yhat': f'Forecast Quantity ({unit})', 'supply': 'Monthly Supply', 'shortfall': 'Shortfall/Surplus', 'action_required': 'Action'}), 
                use_container_width=True
            )

    elif df.empty:
        st.warning(f"Data could not be loaded. Please ensure the required CSV file ('{CSV_FILEPATH}') is correctly formatted and available.")
    else:
        st.info("The loaded data set appears to be empty or missing sufficient ingredient information to perform the analysis.")
