import pandas as pd
from pathlib import Path


DATA_DIR = Path("data/raw")
# DATA_DIR = Path("/content")


files = [
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
]


for file in files:
    path = DATA_DIR / file
    df = pd.read_csv(path)

    print("\n" + "=" * 70)
    print(f"FILE: {file}")
    print("=" * 70)

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:")
    print(df.duplicated().sum())

    print("\nFirst 5 Rows:")
    print(df.head())