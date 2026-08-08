import pandas as pd

from app.services.normalization_service import normalize_dataframe

def test_normalize_sales_transaction_data():

    sales_df = pd.DataFrame([{"transaction_id": "101",
                              "invoice_number": "  INV-2026-000101  ",
                              "product_id": "10",
                              "quantity": "5",
                              "status": "  validated  ",
                              "created_at": "2026-08-08T09:00:00Z"}])

    normalized_df = normalize_dataframe(sales_df)

    assert normalized_df["transaction_id"].iloc[0] == 101
    assert normalized_df["invoice_number"].iloc[0] == "INV-2026-000101"
    assert normalized_df["product_id"].iloc[0] == 10
    assert normalized_df["quantity"].iloc[0] == 5
    assert normalized_df["status"].iloc[0] == "VALIDATED"

    assert pd.api.types.is_integer_dtype(normalized_df["transaction_id"])

    assert pd.api.types.is_integer_dtype(normalized_df["product_id"])

    assert pd.api.types.is_numeric_dtype(normalized_df["quantity"])

    assert pd.api.types.is_datetime64_any_dtype(normalized_df["created_at"])

def test_normalize_inventory_reservation_data():

    inventory_df = pd.DataFrame([{"transaction_id": "101",
                                  "reservation_id": "501",
                                  "batch_id": "20",
                                  "reserved_quantity": "5",
                                  "status": "  reserved  ",
                                  "reserved_at": "2026-08-08T09:01:00Z"}])

    normalized_df = normalize_dataframe(inventory_df)

    assert normalized_df["transaction_id"].iloc[0] == 101
    assert normalized_df["reservation_id"].iloc[0] == 501
    assert normalized_df["batch_id"].iloc[0] == 20
    assert normalized_df["reserved_quantity"].iloc[0] == 5
    assert normalized_df["status"].iloc[0] == "RESERVED"

    assert pd.api.types.is_integer_dtype(normalized_df["transaction_id"])

    assert pd.api.types.is_integer_dtype(normalized_df["reservation_id"])

    assert pd.api.types.is_integer_dtype(normalized_df["batch_id"])

    assert pd.api.types.is_numeric_dtype(normalized_df["reserved_quantity"])

    assert pd.api.types.is_datetime64_any_dtype(normalized_df["reserved_at"])

def test_normalization_preserves_upstream_contract_fields():

    sales_df = pd.DataFrame([{"transaction_id": "101",
                              "invoice_number": "INV-2026-000101",
                              "product_id": "10",
                              "quantity": "5",
                              "status": "validated",
                              "created_at": "2026-08-08T09:00:00Z"}])

    inventory_df = pd.DataFrame([{"transaction_id": "101",
                                  "reservation_id": "501",
                                  "batch_id": "20",
                                  "reserved_quantity": "5",
                                  "status": "reserved",
                                  "reserved_at": "2026-08-08T09:01:00Z"}])

    normalized_sales = normalize_dataframe(sales_df)
    normalized_inventory = normalize_dataframe(inventory_df)

    assert set(normalized_sales.columns) == {"transaction_id",
                                             "invoice_number"
                                             "product_id",
                                             "quantity",
                                             "status",
                                             "created_at"}

    assert set(normalized_inventory.columns) == {"transaction_id",
                                                 "reservation_id",
                                                 "batch_id",
                                                 "reserved_quantity",
                                                 "status",
                                                 "reserved_at"}

def test_normalization_does_not_create_obsolete_csv_fields():

    sales_df = pd.DataFrame([{"transaction_id": "101",
                              "invoice_number": "INV-2026-000101",
                              "product_id": "10",
                              "quantity": "5",
                              "status": "validated",
                              "created_at": "2026-08-08T09:00:00Z"}])

    inventory_df = pd.DataFrame([{"transaction_id": "101",
                                  "reservation_id": "501",
                                  "batch_id": "20",
                                  "reserved_quantity": "5",
                                  "status": "reserved",
                                  "reserved_at": "2026-08-08T09:01:00Z"}])

    normalized_sales = normalize_dataframe(sales_df)
    normalized_inventory = normalize_dataframe(inventory_df)

    obsolete_fields = {"invoice_id",
                       "customer_name",
                       "invoice_date",
                       "amount"}

    assert not (obsolete_fields & set(normalized_sales.columns))

    assert not (obsolete_fields & set(normalized_inventory.columns))