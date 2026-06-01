def compare_records(source_df, target_df):

    results = []

    for _, source_row in source_df.iterrows():

        target_match = target_df[target_df["invoice_id"] == source_row["invoice_id"]]

        if target_match.empty:

            results.append({"invoice_id": source_row["invoice_id"], "status": "MISSING" })

            continue

        target_row = target_match.iloc[0]

        if (source_row["customer_name"] == target_row["customer_name"] and source_row["amount"] == target_row["amount"]):

            status = "MATCHED"

        else:

            status = "MISMATCHED"

        results.append({"invoice_id": source_row["invoice_id"], "status": status})

    return results