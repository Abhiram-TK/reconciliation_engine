import pandas as pd
import matplotlib.pyplot as plt

from app.core.config import REPORTS_DIR, CHARTS_DIR

def generate_summary(comparison_df):

    summary_df = (comparison_df["status"].value_counts().reset_index())

    summary_df.columns = ["Status", "Count"]

    return summary_df

def save_summary(summary_df):

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(REPORTS_DIR / "summary.csv", index=False)

def generate_chart(summary_df):

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8,5))

    plt.bar(summary_df["Status"], summary_df["Count"])

    plt.title("Reconciliation Summary")

    plt.xlabel("Status")
    plt.ylabel("Record Count")

    plt.tight_layout()

    plt.savefig(CHARTS_DIR / "reconciliation_summary.png")

    plt.close()