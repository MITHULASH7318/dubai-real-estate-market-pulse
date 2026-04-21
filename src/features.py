import pandas as pd
import numpy as np
from pathlib import Path

# Hardcoded paths — works regardless of where you run from
BASE_DIR      = Path("c:/dubai-real-estate-pulse")
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_clean() -> pd.DataFrame:
    path = PROCESSED_DIR / "transactions_clean.csv"
    print(f"Looking for: {path}")
    if not path.exists():
        raise FileNotFoundError(f"Not found: {path}  — run clean.py first")
    return pd.read_csv(path, parse_dates=["date"])


def add_price_band(df: pd.DataFrame) -> pd.DataFrame:
    median_psf = df["price_per_sqft"].median()
    df["price_band"] = pd.cut(
        df["price_per_sqft"],
        bins=[0, median_psf * 0.75, median_psf * 1.25, float("inf")],
        labels=["Affordable", "Fair Value", "Premium"],
    )
    return df


def compute_community_summary(df: pd.DataFrame) -> pd.DataFrame:
    quarters = sorted(df["quarter"].unique().tolist(),
                      key=lambda q: (int(q[-4:]), int(q[1])))
    rows = []
    for community in df["community"].unique():
        cd = df[df["community"] == community]
        for q in quarters:
            qd = cd[cd["quarter"] == q]
            if len(qd) == 0:
                continue
            qi = quarters.index(q)
            prev_psf = None
            if qi > 0:
                pqd = cd[cd["quarter"] == quarters[qi - 1]]
                if len(pqd) > 0:
                    prev_psf = pqd["price_per_sqft"].median()
            curr_psf = qd["price_per_sqft"].median()
            qoq = round((curr_psf - prev_psf) / prev_psf * 100, 2) if prev_psf else None
            rows.append({
                "quarter":            q,
                "year":               int(q[-4:]),
                "community":          community,
                "tier":               qd["tier"].iloc[0],
                "transactions":       len(qd),
                "median_psf":         round(curr_psf, 0),
                "qoq_change_pct":     qoq,
                "median_price_aed":   round(qd["price_aed"].median(), -3),
                "total_volume_aed":   round(qd["price_aed"].sum(), -3),
                "avg_roi_pct":        round(qd["gross_roi_pct"].mean(), 2),
                "off_plan_share_pct": round(
                    len(qd[qd["transaction_type"] == "Off-Plan"]) / len(qd) * 100, 1),
                "avg_area_sqft":      round(qd["area_sqft"].mean(), 0),
            })
    return pd.DataFrame(rows)


def compute_market_overview(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for q in sorted(df["quarter"].unique(),
                    key=lambda q: (int(q[-4:]), int(q[1]))):
        qd = df[df["quarter"] == q]
        rows.append({
            "quarter":             q,
            "year":                int(q[-4:]),
            "total_transactions":  len(qd),
            "total_volume_aed_bn": round(qd["price_aed"].sum() / 1e9, 2),
            "median_psf":          round(qd["price_per_sqft"].median(), 0),
            "avg_roi_pct":         round(qd["gross_roi_pct"].mean(), 2),
            "off_plan_share_pct":  round(
                len(qd[qd["transaction_type"] == "Off-Plan"]) / len(qd) * 100, 1),
            "apartment_share_pct": round(
                len(qd[qd["property_type"] == "Apartment"]) / len(qd) * 100, 1),
            "villa_share_pct":     round(
                len(qd[qd["property_type"] == "Villa"]) / len(qd) * 100, 1),
        })
    return pd.DataFrame(rows)


def main():
    print(f"Saving to: {PROCESSED_DIR}")

    print("Loading clean data...")
    df = load_clean()
    print(f"Loaded {len(df):,} rows")

    print("Engineering features...")
    df = add_price_band(df)
    out1 = PROCESSED_DIR / "transactions_features.csv"
    df.to_csv(out1, index=False)
    print(f"Saved → {out1}")

    print("Building community summary...")
    summary = compute_community_summary(df)
    out2 = PROCESSED_DIR / "community_summary.csv"
    summary.to_csv(out2, index=False)
    print(f"Saved → {out2}")

    print("Building market overview...")
    overview = compute_market_overview(df)
    out3 = PROCESSED_DIR / "market_overview.csv"
    overview.to_csv(out3, index=False)
    print(f"Saved → {out3}")

    print("\nAll features done.")


if __name__ == "__main__":
    main()