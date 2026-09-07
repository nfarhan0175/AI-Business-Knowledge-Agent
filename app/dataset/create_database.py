import pandas as pd
import sqlite3
from pathlib import Path


# Paths
PROCESSED_DIR = Path("data/processed")
DATABASE_DIR = Path("data/database")

DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATABASE_DIR / "olist.db"

# Connect to SQLite
connection = sqlite3.connect(DB_PATH)

# Load processed CSV files
customers = pd.read_csv(PROCESSED_DIR / "customers.csv")
order_items = pd.read_csv(PROCESSED_DIR / "order_items.csv")
payments = pd.read_csv(PROCESSED_DIR / "payments.csv")
orders = pd.read_csv(PROCESSED_DIR / "orders.csv")
products = pd.read_csv(PROCESSED_DIR / "products.csv")


# Convert date columns again
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"],errors="coerce")
orders["order_approved_at"] = pd.to_datetime(orders["order_approved_at"],errors="coerce")
orders["order_delivered_carrier_date"] = pd.to_datetime(orders["order_delivered_carrier_date"],errors="coerce")
orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"],errors="coerce")
orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"],errors="coerce")
order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"],errors="coerce")


# Write tables to SQLite
customers.to_sql("customers", connection, if_exists="replace", index=False)
orders.to_sql("orders", connection, if_exists="replace", index=False)
order_items.to_sql("order_items", connection, if_exists="replace", index=False)
payments.to_sql("payments", connection, if_exists="replace", index=False)
products.to_sql("products", connection, if_exists="replace", index=False)


# Close connection
connection.close()

print("SQLite database created successfully!")
print(f"Database location: {DB_PATH}")