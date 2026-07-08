from app.clients.sales_client import SalesClient

from app.services.normalization_service import (normalize_names, normalize_dates,normalize_amounts)

sales_client = SalesClient()

source_df = sales_client.get_sales_records()

source_df = normalize_names(source_df)
source_df = normalize_dates(source_df)
source_df = normalize_amounts(source_df)

print(source_df)