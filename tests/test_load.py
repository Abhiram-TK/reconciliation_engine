import pandas as pd

from app.clients.sales_client import SalesClient
from app.clients.inventory_client import InventoryClient

from app.services.normalization_service import normalize_dataframe

SALES_COLUMNS = {"transaction_id",
                 "invoice_number",
                 "product_id"
                 "quantity",
                 "status",
                 "created_at"}

INVENTORY_COLUMNS = {"transaction_id",
                     "reservation_id"
                     "batch_id",
                     "reserved_quantity",
                     "status",
                     "reserved_at"}

def test_sales_service_load():

    sales_client = SalesClient()

    sales_df = sales_client.get_sales_records()

    assert isinstance(sales_df, pd.DataFrame)

    assert not sales_df.empty

    assert SALES_COLUMNS.issubset(sales_df.columns)

    normalized_df = normalize_dataframe(sales_df)

    assert pd.api.types.is_integer_dtype(normalized_df["transaction_id"])

    assert pd.api.types.is_integer_dtype(normalized_df["product_id"])

    assert pd.api.types.is_numeric_dtype(normalized_df["quantity"])

    assert pd.api.types.is_datetime64_any_dtype(normalized_df["created_at"])

    assert (normalized_df["status"].str.strip().eq(normalized_df["status"]).all())

def test_inventory_service_load():

    inventory_client = InventoryClient()

    inventory_df = (inventory_client.get_inventory_records())

    assert isinstance(inventory_df, pd.DataFrame)

    assert not inventory_df.empty

    assert INVENTORY_COLUMNS.issubset(inventory_df.columns)

    normalized_df = normalize_dataframe(inventory_df)

    assert pd.api.types.is_integer_dtype(normalized_df["transaction_id"])

    assert pd.api.types.is_integer_dtype(normalized_df["reservation_id"])

    assert pd.api.types.is_integer_dtype(normalized_df["batch_id"])

    assert pd.api.types.is_numeric_dtype(normalized_df["reserved_quantity"])

    assert pd.api.types.is_datetime64_any_dtype(normalized_df["reserved_at"])

    assert (normalized_df["status"].str.strip().eq(normalized_df["status"]).all())

def test_upstream_transaction_linkage():

    sales_client = SalesClient()
    inventory_client = InventoryClient()

    sales_df = normalize_dataframe(sales_client.get_sales_records())

    inventory_df = normalize_dataframe(inventory_client.get_inventory_records())

    sales_transaction_ids = set(sales_df["transaction_id"])

    inventory_transaction_ids = set(inventory_df["transaction_id"])

    assert sales_transaction_ids
    assert inventory_transaction_ids

    # The common identifier used by the reconciliation layer is transaction_id.
    assert (sales_transaction_ids & inventory_transaction_ids)