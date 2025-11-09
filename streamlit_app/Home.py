from pathlib import Path
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

# ---------- Page config ----------
st.set_page_config(
    page_title="Mai Shan Yan • Shipments",
    page_icon="📦",
    layout="wide",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Shipments dashboard powered by Streamlit + Altair."
    },
)

# ---------- Title bar ----------
left, mid, right = st.columns([0.85, 0.10, 0.05])
with left:
    st.markdown("### 📦 Mai Shan Yan — **Monthly Shipments**")
    st.caption("Quickly filter, sort, and explore shipment quantities by ingredient.")
with right:
    st.link_button("GitHub", "https://github.com/", use_container_width=True)  # optional

# ---------- Load data ----------
CSV_PATH = Path("data/MSY Data - Shipment.csv")   # keep your relative path
@st.cache_data(show_spinner="Loading data…")
def load_data(p: Path) -> pd.DataFrame:
    df = pd.read_csv(p)
    # normalize expected columns
    df.columns = [c.strip() for c in df.columns]
    # compute monthly shipment
    freq_map = {"weekly": 4, "biweekly": 2, "monthly": 1}
    freq = df["frequency"].astype(str).str.strip().str.lower().map(freq_map)
    df["quantity*shipment"] = df["Quantity per shipment"] * df["Number of shipments"]
    df["Total monthly shipment"] = (df["quantity*shipment"] * freq).fillna(0)
    return df

try:
    df = load_data(CSV_PATH)
except FileNotFoundError:
    st.error(f"Couldn't find **{CSV_PATH}**. Make sure the file exists relative to this page.")
    st.stop()

if df.empty:
    st.info("No rows in the dataset yet. Add data to see the dashboard.")
    st.stop()

# ---------- Sidebar filters ----------
with st.sidebar:
    st.markdown("### 🔎 Controls")
    # "All" behavior for frequency
    freq_options = ["All", "Weekly", "Biweekly", "Monthly"]
    freq_choice = st.selectbox("Order frequency", freq_options, index=0)

    # quick search by ingredient substring
    query = st.text_input("Search ingredient", placeholder="e.g., Chicken")

    # sorting
    sort_label = st.radio(
        "Sort bars by",
        [
            "Highest monthly total",
            "Lowest monthly total",
            "Ingredient (A→Z)",
            "Ingredient (Z→A)",
        ],
        index=0
    )

    # top-N limiter
    n_max = max(3, len(df))
    top_n = st.slider("Show top N rows", 3, n_max, min(12, n_max))

# Apply filters
filt = df.copy()
if freq_choice != "All":
    filt = filt[filt["frequency"].str.lower() == freq_choice.lower()]

if query:
    q = query.strip().lower()
    filt = filt[filt["Ingredient"].astype(str).str.lower().str.contains(q)]

# Sort map
sort_map = {
    "Highest monthly total": ("Total monthly shipment", False),
    "Lowest monthly total": ("Total monthly shipment", True),
    "Ingredient (A→Z)": ("Ingredient", True),
    "Ingredient (Z→A)": ("Ingredient", False),
}
sort_col, ascending = sort_map[sort_label]
filt = filt.sort_values(by=sort_col, ascending=ascending)

plot_df = filt.head(top_n)

# ---------- KPI row ----------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Ingredients shown", f"{plot_df['Ingredient'].nunique():,}")
with k2:
    st.metric("Shipments (rows)", f"{len(plot_df):,}")
with k3:
    st.metric("Avg per item (monthly)", f"{plot_df['Total monthly shipment'].mean():,.0f}")
with k4:
    st.metric("Total (monthly)", f"{plot_df['Total monthly shipment'].sum():,.0f}")

# ---------- Chart ----------
if plot_df.empty:
    st.warning("No results match your filters.")
else:
    # consistent label orientation & elegant style
    alt.themes.enable("none")

    sort_dir = "y" if ascending and sort_col == "Total monthly shipment" else "-y"
    if sort_col.startswith("Ingredient"):
        sort_dir = "x" if ascending else "-x"

    chart = (
        alt.Chart(plot_df)
        .mark_bar(size=22, cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#500000")
        .encode(
            x=alt.X(
                "Ingredient:N",
                title="Ingredient",
                sort="-y",  # keep tallest-first reading; the sort of categories follows y
                axis=alt.Axis(labelAngle=0, labelLimit=220)
            ),
            y=alt.Y("Total monthly shipment:Q", title="Total per Month"),
            tooltip=[
                alt.Tooltip("Ingredient:N"),
                alt.Tooltip("Unit of shipment:N", title="Unit of Shipment"),
                alt.Tooltip("Quantity per shipment:Q", title="Quantity per Shipment"),
                alt.Tooltip("Number of shipments:Q", title="Number of Shipments"),
                alt.Tooltip("frequency:N", title="Order Frequency"),
                alt.Tooltip("Total monthly shipment:Q", title="Total per Month", format=",.0f"),
            ],
        )
        .properties(height=440)
        .interactive()
    )

    # subtle guide line for reference
    rule = alt.Chart(plot_df).mark_rule(strokeDash=[2,4], opacity=0.4).encode(y="mean(Total monthly shipment):Q")
    st.altair_chart(chart + rule, use_container_width=True)

# ---------- Data table + download ----------
with st.expander("📄 Raw data (filtered)"):
    st.dataframe(
        plot_df[
            [
                "Ingredient",
                "Unit of shipment",
                "Quantity per shipment",
                "Number of shipments",
                "frequency",
                "Total monthly shipment",
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    @st.cache_data
    def to_csv(df_): return df_.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        data=to_csv(plot_df),
        file_name="shipments_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

# ---------- Footnote ----------
st.caption("Tip: Use the sidebar to combine search, frequency, and sorting for faster exploration.")
