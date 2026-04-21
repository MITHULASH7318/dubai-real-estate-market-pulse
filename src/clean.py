import pandas as pd
from pathlib import Path

RAW_DIR       = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

COMMUNITY_MAP = {
    "DUBAI MARINA":            "Dubai Marina",
    "MARSA DUBAI":             "Dubai Marina",
    "DOWNTOWN DUBAI":          "Downtown Dubai",
    "BURJ KHALIFA":            "Downtown Dubai",
    "JUMEIRAH VILLAGE CIRCLE": "Jumeirah Village Circle",
    "JVC":                     "Jumeirah Village Circle",
    "BUSINESS BAY":            "Business Bay",
    "PALM JUMEIRAH":           "Palm Jumeirah",
    "DUBAI HILLS ESTATE":      "Dubai Hills Estate",
    "AL BARSHA":               "Al Barsha",
    "JUMEIRAH LAKE TOWERS":    "Jumeirah Lake Towers",
    "JLT":                     "Jumeirah Lake Towers",
    "DIFC":                    "DIFC",
    "SILICON OASIS":           "Silicon Oasis",
    "DISCOVERY GARDENS":       "Discovery Gardens",
    "INTERNATIONAL CITY":      "International City",
    "SPORTS CITY":             "Sports City",
    "MIRDIF":                  "Mirdif",
    "DEIRA":                   "Deira",
    "BUR DUBAI":               "Bur Dubai",
    "DAMAC HILLS":             "Damac Hills",
    "ARABIAN RANCHES":         "Arabian Ranches",
    "ARJAN":                   "Arjan",
    "DUBAI SOUTH":             "Dubai South",
}


def load_raw(filename="dld_transactions.csv") -> pd.DataFrame:
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Raw data not found at {path}. Run src/ingest.py first."
        )
    return pd.read_csv(path)


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["year"].astype(int)
    df["price_aed"] = pd.to_numeric(df["price_aed"], errors="coerce")
    df["area_sqft"] = pd.to_numeric(df["area_sqft"], errors="coerce")
    df["gross_roi_pct"] = pd.to_numeric(df["gross_roi_pct"], errors="coerce")

    df = df.dropna(subset=["price_aed", "area_sqft", "date"])

    df = df[df["price_per_sqft"].between(200, 12000)]
    df = df[df["area_sqft"].between(200, 10000)]
    df = df[df["price_aed"] > 0]

    if "community_raw" in df.columns:
        df["community"] = (
            df["community_raw"]
            .str.upper()
            .str.strip()
            .map(COMMUNITY_MAP)
            .fillna("Other")
        )

    df["price_per_sqft"] = (df["price_aed"] / df["area_sqft"]).round(2)

    return df.reset_index(drop=True)


def main():
    print("Loading raw data...")
    df = load_raw()
    print(f"Raw rows: {len(df):,}")

    print("Cleaning...")
    df_clean = clean_transactions(df)
    print(f"Clean rows: {len(df_clean):,}")

    out_path = PROCESSED_DIR / "transactions_clean.csv"
    df_clean.to_csv(out_path, index=False)
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()