# Home.py — Landing page
import streamlit as st
import os
from Gemani_Ai import render_gemini_chat

st.set_page_config(
    page_title="Home • Mai Shan Yun",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#cd1b1b"

# ---------- GLOBAL CSS ----------
st.markdown(
    """
    <style>
    /* Main page gradient background */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #8b0000 100%);
        background-attachment: fixed;
    }

    /* Make main content background transparent so gradient shows */
    .css-18e3th9 {
        background: transparent;
    }

    /* Sidebar solid black */
    section[data-testid="stSidebar"] {
        background-color: #000000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    image_path = os.path.join(os.path.dirname(__file__), "maiShunYun-removebg-preview.jpg")
    st.image(
        image_path,
        width=600,
        use_container_width=False
    )
    st.markdown(
        """
        <h1 style="font-size:42px; line-height:1.15; margin-top:20px; text-align:center; color:white;">
            Mai-Shan-Yun <span class="accent-underline">Vision</span>
        </h1>
        <p style="font-size:18px; color:white; margin-top:14px; max-width:900px; margin-left:auto; margin-right:auto; text-align:center;">
            A data-powered inventory management dashboard that helps restaurant managers
            monitor essentials, compare periods, and keep operations smooth.
        </p>
        """,
        unsafe_allow_html=True,
    )

spacer1, content_col, spacer2 = st.columns([1, 4, 1])

with content_col:
    # First row of links
    row1, row2, row3 = st.columns(3)
    row1.page_link("pages/Shipment_Dashboard.py", label="📦 Shipments Dashboard")
    row2.page_link("pages/Monthly_Category_Income.py", label="💰 Monthly Category Income")
    row3.page_link("pages/Ingredient_Insights.py", label="🧪 Ingredient Insights")
    
    # Second row of links
    row4, row5, row6 = st.columns(3)
    row4.page_link("pages/Menu_Items_Trend.py", label="📈 Menu Items Trend")
    row5.page_link("pages/Network.py", label="🌐 Menu Item Network")
    row6.page_link("pages/Optimization_by_Item.py", label="⚙️ Item Optimization")
    
    # Third row: last link slightly to the right
    row_left, row_center, row_right = st.columns([1.5, 2, 1])
    with row_center:
        st.page_link("pages/Forecasting_Ingredient_Analysis.py", label="🔮 Forecasting Ingredient Analysis")

st.divider()

# ---------- FEATURE CARDS ----------
fc1, fc2 = st.columns(2)
with fc1:
    st.markdown(
        """
        <div class="msy-card" 
             style="background: rgba(255,255,255,0.06); 
                    padding: 18px 24px; 
                    border-radius: 14px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
                    backdrop-filter: blur(4px);">

          <h3 style="color:#e04e4e; margin-bottom:10px; font-weight:600;">
            Fast Overview
          </h3>

          <ul style="opacity:.9; line-height:1.7; font-size:15px; margin-left:20px; padding-left:0;">
            <li><b>Forecasting Ingredient Analysis</b> — Predictions for future ingredient demand</li>
            <li><b>Ingredient Insights</b> — Ingredient usage trends and patterns</li>
            <li><b>Menu Items Trend</b> — Analysis of popular menu items over time</li>
            <li><b>Monthly Category Income</b> — Revenue breakdown by category</li>
            <li><b>Optimization by Item</b> — Profit optimization and performance suggestions</li>
            <li><b>Shipments Dashboard</b> — Comparison of expected vs. actual shipments</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with fc2:
    st.markdown(
        """
        <div class="msy-card" 
             style="background: rgba(255,255,255,0.06); 
                    padding: 18px 24px; 
                    border-radius: 14px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
                    backdrop-filter: blur(4px);">

          <h3 style="color:#e04e4e; margin-bottom:10px; font-weight:600;">
            Actionable Layouts
          </h3>

          <ul style="opacity:.9; line-height:1.7; font-size:15px; margin-left:20px; padding-left:0;">
            <li><b>Visual dashboards</b> — Clear charts highlight performance trends instantly</li>
            <li><b>Comparative reports</b> — Evaluate ingredient usage and category income side-by-side</li>
            <li><b>Smart forecasting tools</b> — Plan inventory and shipments efficiently</li>
            <li><b>Interactive navigation</b> — Jump quickly between pages for focused analysis</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div style="opacity:.65; font-size:13px; padding-top:28px; color:white;">
      Tip: Use the sidebar to switch pages anytime. This home screen is just a clean starting point.
    </div>
    """,
    unsafe_allow_html=True,
)

render_gemini_chat()
