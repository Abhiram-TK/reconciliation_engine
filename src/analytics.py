import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

def generate_summary(comparison_df):

    summary_df = (comparison_df["status"].value_counts().reset_index())

    summary_df.columns = ["Status", "Count"]

    return summary_df

def save_summary(summary_df):

    BASE_DIR = Path(__file__).resolve().parent.parent

    REPORTS_DIR = BASE_DIR / "reports"

    summary_df.to_csv(REPORTS_DIR / "summary.csv", index=False)

def generate_chart(summary_df):

    plt.figure(figsize=(8,5))

    plt.bar(summary_df["Status"], summary_df["Count"])

    plt.title("Reconciliation Summary")

    plt.xlabel("Status")
    plt.ylabel("Record Count")

    BASE_DIR = Path(__file__).resolve().parent.parent

    REPORTS_DIR = BASE_DIR / "reports"

    plt.savefig(REPORTS_DIR / "reconciliation_summary.png")

    plt.close()