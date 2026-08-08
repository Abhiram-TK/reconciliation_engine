import pandas as pd

from app.services.compare_service import compare_records
from app.services.normalization_service import normalize_dataframe

def test_compare_matching_transaction():

    sales_df = pd.DataFrame([{"transaction_id": 101,
                              "invoice_number": "INV-2026-000101",
                              "product_id": 10,
                              "quantity": 5,
                              "status": "VALIDATED",
                              "created_at": "2026-08-08T09:00:00Z"}])

    inventory_df = pd.DataFrame([{"transaction_id": 101,
                                  "reservation_id": 501,
                                  "batch_id": 20,
                                  "reserved_quantity": 5,
                                  "status": "RESERVED",
                                  "reserved_at": "2026-08-08T09:01:00Z"}])

    sales_df = normalize_dataframe(sales_df)
    inventory_df = normalize_dataframe(inventory_df)

    results = compare_records(sales_df, inventory_df)

    assert len(results) == 1

    result = results[0]

    assert result["transaction_id"] == 101
    assert result["invoice_number"] == "INV-2026-000101"
    assert result["status"] == "MATCHED"
    assert result["sales_status"] == "VALIDATED"
    assert result["inventory_status"] == "RESERVED"
    assert result["quantity"] == 5
    assert result["reserved_quantity"] == 5
    assert result["reservation_id"] == 501
    assert result["batch_id"] == 20

def test_compare_quantity_mismatch():

    sales_df = pd.DataFrame([{"transaction_id": 102,
                              "invoice_number": "INV-2026-000102",
                              "product_id": 11,
                              "quantity": 8,
                              "status": "COMPLETED",
                              "created_at": "2026-08-08T10:00:00Z"}])

    inventory_df = pd.DataFrame([{"transaction_id": 102,
                                  "reservation_id": 502,
                                  "batch_id": 21,
                                  "reserved_quantity": 5,
                                  "status": "RESERVED",
                                  "reserved_at": "2026-08-08T10:01:00Z"}])

    sales_df = normalize_dataframe(sales_df)
    inventory_df = normalize_dataframe(inventory_df)

    results = compare_records(sales_df, inventory_df)

    assert len(results) == 1

    result = results[0]

    assert result["transaction_id"] == 102
    assert result["status"] == "MISMATCHED"
    assert result["quantity"] == 8
    assert result["reserved_quantity"] == 5

def test_compare_missing_inventory_reservation():

    sales_df = pd.DataFrame([{"transaction_id": 103,
                              "invoice_number": "INV-2026-000103",
                              "product_id": 12,
                              "quantity": 3,
                              "status": "VALIDATED",
                              "created_at": "2026-08-08T11:00:00Z"}])

    inventory_df = pd.DataFrame(columns=["transaction_id",
                                         "reservation_id",
                                         "batch_id",
                                         "reserved_quantity"
                                         "status"
                                         "reserved_at"])

    sales_df = normalize_dataframe(sales_df)
    inventory_df = normalize_dataframe(inventory_df)

    results = compare_records(sales_df, inventory_df)

    assert len(results) == 1

    result = results[0]

    assert result["transaction_id"] == 103
    assert result["invoice_number"] == "INV-2026-000103"
    assert result["status"] == "MISSING"
    assert result["sales_status"] == "VALIDATED"
    assert result["inventory_status"] is None
    assert result["quantity"] == 3
    assert result["reserved_quantity"] is None