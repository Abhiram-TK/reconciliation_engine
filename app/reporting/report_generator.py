import json

import pandas as pd

from app.core.config import settings

class ReportGenerator:

    MISSING_MISMATCH_TYPE = "MISSING_RESERVATION"

    DETAILED_MISMATCH_TYPES = {"DUPLICATE_RESERVATION",
                               "QUANTITY_MISMATCH",
                               "ORPHAN_RESERVATION"}

    def _serialize_value(self, value):

        if isinstance(value, (list, dict, tuple)):

            return json.dumps(value, default=str, ensure_ascii=False)

        return value

    def _prepare_records(self, records):

        prepared_records = []

        for record in records:

            prepared_record = {key: self._serialize_value(value) for key, value in record.items()}

            prepared_records.append(prepared_record)

        return prepared_records

    def _build_dataframe(self, records):

        prepared_records = self._prepare_records(records)

        return pd.DataFrame(prepared_records)

    @staticmethod
    def _classify_result(result):

        mismatch_type = result.get("mismatch_type")

        if mismatch_type == ReportGenerator.MISSING_MISMATCH_TYPE:

            return "MISSING"

        if mismatch_type in ReportGenerator.DETAILED_MISMATCH_TYPES:

            return "MISMATCHED"

        status = result.get("status")

        if status in {"MATCHED", "MISMATCHED", "MISSING"}:

            return status

        raise ValueError("Reconciliation result has no valid status or mismatch_type: " f"{result}")

    def generate_reports(self, results) -> None:

        settings.reports_dir.mkdir(parents=True, exist_ok=True)

        matched_records = []
        mismatched_records = []
        missing_records = []

        for result in results:

            report_type = self._classify_result(result)

            if report_type == "MATCHED":

                matched_records.append(result)

            elif report_type == "MISMATCHED":

                mismatched_records.append(result)

            elif report_type == "MISSING":

                missing_records.append(result)

        matched_df = self._build_dataframe(matched_records)

        mismatched_df = self._build_dataframe(mismatched_records)

        missing_df = self._build_dataframe(missing_records)

        matched_df.to_csv(settings.reports_dir / "matched.csv", index=False)

        mismatched_df.to_csv(settings.reports_dir / "mismatched.csv", index=False)

        missing_df.to_csv(settings.reports_dir / "missing.csv", index=False)