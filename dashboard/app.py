import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os

# ── DEBUG (optional, can remove later) ──
st.write("Current working dir:", os.getcwd())
st.write("Files:", os.listdir())

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="Dubai Real Estate Market Pulse",
    page_icon="🏙️",
    layout="wide",
)

# ── PATH FIX (VERY IMPORTANT) ──
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "src" / "data" / "processed"

# ── LOAD DATA ──
@st.cache_data
def load_data():
    txn = pd.read_csv(PROCESSED_DIR / "transactions_features.csv", parse_dates=["date"])
    summary = pd.read_csv(PROCESSED_DIR / "community_summary.csv")
    overview = pd.read_csv(PROCESSED_DIR / "market_overview.csv")
    return txn, summary, overview

# ── FORMAT FUNCTION ──
def fmt_aed(val):
    if val >= 1e9:
        return f"AED {val/1e9:.1f}Bn"
    if val >= 1e6:
        return f"AED {val/1e6:.1f}M"
    return f"AED {val:,.0f}"

# ── LOAD ──
txn, summary, overview = load_data()

# ── UI ──
st.title("🏙️ Dubai Real Estate Market Pulse")
st.caption("DLD transaction data · 20 communities · Q1 2022 – Q4 2024")

st.divider()

# ── KPI ──
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Transactions", f"{len(txn):,}")
k2.metric("Total Volume", fmt_aed(txn["price_aed"].sum()))
k3.metric("Median Price/sqft", f"AED {txn['price_per_sqft'].median():,.0f}")
k4.metric("Avg Gross ROI", f"{txn['gross_roi_pct'].mean():.1f}%")
k5.metric("Communities", txn["community"].nunique())

st.divider()

# ── SIDEBAR ──
st.sidebar.header("Filters")

quarters = sorted(txn["quarter"].unique(), key=lambda q: (int(q[-4:]), int(q[1])))
sel_q = st.sidebar.multiselect("Quarter", quarters, default=quarters[-4:])
sel_tier = st.sidebar.multiselect("Tier", txn["tier"].unique(), default=list(txn["tier"].unique()))
sel_type = st.sidebar.multiselect("Property Type", txn["property_type"].unique(), default=list(txn["property_type"].unique()))

filtered = txn[
    (txn["quarter"].isin(sel_q)) &
    (txn["tier"].isin(sel_tier)) &
    (txn["property_type"].isin(sel_type))
]

# ── TABS ──
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Market Overview",
    "🏘️ Community Deep-Dive",
    "💰 ROI Calculator",
    "📈 Price Trends",
])

# ── TAB 1 ──
with tab1:
    st.subheader("Price per sqft by community")

    community_psf = (
        filtered.groupby("community")["price_per_sqft"]
        .median()
        .sort_values()
        .reset_index()
    )

    fig = px.bar(
        community_psf,
        x="price_per_sqft",
        y="community",
        orientation="h",
        color="price_per_sqft"
    )

    st.plotly_chart(fig, use_container_width=True)

# (rest of your code can stay same — no issue)