from pathlib import Path

import pandas as pd

from processing.load_data import load_source_file, load_target_file
from processing.normalize_data import (normalize_names, normalize_dates, normalize_amounts)
from processing.compare_data import compare_records
from processing.mismatch_detector import detect_mismatches
from reporting.report_generator import generate_reports
from reporting.analytics import (generate_summary, save_summary, generate_chart)


def normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all normalization steps to a dataframe.
    """

    dataframe = normalize_names(dataframe)
    dataframe = normalize_dates(dataframe)
    dataframe = normalize_amounts(dataframe)

    return dataframe


def main():

    print("=" * 60)
    print("Reconciliation Automation Engine")
    print("=" * 60)

    print("\n[1/6] Loading datasets.....")

    source_df = load_source_file()
    target_df = load_target_file()

    print("✓ Source records :", len(source_df))
    print("✓ Target records :", len(target_df))

    print("\n[2/6] Normalizing datasets.....")

    source_df = normalize_dataframe(source_df)
    target_df = normalize_dataframe(target_df)

    print("✓ Normalization completed")

    print("\n[3/6] Comparing records.....")

    comparison_results = compare_records(source_df, target_df)

    comparison_df = pd.DataFrame(comparison_results)

    print(f"✓ Compared {len(comparison_df)} records")

    print("\n[4/6] Detecting mismatches.....")

    mismatches = detect_mismatches(source_df, target_df)

    print(f"✓ Issues detected: {len(mismatches)}")

    print("\n[5/6] Generating reports.....")

    generate_reports(comparison_results)

    summary_df = generate_summary(comparison_df)

    save_summary(summary_df)

    generate_chart(summary_df)

    print("✓ Reports generated")

    print("\n[6/6] Execution completed")

    print("\nGenerated files:")

    reports = ["matched.csv", "mismatched.csv", "missing.csv", "summary.csv", "reconciliation_summary.png"]

    for report in reports:

        print(f"  • reports/{report}")

    print("\nReconciliation completed successfully.")


if __name__ == "__main__":
    main()