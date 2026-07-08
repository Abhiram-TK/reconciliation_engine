from app.clients.sales_client import SalesClient
from app.clients.inventory_client import InventoryClient

from app.services.normalization_service import (normalize_names, normalize_dates, normalize_amounts)

from app.services.mismatch_service import (detect_mismatches)

sales_client = SalesClient()
inventory_client = InventoryClient()

source_df = sales_client.get_sales_records()
target_df = inventory_client.get_inventory_records()

source_df = normalize_names(source_df)
source_df = normalize_dates(source_df)
source_df = normalize_amounts(source_df)

target_df = normalize_names(target_df)
target_df = normalize_dates(target_df)
target_df = normalize_amounts(target_df)

results = detect_mismatches(source_df, target_df)

for result in results:

    print()

    for key, value in result.items():

        print(f"{key}: {value}")