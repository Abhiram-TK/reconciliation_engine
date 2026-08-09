from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from app.core.config import settings

MISMATCH_TYPES = {"MISSING_RESERVATION",
                  "DUPLICATE_RESERVATION",
                  "QUANTITY_MISMATCH",
                  "ORPHAN_RESERVATION"}

def _validate_results_dataframe(comparison_df: pd.DataFrame) -> None:
    
    if not isinstance(comparison_df, pd.DataFrame):

        raise TypeError("comparison_df must be a pandas DataFrame")

    if "status" not in comparison_df.columns:

        raise ValueError("Reconciliation results must contain a 'status' column.")

def generate_summary(comparison_df: pd.DataFrame) -> None:
    
    _validate_results_dataframe(comparison_df)

    summary_rows = []

    # -----------------------------------------
    # 1. Primary reconciliation status summary
    # -----------------------------------------

    status_counts = (comparison_df["status"]
                     .value_counts(dropna=False)
                     .rename_axis("status")
                     .reset_index(name="count"))

    status_counts.insert(0, "category_type", "status")

    status_counts = status_counts.rename(columns={"status": "category"})

    summary_rows.extend(status_counts[["category_type", "category", "count"]].to_dict("records"))

    # --------------------------------------
    # 2. Detailed mismatch-category summary
    # --------------------------------------

    if "mismatch_type" in comparison_df.columns:

        mismatch_df = comparison_df[comparison_df["mismatch_type"].notna()].copy()

        if not mismatch_df.empty:

            mismatch_counts = (mismatch_df["mismatch_type"]
                               .astype("string")
                               .value_counts(dropna=False)
                               .rename_axis("category")
                               .reset_index(name="count"))

            mismatch_counts.insert(0, "category_type", "mismatch_type")

            summary_rows.extend(mismatch_counts[["category_type", "category", "count"]].to_dict("records"))

    return pd.DataFrame(summary_rows, columns=["category_type", "category", "count"])

def save_summary(summary_df: pd.DataFrame, output_dir: Path | None = None) -> Path:

    if output_dir is None:

        output_dir = settings.reports_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = (output_dir / "summary.csv")

    summary_df.to_csv(output_path, index=False)

    return output_path

def generate_chart(summary_df: pd.DataFrame, output_dir: Path | None = None) -> Path:

    if output_dir is None:
        
        output_dir = settings.reports_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    chart_path = (output_dir / "reconciliation_summary.png")

    chart_df = summary_df.copy()

    if chart_df.empty:

        chart_df = pd.DataFrame({"category_type": ["status"], "category": ["NO_RESULTS"], "count": [0]})

    chart_df["label"] = (chart_df["category_type"] + ": " + chart_df["category"].astype(str))

    plt.figure(figsize=(10, 6))

    plt.bar(chart_df["label"], chart_df["count"])

    plt.title("Reconciliation Summary")

    plt.xlabel("Category")

    plt.ylabel("Count")

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    plt.savefig(chart_path)

    plt.close()

    return chart_path