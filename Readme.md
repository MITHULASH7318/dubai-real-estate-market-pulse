🏙️ Dubai Real Estate Market Pulse

An end-to-end data analytics project tracking price trends, rental yields, and investment signals across 20+ Dubai communities using DLD transaction data.
📌 Project Summary
Dubai's real estate market transacts billions of AED every quarter across 20+ communities — yet most investors and analysts rely on lagging reports or gut feel. This project builds a fully automated data pipeline + interactive dashboard that answers:

Which communities offer the best risk-adjusted ROI right now?
Is the off-plan market overheating or presenting opportunity?
How has price per sqft changed year-over-year across tiers?
What is the realistic rental yield for a given budget and community?
🚀 Live Dashboard
→ View Live App on Streamlit Cloud
(Deploy instructions below)

📊 Key Findings (Q4 2024)
MetricValueTotal transactions analysed32,948Communities covered20PeriodQ1 2022 – Q4 2024Market-wide price/sqft growth+37% over 3 yearsHighest ROI communityInternational City (9.2%)Lowest ROI communityPalm Jumeirah (3.5%)Off-plan share Q4 202457% (vs 45% in Q1 2022)Best value communityJumeirah Village Circle — 7.9% ROI at AED 1,150/sqft

🗂️ Project Structure
dubai-real-estate-pulse/
│
├── src/
│   ├── ingest.py           # Generates/downloads DLD transaction data
│   ├── clean.py            # Standardises community names, removes outliers
│   └── features.py         # Engineers price/sqft, ROI, QoQ change, off-plan share
│
├── dashboard/
│   └── app.py              # Streamlit app — 4 pages with sidebar navigation
│
├── data/
│   ├── raw/
│   │   └── dld_transactions.csv
│   └── processed/
│       ├── transactions_clean.csv
│       ├── transactions_features.csv
│       ├── community_summary.csv
│       └── market_overview.csv
│
├── tests/
│   └── test_features.py    # Pytest unit tests for feature engineering
│
├── requirements.txt
└── README.md

⚙️ Setup & Installation
Prerequisites

Python 3.10 or higher
Windows / Mac / Linux

Step 1 — Clone the repository
bashgit clone https://github.com/yourusername/dubai-real-estate-pulse.git
cd dubai-real-estate-pulse
Step 2 — Create and activate virtual environment
Windows:
cmdpython -m venv venv
venv\Scripts\activate
Mac / Linux:
bashpython3 -m venv venv
source venv/bin/activate
Step 3 — Install dependencies
bashpip install -r requirements.txt

▶️ How to Run
Run the scripts in this exact order:
bash# 1. Generate raw transaction data
python src/ingest.py

# 2. Clean and standardise the data
python src/clean.py

# 3. Engineer all analytical features
python src/features.py

# 4. Launch the dashboard
streamlit run dashboard/app.py
The dashboard opens automatically at http://localhost:8501

📋 Dashboard Pages
📊 Market Overview

KPI cards: total transactions, volume, median price/sqft, avg ROI, off-plan share
Horizontal bar charts: price/sqft and ROI ranked by community
Dual-axis trend line: price/sqft vs ROI over 12 quarters
Pie charts: off-plan vs ready split, property type breakdown

🏘️ Community Deep-Dive

Select any of 20 communities from a dropdown
Price/sqft trend line over time
Transaction volume bar chart by quarter
Price distribution histogram
Bedroom type breakdown
ROI vs price/sqft scatter plot
Raw transactions table (latest 200)

💰 ROI Calculator

Inputs: budget, community, property type, LTV, mortgage rate, hold period, capital growth
Outputs: gross ROI, net rent, cash flow, cash-on-cash return, exit value, total return, breakeven years
Dynamic chart: cumulative cash flow vs property value over hold period
Full community ROI ranking table

🏗️ Off-Plan Tracker

Off-plan share trend line (with 50% reference mark)
Off-plan share by community horizontal bar chart
Off-plan vs ready price comparison by community
Volume by tier stacked bar over time
ROI box plot: off-plan vs ready comparison
Off-plan transactions detail table


🧪 Running Tests
bashpytest tests/ -v
Expected output:
tests/test_features.py::test_price_band_columns    PASSED
tests/test_features.py::test_price_band_values     PASSED
tests/test_features.py::test_market_overview_shape PASSED
tests/test_features.py::test_market_overview_totals PASSED
tests/test_features.py::test_roi_positive          PASSED

5 passed in 2.61s

📦 Tech Stack
ToolPurposePython 3.12Core languagePandasData manipulation and aggregationNumPyNumerical computationsStreamlitInteractive dashboardPlotlyCharts and visualisationsPytestUnit testingOpenPyXLExcel export

📐 Key Metrics Engineered
MetricDefinitionprice_per_sqftTransaction price ÷ area in sqftgross_roi_pct(Annual rent ÷ purchase price) × 100qoq_change_pctQuarter-on-quarter % change in median price/sqftoff_plan_share_pct% of transactions that are off-plan per community per quarterprice_bandAffordable / Fair Value / Premium — based on distance from Dubai mediantransaction_velocityNumber of transactions per community per quarter

🗃️ Data Sources
SourceUsageDubai Land Department (DLD)Primary transaction data — price, area, community, typeBayut.comRental listing prices for ROI estimationDubai Statistics CentrePopulation data for demand normalisation

Note: The data in this project is generated to replicate DLD transaction patterns for portfolio demonstration purposes. Structure, column names, and statistical distributions match real DLD open data available at dubailand.gov.ae.