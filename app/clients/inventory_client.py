from typing import Any

import pandas as pd
import requests

from app.core.config import settings

class InventoryClient:

    def __init__(self) -> None:

        self.base_url = settings.INVENTORY_SERVICE_URL.rstrip("/")
        self.timeout = 10

    def get_inventory_records(self) -> pd.DataFrame:

        url = f"{self.base_url}/reservations/reconciliation"

        try:

            response = requests.get(url, timeout=self.timeout)

            response.raise_for_status()

        except requests.exceptions.Timeout as error:

            raise RuntimeError("Inventory Dispatch System request timed out") from error

        except requests.exceptions.HTTPError as error:

            status_code = error.response.status_code

            raise RuntimeError(f"Inventory Dispatch System returned HTTP {status_code}") from error

        except requests.exceptions.RequestException as error:

            raise RuntimeError("Failed to connect to Inventory Dispatch System") from error

        try:

            records: Any = response.json()

        except ValueError as error:

            raise RuntimeError("Inventory Dispatch System returned invalid JSON") from error

        if not isinstance(records, list):

            raise RuntimeError("Inventory Dispatch System returned an invalid response format")

        if not records:

            return pd.DataFrame(columns=["transaction_id",
                                         "reservation_id",
                                         "batch_id",
                                         "reserved_quantity",
                                         "status",
                                         "reserved_at"])

        required_fields = {"transaction_id",
                           "reservation_id",
                           "batch_id",
                           "reserved_quantity",
                           "status",
                           "reserved_at"}

        for index, record in enumerate(records):

            if not isinstance(record, dict):

                raise RuntimeError(f"Invalid Inventory reservation record at index {index}")

            missing_fields = required_fields - record.keys()

            if missing_fields:

                raise RuntimeError("Inventory Dispatch System response is missing " f"required fields: {sorted(missing_fields)}")

        return pd.DataFrame(records)