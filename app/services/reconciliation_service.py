import pandas as pd

from app.services.normalization_service import (normalize_names, normalize_dates, normalize_amounts)

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

        missing_columns = required_columns - set(dataframe.columns)

        if missing_columns:

            raise ValueError(f"{source_name} data is missing required columns: " f"{sorted(missing_columns)}")

    def retrieve_data(self):

        self.source_df = self.sales_client.get_sales_records()
        self.target_df = self.inventory_client.get_inventory_records()

        self._validate_columns(dataframe=self.source_df,
                               required_columns=self.SALES_REQUIRED_COLUMNS,
                               source_name="Sales Transaction Service")

        self._validate_columns(dataframe=self.target_df,
                               required_columns=self.INVENTORY_REQUIRED_COLUMNS,
                               source_name="Inventory Dispatch System")

        return self.source_df, self.target_df

    @staticmethod
    def normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe = dataframe.copy()

        return dataframe

    def normalize(self):

        self.source_df = self.normalize_dataframe(self.source_df)
        self.target_df = self.normalize_dataframe(self.target_df)

        return self.source_df, self.target_df

    def compare(self):

        self.comparison_results = compare_records(self.source_df, self.target_df)

        self.comparison_df = pd.DataFrame(self.comparison_results)

        return self.comparison_results

    def detect_mismatches(self):

        self.mismatches = detect_mismatches(self.source_df, self.target_df)

        return self.mismatches

    def generate_reports(self):

        self.report_generator.generate_reports(self.comparison_results)

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

        self.generate_reports()

        self.generate_analytics()

        self.generate_visualizations()

        return {"source_df": self.source_df,
                "target_df": self.target_df,
                "comparison_results": self.comparison_results,
                "comparison_df": self.comparison_df,
                "mismatches": self.mismatches,
                "summary_df": self.summary_df}