import streamlit as st

# ✅ MUST BE FIRST STREAMLIT COMMAND (ONLY ONCE)
st.set_page_config(
    page_title="Dubai Real Estate Market Pulse",
    page_icon="🏙️",
    layout="wide",
)

import pandas as pd
import plotly.express as px
from pathlib import Path

# ✅ PATH FIX (CLOUD SAFE)
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "src" / "data" / "processed"

# ✅ LOAD DATA
@st.cache_data
def load_data():
    txn_path = PROCESSED_DIR / "transactions_features.csv"
    summary_path = PROCESSED_DIR / "community_summary.csv"
    overview_path = PROCESSED_DIR / "market_overview.csv"

    # Debug check (will show if file missing)
    st.write("Looking for files in:", PROCESSED_DIR)

    if not txn_path.exists():
        st.error(f"Missing file: {txn_path}")
        st.stop()

    txn = pd.read_csv(txn_path, parse_dates=["date"])
    summary = pd.read_csv(summary_path)
    overview = pd.read_csv(overview_path)

    return txn, summary, overview


# ✅ FORMAT
def fmt_aed(val):
    if val >= 1e9:
        return f"AED {val/1e9:.1f}Bn"
    if val >= 1e6:
        return f"AED {val/1e6:.1f}M"
    return f"AED {val:,.0f}"


# ✅ LOAD DATA
txn, summary, overview = load_data()

# ✅ UI
st.title("🏙️ Dubai Real Estate Market Pulse")
st.caption("DLD transaction data · 20 communities · Q1 2022 – Q4 2024")

st.divider()

# ✅ KPI
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Transactions", f"{len(txn):,}")
k2.metric("Total Volume", fmt_aed(txn["price_aed"].sum()))
k3.metric("Median Price/sqft", f"AED {txn['price_per_sqft'].median():,.0f}")
k4.metric("Avg Gross ROI", f"{txn['gross_roi_pct'].mean():.1f}%")
k5.metric("Communities", txn["community"].nunique())

st.divider()

# ✅ SIDEBAR
st.sidebar.header("Filters")

quarters = sorted(txn["quarter"].unique())
sel_q = st.sidebar.multiselect("Quarter", quarters, default=quarters)

sel_tier = st.sidebar.multiselect(
    "Tier", txn["tier"].unique(), default=list(txn["tier"].unique())
)

sel_type = st.sidebar.multiselect(
    "Property Type",
    txn["property_type"].unique(),
    default=list(txn["property_type"].unique())
)

filtered = txn[
    (txn["quarter"].isin(sel_q)) &
    (txn["tier"].isin(sel_tier)) &
    (txn["property_type"].isin(sel_type))
]

# ✅ SIMPLE CHART (TEST FIRST)
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
)

st.plotly_chart(fig, use_container_width=True)