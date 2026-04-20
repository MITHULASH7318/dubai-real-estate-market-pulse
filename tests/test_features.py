import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from features import add_price_band, compute_market_overview


def make_sample_df():
    return pd.DataFrame({
        "transaction_id":   ["DLD-1", "DLD-2", "DLD-3"],
        "date":             pd.to_datetime(["2023-01-15", "2023-02-20", "2023-03-10"]),
        "quarter":          ["Q1 2023", "Q1 2023", "Q1 2023"],
        "year":             [2023, 2023, 2023],
        "community":        ["Dubai Marina", "JVC", "Downtown Dubai"],
        "tier":             ["Premium", "Mid-Market", "Premium"],
        "property_type":    ["Apartment", "Apartment", "Apartment"],
        "bedrooms":         [2, 1, 2],
        "area_sqft":        [1000, 750, 1100],
        "price_aed":        [2_200_000, 900_000, 2_800_000],
        "price_per_sqft":   [2200.0, 1200.0, 2545.0],
        "transaction_type": ["Ready", "Off-Plan", "Ready"],
        "gross_roi_pct":    [5.9, 7.8, 5.0],
        "annual_rent_est_aed": [129_800, 70_200, 140_000],
    })


def test_price_band_columns():
    df = add_price_band(make_sample_df())
    assert "price_band" in df.columns


def test_price_band_values():
    df = add_price_band(make_sample_df())
    assert set(df["price_band"].dropna()).issubset({"Affordable", "Fair Value", "Premium"})


def test_market_overview_shape():
    df = make_sample_df()
    overview = compute_market_overview(df)
    assert len(overview) == 1
    assert "total_transactions" in overview.columns


def test_market_overview_totals():
    df = make_sample_df()
    overview = compute_market_overview(df)
    assert overview["total_transactions"].iloc[0] == 3


def test_roi_positive():
    df = make_sample_df()
    assert (df["gross_roi_pct"] > 0).all()