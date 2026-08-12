from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from app.core.config import settings

MISMATCH_TYPES = {"MISSING_RESERVATION",
                  "DUPLICATE_RESERVATION",
                  "QUANTITY_MISMATCH",
                  "ORPHAN_RESERVATION"}

SOURCE_SYSTEM = "Project 3 — Sales Transaction Service"
TARGET_SYSTEM = "Project 2 — Inventory Dispatch System"

SOURCE_ENDPOINT = "/internal/transactions"
TARGET_ENDPOINT = "/reservations/reconciliation"

COMPARISON_KEY = "transaction_id"

RESULT_DEFINITIONS = {"MATCHED": ("Sales transaction has a corresponding Inventory reservation and the compared quantities agree."),
                      "MISMATCHED": ("Sales transaction and Inventory reservation participate in the comparison but contain a detected "
                                     "reconciliation discrepancy."),
                      "MISSING": ("Sales transaction exists but no corresponding Inventory reservation exists.")}


MISMATCH_DEFINITIONS = {"QUANTITY_MISMATCH": ("Sales quantity differs from the corresponding reserved quantity."),
                        "DUPLICATE_RESERVATION": ("More than one Inventory reservation exists for the same transaction_id."),
                        "MISSING_RESERVATION": ("A Sales transaction has no corresponding Inventory reservation."),
                        "ORPHAN_RESERVATION": ("An Inventory reservation has no corresponding Sales transaction.")}

SUMMARY_COLUMNS = ["category_type",
                   "category",
                   "count",
                   "definition",
                   "source_system",
                   "source_endpoint",
                   "source_record_count",
                   "target_system",
                   "target_endpoint",
                   "target_record_count",
                   "comparison_key"]

def _validate_results_dataframe(comparison_df: pd.DataFrame) -> None:

    if not isinstance(comparison_df, pd.DataFrame):

        raise TypeError("comparison_df must be a pandas DataFrame")

    if "status" not in comparison_df.columns:

        raise ValueError("Reconciliation results must contain a 'status' column.")

def _default_run_metadata():

    return {"run_id": "UNSPECIFIED",
            "execution_time": "UNSPECIFIED",
            "source": {"project": SOURCE_SYSTEM,
                       "service": "Sales Transaction Service",
                       "endpoint": SOURCE_ENDPOINT,
                       "records_retrieved": "NOT PROVIDED"},
            "target": {"project": TARGET_SYSTEM,
                       "service": "Inventory Dispatch System",
                       "endpoint": TARGET_ENDPOINT,
                       "records_retrieved": "NOT PROVIDED"},
            "reconciliation": {"comparison_key": COMPARISON_KEY}}

def _normalize_run_metadata(run_metadata):

    metadata = _default_run_metadata()

    if run_metadata is None:

        return metadata

    if not isinstance(run_metadata, dict):

        raise TypeError("run_metadata must be a dictionary")

    metadata["run_id"] = run_metadata.get("run_id", metadata["run_id"])

    metadata["execution_time"] = run_metadata.get("execution_time", metadata["execution_time"])

    source = run_metadata.get("source", {})

    if isinstance(source, dict):

        metadata["source"].update(source)

    target = run_metadata.get("target", {})

    if isinstance(target, dict):

        metadata["target"].update(target)

    reconciliation = run_metadata.get("reconciliation", {})

    if isinstance(reconciliation, dict):

        metadata["reconciliation"].update(reconciliation)

    return metadata

def _build_context_row(category_type, category, count, definition, metadata):

    source = metadata["source"]
    target = metadata["target"]
    reconciliation = metadata["reconciliation"]

    return {"category_type": category_type,
            "category": category,
            "count": count,
            "definition": definition,
            "source_system": source.get("project", SOURCE_SYSTEM),
            "source_endpoint": source.get("endpoint", SOURCE_ENDPOINT),
            "source_record_count": source.get("records_retrieved", "NOT PROVIDED"),
            "target_system": target.get("project", TARGET_SYSTEM),
            "target_endpoint": target.get("endpoint", TARGET_ENDPOINT),
            "target_record_count": target.get("records_retrieved", "NOT PROVIDED"),
            "comparison_key": reconciliation.get("comparison_key", COMPARISON_KEY)}

def generate_summary(comparison_df: pd.DataFrame, run_metadata=None) -> pd.DataFrame:

    _validate_results_dataframe(comparison_df)

    metadata = _normalize_run_metadata(run_metadata)

    summary_rows = []

    # -----------------------------------------
    # 1. Primary reconciliation status summary
    # -----------------------------------------

    status_counts = (comparison_df["status"]
                     .value_counts(dropna=False)
                     .rename_axis("status")
                     .reset_index(name="count"))

    for row in status_counts.to_dict("records"):

        status = row["status"]

        definition = RESULT_DEFINITIONS.get(status, "Reconciliation status produced by the final comparison pipeline.")

        summary_rows.append(_build_context_row(category_type="status",
                                               category=str(status),
                                               count=int(row["count"]),
                                               definition=definition,
                                               metadata=metadata))

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

            for row in mismatch_counts.to_dict("records"):

                mismatch_type = str(row["category"])

                definition = MISMATCH_DEFINITIONS.get(mismatch_type, "Detailed reconciliation discrepancy classification.")

                summary_rows.append(_build_context_row(category_type="mismatch_type",
                                                       category=mismatch_type,
                                                       count=int(row["count"]),
                                                       definition=definition,
                                                       metadata=metadata))

    return pd.DataFrame(summary_rows, columns=SUMMARY_COLUMNS)

def save_summary(summary_df: pd.DataFrame, output_dir: Path | None = None) -> Path:

    if output_dir is None:

        output_dir = settings.reports_dir

    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = (output_dir / "summary.csv")

    summary_df.to_csv(output_path, index=False)

    return output_path

def _get_chart_metadata(summary_df):

    if summary_df.empty:

        return {"source_system": SOURCE_SYSTEM,
                "target_system": TARGET_SYSTEM,
                "comparison_key": COMPARISON_KEY}

    first_row = summary_df.iloc[0]

    return {"source_system": first_row.get("source_system", SOURCE_SYSTEM),
            "target_system": first_row.get("target_system", TARGET_SYSTEM),
            "comparison_key": first_row.get("comparison_key", COMPARISON_KEY)}

def generate_chart(summary_df: pd.DataFrame, output_dir: Path | None = None) -> Path:

    if output_dir is None:

        output_dir = settings.charts_dir

    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    chart_path = (output_dir / "reconciliation_summary.png")

    chart_df = summary_df.copy()

    # ---------------------------------------------------------------------------------------------------------
    # The primary chart represents final reconciliation status only.
    #
    # Mismatch types are diagnostic classifications.
    # Plotting both status and mismatch categories together would visually double-count reconciliation records.
    # ---------------------------------------------------------------------------------------------------------

    if (not chart_df.empty and "category_type" in chart_df.columns):

        chart_df = chart_df[chart_df["category_type"] == "status"].copy()

    if chart_df.empty:

        chart_df = pd.DataFrame({"category_type": ["status"],
                                 "category": ["NO_RESULTS"],
                                 "count": [0]})

    chart_df["category"] = (chart_df["category"].astype(str))

    chart_df["label"] = ("Status: " + chart_df["category"])

    metadata = _get_chart_metadata(summary_df)

    source_system = str(metadata["source_system"])

    target_system = str(metadata["target_system"])

    comparison_key = str(metadata["comparison_key"])

    title = ("Project 3 Sales Transactions vs Project 2 Inventory Reservations — Reconciliation Summary")

    subtitle = (f"Source: {source_system} | "
                f"Target: {target_system} | "
                f"Comparison key: {comparison_key}")

    figure, axis = plt.subplots(figsize=(12, 7))

    axis.bar(chart_df["label"], chart_df["count"])

    axis.set_title(title, fontsize=14, pad=28)

    axis.text(0.5, 1.01, subtitle, transform=axis.transAxes, ha="center", va="bottom", fontsize=9)

    axis.set_xlabel("Final Reconciliation Status")

    axis.set_ylabel("Record Count")

    axis.tick_params(axis="x", rotation=0)

    figure.tight_layout()

    figure.savefig(chart_path, bbox_inches="tight")

    plt.close(figure)

    return chart_path