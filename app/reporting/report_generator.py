import json
from pathlib import Path

import pandas as pd

from app.core.config import settings

class ReportGenerator:

    MISSING_MISMATCH_TYPE = "MISSING_RESERVATION"

    DETAILED_MISMATCH_TYPES = {"DUPLICATE_RESERVATION",
                               "QUANTITY_MISMATCH",
                               "ORPHAN_RESERVATION"}

    SOURCE_SYSTEM = "Project 3 — Sales Transaction Service"
    TARGET_SYSTEM = "Project 2 — Inventory Dispatch System"
    COMPARISON_KEY = "transaction_id"

    SALES_FIELDS = ["transaction_id",
                    "invoice_number",
                    "product_id",
                    "quantity",
                    "status",
                    "created_at"]

    INVENTORY_FIELDS = ["transaction_id",
                        "reservation_id",
                        "batch_id",
                        "reserved_quantity",
                        "status",
                        "reserved_at"]

    RESULT_DEFINITIONS = {"MATCHED": ("Sales transaction has a corresponding Inventory reservation and the compared quantities agree."),
                          "MISMATCHED": ("Both sides participate in the comparison, but a configured reconciliation discrepancy exists."),
                          "MISSING": ("Sales transaction exists but no corresponding Inventory reservation exists.")}

    def _serialize_value(self, value):

        if isinstance(value, (list, dict, tuple)):

            return json.dumps(value,
                              default=str,
                              ensure_ascii=False)

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

    def _default_run_metadata(self, results):

        return {"run_id": "UNSPECIFIED",
                "execution_time": "UNSPECIFIED",
                "source": {"project": self.SOURCE_SYSTEM,
                           "service": "Sales Transaction Service",
                           "endpoint": "/internal/transactions",
                           "records_retrieved": None,
                           "fields": self.SALES_FIELDS},
                "target": {"project": self.TARGET_SYSTEM,
                           "service": "Inventory Dispatch System",
                           "endpoint": "/reservations/reconciliation",
                           "records_retrieved": None,
                           "fields": self.INVENTORY_FIELDS},
                "reconciliation": {"comparison_key": self.COMPARISON_KEY,
                                   "source_system": self.SOURCE_SYSTEM,
                                   "target_system": self.TARGET_SYSTEM}}

    def _normalize_run_metadata(self, results, run_metadata):

        if run_metadata is None:

            return self._default_run_metadata(results)

        if not isinstance(run_metadata, dict):

            raise TypeError("run_metadata must be a dictionary")

        metadata = dict(run_metadata)

        source = dict(metadata.get("source", {}))
        target = dict(metadata.get("target", {}))
        reconciliation = dict(metadata.get("reconciliation", {}))

        source.setdefault("project", self.SOURCE_SYSTEM)
        source.setdefault("service", "Sales Transaction Service")
        source.setdefault("endpoint", "/internal/transactions")
        source.setdefault("records_retrieved", None)
        source.setdefault("fields", self.SALES_FIELDS)

        target.setdefault("project", self.TARGET_SYSTEM)
        target.setdefault("service", "Inventory Dispatch System")
        target.setdefault("endpoint", "/reservations/reconciliation")
        target.setdefault("records_retrieved", None)
        target.setdefault("fields", self.INVENTORY_FIELDS)

        reconciliation.setdefault("comparison_key", self.COMPARISON_KEY)
        reconciliation.setdefault("source_system", self.SOURCE_SYSTEM)
        reconciliation.setdefault("target_system", self.TARGET_SYSTEM)

        metadata["source"] = source
        metadata["target"] = target
        metadata["reconciliation"] = reconciliation

        metadata.setdefault("run_id", "UNSPECIFIED")
        metadata.setdefault("execution_time", "UNSPECIFIED")

        return metadata

    @staticmethod

    def _count_status(records, status):

        return sum(1 for record in records if record.get("status") == status)

    @staticmethod

    def _count_mismatch_type(records, mismatch_type):

        return sum(1 for record in records if record.get("mismatch_type") == mismatch_type)

    def _add_provenance(self,
                        dataframe,
                        report_type,
                        run_metadata):

        provenance = {"run_id": run_metadata["run_id"],
                      "source_system": (run_metadata["reconciliation"].get("source_system",
                                                                           self.SOURCE_SYSTEM)),
                      "source_endpoint": run_metadata["source"].get("endpoint",
                                                                    "/internal/transactions"),
                      "target_system": (run_metadata["reconciliation"].get("target_system",
                                                                           self.TARGET_SYSTEM)),
                      "target_endpoint": run_metadata["target"].get("endpoint",
                                                                    "/reservations/reconciliation"),
                      "comparison_key": (run_metadata["reconciliation"].get("comparison_key",
                                                                            self.COMPARISON_KEY)),
                      "report_type": report_type}

        for column, value in reversed(list(provenance.items())):

            dataframe.insert(0, column, value)

        return dataframe

    def _build_report_text(self,
                           run_metadata,
                           matched_records,
                           mismatched_records,
                           missing_records):

        source = run_metadata["source"]
        target = run_metadata["target"]
        reconciliation = run_metadata["reconciliation"]

        matched_count = len(matched_records)
        mismatched_count = len(mismatched_records)
        missing_count = len(missing_records)

        total_results = (matched_count + mismatched_count + missing_count)

        mismatch_types = ["QUANTITY_MISMATCH",
                          "DUPLICATE_RESERVATION",
                          "MISSING_RESERVATION",
                          "ORPHAN_RESERVATION"]

        mismatch_counts = {mismatch_type: (self._count_mismatch_type(mismatched_records,
                                                                     mismatch_type) + self._count_mismatch_type(missing_records,
                                                                                                                mismatch_type)) for mismatch_type in mismatch_types}

        sales_fields = source.get("fields", self.SALES_FIELDS)

        inventory_fields = target.get("fields", self.INVENTORY_FIELDS)

        lines = [
            "RECONCILIATION RUN",
            "────────────────────────────────────────────",
            "",
            f"Run ID:                  {run_metadata['run_id']}",
            (
                "Execution time:          "
                f"{run_metadata['execution_time']}"
            ),
            "",
            "SOURCE DATA",
            "────────────────────────────────────────────",
            f"System:                  {source.get('project')}",
            f"Service:                 {source.get('service')}",
            f"Endpoint:                GET {source.get('endpoint')}",
            (
                "Records retrieved:      "
                f"{source.get('records_retrieved')}"
            ),
            "",
            "Sales fields:"]

        lines.extend(f"  {field}" for field in sales_fields)

        lines.extend(
            [
                "",
                "TARGET DATA",
                "────────────────────────────────────────────",
                f"System:                  {target.get('project')}",
                f"Service:                 {target.get('service')}",
                (
                    "Endpoint:                GET "
                    f"{target.get('endpoint')}"
                ),
                (
                    "Records retrieved:      "
                    f"{target.get('records_retrieved')}"
                ),
                "",
                "Inventory fields:"])

        lines.extend(f"  {field}" for field in inventory_fields)

        lines.extend(
            [
                "",
                "RECONCILIATION",
                "────────────────────────────────────────────",
                (
                    "Comparison key:         "
                    f"{reconciliation.get('comparison_key')}"
                ),
                (
                    "Source:                  "
                    f"{reconciliation.get('source_system')}"
                ),
                (
                    "Target:                  "
                    f"{reconciliation.get('target_system')}"
                ),
                "",
                "RESULT",
                "────────────────────────────────────────────",
                f"MATCHED:                 {matched_count}",
                f"MISMATCHED:              {mismatched_count}",
                f"MISSING:                 {missing_count}",
                f"TOTAL RESULTS:           {total_results}",
                "",
                "RESULT DEFINITIONS",
                "────────────────────────────────────────────",
                (
                    "MATCHED:                 "
                    f"{self.RESULT_DEFINITIONS['MATCHED']}"
                ),
                "",
                (
                    "MISMATCHED:              "
                    f"{self.RESULT_DEFINITIONS['MISMATCHED']}"
                ),
                "",
                (
                    "MISSING:                 "
                    f"{self.RESULT_DEFINITIONS['MISSING']}"
                ),
                "",
                "MISMATCH TYPES",
                "────────────────────────────────────────────",
                (
                    "QUANTITY_MISMATCH:       "
                    f"{mismatch_counts['QUANTITY_MISMATCH']}"
                ),
                (
                    "DUPLICATE_RESERVATION:   "
                    f"{mismatch_counts['DUPLICATE_RESERVATION']}"
                ),
                (
                    "MISSING_RESERVATION:     "
                    f"{mismatch_counts['MISSING_RESERVATION']}"
                ),
                (
                    "ORPHAN_RESERVATION:      "
                    f"{mismatch_counts['ORPHAN_RESERVATION']}"
                ),
                "",
                "DATA OWNERSHIP",
                "────────────────────────────────────────────",
                (
                    "Project 1 — Authentication Service:"
                    " authentication and authorization infrastructure"
                ),
                (
                    "Project 2 — Inventory Dispatch System:"
                    " authoritative owner of reservations"
                ),
                (
                    "Project 3 — Sales Transaction Service:"
                    " authoritative owner of transactions"
                ),
                (
                    "Project 4 — Reconciliation Automation Engine:"
                    " owner of reconciliation reports and results"
                ),
                ""])

        return "\n".join(lines)

    def generate_reports(self,
                         results,
                         run_metadata=None) -> None:

        reports_dir = Path(settings.reports_dir)

        reports_dir.mkdir(parents=True, exist_ok=True)

        run_metadata = self._normalize_run_metadata(results, run_metadata)

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

        matched_df = self._add_provenance(matched_df,
                                          "MATCHED",
                                          run_metadata)

        mismatched_df = self._add_provenance(mismatched_df,
                                             "MISMATCHED",
                                             run_metadata)

        missing_df = self._add_provenance(missing_df,
                                          "MISSING",
                                          run_metadata)

        matched_df.to_csv(reports_dir / "matched.csv", index=False)

        mismatched_df.to_csv(reports_dir / "mismatched.csv", index=False)

        missing_df.to_csv(reports_dir / "missing.csv", index=False)

        report_text = self._build_report_text(run_metadata=run_metadata,
                                              matched_records=matched_records,
                                              mismatched_records=mismatched_records,
                                              missing_records=missing_records)

        report_path = (reports_dir / "reconciliation_report.txt")

        report_path.write_text(report_text, encoding="utf-8")