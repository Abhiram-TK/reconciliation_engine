import pandas as pd

def load_source_file():

    source_df = pd.read_csv("data/source.csv")

    return source_df

def load_target_file():

    target_df = pd.read_csv("data/target.csv")

    return target_df