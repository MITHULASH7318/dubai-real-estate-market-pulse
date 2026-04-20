import pkg_resources
st.write([pkg.key for pkg in pkg_resources.working_set])
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import subprocess

subprocess.run(["pip", "install", "plotly"])

st.set_page_config(
    page_title="Dubai Real Estate Market Pulse",
    page_icon="🏙️",
    layout="wide",
)

PROCESSED_DIR = Path("c:/dubai-real-estate-pulse/src/data/processed")


@st.cache_data
def load_data():
    txn      = pd.read_csv(PROCESSED_DIR / "transactions_features.csv", parse_dates=["date"])
    summary  = pd.read_csv(PROCESSED_DIR / "community_summary.csv")
    overview = pd.read_csv(PROCESSED_DIR / "market_overview.csv")
    return txn, summary, overview


def fmt_aed(val):
    if val >= 1e9:
        return f"AED {val/1e9:.1f}Bn"
    if val >= 1e6:
        return f"AED {val/1e6:.1f}M"
    return f"AED {val:,.0f}"


txn, summary, overview = load_data()

st.title("🏙️ Dubai Real Estate Market Pulse")
st.caption("DLD transaction data · 20 communities · Q1 2022 – Q4 2024")

st.divider()

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Transactions",  f"{len(txn):,}")
k2.metric("Total Volume",        fmt_aed(txn["price_aed"].sum()))
k3.metric("Median Price/sqft",   f"AED {txn['price_per_sqft'].median():,.0f}")
k4.metric("Avg Gross ROI",       f"{txn['gross_roi_pct'].mean():.1f}%")
k5.metric("Communities",         txn["community"].nunique())

st.divider()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")

quarters   = sorted(txn["quarter"].unique(), key=lambda q: (int(q[-4:]), int(q[1])))
sel_q      = st.sidebar.multiselect("Quarter", quarters, default=quarters[-4:])
sel_tier   = st.sidebar.multiselect("Tier", txn["tier"].unique(), default=list(txn["tier"].unique()))
sel_type   = st.sidebar.multiselect("Property Type", txn["property_type"].unique(), default=list(txn["property_type"].unique()))

mask = (
    txn["quarter"].isin(sel_q) &
    txn["tier"].isin(sel_tier) &
    txn["property_type"].isin(sel_type)
)
filtered = txn[mask]

# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Market Overview",
    "🏘️ Community Deep-Dive",
    "💰 ROI Calculator",
    "📈 Price Trends",
])

# ─── Tab 1: Market Overview ───────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Price per sqft by community")
        community_psf = (
            filtered.groupby("community")["price_per_sqft"]
            .median()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig = px.bar(
            community_psf,
            x="price_per_sqft",
            y="community",
            orientation="h",
            labels={"price_per_sqft": "Median AED/sqft", "community": ""},
            color="price_per_sqft",
            color_continuous_scale="Teal",
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Gross ROI by community")
        community_roi = (
            filtered.groupby(["community","tier"])["gross_roi_pct"]
            .mean()
            .reset_index()
            .sort_values("gross_roi_pct", ascending=True)
        )
        fig2 = px.bar(
            community_roi,
            x="gross_roi_pct",
            y="community",
            orientation="h",
            color="tier",
            labels={"gross_roi_pct": "Avg Gross ROI (%)", "community": ""},
            color_discrete_map={
                "Luxury": "#E8D5B7",
                "Premium": "#85B7EB",
                "Mid-Market": "#5DCAA5",
                "Affordable": "#888780",
            },
        )
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Quarterly market trend")
    fig3 = px.line(
        overview,
        x="quarter",
        y=["median_psf", "avg_roi_pct"],
        markers=True,
        labels={"value": "Value", "quarter": "Quarter", "variable": "Metric"},
    )
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Off-plan vs ready split")
    off_plan_data = (
        filtered["transaction_type"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "type", "transaction_type": "count"})
    )
    fig4 = px.pie(
        filtered,
        names="transaction_type",
        color_discrete_sequence=["#378ADD", "#E1F5EE"],
        hole=0.5,
    )
    fig4.update_layout(height=320)
    st.plotly_chart(fig4, use_container_width=True)


# ─── Tab 2: Community Deep-Dive ───────────────────────────────────────────────
with tab2:
    community = st.selectbox("Select community", sorted(txn["community"].unique()))
    cd = filtered[filtered["community"] == community]

    if cd.empty:
        st.warning("No data for this selection. Adjust the sidebar filters.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Transactions",     f"{len(cd):,}")
        m2.metric("Median Price/sqft",f"AED {cd['price_per_sqft'].median():,.0f}")
        m3.metric("Avg Gross ROI",    f"{cd['gross_roi_pct'].mean():.1f}%")
        m4.metric("Off-Plan Share",   f"{len(cd[cd['transaction_type']=='Off-Plan'])/len(cd)*100:.0f}%")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Price/sqft over time")
            psf_trend = (
                cd.groupby("quarter")["price_per_sqft"]
                .median()
                .reset_index()
            )
            fig = px.line(psf_trend, x="quarter", y="price_per_sqft", markers=True,
                          labels={"price_per_sqft": "Median AED/sqft", "quarter": ""})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Transaction volume over time")
            vol_trend = cd.groupby("quarter").size().reset_index(name="transactions")
            fig = px.bar(vol_trend, x="quarter", y="transactions",
                         labels={"transactions": "No. of transactions", "quarter": ""})
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Price distribution")
        fig = px.histogram(cd, x="price_per_sqft", nbins=40,
                           labels={"price_per_sqft": "AED per sqft"},
                           color_discrete_sequence=["#378ADD"])
        st.plotly_chart(fig, use_container_width=True)


# ─── Tab 3: ROI Calculator ────────────────────────────────────────────────────
with tab3:
    st.subheader("Investment ROI calculator")
    col1, col2 = st.columns(2)

    with col1:
        budget    = st.slider("Budget (AED)", 500_000, 10_000_000, 1_500_000, step=50_000)
        sel_comm  = st.selectbox("Community", sorted(txn["community"].unique()), key="roi_comm")
        sel_ptype = st.radio("Property type", ["Apartment", "Villa", "Townhouse"])

    band = (budget * 0.8, budget * 1.2)
    roi_data = txn[
        (txn["community"] == sel_comm) &
        (txn["property_type"] == sel_ptype) &
        (txn["price_aed"].between(*band))
    ]

    with col2:
        if roi_data.empty:
            st.warning("No transactions found in this price range for the selected filters.")
        else:
            roi_val  = roi_data["gross_roi_pct"].median()
            psf_val  = roi_data["price_per_sqft"].median()
            ann_rent = budget * roi_val / 100
            breakeven = budget / ann_rent if ann_rent > 0 else 0

            r1, r2 = st.columns(2)
            r1.metric("Gross ROI",         f"{roi_val:.1f}%")
            r2.metric("Price/sqft",        f"AED {psf_val:,.0f}")
            r1.metric("Est. Annual Rent",  fmt_aed(ann_rent))
            r2.metric("Break-even",        f"{breakeven:.1f} years")

            st.caption(f"Based on {len(roi_data):,} comparable transactions")

    st.subheader("All communities ranked by ROI")
    roi_rank = (
        txn.groupby(["community", "tier"])["gross_roi_pct"]
        .mean()
        .reset_index()
        .sort_values("gross_roi_pct", ascending=False)
        .round(2)
    )
    roi_rank.columns = ["Community", "Tier", "Avg Gross ROI (%)"]
    st.dataframe(roi_rank, use_container_width=True, hide_index=True)


# ─── Tab 4: Price Trends ──────────────────────────────────────────────────────
with tab4:
    st.subheader("Price per sqft heatmap — community vs quarter")

    pivot = (
        summary.pivot_table(
            index="community", columns="quarter",
            values="median_psf", aggfunc="mean"
        )
        .round(0)
    )

    quarters_ordered = sorted(pivot.columns, key=lambda q: (int(q[-4:]), int(q[1])))
    pivot = pivot[quarters_ordered]

    fig = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        labels={"color": "AED/sqft"},
        aspect="auto",
        height=600,
    )
    fig.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("YoY price change by community (latest year)")
    yoy = (
        summary[summary["qoq_change_pct"].notna()]
        .groupby("community")["qoq_change_pct"]
        .mean()
        .reset_index()
        .sort_values("qoq_change_pct", ascending=False)
    )
    yoy["color"] = yoy["qoq_change_pct"].apply(lambda x: "Positive" if x >= 0 else "Negative")
    fig = px.bar(
        yoy, x="community", y="qoq_change_pct",
        color="color",
        color_discrete_map={"Positive": "#1D9E75", "Negative": "#E24B4A"},
        labels={"qoq_change_pct": "Avg QoQ Change (%)", "community": ""},
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True)