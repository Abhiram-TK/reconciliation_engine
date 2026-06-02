import pandas as pd
from pathlib import Path

def generate_reports(results):

    BASE_DIR = Path(__file__).resolve().parent.parent

    REPORTS_DIR = BASE_DIR / "reports"

    matched_records = []
    mismatched_records = []
    missing_records = []

    for result in results:

        if result["status"] == "MATCHED":

            matched_records.append(result)

        elif result["status"] == "MISSING":

            missing_records.append(result)

        elif result["status"] == "MISMATCHED":

            mismatched_records.append(result)

    matched_df = pd.DataFrame(matched_records)
    mismatched_df = pd.DataFrame(mismatched_records)
    missing_df = pd.DataFrame(missing_records)

    matched_df.to_csv(REPORTS_DIR / "matched.csv", index=False)
    mismatched_df.to_csv(REPORTS_DIR / "mismatched.csv", index=False)
    missing_df.to_csv(REPORTS_DIR / "missing.csv", index=False)