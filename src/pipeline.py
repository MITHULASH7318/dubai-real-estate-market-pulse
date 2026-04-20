from ingestion.ingest import load_dld_data
from cleaning.clean import standardise_community
from features.features import prepare_features

def run_pipeline():
    df = load_dld_data("dld_transactions.csv")

    df = standardise_community(df)
    df = prepare_features(df)

    df.to_csv("data/processed/cleaned_data.csv", index=False)

    print("✅ Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()