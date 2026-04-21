import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ─────────────────────────────────────
# STREAMLIT CONFIG (MUST BE FIRST)
# ─────────────────────────────────────
st.set_page_config(
    page_title="Dubai Real Estate Market Pulse",
    page_icon="🏙️",
    layout="wide",
)

# ─────────────────────────────────────
# FIXED PATH (LOCAL + DEPLOY SAFE)
# ─────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT_DIR / "data" / "processed"


# ─────────────────────────────────────
# SAFE DATA LOADER
# ─────────────────────────────────────
@st.cache_data
def load_data():
    try:
        txn = pd.read_csv(PROCESSED_DIR / "transactions_features.csv", parse_dates=["date"])
        summary = pd.read_csv(PROCESSED_DIR / "community_summary.csv")
        overview = pd.read_csv(PROCESSED_DIR / "market_overview.csv")
        return txn, summary, overview

    except Exception as e:
        st.error("❌ Data not found. Check folder structure.")
        st.stop()


def fmt_aed(val):
    if val >= 1e9:
        return f"AED {val/1e9:.1f}Bn"
    if val >= 1e6:
        return f"AED {val/1e6:.1f}M"
    return f"AED {val:,.0f}"


txn, summary, overview = load_data()

# ─────────────────────────────────────
# TITLE
# ─────────────────────────────────────
st.title("🏙️ Dubai Real Estate Market Pulse")
st.caption("DLD transaction data · 2022–2024")

st.divider()

# ─────────────────────────────────────
# KPI SECTION (SAFE)
# ─────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Transactions", f"{len(txn):,}")
k2.metric("Total Volume", fmt_aed(txn["price_aed"].sum()))
k3.metric("Median Price/sqft", f"AED {txn['price_per_sqft'].median():,.0f}")
k4.metric("Avg ROI", f"{txn['gross_roi_pct'].mean():.1f}%")
k5.metric("Communities", txn["community"].nunique())

st.divider()

# ─────────────────────────────────────
# FILTERS
# ─────────────────────────────────────
st.sidebar.header("Filters")

quarters = sorted(txn["quarter"].unique())
sel_q = st.sidebar.multiselect("Quarter", quarters, default=quarters[-4:])
sel_tier = st.sidebar.multiselect("Tier", txn["tier"].unique(), default=list(txn["tier"].unique()))
sel_type = st.sidebar.multiselect("Property Type", txn["property_type"].unique(), default=list(txn["property_type"].unique()))

filtered = txn[
    (txn["quarter"].isin(sel_q)) &
    (txn["tier"].isin(sel_tier)) &
    (txn["property_type"].isin(sel_type))
]

# ─────────────────────────────────────
# TABS
# ─────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Market Overview",
    "🏘️ Community",
    "💰 ROI",
    "📈 Trends"
])

# ─────────────────────────────────────
# TAB 1
# ─────────────────────────────────────
with tab1:

    st.subheader("Price per sqft")

    psf = filtered.groupby("community")["price_per_sqft"].median().reset_index()

    st.plotly_chart(
        px.bar(psf, x="price_per_sqft", y="community", orientation="h"),
        use_container_width=True
    )

    st.subheader("ROI")

    roi = filtered.groupby("community")["gross_roi_pct"].mean().reset_index()

    st.plotly_chart(
        px.bar(roi, x="gross_roi_pct", y="community", orientation="h"),
        use_container_width=True
    )

    st.subheader("Market Trend")

    st.plotly_chart(
        px.line(overview, x="quarter", y=["median_psf", "avg_roi_pct"], markers=True),
        use_container_width=True
    )

# ─────────────────────────────────────
# TAB 2
# ─────────────────────────────────────
with tab2:

    community = st.selectbox("Community", sorted(txn["community"].unique()))
    cd = filtered[filtered["community"] == community]

    if cd.empty:
        st.warning("No data")
    else:
        st.metric("Transactions", len(cd))

        st.plotly_chart(
            px.line(cd.groupby("quarter")["price_per_sqft"].median().reset_index(),
                    x="quarter", y="price_per_sqft"),
            use_container_width=True
        )

# ─────────────────────────────────────
# TAB 3
# ─────────────────────────────────────
with tab3:

    budget = st.slider("Budget", 500000, 10000000, 1500000)

    roi_val = txn["gross_roi_pct"].median()
    st.metric("ROI", f"{roi_val:.2f}%")
    st.metric("Annual Return", fmt_aed(budget * roi_val / 100))

# ─────────────────────────────────────
# TAB 4
# ─────────────────────────────────────
with tab4:

    pivot = summary.pivot_table(
        index="community",
        columns="quarter",
        values="median_psf"
    )

    st.plotly_chart(px.imshow(pivot), use_container_width=True)