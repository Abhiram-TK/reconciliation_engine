import pandas as pd

from app.services.mismatch_service import detect_mismatches
from app.services.normalization_service import normalize_dataframe

def build_sales_dataframe(records):

    return normalize_dataframe(pd.DataFrame(records))

def build_inventory_dataframe(records):

    return normalize_dataframe(pd.DataFrame(records))

def get_mismatch(mismatches, transaction_id, mismatch_type):
    
    matches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == transaction_id and mismatch["mismatch_type"] == mismatch_type]

    assert len(matches) == 1

    return matches[0]

def test_detect_all_required_mismatch_types():

    sales_df = build_sales_dataframe([
            {
                "transaction_id": 101,
                "invoice_number": "INV-2026-000101",
                "product_id": 10,
                "quantity": 5,
                "status": "VALIDATED",
                "created_at": "2026-08-08T09:00:00Z"
            },
            {
                "transaction_id": 102,
                "invoice_number": "INV-2026-000102",
                "product_id": 11,
                "quantity": 8,
                "status": "COMPLETED",
                "created_at": "2026-08-08T10:00:00Z"
            },
            {
                "transaction_id": 103,
                "invoice_number": "INV-2026-000103",
                "product_id": 12,
                "quantity": 3,
                "status": "VALIDATED",
                "created_at": "2026-08-08T11:00:00Z"
            },
            {
                "transaction_id": 104,
                "invoice_number": "INV-2026-000104",
                "product_id": 13,
                "quantity": 5,
                "status": "VALIDATED",
                "created_at": "2026-08-08T12:00:00Z"
            }])

    inventory_df = build_inventory_dataframe([
            {
                "transaction_id": 101,
                "reservation_id": 501,
                "batch_id": 20,
                "reserved_quantity": 5,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T09:01:00Z"
            },
            {
                "transaction_id": 102,
                "reservation_id": 502,
                "batch_id": 21,
                "reserved_quantity": 5,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T10:01:00Z"
            },
            {
                "transaction_id": 104,
                "reservation_id": 503,
                "batch_id": 22,
                "reserved_quantity": 3,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T12:01:00Z"
            },
            {
                "transaction_id": 104,
                "reservation_id": 504,
                "batch_id": 23,
                "reserved_quantity": 2,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T12:02:00Z"
            },
            {
                "transaction_id": 105,
                "reservation_id": 505,
                "batch_id": 24,
                "reserved_quantity": 6,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T13:01:00Z"
            }])

    mismatches = detect_mismatches(sales_df, inventory_df)

    mismatch_types = {mismatch["mismatch_type"] for mismatch in mismatches}

    assert mismatch_types == {"MISSING_RESERVATION",
                              "QUANTITY_MISMATCH",
                              "DUPLICATE_RESERVATION",
                              "ORPHAN_RESERVATION"}

def test_detect_missing_reservation():

    sales_df = build_sales_dataframe([
            {
                "transaction_id": 201,
                "invoice_number": "INV-2026-000201",
                "product_id": 20,
                "quantity": 4,
                "status": "VALIDATED",
                "created_at": "2026-08-08T09:00:00Z"
            }])

    inventory_df = build_inventory_dataframe([])

    # Ensure the empty Inventory DataFrame still has the required upstream contract columns.
    inventory_df = pd.DataFrame(columns=["transaction_id",
                                         "reservation_id",
                                         "batch_id",
                                         "reserved_quantity",
                                         "status",
                                         "reserved_at"])

    inventory_df = normalize_dataframe(inventory_df)

    mismatches = detect_mismatches(sales_df, inventory_df)

    assert len(mismatches) == 1

    mismatch = mismatches[0]

    assert mismatch["transaction_id"] == 201
    assert mismatch["mismatch_type"] == ("MISSING_RESERVATION")

    assert mismatch["invoice_number"] == ("INV-2026-000201")

    assert mismatch["sales_quantity"] == 4
    assert mismatch["reserved_quantity"] is None

    assert mismatch["reservation_count"] == 0

    assert mismatch["reservation_id"] is None
    assert mismatch["batch_id"] is None

    assert mismatch["reservation_ids"] == []
    assert mismatch["batch_ids"] == []
    assert mismatch["reserved_quantities"] == []

    assert mismatch["reservation_statuses"] == []
    assert mismatch["reservation_timestamps"] == []

    assert mismatch["details"] == ("Sales transaction has no corresponding Inventory reservation")

def test_detect_quantity_mismatch():

    sales_df = build_sales_dataframe([
            {
                "transaction_id": 202,
                "invoice_number": "INV-2026-000202",
                "product_id": 21,
                "quantity": 10,
                "status": "COMPLETED",
                "created_at": "2026-08-08T10:00:00Z"
            }])

    inventory_df = build_inventory_dataframe([
            {
                "transaction_id": 202,
                "reservation_id": 602,
                "batch_id": 31,
                "reserved_quantity": 7,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T10:01:00Z"
            }])

    mismatches = detect_mismatches(sales_df, inventory_df)

    assert len(mismatches) == 1

    mismatch = mismatches[0]

    assert mismatch["transaction_id"] == 202

    assert mismatch["mismatch_type"] == ("QUANTITY_MISMATCH")

    assert mismatch["invoice_number"] == ("INV-2026-000202")

    assert mismatch["sales_quantity"] == 10
    assert mismatch["reserved_quantity"] == 7

    assert mismatch["reservation_count"] == 1

    assert mismatch["reservation_id"] == 602
    assert mismatch["batch_id"] == 31

    assert mismatch["reservation_ids"] == [602]
    assert mismatch["batch_ids"] == [31]
    assert mismatch["reserved_quantities"] == [7]

    assert mismatch["reservation_statuses"] == ["RESERVED"]

    assert len(mismatch["reservation_timestamps"]) == 1

    assert mismatch["details"] == ("Sales transaction quantity does not match Inventory reserved quantity")

def test_detect_duplicate_reservation_once_per_transaction():

    sales_df = build_sales_dataframe([
            {
                "transaction_id": 203,
                "invoice_number": "INV-2026-000203",
                "product_id": 22,
                "quantity": 5,
                "status": "VALIDATED",
                "created_at": "2026-08-08T11:00:00Z"
            }])

    inventory_df = build_inventory_dataframe([
            {
                "transaction_id": 203,
                "reservation_id": 603,
                "batch_id": 32,
                "reserved_quantity": 3,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T11:01:00Z"
            },
            {
                "transaction_id": 203,
                "reservation_id": 604,
                "batch_id": 33,
                "reserved_quantity": 2,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T11:02:00Z"
            }])

    mismatches = detect_mismatches(sales_df, inventory_df)

    duplicate_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 203 and mismatch["mismatch_type"] == "DUPLICATE_RESERVATION"]

    assert len(duplicate_mismatches) == 1

    mismatch = duplicate_mismatches[0]

    assert mismatch["transaction_id"] == 203
    assert mismatch["mismatch_type"] == ("DUPLICATE_RESERVATION")

    assert mismatch["reservation_count"] == 2

    assert mismatch["reserved_quantity"] == 5

    assert mismatch["reservation_ids"] == [603, 604]

    assert mismatch["batch_ids"] == [32, 33]

    assert mismatch["reserved_quantities"] == [3, 2]

    assert mismatch["reservation_statuses"] == ["RESERVED", "RESERVED"]

    assert len(mismatch["reservation_timestamps"]) == 2
    assert len(mismatch["reservations"]) == 2

def test_duplicate_reservation_does_not_generate_quantity_mismatch():

    sales_df = build_sales_dataframe([
            {
                "transaction_id": 204,
                "invoice_number": "INV-2026-000204",
                "product_id": 23,
                "quantity": 5,
                "status": "VALIDATED",
                "created_at": "2026-08-08T12:00:00Z"
            }])

    inventory_df = build_inventory_dataframe([
            {
                "transaction_id": 204,
                "reservation_id": 605,
                "batch_id": 34,
                "reserved_quantity": 99,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T12:01:00Z"
            },
            {
                "transaction_id": 204,
                "reservation_id": 606,
                "batch_id": 35,
                "reserved_quantity": 1,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T12:02:00Z"
            }])

    mismatches = detect_mismatches(sales_df, inventory_df)

    transaction_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 204]

    assert len(transaction_mismatches) == 1

    assert (transaction_mismatches[0]["mismatch_type"] == "DUPLICATE_RESERVATION")

    assert not any(mismatch["mismatch_type"] == "QUANTITY_MISMATCH" for mismatch in transaction_mismatches)

    assert transaction_mismatches[0]["reserved_quantity"] == 100

def test_detect_orphan_reservation():

    sales_df = pd.DataFrame(columns=["transaction_id",
                                    "invoice_number",
                                    "product_id",
                                    "quantity",
                                    "status",
                                    "created_at"])

    inventory_df = pd.DataFrame([
            {
                "transaction_id": 205,
                "reservation_id": 607,
                "batch_id": 36,
                "reserved_quantity": 6,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T13:00:00Z"
            }])

    sales_df = normalize_dataframe(sales_df)

    inventory_df = normalize_dataframe(inventory_df)

    mismatches = detect_mismatches(sales_df, inventory_df)

    assert len(mismatches) == 1

    mismatch = mismatches[0]

    assert mismatch["transaction_id"] == 205
    assert mismatch["mismatch_type"] == ("ORPHAN_RESERVATION")

    assert mismatch["invoice_number"] is None

    assert mismatch["sales_quantity"] is None
    assert mismatch["reserved_quantity"] == 6

    assert mismatch["reservation_count"] == 1

    assert mismatch["reservation_ids"] == [607]
    assert mismatch["batch_ids"] == [36]
    assert mismatch["reserved_quantities"] == [6]

    assert mismatch["reservation_statuses"] == ["RESERVED"]

    assert len(mismatch["reservation_timestamps"]) == 1

    assert mismatch["details"] == ("Inventory reservation references a transaction that does not exist in Sales")

def test_duplicate_transaction_produces_exactly_one_detailed_mismatch():

    sales_df = build_sales_dataframe([
            {
                "transaction_id": 206,
                "invoice_number": "INV-2026-000206",
                "product_id": 24,
                "quantity": 10,
                "status": "COMPLETED",
                "created_at": "2026-08-08T14:00:00Z"
            }])

    inventory_df = build_inventory_dataframe([
            {
                "transaction_id": 206,
                "reservation_id": 608,
                "batch_id": 37,
                "reserved_quantity": 4,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T14:01:00Z"
            },
            {
                "transaction_id": 206,
                "reservation_id": 609,
                "batch_id": 38,
                "reserved_quantity": 6,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T14:02:00Z"
            },
            {
                "transaction_id": 206,
                "reservation_id": 610,
                "batch_id": 39,
                "reserved_quantity": 1,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T14:03:00Z"
            }])

    mismatches = detect_mismatches(sales_df, inventory_df)

    transaction_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 206]

    assert len(transaction_mismatches) == 1

    mismatch = transaction_mismatches[0]

    assert mismatch["mismatch_type"] == ("DUPLICATE_RESERVATION")

    assert mismatch["reservation_count"] == 3

    assert mismatch["reservation_ids"] == [608, 609, 610]

    assert mismatch["reserved_quantities"] == [4, 6, 1]

    assert mismatch["reserved_quantity"] == 11

def test_mismatch_output_order_is_deterministic():

    sales_df = build_sales_dataframe([
            {
                "transaction_id": 302,
                "invoice_number": "INV-2026-000302",
                "product_id": 30,
                "quantity": 5,
                "status": "VALIDATED",
                "created_at": "2026-08-08T15:00:00Z"
            },
            {
                "transaction_id": 301,
                "invoice_number": "INV-2026-000301",
                "product_id": 31,
                "quantity": 8,
                "status": "VALIDATED",
                "created_at": "2026-08-08T16:00:00Z"
            }])

    inventory_df = build_inventory_dataframe([
            {
                "transaction_id": 302,
                "reservation_id": 702,
                "batch_id": 42,
                "reserved_quantity": 3,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T15:01:00Z"
            },
            {
                "transaction_id": 301,
                "reservation_id": 701,
                "batch_id": 41,
                "reserved_quantity": 8,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T16:01:00Z"
            },
            {
                "transaction_id": 303,
                "reservation_id": 703,
                "batch_id": 43,
                "reserved_quantity": 2,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T17:01:00Z"
            }])

    mismatches_first = detect_mismatches(sales_df, inventory_df)

    mismatches_second = detect_mismatches(sales_df, inventory_df)

    assert mismatches_first == mismatches_second