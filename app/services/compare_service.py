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

SOURCE_SYSTEM = "Project 3 — Sales Transaction Service"

TARGET_SYSTEM = "Project 2 — Inventory Dispatch System"

COMPARISON_KEY = "transaction_id"

COMPARISON_SCOPE = ("Sales transactions compared against Inventory reservations by transaction_id")

def _validate_columns(dataframe: pd.DataFrame, required_columns: set[str], dataset_name: str) -> None:

    missing_columns = (required_columns - set(dataframe.columns))

    if missing_columns:

        raise ValueError(f"{dataset_name} data is missing required columns: "
                         f"{sorted(missing_columns)}")

def _serialize_reservation_rows(reservation_rows: pd.DataFrame) -> list[dict]:

    reservations = []

    for _, row in reservation_rows.iterrows():

        reservations.append({"reservation_id": row["reservation_id"],
                             "batch_id": row["batch_id"],
                             "reserved_quantity": row["reserved_quantity"],
                             "status": row["status"],
                             "reserved_at": row["reserved_at"]})

    return reservations

def _build_result(*,
                  transaction_id,
                  invoice_number,
                  status,
                  mismatch_type,
                  sales_status,
                  inventory_status,
                  quantity,
                  reserved_quantity,
                  reservation_count,
                  reservation_id,
                  batch_id,
                  reservation_ids,
                  batch_ids,
                  reserved_quantities,
                  reservation_statuses,
                  reservation_timestamps,
                  sales_record_present,
                  inventory_record_present,
                  reservations=None,
                  details=None) -> dict:

    result = {
        # --------------------------
        # Reconciliation provenance
        # --------------------------
        "source_system": SOURCE_SYSTEM,
        "target_system": TARGET_SYSTEM,
        "comparison_key": COMPARISON_KEY,
        "comparison_scope": COMPARISON_SCOPE,

        # --------------------------
        # Record presence semantics
        # --------------------------
        "sales_record_present": sales_record_present,
        "inventory_record_present": inventory_record_present,

        # -------------------------------
        # Existing reconciliation fields
        # -------------------------------
        "transaction_id": transaction_id,
        "invoice_number": invoice_number,
        "status": status,
        "mismatch_type": mismatch_type,
        "sales_status": sales_status,
        "inventory_status": inventory_status,
        "quantity": quantity,
        "reserved_quantity": reserved_quantity,
        "reservation_count": reservation_count,
        "reservation_id": reservation_id,
        "batch_id": batch_id,
        "reservation_ids": reservation_ids,
        "batch_ids": batch_ids,
        "reserved_quantities": reserved_quantities,
        "reservation_statuses": reservation_statuses,
        "reservation_timestamps": reservation_timestamps}

    if details is not None:

        result["details"] = details

    if reservations is not None:

        result["reservations"] = reservations

    return result

def compare_records(source_df: pd.DataFrame, target_df: pd.DataFrame) -> list[dict]:

    _validate_columns(dataframe=source_df,
                      required_columns=SALES_REQUIRED_COLUMNS,
                      dataset_name=SOURCE_SYSTEM)

    _validate_columns(dataframe=target_df,
                      required_columns=INVENTORY_REQUIRED_COLUMNS,
                      dataset_name=TARGET_SYSTEM)

    results = []

    # ==================================================
    # 1. Iterate over authoritative Sales transactions
    # ==================================================

    for _, source_row in source_df.iterrows():

        transaction_id = source_row["transaction_id"]

        target_matches = target_df[target_df["transaction_id"] == transaction_id]

        # --------------------------------------------
        # 1A. Sales record exists, Inventory does not
        # --------------------------------------------

        if target_matches.empty:

            results.append(_build_result(transaction_id=transaction_id,
                                         invoice_number=source_row["invoice_number"],
                                         status="MISSING",
                                         mismatch_type="MISSING_RESERVATION",
                                         sales_status=source_row["status"],
                                         inventory_status=None,
                                         quantity=source_row["quantity"],
                                         reserved_quantity=None,
                                         reservation_count=0,
                                         reservation_id=None,
                                         batch_id=None,
                                         reservation_ids=[],
                                         batch_ids=[],
                                         reserved_quantities=[],
                                         reservation_statuses=[],
                                         reservation_timestamps=[],
                                         sales_record_present=True,
                                         inventory_record_present=False))

            continue

        # ============================================
        # 2. Preserve every matching Inventory record
        # ============================================

        reservation_records = ( _serialize_reservation_rows(target_matches))

        reservation_count = len(reservation_records)

        reservation_ids = [reservation["reservation_id"] for reservation in reservation_records]

        batch_ids = [reservation["batch_id"] for reservation in reservation_records]

        reserved_quantities = [reservation["reserved_quantity"] for reservation in reservation_records]

        reservation_statuses = [reservation["status"] for reservation in reservation_records]

        reservation_timestamps = [reservation["reserved_at"] for reservation in reservation_records]

        total_reserved_quantity = sum(reserved_quantities)

        # ===================================
        # 3. Multiple Inventory reservations
        # ===================================

        if reservation_count > 1:

            results.append(_build_result(transaction_id=transaction_id,
                                         invoice_number=source_row["invoice_number"],
                                         status="MISMATCHED",
                                         mismatch_type=("DUPLICATE_RESERVATION"),
                                         sales_status=source_row["status"],
                                         inventory_status=(reservation_statuses),
                                         quantity=source_row["quantity"],
                                         reserved_quantity=(total_reserved_quantity),
                                         reservation_count=(reservation_count),
                                         reservation_id=None,
                                         batch_id=None,
                                         reservation_ids=(reservation_ids),
                                         batch_ids=batch_ids,
                                         reserved_quantities=(reserved_quantities),
                                         reservation_statuses=(reservation_statuses),
                                         reservation_timestamps=(reservation_timestamps),
                                         sales_record_present=True,
                                         inventory_record_present=True,
                                         details=("Multiple Inventory reservations exist for the same Sales transaction"),
                                         reservations=(reservation_records)))

            continue

        # =====================================
        # 4. Exactly one Inventory reservation
        # =====================================

        reservation = reservation_records[0]

        quantity_matches = (source_row["quantity"] == reservation["reserved_quantity"])

        if quantity_matches:

            status = "MATCHED"
            mismatch_type = None

        else:

            status = "MISMATCHED"
            mismatch_type = "QUANTITY_MISMATCH"

        results.append( _build_result(transaction_id=transaction_id,
                                      invoice_number=source_row["invoice_number"],
                                      status=status,
                                      mismatch_type=mismatch_type,
                                      sales_status=source_row["status"],
                                      inventory_status=reservation["status"],
                                      quantity=source_row["quantity"],
                                      reserved_quantity=reservation["reserved_quantity"],
                                      reservation_count=1,
                                      reservation_id=reservation["reservation_id"],
                                      batch_id=reservation["batch_id"],
                                      reservation_ids=[reservation["reservation_id"]],
                                      batch_ids=[reservation["batch_id"]],
                                      reserved_quantities=[reservation["reserved_quantity"]],
                                      reservation_statuses=[reservation["status"]],
                                      reservation_timestamps=[reservation["reserved_at"]],
                                      sales_record_present=True,
                                      inventory_record_present=True,
                                      reservations=reservation_records))

    # ===============================================
    # 5. Detect Inventory reservations with no Sales
    # ===============================================

    source_transaction_ids = set(source_df["transaction_id"])

    orphan_inventory_rows = target_df[~target_df["transaction_id"].isin(source_transaction_ids)]

    for transaction_id, inventory_group in (orphan_inventory_rows.groupby("transaction_id", sort=False)):

        reservation_records = ( _serialize_reservation_rows(inventory_group))

        reservation_count = len(reservation_records)

        reservation_ids = [reservation["reservation_id"] for reservation in reservation_records]

        batch_ids = [reservation["batch_id"] for reservation in reservation_records]

        reserved_quantities = [reservation["reserved_quantity"] for reservation in reservation_records]

        reservation_statuses = [reservation["status"] for reservation in reservation_records]

        reservation_timestamps = [reservation["reserved_at"] for reservation in reservation_records]

        total_reserved_quantity = sum(reserved_quantities)

        if reservation_count == 1:

            reservation_id = reservation_ids[0]
            batch_id = batch_ids[0]

        else:

            reservation_id = None
            batch_id = None

        results.append(_build_result(transaction_id=transaction_id,
                                     invoice_number=None,
                                     status="MISMATCHED",
                                     mismatch_type="ORPHAN_RESERVATION",
                                     sales_status=None,
                                     inventory_status=(reservation_statuses[0] if reservation_count == 1 else reservation_statuses),
                                     quantity=None,
                                     reserved_quantity=(total_reserved_quantity),
                                     reservation_count=(reservation_count),
                                     reservation_id=reservation_id,
                                     batch_id=batch_id,
                                     reservation_ids=reservation_ids,
                                     batch_ids=batch_ids,
                                     reserved_quantities=(reserved_quantities),
                                     reservation_statuses=(reservation_statuses),
                                     reservation_timestamps=(reservation_timestamps),
                                     sales_record_present=False,
                                     inventory_record_present=True,
                                     details=("Inventory reservation references a transaction_id with no corresponding Sales transaction"),
                                     reservations=(reservation_records)))

    return results