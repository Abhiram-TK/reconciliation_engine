from app.clients.load_data import (load_source_file, load_target_file)

from app.services.normalization_service import (normalize_names, normalize_dates, normalize_amounts)

from app.services.compare_service import compare_records

source_df = load_source_file()
target_df = load_target_file()

source_df = normalize_names(source_df)
source_df = normalize_dates(source_df)
source_df = normalize_amounts(source_df)

target_df = normalize_names(target_df)
target_df = normalize_dates(target_df)
target_df = normalize_amounts(target_df)

results = compare_records(source_df, target_df)

for result in results:

    print(result)