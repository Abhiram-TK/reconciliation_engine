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

def detect_mismatches(source_df: pd.DataFrame, target_df: pd.DataFrame) -> list[dict]:

    _validate_columns(dataframe=source_df,
                      required_columns=SALES_REQUIRED_COLUMNS,
                      dataset_name="Sales Transaction Service")

    _validate_columns(dataframe=target_df,
                      required_columns=INVENTORY_REQUIRED_COLUMNS,
                      dataset_name="Inventory Dispatch System")

    mismatches = []

    sales_transaction_ids = set(source_df["transaction_id"])

    inventory_transaction_ids = set(target_df["transaction_id"])

    # ---------------------------------------------------------
    # 1. Sales transactions without an inventory reservation
    # ---------------------------------------------------------

    missing_reservations = (sales_transaction_ids - inventory_transaction_ids)

    for transaction_id in sorted(missing_reservations):

        sales_match = source_df[source_df["transaction_id"] == transaction_id].iloc[0]

        mismatches.append({"transaction_id": transaction_id,
                           "mismatch_type": "MISSING_RESERVATION",
                           "invoice_number": sales_match["invoice_number"],
                           "sales_quantity": sales_match["quantity"],
                           "reserved_quantity": None,
                           "details": ("Sales transaction has no corresponding Inventory reservation")})

    # ---------------------------------------------------------
    # 2. Duplicate Inventory reservations
    # ---------------------------------------------------------

    reservation_counts = (target_df.groupby("transaction_id").size())

    duplicate_transactions = reservation_counts[reservation_counts > 1].index

    for transaction_id in duplicate_transactions:

        inventory_matches = target_df[target_df["transaction_id"] == transaction_id]

        mismatches.append({"transaction_id": transaction_id,
                           "mismatch_type": "DUPLICATE_RESERVATION",
                           "invoice_number": None,
                           "sales_quantity": None,
                           "reserved_quantity": (inventory_matches["reserved_quantity"].sum()),
                           "details": ("Multiple Inventory reservations exist for the same transaction")})

    # ---------------------------------------------------------
    # 3. Quantity mismatches
    # ---------------------------------------------------------

    common_transaction_ids = (sales_transaction_ids & inventory_transaction_ids)

    for transaction_id in sorted(common_transaction_ids):

        sales_match = source_df[source_df["transaction_id"] == transaction_id].iloc[0]

        inventory_matches = target_df[target_df["transaction_id"] == transaction_id]

        # Do not silently choose one reservation.
        # Duplicate reservations were already reported above.
        if len(inventory_matches) != 1:

            continue

        inventory_match = inventory_matches.iloc[0]

        sales_quantity = sales_match["quantity"]
        reserved_quantity = inventory_match["reserved_quantity"]

        if sales_quantity != reserved_quantity:

            mismatches.append({"transaction_id": transaction_id,
                               "mismatch_type": "QUANTITY_MISMATCH",
                               "invoice_number": sales_match["invoice_number"],
                               "sales_quantity": sales_quantity,
                               "reserved_quantity": reserved_quantity,
                               "details": ("Sales transaction quantity does not match Inventory reserved quantity")})

    # ---------------------------------------------------------
    # 4. Inventory reservations without a Sales transaction
    # ---------------------------------------------------------

    orphan_reservations = (inventory_transaction_ids - sales_transaction_ids)

    for transaction_id in sorted(orphan_reservations):

        inventory_matches = target_df[target_df["transaction_id"] == transaction_id]

        for _, inventory_match in inventory_matches.iterrows():

            mismatches.append({"transaction_id": transaction_id,
                               "mismatch_type": "ORPHAN_RESERVATION",
                               "invoice_number": None,
                               "sales_quantity": None,
                               "reserved_quantity": (inventory_match["reserved_quantity"]),
                               "details": ("Inventory reservation references a transaction that does not exist in Sales")})

    return mismatches