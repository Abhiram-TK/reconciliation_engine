import pandas as pd

from app.services.mismatch_service import detect_mismatches
from app.services.normalization_service import normalize_dataframe

def test_detect_mismatches_from_upstream_contracts():

    sales_df = pd.DataFrame([
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
            }])

    inventory_df = pd.DataFrame([
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
                "reservation_id": 504,
                "batch_id": 22,
                "reserved_quantity": 2,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T12:01:00Z"
            }])

    sales_df = normalize_dataframe(sales_df)
    inventory_df = normalize_dataframe(inventory_df)

    mismatches = detect_mismatches(sales_df, inventory_df)

    mismatch_types = {mismatch["mismatch_type"] for mismatch in mismatches}

    assert "MISSING_RESERVATION" in mismatch_types
    assert "QUANTITY_MISMATCH" in mismatch_types
    assert "ORPHAN_RESERVATION" in mismatch_types

def test_detect_missing_reservation():

    sales_df = pd.DataFrame([{"transaction_id": 201,
                              "invoice_number": "INV-2026-000201",
                              "product_id": 20,
                              "quantity": 4,
                              "status": "VALIDATED",
                              "created_at": "2026-08-08T09:00:00Z"}])

    inventory_df = pd.DataFrame(columns=["transaction_id",
                                         "reservation_id",
                                         "batch_id",
                                         "reserved_quantity",
                                         "status",
                                         "reserved_at"])

    sales_df = normalize_dataframe(sales_df)
    inventory_df = normalize_dataframe(inventory_df)

    mismatches = detect_mismatches(sales_df, inventory_df)

    assert mismatches == [{"transaction_id": 201,
                           "mismatch_type": "MISSING_RESERVATION",
                           "invoice_number": "INV-2026-000201",
                           "sales_quantity": 4,
                           "reserved_quantity": None,
                           "details": ("Sales transaction has no corresponding Inventory reservation")}]

def test_detect_quantity_mismatch():

    sales_df = pd.DataFrame([{"transaction_id": 202,
                              "invoice_number": "INV-2026-000202",
                              "product_id": 21,
                              "quantity": 10,
                              "status": "COMPLETED",
                              "created_at": "2026-08-08T10:00:00Z"}])

    inventory_df = pd.DataFrame([{"transaction_id": 202,
                                  "reservation_id": 602,
                                  "batch_id": 31,
                                  "reserved_quantity": 7,
                                  "status": "RESERVED",
                                  "reserved_at": "2026-08-08T10:01:00Z"}])

    sales_df = normalize_dataframe(sales_df)
    inventory_df = normalize_dataframe(inventory_df)

    mismatches = detect_mismatches(sales_df, inventory_df)

    assert len(mismatches) == 1

    assert mismatches[0]["transaction_id"] == 202
    assert mismatches[0]["mismatch_type"] == "QUANTITY_MISMATCH"
    assert mismatches[0]["sales_quantity"] == 10
    assert mismatches[0]["reserved_quantity"] == 7

def test_detect_duplicate_reservation():

    sales_df = pd.DataFrame([{"transaction_id": 203,
                              "invoice_number": "INV-2026-000203",
                              "product_id": 22,
                              "quantity": 5,
                              "status": "VALIDATED",
                              "created_at": "2026-08-08T11:00:00Z"}])

    inventory_df = pd.DataFrame([
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

    sales_df = normalize_dataframe(sales_df)
    inventory_df = normalize_dataframe(inventory_df)

    mismatches = detect_mismatches(sales_df, inventory_df)

    duplicate_mismatches = [mismatch for mismatch in mismatches if mismatch["mismatch_type"] == "DUPLICATE_RESERVATION"]

    assert len(duplicate_mismatches) == 1

    assert duplicate_mismatches[0]["transaction_id"] == 203
    assert duplicate_mismatches[0]["reserved_quantity"] == 5

def test_detect_orphan_reservation():

    sales_df = pd.DataFrame(columns=["transaction_id",
                                     "invoice_number",
                                     "product_id"
                                     "quantity",
                                     "status",
                                     "created_at"])

    inventory_df = pd.DataFrame([{"transaction_id": 204,
                                  "reservation_id": 605,
                                  "batch_id": 34,
                                  "reserved_quantity": 6,
                                  "status": "RESERVED",
                                  "reserved_at": "2026-08-08T12:00:00Z"}])

    sales_df = normalize_dataframe(sales_df)
    inventory_df = normalize_dataframe(inventory_df)

    mismatches = detect_mismatches(sales_df, inventory_df)

    assert mismatches == [{"transaction_id": 204,
                           "mismatch_type": "ORPHAN_RESERVATION",
                           "invoice_number": None,
                           "sales_quantity": None,
                           "reserved_quantity": 6,
                           "details": ("Inventory reservation references a transaction that does not exist in Sales")}]