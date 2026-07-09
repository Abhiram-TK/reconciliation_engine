import pandas as pd

from app.core.config import settings

class InventoryClient:

    def get_inventory_records(self) -> pd.DataFrame:

        return pd.read_csv(settings.target_file)