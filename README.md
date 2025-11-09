# TAMU-DATATHON-Project 2025 📊
**Mai-Shan-Yun Inventory Intelligence Challenge** <br/>
Mai-Shan-Yun project is to design and build an interactive dashboard that transforms raw restaurant data into actionable intelligence.

<br/>

## Description:
- Developed a Decision Support System (Streamlit) that integrates item sales, recipe matrices, and supply data to generate precise 3-month ingredient usage forecasts.
- Implemented a predictive analytics pipeline (Python/Prophet) to convert forecasted demand into specific ingredient requirements.
- Automated a constraint analysis module to proactively identify potential supply shortfall risks by comparing projected demand against planned inventory capacity, facilitating optimized procurement and inventory management.

<br/>

## Dashboard purpose and Key Insights 🔑
 - Identify top-profit items and frequently used ingredients.
 - Vizualize ingredient shipments in comparison to monthly ingredient usage.
 - Track monthly profit trends by menu item.
 - Forecast future ingredient demand.

<br/>

## Datasets used and How They were integrated 📈
- Shipments: Tracked total quantities of ingredients received each period of time (by unit) and compared them with monthly ingredient usage to analyze inventory flow.
- Ingredients: Combined with monthly data to identify the most frequently used ingredients and their contribution to profit generation.
- Months: Used to evaluate and visualize item profitability by month and to compare monthly performance with overall averages.


## Technologies used 💻
- Frontend : Streamlit, CSS, HTML
- Backend : Python, Pandas, Prophet (Forecasting Model), Altair 


## Potential Improvements for the Future 
To further increase its accuracy, scope, and strategic value, the following improvements could be implemented:

1. Model and Data Enrichment
Integrate External Variables (Uplift Modeling): Enhance the prediction model (Prophet) by incorporating external time-series data that directly influences demand. <br/>
Local Events and Seasonality: Integrate local calendar data (e.g., major sports games, holidays) that drive foot traffic.  <br/>
Weather Data: Use local weather forecasts (e.g., cold weather correlating with hot ramen sales) to refine short-term predictions.

3. User Experience and Operational Integration
Interactive Simulation Dashboard: Develop a user interface feature that allows managers to run "What-If" simulations.
For example, a manager could input a planned sales increase for "Beef Ramen" and instantly see the projected impact on all dependent ingredient requirements and potential supply risks.  <br/>
Mobile Alerting: Implement a mobile notification system for critical constraint alerts, ensuring that supply shortfall risks are escalated to relevant personnel immediately, even when they are not at their desktop.












