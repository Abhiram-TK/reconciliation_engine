import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_source_file():

    source_df = pd.read_csv(BASE_DIR / "data" / "source.csv")

    return source_df

def load_target_file():

    target_df = pd.read_csv(BASE_DIR / "data" / "target.csv")

    return target_df