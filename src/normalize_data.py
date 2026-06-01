import pandas as pd

def normalize_names(dataframe):

    dataframe["customer_name"] = (dataframe["customer_name"].str.lower().str.strip())

    return dataframe

def normalize_dates(dataframe):

    dataframe["invoice_date"] = pd.to_datetime(dataframe["invoice_date"], format="mixed")

    dataframe["invoice_date"] = (dataframe["invoice_date"].dt.strftime("%Y-%m-%d"))

    return dataframe

def normalize_amounts(dataframe):

    dataframe["amount"] = (dataframe["amount"].astype(float).round(2))

    return dataframe