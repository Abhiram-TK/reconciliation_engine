import pandas as pd

from config import REPORTS_DIR

def generate_reports(results):

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

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