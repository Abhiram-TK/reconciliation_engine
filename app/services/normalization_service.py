import pandas as pd

def normalize_transaction_ids(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    if "transaction_id" in df.columns:

        df["transaction_id"] = pd.to_numeric(df["transaction_id"], errors="raise").astype("int64")

    return df

def normalize_invoice_numbers(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    if "invoice_number" in df.columns:

        df["invoice_number"] = (df["invoice_number"].astype("string").str.strip())

    return df

def normalize_product_ids(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    if "product_id" in df.columns:

        df["product_id"] = pd.to_numeric(df["product_id"], errors="raise").astype("int64")

    return df

def normalize_quantities(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    if "quantity" in df.columns:

        df["quantity"] = pd.to_numeric(df["quantity"], errors="raise")

    if "reserved_quantity" in df.columns:

        df["reserved_quantity"] = pd.to_numeric(df["reserved_quantity"], errors="raise")

    return df

def normalize_statuses(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    if "status" in df.columns:

        df["status"] = (df["status"].astype("string").str.strip().str.upper())

    return df

def normalize_timestamps(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    if "created_at" in df.columns:

        df["created_at"] = pd.to_datetime(df["created_at"], errors="raise", utc=True)

    if "reserved_at" in df.columns:

        df["reserved_at"] = pd.to_datetime(df["reserved_at"], errors="raise", utc=True)

    return df

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df = normalize_transaction_ids(df)
    df = normalize_invoice_numbers(df)
    df = normalize_product_ids(df)
    df = normalize_quantities(df)
    df = normalize_statuses(df)
    df = normalize_timestamps(df)

    return df