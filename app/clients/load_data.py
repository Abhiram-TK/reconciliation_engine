import pandas as pd
from app.core.config import SOURCE_FILE, TARGET_FILE

def load_source_file():

    return pd.read_csv(SOURCE_FILE)

def load_target_file():

    return pd.read_csv(TARGET_FILE)