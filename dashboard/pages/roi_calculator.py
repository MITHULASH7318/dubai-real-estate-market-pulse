import streamlit as st
import pandas as pd

def render(df: pd.DataFrame):
    st.subheader("ROI calculator")
    community = st.selectbox("Community", sorted(df["community"].unique()))
    prop_type = st.radio("Property type", ["Apartment", "Villa", "Townhouse"])
    budget = st.slider("Budget (AED)", 500_000, 10_000_000, 1_500_000, step=50_000)

    filtered = df[
        (df["community"] == community) &
        (df["property_type"] == prop_type) &
        (df["price"].between(budget * 0.85, budget * 1.15))
    ]

    if filtered.empty:
        st.warning("No transactions found in this range — try widening the budget.")
        return

    roi = filtered["roi_gross"].median()
    psf = filtered["price_per_sqft"].median()

    col1, col2, col3 = st.columns(3)
    col1.metric("Gross ROI", f"{roi:.1f}%")
    col2.metric("Price / sqft", f"AED {psf:,.0f}")
    col3.metric("Transactions", len(filtered))