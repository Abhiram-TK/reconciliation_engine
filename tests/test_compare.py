import pandas as pd

from app.services.compare_service import compare_records
from app.services.normalization_service import normalize_dataframe

def build_sales_dataframe(transaction_id,
                          invoice_number,
                          product_id,
                          quantity,
                          status="VALIDATED",
                          created_at="2026-08-08T09:00:00Z"):
    
    return pd.DataFrame([{"transaction_id": transaction_id,
                          "invoice_number": invoice_number,
                          "product_id": product_id,
                          "quantity": quantity,
                          "status": status,
                          "created_at": created_at}])

def build_inventory_dataframe(transaction_id,
                              reservation_id,
                              batch_id,
                              reserved_quantity,
                              status="RESERVED",
                              reserved_at="2026-08-08T09:01:00Z"):
    
    return pd.DataFrame([{"transaction_id": transaction_id,
                          "reservation_id": reservation_id,
                          "batch_id": batch_id,
                          "reserved_quantity": reserved_quantity,
                          "status": status,
                          "reserved_at": reserved_at}])

def normalize_inputs(sales_df, inventory_df):
    
    return (normalize_dataframe(sales_df), normalize_dataframe(inventory_df))

def test_compare_exact_match():

    sales_df = build_sales_dataframe(transaction_id=101,
                                     invoice_number="INV-2026-000101",
                                     product_id=10,
                                     quantity=5)

    inventory_df = build_inventory_dataframe(transaction_id=101,
                                             reservation_id=501,
                                             batch_id=20,
                                             reserved_quantity=5)

    sales_df, inventory_df = normalize_inputs(sales_df, inventory_df)

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

    assert result["reservation_count"] == 1
    assert result["reservation_id"] == 501
    assert result["batch_id"] == 20

    assert result["reservation_ids"] == [501]
    assert result["batch_ids"] == [20]
    assert result["reserved_quantities"] == [5]

def test_compare_quantity_mismatch():

    sales_df = build_sales_dataframe(transaction_id=102,
                                     invoice_number="INV-2026-000102",
                                     product_id=11,
                                     quantity=8,
                                     status="COMPLETED",
                                     created_at="2026-08-08T10:00:00Z")

    inventory_df = build_inventory_dataframe(transaction_id=102,
                                             reservation_id=502,
                                             batch_id=21,
                                             reserved_quantity=5,
                                             reserved_at="2026-08-08T10:01:00Z")

    sales_df, inventory_df = normalize_inputs(sales_df, inventory_df)

    results = compare_records(sales_df, inventory_df)

    assert len(results) == 1

    result = results[0]

    assert result["transaction_id"] == 102
    assert result["status"] == "MISMATCHED"
    assert result["mismatch_type"] == "QUANTITY_MISMATCH"

    assert result["quantity"] == 8
    assert result["reserved_quantity"] == 5

    assert result["reservation_count"] == 1
    assert result["reservation_id"] == 502
    assert result["batch_id"] == 21

    assert result["reservation_ids"] == [502]
    assert result["reserved_quantities"] == [5]

def test_compare_missing_inventory_reservation():

    sales_df = build_sales_dataframe(transaction_id=103,
                                     invoice_number="INV-2026-000103",
                                     product_id=12,
                                     quantity=3,
                                     created_at="2026-08-08T11:00:00Z")

    inventory_df = pd.DataFrame(columns=["transaction_id",
                                         "reservation_id",
                                         "batch_id",
                                         "reserved_quantity",
                                         "status",
                                         "reserved_at"])

    sales_df, inventory_df = normalize_inputs(sales_df, inventory_df)

    results = compare_records(sales_df, inventory_df)

    assert len(results) == 1

    result = results[0]

    assert result["transaction_id"] == 103
    assert result["status"] == "MISSING"
    assert result["mismatch_type"] == "MISSING_RESERVATION"

    assert result["quantity"] == 3
    assert result["reserved_quantity"] is None

    assert result["reservation_count"] == 0
    assert result["reservation_id"] is None
    assert result["batch_id"] is None

    assert result["reservation_ids"] == []
    assert result["batch_ids"] == []
    assert result["reserved_quantities"] == []

def test_compare_duplicate_reservations_are_not_collapsed():

    sales_df = build_sales_dataframe(transaction_id=104,
                                     invoice_number="INV-2026-000104",
                                     product_id=13,
                                     quantity=5,
                                     created_at="2026-08-08T12:00:00Z")

    inventory_df = pd.DataFrame([
            {
                "transaction_id": 104,
                "reservation_id": 601,
                "batch_id": 30,
                "reserved_quantity": 3,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T12:01:00Z"
            },
            {
                "transaction_id": 104,
                "reservation_id": 602,
                "batch_id": 31,
                "reserved_quantity": 2,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T12:02:00Z"
            }])

    sales_df, inventory_df = normalize_inputs(sales_df, inventory_df)

    results = compare_records(sales_df, inventory_df)

    assert len(results) == 1

    result = results[0]

    assert result["transaction_id"] == 104
    assert result["status"] == "MISMATCHED"
    assert result["mismatch_type"] == "DUPLICATE_RESERVATION"

    assert result["reservation_count"] == 2

    # Both reservations must survive comparison.
    assert result["reservation_ids"] == [601, 602]

    assert result["batch_ids"] == [30, 31]

    assert result["reserved_quantities"] == [3, 2]

    # The aggregate quantity is preserved for reporting, but no arbitrary first reservation is selected.
    assert result["reserved_quantity"] == 5

    assert result["reservation_id"] is None
    assert result["batch_id"] is None

    assert len(result["reservations"]) == 2

    assert result["reservations"][0]["reservation_id"] == 601
    assert result["reservations"][1]["reservation_id"] == 602

def test_compare_duplicate_reservation_does_not_perform_single_row_quantity_check():

    sales_df = build_sales_dataframe(transaction_id=105,
                                     invoice_number="INV-2026-000105",
                                     product_id=14,
                                     quantity=5,
                                     created_at="2026-08-08T13:00:00Z")

    inventory_df = pd.DataFrame([
            {
                "transaction_id": 105,
                "reservation_id": 603,
                "batch_id": 32,
                "reserved_quantity": 99,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T13:01:00Z"
            },
            {
                "transaction_id": 105,
                "reservation_id": 604,
                "batch_id": 33,
                "reserved_quantity": 1,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T13:02:00Z"
            }])

    sales_df, inventory_df = normalize_inputs(sales_df, inventory_df)

    results = compare_records(sales_df, inventory_df)

    assert len(results) == 1

    result = results[0]

    assert result["status"] == "MISMATCHED"
    assert result["mismatch_type"] == "DUPLICATE_RESERVATION"

    assert result["reservation_count"] == 2

    # The comparison must not select reservation 603 simply because it happens to be the first row.
    assert result["reservation_id"] is None
    assert result["batch_id"] is None

    assert result["reservation_ids"] == [603, 604]

    assert result["reserved_quantities"] == [99, 1]

    assert result["reserved_quantity"] == 100

def test_compare_orphan_inventory_reservation():

    sales_df = pd.DataFrame(columns=["transaction_id",
                                     "invoice_number",
                                     "product_id",
                                     "quantity",
                                     "status",
                                     "created_at"])

    inventory_df = build_inventory_dataframe(transaction_id=106,
                                             reservation_id=605,
                                             batch_id=34,
                                             reserved_quantity=6,
                                             reserved_at="2026-08-08T14:00:00Z")

    sales_df, inventory_df = normalize_inputs(sales_df, inventory_df)

    results = compare_records(sales_df, inventory_df)

    orphan_results = [result for result in results if result.get("mismatch_type") == "ORPHAN_RESERVATION"]

    assert len(orphan_results) == 1

    result = orphan_results[0]

    assert result["transaction_id"] == 106
    assert result["status"] == "MISMATCHED"
    assert result["mismatch_type"] == "ORPHAN_RESERVATION"

    assert result["invoice_number"] is None

    assert result["quantity"] is None
    assert result["reserved_quantity"] == 6

    assert result["reservation_count"] == 1
    assert result["reservation_ids"] == [605]
    assert result["batch_ids"] == [34]
    assert result["reserved_quantities"] == [6]

def test_compare_multiple_transactions_returns_one_result_per_transaction():

    sales_df = pd.DataFrame([
            {
                "transaction_id": 107,
                "invoice_number": "INV-2026-000107",
                "product_id": 15,
                "quantity": 5,
                "status": "VALIDATED",
                "created_at": "2026-08-08T15:00:00Z"
            },
            {
                "transaction_id": 108,
                "invoice_number": "INV-2026-000108",
                "product_id": 16,
                "quantity": 8,
                "status": "COMPLETED",
                "created_at": "2026-08-08T16:00:00Z"
            },
            {
                "transaction_id": 109,
                "invoice_number": "INV-2026-000109",
                "product_id": 17,
                "quantity": 3,
                "status": "VALIDATED",
                "created_at": "2026-08-08T17:00:00Z"
            }])

    inventory_df = pd.DataFrame([
            {
                "transaction_id": 107,
                "reservation_id": 607,
                "batch_id": 36,
                "reserved_quantity": 5,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T15:01:00Z"
            },
            {
                "transaction_id": 108,
                "reservation_id": 608,
                "batch_id": 37,
                "reserved_quantity": 6,
                "status": "RESERVED",
                "reserved_at": "2026-08-08T16:01:00Z"
            }])

    sales_df, inventory_df = normalize_inputs(sales_df, inventory_df)

    results = compare_records(sales_df, inventory_df)

    results_by_transaction = {result["transaction_id"]: result for result in results}

    assert len(results) == 3

    assert results_by_transaction[107]["status"] == "MATCHED"

    assert results_by_transaction[108]["status"] == "MISMATCHED"
    assert (results_by_transaction[108]["mismatch_type"] == "QUANTITY_MISMATCH")

    assert results_by_transaction[109]["status"] == "MISSING"
    assert (results_by_transaction[109]["mismatch_type"] == "MISSING_RESERVATION")