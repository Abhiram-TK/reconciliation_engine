from load_data import (load_source_file, load_target_file)

from normalize_data import (normalize_names, normalize_dates,normalize_amounts)

source_df = load_source_file()

source_df = normalize_names(source_df)
source_df = normalize_dates(source_df)
source_df = normalize_amounts(source_df)

print(source_df)