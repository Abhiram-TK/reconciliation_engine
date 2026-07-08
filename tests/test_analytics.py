import pandas as pd

from app.clients.sales_client import SalesClient 
from app.clients.inventory_client import InventoryClient

from app.services.compare_service import compare_records

from app.reporting.analytics import (generate_summary, save_summary, generate_chart)

from app.services.normalization_service import (normalize_names, normalize_dates, normalize_amounts)

sales_client = SalesClient()
inventory_client = InventoryClient()

source_df = sales_client.get_sales_records()
target_df = inventory_client.get_inventory_records()

source_df = normalize_names(source_df)
target_df = normalize_names(target_df)

source_df = normalize_dates(source_df)
target_df = normalize_dates(target_df)

source_df = normalize_amounts(source_df)
target_df = normalize_amounts(target_df)

comparison_results = compare_records(source_df, target_df)

comparison_df = pd.DataFrame(comparison_results)

print(comparison_df.head())

summary_df = generate_summary(comparison_df)

print(summary_df)

save_summary(summary_df)

generate_chart(summary_df)

print("Analytics Generated Successfully")