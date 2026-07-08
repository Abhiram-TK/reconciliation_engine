import pandas as pd

from app.core.config import TARGET_FILE

class InventoryClient:

    def get_inventory_records(self) -> pd.DataFrame:

        return pd.read_csv(TARGET_FILE)