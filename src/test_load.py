from load_data import (load_source_file, load_target_file)

source_df = load_source_file()
target_df = load_target_file()

print(f"Rows Loaded: {len(source_df)}")
print(f"Rows Loaded: {len(target_df)}")