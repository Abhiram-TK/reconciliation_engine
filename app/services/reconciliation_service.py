import pandas as pd

from app.clients.load_data import (load_source_file, load_target_file)

from app.services.normalization_service import (normalize_names, normalize_dates, normalize_amounts)
from app.services.compare_service import compare_records
from app.services.mismatch_service import detect_mismatches

from app.reporting.report_generator import generate_reports
from app.reporting.analytics import (generate_summary, save_summary, generate_chart)


class ReconciliationService:
 
    def __init__(self):

        self.source_df = None
        self.target_df = None

        self.comparison_results = None
        self.comparison_df = None
        self.mismatches = None
        self.summary_df = None

    def retrieve_data(self):

        self.source_df = load_source_file()
        self.target_df = load_target_file()

        return self.source_df, self.target_df

    @staticmethod
    def normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        
        dataframe = normalize_names(dataframe)
        dataframe = normalize_dates(dataframe)
        dataframe = normalize_amounts(dataframe)

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

        generate_reports(self.comparison_results)

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

        return {"source_df": self.source_df, "target_df": self.target_df,
                "comparison_results": self.comparison_results, "comparison_df": self.comparison_df,
                "mismatches": self.mismatches, "summary_df": self.summary_df}