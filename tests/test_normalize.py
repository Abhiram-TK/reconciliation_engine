import pandas as pd

from app.services.normalization_service import normalize_dataframe
from app.services.compare_service import compare_records

SALES_COLUMNS = {"transaction_id",
                 "invoice_number",
                 "product_id",
                 "quantity",
                 "status",
                 "created_at"}

INVENTORY_COLUMNS = {"transaction_id",
                     "reservation_id",
                     "batch_id"
                     "reserved_quantity",
                     "status",
                     "reserved_at"}

def test_normalize_sales_transaction_data():

    sales_df = pd.DataFrame([{"transaction_id": "101",
                              "invoice_number": "  INV-2026-000101  ",
                              "product_id": "10",
                              "quantity": "5",
                              "status": "  validated  ",
                              "created_at": "2026-08-08T09:00:00Z"}])

    normalized_df = normalize_dataframe(sales_df)

    assert normalized_df["transaction_id"].iloc[0] == 101
    assert normalized_df["invoice_number"].iloc[0] == ("INV-2026-000101")
    assert normalized_df["product_id"].iloc[0] == 10
    assert normalized_df["quantity"].iloc[0] == 5
    assert normalized_df["status"].iloc[0] == "VALIDATED"

    assert pd.api.types.is_integer_dtype(normalized_df["transaction_id"])

    assert pd.api.types.is_integer_dtype(normalized_df["product_id"])

    assert pd.api.types.is_numeric_dtype(normalized_df["quantity"])

    assert pd.api.types.is_datetime64_any_dtype(normalized_df["created_at"])

    assert normalized_df["created_at"].iloc[0].tz is not None


def test_normalize_inventory_reservation_data():

    inventory_df = pd.DataFrame([{"transaction_id": "101",
                                  "reservation_id": "501",
                                  "batch_id": "20",
                                  "reserved_quantity": "5",
                                  "status": "  reserved  ",
                                  "reserved_at": "2026-08-08T09:01:00Z"}])

    normalized_df = normalize_dataframe(inventory_df)

    assert normalized_df["transaction_id"].iloc[0] == 101
    assert normalized_df["reservation_id"].iloc[0] == "501"
    assert normalized_df["batch_id"].iloc[0] == "20"
    assert normalized_df["reserved_quantity"].iloc[0] == 5
    assert normalized_df["status"].iloc[0] == "RESERVED"

    assert pd.api.types.is_integer_dtype(normalized_df["transaction_id"])

    assert pd.api.types.is_numeric_dtype(normalized_df["reserved_quantity"])

    assert pd.api.types.is_datetime64_any_dtype(normalized_df["reserved_at"])

    assert normalized_df["reserved_at"].iloc[0].tz is not None

def test_normalization_preserves_sales_upstream_contract():

    sales_df = pd.DataFrame([{"transaction_id": "101",
                              "invoice_number": "INV-2026-000101",
                              "product_id": "10",
                              "quantity": "5",
                              "status": "validated",
                              "created_at": "2026-08-08T09:00:00Z"}])

    normalized_df = normalize_dataframe(sales_df)

    assert set(normalized_df.columns) == SALES_COLUMNS

def test_normalization_preserves_inventory_upstream_contract():

    inventory_df = pd.DataFrame([{"transaction_id": "101",
                                  "reservation_id": "501",
                                  "batch_id": "20",
                                  "reserved_quantity": "5",
                                  "status": "reserved",
                                  "reserved_at": "2026-08-08T09:01:00Z"}])

    normalized_df = normalize_dataframe(inventory_df)

    assert set(normalized_df.columns) == INVENTORY_COLUMNS

def test_sales_and_inventory_transaction_ids_are_compatible():

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

    assert (normalized_sales["transaction_id"].dtype == normalized_inventory["transaction_id"].dtype)

    assert (normalized_sales["transaction_id"].iloc[0] == normalized_inventory["transaction_id"].iloc[0])

    assert pd.api.types.is_integer_dtype(normalized_sales["transaction_id"])

    assert pd.api.types.is_integer_dtype(normalized_inventory["transaction_id"])

def test_sales_and_inventory_quantities_are_compatible():

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

    sales_quantity = normalized_sales["quantity"].iloc[0]

    reserved_quantity = normalized_inventory["reserved_quantity"].iloc[0]

    assert pd.api.types.is_numeric_dtype(normalized_sales["quantity"])

    assert pd.api.types.is_numeric_dtype(normalized_inventory["reserved_quantity"])

    assert sales_quantity == reserved_quantity

def test_normalized_upstream_data_can_be_compared():

    sales_df = pd.DataFrame([{"transaction_id": "101",
                              "invoice_number": "  INV-2026-000101  ",
                              "product_id": "10",
                              "quantity": "5",
                              "status": "  validated  ",
                              "created_at": "2026-08-08T09:00:00Z"}])

    inventory_df = pd.DataFrame([{"transaction_id": "101",
                                  "reservation_id": "501",
                                  "batch_id": "20",
                                  "reserved_quantity": "5",
                                  "status": "  reserved  ",
                                  "reserved_at": "2026-08-08T09:01:00Z"}])

    normalized_sales = normalize_dataframe(sales_df)

    normalized_inventory = normalize_dataframe(inventory_df)

    results = compare_records(normalized_sales, normalized_inventory)

    assert len(results) == 1

    result = results[0]

    assert result["transaction_id"] == 101
    assert result["status"] == "MATCHED"
    assert result["quantity"] == 5
    assert result["reserved_quantity"] == 5


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

def test_normalization_preserves_row_count():

    sales_df = pd.DataFrame([
            {
                "transaction_id": "101",
                "invoice_number": "INV-2026-000101",
                "product_id": "10",
                "quantity": "5",
                "status": "validated",
                "created_at": "2026-08-08T09:00:00Z"
            },
            {
                "transaction_id": "102",
                "invoice_number": "INV-2026-000102",
                "product_id": "11",
                "quantity": "8",
                "status": "completed",
                "created_at": "2026-08-08T10:00:00Z"
            }])

    inventory_df = pd.DataFrame([
            {
                "transaction_id": "101",
                "reservation_id": "501",
                "batch_id": "20",
                "reserved_quantity": "5",
                "status": "reserved",
                "reserved_at": "2026-08-08T09:01:00Z"
            },
            {
                "transaction_id": "102",
                "reservation_id": "502",
                "batch_id": "21",
                "reserved_quantity": "8",
                "status": "reserved",
                "reserved_at": "2026-08-08T10:01:00Z"
            }])

    normalized_sales = normalize_dataframe(sales_df)

    normalized_inventory = normalize_dataframe(inventory_df)

    assert len(normalized_sales) == len(sales_df)

    assert len(normalized_inventory) == len(inventory_df)