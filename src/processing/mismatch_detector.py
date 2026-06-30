def detect_mismatches(source_df, target_df):

    results = []

    for _, source_row in source_df.iterrows():

        target_match = target_df[target_df["invoice_id"] == source_row["invoice_id"]]

        if target_match.empty:

            results.append({"invoice_id": source_row["invoice_id"], 
                            "issue": "MISSING_RECORD"})

            continue

        target_row = target_match.iloc[0]

        if source_row["customer_name"] != target_row["customer_name"]:

            results.append({"invoice_id": source_row["invoice_id"], 
                            "issue": "CUSTOMER_MISMATCH", 
                            "source": source_row["customer_name"], 
                            "target": target_row["customer_name"]})

        if source_row["invoice_date"] != target_row["invoice_date"]:

            results.append({"invoice_id": source_row["invoice_id"], 
                            "issue": "DATE_MISMATCH", 
                            "source": source_row["invoice_date"], 
                            "target": target_row["invoice_date"]})

        if source_row["amount"] != target_row["amount"]:

            results.append({"invoice_id": source_row["invoice_id"], 
                            "issue": "AMOUNT_MISMATCH", 
                            "source": float(source_row["amount"]), 
                            "target": float(target_row["amount"])})

    duplicate_invoices = target_df[target_df.duplicated( subset=["invoice_id"], keep=False)]

    for _, duplicate_row in duplicate_invoices.iterrows():

        results.append({"invoice_id": duplicate_row["invoice_id"], 
                        "issue": "DUPLICATE_RECORD"})

    return results