import pandas as pd

from app.clients.load_data import load_source_file
from app.clients.load_data import load_target_file

from app.services.compare_service import compare_records

from app.reporting.analytics import generate_summary
from app.reporting.analytics import save_summary
from app.reporting.analytics import generate_chart

from app.services.normalization_service import normalize_names
from app.services.normalization_service import normalize_dates
from app.services.normalization_service import normalize_amounts

source_df = load_source_file()
target_df = load_target_file()

source_df = normalize_names(source_df)
target_df = normalize_names(target_df)

source_df = normalize_dates(source_df)
target_df = normalize_dates(target_df)

source_df = normalize_amounts(source_df)
target_df = normalize_amounts(target_df)

comparison_results = compare_records(source_df, target_df)

comparison_df = pd.DataFrame(comparison_results)

print(comparison_df.head())

summary_df = generate_summary(comparison_df)

print(summary_df)

save_summary(summary_df)

generate_chart(summary_df)

print("Analytics Generated Successfully")