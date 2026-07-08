import pandas as pd

from app.core.config import SOURCE_FILE

class SalesClient:

    def get_sales_records(self) -> pd.DataFrame:

        return pd.read_csv(SOURCE_FILE)