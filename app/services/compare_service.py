import pandas as pd

SALES_REQUIRED_COLUMNS = {"transaction_id",
                          "invoice_number",
                          "product_id",
                          "quantity",
                          "status",
                          "created_at"}

INVENTORY_REQUIRED_COLUMNS = {"transaction_id",
                              "reservation_id",
                              "batch_id",
                              "reserved_quantity",
                              "status",
                              "reserved_at"}

def _validate_columns(dataframe: pd.DataFrame, required_columns: set[str], dataset_name: str) -> None:

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:

        raise ValueError(f"{dataset_name} data is missing required columns: " f"{sorted(missing_columns)}")

def compare_records(source_df: pd.DataFrame, target_df: pd.DataFrame) -> list[dict]:

    _validate_columns(dataframe=source_df,
                      required_columns=SALES_REQUIRED_COLUMNS,
                      dataset_name="Sales Transaction Service")
    
    _validate_columns(dataframe=target_df,
                      required_columns=INVENTORY_REQUIRED_COLUMNS,
                      dataset_name="Inventory Dispatch System")

    results = []

    for _, source_row in source_df.iterrows():

        transaction_id = source_row["transaction_id"]

        target_match = target_df[target_df["transaction_id"] == transaction_id]

        if target_match.empty:

            results.append({"transaction_id": transaction_id,
                            "invoice_number": source_row["invoice_number"],
                            "status": "MISSING",
                            "sales_status": source_row["status"],
                            "inventory_status": None,
                            "quantity": source_row["quantity"],
                            "reserved_quantity": None})

            continue

        target_row = target_match.iloc[0]

        quantity_matches = (source_row["quantity"] == target_row["reserved_quantity"])

        if quantity_matches:

            status = "MATCHED"

        else:

            status = "MISMATCHED"

        results.append({"transaction_id": transaction_id,
                        "invoice_number": source_row["invoice_number"],
                        "status": status,
                        "sales_status": source_row["status"],
                        "inventory_status": target_row["status"],
                        "quantity": source_row["quantity"],
                        "reserved_quantity": target_row["reserved_quantity"],
                        "reservation_id": target_row["reservation_id"],
                        "batch_id": target_row["batch_id"]})

    return results