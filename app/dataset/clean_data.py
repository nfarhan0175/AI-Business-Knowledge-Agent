import pandas as pd
from pathlib import Path

# Paths
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
# RAW_DIR = Path("/content")
# PROCESSED_DIR = Path("processed")

# Create processed directory if it doesn't exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load datasets
customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
order_items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv")
orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
products = pd.read_csv(RAW_DIR / "olist_products_dataset.csv")

# 2. Convert date columns
order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"],  errors="coerce")
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

# 3. Handle missing product category
products["product_category_name"] = (products["product_category_name"].fillna("unknown"))

# 4. Verify cleaning

print("\n" + "=" * 70)
print("DATE COLUMN TYPES")
print("=" * 70)

print("\nOrders:")
print(orders[date_columns].dtypes)

print("\nOrder Items:")
print(order_items["shipping_limit_date"].dtype)


print("\n" + "=" * 70)
print("PRODUCT CATEGORY")
print("=" * 70)

print("Missing product categories:", products["product_category_name"].isna().sum())
print("'unknown' categories:", (products["product_category_name"] == "unknown").sum())

# 5. Save processed datasets
customers.to_csv(PROCESSED_DIR / "customers.csv", index=False)
order_items.to_csv(PROCESSED_DIR / "order_items.csv", index=False)
payments.to_csv(PROCESSED_DIR / "payments.csv", index=False)
orders.to_csv(PROCESSED_DIR / "orders.csv", index=False)
products.to_csv(PROCESSED_DIR / "products.csv", index=False)


print("Data cleaning completed successfully!")
print(f"Processed files saved to: {PROCESSED_DIR}")