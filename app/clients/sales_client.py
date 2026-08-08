from typing import Any

import pandas as pd
import requests

from app.core.config import settings

class SalesClient:

    def __init__(self) -> None:

        self.base_url = settings.SALES_SERVICE_URL.rstrip("/")
        self.timeout = 10

    def get_sales_records(self) -> pd.DataFrame:

        url = f"{self.base_url}/internal/transactions"

        try:

            response = requests.get(url, timeout=self.timeout)

            response.raise_for_status()

        except requests.exceptions.Timeout as error:

            raise RuntimeError("Sales Transaction Service request timed out") from error

        except requests.exceptions.HTTPError as error:

            status_code = error.response.status_code

            raise RuntimeError(f"Sales Transaction Service returned HTTP {status_code}") from error

        except requests.exceptions.RequestException as error:

            raise RuntimeError("Failed to connect to Sales Transaction Service") from error

        try:

            records: Any = response.json()

        except ValueError as error:

            raise RuntimeError("Sales Transaction Service returned invalid JSON") from error

        if not isinstance(records, list):

            raise RuntimeError("Sales Transaction Service returned an invalid response format")

        if not records:

            return pd.DataFrame(columns=["transaction_id",
                                         "invoice_number",
                                         "product_id",
                                         "quantity",
                                         "status",
                                         "created_at",])

        required_fields = {"transaction_id",
                           "invoice_number",
                           "product_id",
                           "quantity",
                           "status",
                           "created_at"}

        for index, record in enumerate(records):

            if not isinstance(record, dict):

                raise RuntimeError(f"Invalid Sales transaction record at index {index}")

            missing_fields = required_fields - record.keys()

            if missing_fields:

                raise RuntimeError("Sales Transaction Service response is missing " f"required fields: {sorted(missing_fields)}")

        return pd.DataFrame(records)