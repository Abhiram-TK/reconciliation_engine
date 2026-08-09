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

        raise ValueError( f"{dataset_name} data is missing required columns: " f"{sorted(missing_columns)}")

def _build_reservation_details(inventory_matches: pd.DataFrame) -> list[dict]:

    reservations = []

    for _, inventory_match in inventory_matches.iterrows():

        reservations.append({"reservation_id": inventory_match["reservation_id"],
                             "batch_id": inventory_match["batch_id"],
                             "reserved_quantity": inventory_match["reserved_quantity"],
                             "status": inventory_match["status"],
                             "reserved_at": inventory_match["reserved_at"]})

    return reservations

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

    # -------------------------------------------------------
    # 1. Sales transactions without an Inventory reservation
    # -------------------------------------------------------

    missing_reservations = (sales_transaction_ids - inventory_transaction_ids)

    for transaction_id in sorted(missing_reservations):

        sales_matches = source_df[source_df["transaction_id"] == transaction_id]

        sales_match = sales_matches.iloc[0]

        mismatches.append({"transaction_id": transaction_id,
                           "mismatch_type": "MISSING_RESERVATION",
                           "invoice_number": sales_match["invoice_number"],
                           "sales_quantity": sales_match["quantity"],
                           "reserved_quantity": None,
                           "reservation_count": 0,
                           "reservation_id": None,
                           "batch_id": None,
                           "reservation_ids": [],
                           "batch_ids": [],
                           "reserved_quantities": [],
                           "reservation_statuses": [],
                           "reservation_timestamps": [],
                           "details": ("Sales transaction has no corresponding Inventory reservation")})

    # ------------------------------------
    # 2. Duplicate Inventory reservations
    # ------------------------------------

    reservation_counts = (target_df.groupby("transaction_id").size())

    duplicate_transactions = (reservation_counts[reservation_counts > 1].index)

    for transaction_id in sorted(duplicate_transactions):

        inventory_matches = target_df[target_df["transaction_id"] == transaction_id]

        reservations = _build_reservation_details(inventory_matches)

        reserved_quantities = [reservation["reserved_quantity"] for reservation in reservations]

        reservation_ids = [reservation["reservation_id"] for reservation in reservations]

        batch_ids = [reservation["batch_id"] for reservation in reservations]

        reservation_statuses = [reservation["status"] for reservation in reservations]

        reservation_timestamps = [reservation["reserved_at"] for reservation in reservations]

        mismatches.append({"transaction_id": transaction_id,
                           "mismatch_type": "DUPLICATE_RESERVATION",
                           "invoice_number": None,
                           "sales_quantity": None,
                           "reserved_quantity": sum(reserved_quantities),
                           "reservation_count": len(reservations),
                           "reservation_id": None,
                           "batch_id": None,
                           "reservation_ids": reservation_ids,
                           "batch_ids": batch_ids,
                           "reserved_quantities": reserved_quantities,
                           "reservation_statuses": reservation_statuses,
                           "reservation_timestamps": reservation_timestamps,
                           "details": ("Multiple Inventory reservations exist for the same transaction"),
                           "reservations": reservations})

    # -----------------------
    # 3. Quantity mismatches
    # -----------------------

    common_transaction_ids = (sales_transaction_ids & inventory_transaction_ids)

    for transaction_id in sorted(common_transaction_ids):

        sales_matches = source_df[source_df["transaction_id"] == transaction_id]

        inventory_matches = target_df[target_df["transaction_id"] == transaction_id]

        # Duplicate reservations were already reported above.
        #
        # Do not select one reservation arbitrarily and compare its quantity against the Sales quantity.
        if len(inventory_matches) != 1:

            continue

        sales_match = sales_matches.iloc[0]
        inventory_match = inventory_matches.iloc[0]

        sales_quantity = sales_match["quantity"]
        reserved_quantity = inventory_match["reserved_quantity"]

        if sales_quantity == reserved_quantity:

            continue

        mismatches.append({"transaction_id": transaction_id,
                           "mismatch_type": "QUANTITY_MISMATCH",
                           "invoice_number": sales_match["invoice_number"],
                           "sales_quantity": sales_quantity,
                           "reserved_quantity": reserved_quantity,
                           "reservation_count": 1,
                           "reservation_id": inventory_match["reservation_id"],
                           "batch_id": inventory_match["batch_id"],
                           "reservation_ids": [inventory_match["reservation_id"]],
                           "batch_ids": [inventory_match["batch_id"]],
                           "reserved_quantities": [inventory_match["reserved_quantity"]],
                           "reservation_statuses": [inventory_match["status"]],
                           "reservation_timestamps": [inventory_match["reserved_at"]],
                           "details": ("Sales transaction quantity does not match Inventory reserved quantity"),
                           "reservations": [{"reservation_id": inventory_match["reservation_id"],
                                             "batch_id": inventory_match["batch_id"],
                                             "reserved_quantity": inventory_match["reserved_quantity"],
                                             "status": inventory_match["status"],
                                             "reserved_at": inventory_match["reserved_at"]}]})

    # ------------------------------------------------------
    # 4. Inventory reservations without a Sales transaction
    # ------------------------------------------------------

    orphan_reservations = (inventory_transaction_ids - sales_transaction_ids)

    for transaction_id in sorted(orphan_reservations):

        inventory_matches = target_df[target_df["transaction_id"] == transaction_id]

        reservations = _build_reservation_details(inventory_matches)

        # The mismatch is one transaction-level orphan condition.
        # Preserve all associated reservation records instead of producing one redundant mismatch for every reservation.
        mismatches.append({"transaction_id": transaction_id,
                           "mismatch_type": "ORPHAN_RESERVATION",
                           "invoice_number": None,
                           "sales_quantity": None,
                           "reserved_quantity": sum(reservation["reserved_quantity"] for reservation in reservations),
                           "reservation_count": len(reservations),
                           "reservation_id": None,
                           "batch_id": None,
                           "reservation_ids": [reservation["reservation_id"] for reservation in reservations],
                           "batch_ids": [reservation["batch_id"] for reservation in reservations],
                           "reserved_quantities": [reservation["reserved_quantity"] for reservation in reservations],
                           "reservation_statuses": [reservation["status"] for reservation in reservations],
                           "reservation_timestamps": [reservation["reserved_at"] for reservation in reservations],
                           "details": ("Inventory reservation references a transaction that does not exist in Sales"),
                           "reservations": reservations})

    return mismatches