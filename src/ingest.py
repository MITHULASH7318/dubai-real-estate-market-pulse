import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

np.random.seed(42)
random.seed(42)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

COMMUNITIES = {
    "Palm Jumeirah":          {"base_psf": 3200, "base_roi": 3.8, "vol": 80,  "tier": "Luxury"},
    "Downtown Dubai":         {"base_psf": 2700, "base_roi": 5.0, "vol": 180, "tier": "Premium"},
    "DIFC":                   {"base_psf": 2500, "base_roi": 4.2, "vol": 90,  "tier": "Premium"},
    "Dubai Marina":           {"base_psf": 2200, "base_roi": 5.9, "vol": 290, "tier": "Premium"},
    "Business Bay":           {"base_psf": 1950, "base_roi": 5.6, "vol": 240, "tier": "Mid-Market"},
    "Dubai Hills Estate":     {"base_psf": 1800, "base_roi": 4.3, "vol": 200, "tier": "Mid-Market"},
    "Jumeirah Village Circle":{"base_psf": 1150, "base_roi": 7.9, "vol": 320, "tier": "Mid-Market"},
    "Al Barsha":              {"base_psf": 1480, "base_roi": 6.4, "vol": 140, "tier": "Mid-Market"},
    "Jumeirah Lake Towers":   {"base_psf": 1350, "base_roi": 6.8, "vol": 160, "tier": "Mid-Market"},
    "Mirdif":                 {"base_psf": 980,  "base_roi": 6.2, "vol": 110, "tier": "Affordable"},
    "Sports City":            {"base_psf": 920,  "base_roi": 7.3, "vol": 130, "tier": "Affordable"},
    "Silicon Oasis":          {"base_psf": 890,  "base_roi": 7.1, "vol": 120, "tier": "Affordable"},
    "Discovery Gardens":      {"base_psf": 760,  "base_roi": 8.5, "vol": 90,  "tier": "Affordable"},
    "Deira":                  {"base_psf": 870,  "base_roi": 6.9, "vol": 100, "tier": "Affordable"},
    "Bur Dubai":              {"base_psf": 910,  "base_roi": 6.6, "vol": 95,  "tier": "Affordable"},
    "International City":     {"base_psf": 650,  "base_roi": 9.2, "vol": 75,  "tier": "Affordable"},
    "Arjan":                  {"base_psf": 1020, "base_roi": 7.0, "vol": 85,  "tier": "Affordable"},
    "Dubai South":            {"base_psf": 830,  "base_roi": 6.5, "vol": 70,  "tier": "Affordable"},
    "Damac Hills":            {"base_psf": 1100, "base_roi": 5.8, "vol": 95,  "tier": "Mid-Market"},
    "Arabian Ranches":        {"base_psf": 1600, "base_roi": 4.9, "vol": 85,  "tier": "Mid-Market"},
}

QUARTERS = [
    "Q1 2022","Q2 2022","Q3 2022","Q4 2022",
    "Q1 2023","Q2 2023","Q3 2023","Q4 2023",
    "Q1 2024","Q2 2024","Q3 2024","Q4 2024",
]

GROWTH_RATES = [0.02,0.025,0.03,0.028,0.03,0.032,0.031,0.029,0.027,0.025,0.022,0.020]

PROP_TYPES   = ["Apartment", "Villa", "Townhouse"]
PROP_WEIGHTS = [0.65, 0.20, 0.15]


def generate_transactions():
    rows = []
    txn_id = 100000

    for community, cfg in COMMUNITIES.items():
        cum_growth = 1.0
        for qi, (q, gr) in enumerate(zip(QUARTERS, GROWTH_RATES)):
            cum_growth *= (1 + gr)
            q_psf = cfg["base_psf"] * cum_growth * np.random.normal(1.0, 0.03)
            n     = int(cfg["vol"] * np.random.uniform(0.85, 1.15))
            qn    = int(q[1])
            yr    = int(q[-4:])
            q_start = datetime(yr, (qn - 1) * 3 + 1, 1)

            for _ in range(n):
                pt = np.random.choice(PROP_TYPES, p=PROP_WEIGHTS)

                if pt == "Apartment":
                    sz = np.random.choice(
                        [450,600,750,900,1100,1400,1800,2200],
                        p=[0.05,0.15,0.25,0.25,0.15,0.08,0.05,0.02]
                    )
                elif pt == "Villa":
                    sz = np.random.choice(
                        [2000,2500,3000,3500,4000,5000],
                        p=[0.10,0.20,0.30,0.20,0.15,0.05]
                    )
                else:
                    sz = np.random.choice(
                        [1400,1600,1800,2000,2200,2500],
                        p=[0.15,0.25,0.25,0.20,0.10,0.05]
                    )

                psf   = q_psf * np.random.normal(1.0, 0.08)
                price = int(psf * sz / 1000) * 1000

                off_plan = "Off-Plan" if np.random.random() < (0.45 + qi * 0.01) else "Ready"
                txn_date = q_start + timedelta(days=random.randint(0, 89))
                beds     = 0 if (pt == "Apartment" and sz < 600) else (
                           1 if sz < 900 else (2 if sz < 1400 else (3 if sz < 2200 else 4)))
                roi      = cfg["base_roi"] * np.random.normal(1.0, 0.05)

                rows.append({
                    "transaction_id":      f"DLD-{txn_id}",
                    "date":                txn_date.strftime("%Y-%m-%d"),
                    "quarter":             q,
                    "year":                yr,
                    "community":           community,
                    "tier":                cfg["tier"],
                    "property_type":       pt,
                    "bedrooms":            beds,
                    "area_sqft":           sz,
                    "price_aed":           price,
                    "price_per_sqft":      round(price / sz, 2),
                    "transaction_type":    off_plan,
                    "gross_roi_pct":       round(roi, 2),
                    "annual_rent_est_aed": round(price * roi / 100, -3),
                })
                txn_id += 1

    return pd.DataFrame(rows)


def main():
    print("Generating DLD transaction data...")
    df = generate_transactions()
    out_path = RAW_DIR / "dld_transactions.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df):,} transactions → {out_path}")


if __name__ == "__main__":
    main()