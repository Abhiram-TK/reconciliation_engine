import pandas as pd

from app.core.config import settings

class SalesClient:

    def get_sales_records(self) -> pd.DataFrame:

        return pd.read_csv(settings.source_file)