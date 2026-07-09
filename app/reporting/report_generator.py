import pandas as pd

from app.core.config import settings

def generate_reports(results):

    settings.reports_dir.mkdir(parents=True, exist_ok=True)

    matched_records = []
    mismatched_records = []
    missing_records = []

    for result in results:

        status = result.get("status")

        if status == "MATCHED":

            matched_records.append(result)

        elif status == "MISSING":

            missing_records.append(result)

        elif status == "MISMATCHED":

            mismatched_records.append(result)

    matched_df = pd.DataFrame(matched_records)
    mismatched_df = pd.DataFrame(mismatched_records)
    missing_df = pd.DataFrame(missing_records)

    matched_df.to_csv(settings.reports_dir / "matched.csv", index=False)
    mismatched_df.to_csv(settings.reports_dir / "mismatched.csv", index=False)
    missing_df.to_csv(settings.reports_dir / "missing.csv", index=False)