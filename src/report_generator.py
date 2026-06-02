import pandas as pd

def generate_reports(results):

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

    matched_df.to_csv("reports/matched.csv", index=False)
    mismatched_df.to_csv("reports/mismatched.csv", index=False)
    missing_df.to_csv("reports/missing.csv", index=False)