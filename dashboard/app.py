import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -------------------------------
# STREAMLIT CONFIG (MUST BE FIRST)
# -------------------------------
st.set_page_config(
    page_title="Dubai Real Estate Market Pulse",
    page_icon="🏙️",
    layout="wide",
)

# -------------------------------
# SAFE BASE PATH (FIXED FOR DEPLOYMENT)
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent

# If app.py is inside src/
# then data/ is OUTSIDE src
DATA_DIR = BASE_DIR.parent / "data" / "processed"

# -------------------------------
# LOAD DATA SAFELY
# -------------------------------
@st.cache_data
def load_data():
    try:
        txn = pd.read_csv(DATA_DIR / "transactions_features.csv", parse_dates=["date"])
        summary = pd.read_csv(DATA_DIR / "community_summary.csv")
        overview = pd.read_csv(DATA_DIR / "market_overview.csv")
        return txn, summary, overview
    except Exception as e:
        st.error(f"❌ Data loading failed: {e}")
        st.stop()

# -------------------------------
# FORMAT FUNCTION
# -------------------------------
def fmt_aed(val):
    if val >= 1e9:
        return f"AED {val/1e9:.1f}Bn"
    if val >= 1e6:
        return f"AED {val/1e6:.1f}M"
    return f"AED {val:,.0f}"

# -------------------------------
# LOAD DATA
# -------------------------------
txn, summary, overview = load_data()

# -------------------------------
# TITLE
# -------------------------------
st.title("🏙️ Dubai Real Estate Market Pulse")
st.caption("DLD transaction data · 20 communities · Q1 2022 – Q4 2024")

st.divider()

# -------------------------------
# KPI SECTION
# -------------------------------
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Transactions", f"{len(txn):,}")
c2.metric("Total Volume", fmt_aed(txn["price_aed"].sum()))
c3.metric("Median Price/sqft", f"AED {txn['price_per_sqft'].median():,.0f}")
c4.metric("Avg Gross ROI", f"{txn['gross_roi_pct'].mean():.1f}%")
c5.metric("Communities", txn["community"].nunique())

st.divider()

# -------------------------------
# FILTERS
# -------------------------------
st.sidebar.header("Filters")

quarters = sorted(txn["quarter"].unique())
sel_q = st.sidebar.multiselect("Quarter", quarters, default=quarters[-4:])
sel_tier = st.sidebar.multiselect("Tier", txn["tier"].unique(), default=txn["tier"].unique())
sel_type = st.sidebar.multiselect("Property Type", txn["property_type"].unique(), default=txn["property_type"].unique())

filtered = txn[
    (txn["quarter"].isin(sel_q)) &
    (txn["tier"].isin(sel_tier)) &
    (txn["property_type"].isin(sel_type))
]

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Market Overview",
    "🏘️ Community Deep-Dive",
    "💰 ROI Calculator",
    "📈 Price Trends",
])

# -------------------------------
# TAB 1
# -------------------------------
with tab1:
    st.subheader("Price per sqft by community")

    psf = filtered.groupby("community")["price_per_sqft"].median().reset_index()

    fig = px.bar(psf, x="price_per_sqft", y="community", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Gross ROI by community")

    roi = filtered.groupby("community")["gross_roi_pct"].mean().reset_index()

    fig2 = px.bar(roi, x="gross_roi_pct", y="community", orientation="h")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Quarterly trends")

    fig3 = px.line(overview, x="quarter", y=["median_psf", "avg_roi_pct"], markers=True)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Off-plan vs Ready")

    fig4 = px.pie(filtered, names="transaction_type", hole=0.5)
    st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# TAB 2
# -------------------------------
with tab2:
    community = st.selectbox("Select community", txn["community"].unique())
    cd = filtered[filtered["community"] == community]

    if cd.empty:
        st.warning("No data available")
    else:
        st.metric("Transactions", len(cd))

        fig = px.line(
            cd.groupby("quarter")["price_per_sqft"].median().reset_index(),
            x="quarter",
            y="price_per_sqft"
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# TAB 3
# -------------------------------
with tab3:
    budget = st.slider("Budget", 500000, 10000000, 1500000)

    roi_val = txn["gross_roi_pct"].median()
    annual = budget * roi_val / 100

    st.metric("ROI", f"{roi_val:.2f}%")
    st.metric("Annual Rent", fmt_aed(annual))

# -------------------------------
# TAB 4
# -------------------------------
with tab4:
    pivot = summary.pivot_table(
        index="community",
        columns="quarter",
        values="median_psf"
    )

    fig = px.imshow(pivot)
    st.plotly_chart(fig, use_container_width=True)