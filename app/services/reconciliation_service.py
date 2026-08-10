import pandas as pd

from app.services.normalization_service import normalize_dataframe

from app.services.compare_service import compare_records

from app.services.mismatch_service import detect_mismatches

from app.services.fuzzy_match_service import fuzzy_match_field

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

    def __init__(self, sales_client, inventory_client, report_generator, fuzzy_match_field_name=None, fuzzy_match_threshold=90.0):

        self.sales_client = sales_client
        self.inventory_client = inventory_client
        self.report_generator = report_generator

        self.fuzzy_match_field_name = fuzzy_match_field_name
        self.fuzzy_match_threshold = fuzzy_match_threshold

        self.source_df = None
        self.target_df = None

        self.comparison_results = None
        self.comparison_df = None

        self.mismatches = None
        self.fuzzy_matches = None
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

    def apply_fuzzy_matching(self):

        self.fuzzy_matches = {}

        if self.fuzzy_match_field_name is None:

            return self.comparison_results

        field_name = self.fuzzy_match_field_name

        if field_name in {"transaction_id", "invoice_number", "product_id"}:

            raise ValueError("Fuzzy matching cannot be used for authoritative " f"reconciliation key field: {field_name}")

        if field_name not in self.source_df.columns:

            raise ValueError("Configured fuzzy-match field is missing from " f"Sales data: {field_name}")

        if field_name not in self.target_df.columns:

            raise ValueError("Configured fuzzy-match field is missing from " f"Inventory data: {field_name}")

        target_by_transaction_id = (self.target_df.set_index("transaction_id"))

        for result in self.comparison_results:

            transaction_id = result["transaction_id"]

            if transaction_id not in target_by_transaction_id.index:

                continue

            source_rows = self.source_df[self.source_df["transaction_id"] == transaction_id]

            target_rows = self.target_df[self.target_df["transaction_id"] == transaction_id]

            if source_rows.empty or target_rows.empty:

                continue

            source_value = source_rows.iloc[0][field_name]

            # Fuzzy matching is secondary and does not select or replace the authoritative transaction match.
            #
            # For duplicate reservations, compare against each textual value and retain the best score.
            scores = []

            for _, target_row in target_rows.iterrows():

                fuzzy_result = fuzzy_match_field(left_value=source_value,
                                                 right_value=target_row[field_name],
                                                 field_name=field_name,
                                                 threshold=self.fuzzy_match_threshold)

                scores.append(fuzzy_result)

            if not scores:

                continue

            best_result = max(scores, key=lambda item: item["score"])

            fuzzy_result = {"field": best_result["field"],
                            "score": best_result["score"],
                            "threshold": best_result["threshold"],
                            "matched": best_result["matched"]}

            result["fuzzy_match"] = fuzzy_result

            self.fuzzy_matches[transaction_id] = fuzzy_result

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

        self.apply_fuzzy_matching()

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
                "fuzzy_matches": self.fuzzy_matches,
                "summary_df": self.summary_df}