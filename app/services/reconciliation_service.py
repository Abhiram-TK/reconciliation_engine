import pandas as pd

from app.services.normalization_service import normalize_dataframe

from app.services.compare_service import compare_records

from app.services.mismatch_service import detect_mismatches

from app.reporting.analytics import (generate_summary, save_summary, generate_chart)

class ReconciliationService:

    SALES_REQUIRED_COLUMNS = {"transaction_id",
                              "invoice_number",
                              "product_id",
                              "quantity",
                              "status",
                              "created_at"}

    INVENTORY_REQUIRED_COLUMNS = {"transaction_id",
                                  "reservation_id",
                                  "batch_id",
                                  "reserved_quantity",
                                  "status",
                                  "reserved_at"}

    def __init__(self, sales_client, inventory_client, report_generator):

        self.sales_client = sales_client
        self.inventory_client = inventory_client
        self.report_generator = report_generator

        self.source_df = None
        self.target_df = None

        self.comparison_results = None
        self.comparison_df = None

        self.mismatches = None
        self.summary_df = None

    @staticmethod
    def _validate_columns(dataframe: pd.DataFrame, required_columns: set[str], source_name: str) -> None:

        missing_columns = (required_columns - set(dataframe.columns))

        if missing_columns:

            raise ValueError(f"{source_name} data is missing required columns: " f"{sorted(missing_columns)}")

    def retrieve_data(self):

        self.source_df = (self.sales_client.get_sales_records())

        self.target_df = (self.inventory_client.get_inventory_records())

        self._validate_columns(dataframe=self.source_df,
                               required_columns=self.SALES_REQUIRED_COLUMNS,
                               source_name="Sales Transaction Service")

        self._validate_columns(dataframe=self.target_df,
                               required_columns=self.INVENTORY_REQUIRED_COLUMNS,
                               source_name="Inventory Dispatch System")

        return self.source_df, self.target_df

    def normalize(self):

        if self.source_df is None:
            
            raise RuntimeError("Sales data must be retrieved before normalization.")

        if self.target_df is None:
            
            raise RuntimeError("Inventory data must be retrieved before normalization.")

        self.source_df = normalize_dataframe(self.source_df)

        self.target_df = normalize_dataframe(self.target_df)

        return self.source_df, self.target_df

    def compare(self):

        self.comparison_results = compare_records(self.source_df, self.target_df)

        self.comparison_df = pd.DataFrame(self.comparison_results)

        return self.comparison_results

    def detect_mismatches(self):

        self.mismatches = detect_mismatches(self.source_df, self.target_df)

        return self.mismatches

    @staticmethod
    def _merge_mismatch_details(comparison_results: list[dict], mismatches: list[dict]) -> list[dict]:

        merged_results = [result.copy() for result in comparison_results]

        result_by_transaction_id = {result["transaction_id"]: result for result in merged_results}

        orphan_mismatches = []

        for mismatch in mismatches:

            transaction_id = mismatch["transaction_id"]

            existing_result = (result_by_transaction_id.get(transaction_id))

            if existing_result is not None:

                # Preserve the primary comparison status.
                #
                # Mismatch detection enriches the result but does not independently create a second row for the same transaction.
                for key, value in mismatch.items():

                    if key == "transaction_id":

                        continue

                    existing_result[key] = value

                # Detailed mismatch detection is authoritative regarding discrepancy classification.
                existing_result["status"] = "MISMATCHED"

            else:

                # This occurs for ORPHAN_RESERVATION because there is no corresponding Sales transaction for the comparison layer to iterate over.
                orphan_result = {"transaction_id": transaction_id,
                                 "invoice_number": mismatch.get("invoice_number"),
                                 "status": "MISMATCHED",
                                 "sales_status": None,
                                 "inventory_status": (mismatch.get("reservation_statuses")),
                                 "quantity": mismatch.get("sales_quantity"),
                                 "reserved_quantity": mismatch.get("reserved_quantity")}

                orphan_result.update(mismatch)

                orphan_mismatches.append(orphan_result)

        merged_results.extend(orphan_mismatches)

        return merged_results

    def combine_results(self):

        if self.comparison_results is None:

            raise RuntimeError("Comparison must be completed before results can be combined.")

        if self.mismatches is None:

            raise RuntimeError("Mismatch detection must be completed before results can be combined.")

        self.comparison_results = (self._merge_mismatch_details(comparison_results=self.comparison_results, mismatches=self.mismatches))

        self.comparison_df = pd.DataFrame(self.comparison_results)

        return self.comparison_results

    def generate_reports(self):

        self.report_generator.generate_reports(self.comparison_results)

        return self.comparison_results

    def generate_analytics(self):

        self.summary_df = generate_summary(self.comparison_df)

        save_summary(self.summary_df)

        return self.summary_df

    def generate_visualizations(self):

        generate_chart(self.summary_df)

    def run(self):

        self.retrieve_data()

        self.normalize()

        self.compare()

        self.detect_mismatches()

        self.combine_results()

        self.generate_reports()

        self.generate_analytics()

        self.generate_visualizations()

        return {"source_df": self.source_df,
                "target_df": self.target_df,
                "comparison_results": self.comparison_results,
                "comparison_df": self.comparison_df,
                "mismatches": self.mismatches,
                "summary_df": self.summary_df}