from app.clients.sales_client import SalesClient
from app.clients.inventory_client import InventoryClient

sales_client = SalesClient()
inventory_client = InventoryClient()

source_df = sales_client.get_sales_records()
target_df = inventory_client.get_inventory_records()

print(f"Rows Loaded: {len(source_df)}")
print(f"Rows Loaded: {len(target_df)}")