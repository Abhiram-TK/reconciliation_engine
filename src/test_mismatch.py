from load_data import (load_source_file, load_target_file)

from normalize_data import (normalize_names, normalize_dates, normalize_amounts)

from mismatch_detector import (detect_mismatches)

source_df = load_source_file()
target_df = load_target_file()

source_df = normalize_names(source_df)
source_df = normalize_dates(source_df)
source_df = normalize_amounts(source_df)

target_df = normalize_names(target_df)
target_df = normalize_dates(target_df)
target_df = normalize_amounts(target_df)

results = detect_mismatches(source_df, target_df)

for result in results:

    print()

    for key, value in result.items():

        print(f"{key}: {value}")