import sqlite3 
from pathlib import Path
DB_PATH = Path("data/database/olist.db") 
connection = sqlite3.connect(DB_PATH) 
cursor = connection.cursor()

# Test 1: Number of orders
cursor.execute(""" 
    SELECT COUNT(*)     
    FROM orders; 
""")
print("\nTotal orders:", cursor.fetchone()[0])

# Test 2: Order status
cursor.execute("""
    SELECT order_status, COUNT(*)
    FROM orders
    GROUP BY order_status;
""")
print("\nOrders by status:")
for row in cursor.fetchall():
    print(row)

# Test 3: Total payment value
cursor.execute("""
    SELECT SUM(payment_value)
    FROM payments;
""")
print("\nTotal payment value:", cursor.fetchone()[0])

# Test 4: Average payment
cursor.execute("""
    SELECT AVG(payment_value)
    FROM payments;
""")
print("\nAverage payment:", cursor.fetchone()[0])

# Test 5: Customer → Orders relationship
cursor.execute("""
    SELECT c.customer_unique_id, COUNT(o.order_id) AS total_orders
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
    ORDER BY total_orders DESC
    LIMIT 5;
""")
print("\nTop customers by number of orders:")
for row in cursor.fetchall():
    print(row)

# Test 6: Orders → Products relationship
cursor.execute("""
    SELECT o.order_id, p.product_category_name, oi.price
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    LIMIT 5;
""")
print("\nOrders with product information:")
for row in cursor.fetchall():
    print(row)

# Test 7: Orders → Payments relationship
cursor.execute("""
    SELECT o.order_id, o.order_status, p.payment_type, p.payment_value
    FROM orders o
    JOIN payments p
        ON o.order_id = p.order_id
    LIMIT 5;
""")
print("\nOrders with payment information:")
for row in cursor.fetchall():
    print(row)

# Test 8: Revenue by product category
cursor.execute("""
    SELECT p.product_category_name, SUM(oi.price) AS total_revenue
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY p.product_category_name
    ORDER BY total_revenue DESC
    LIMIT 10;
""")
print("\nTop 10 product categories by revenue:")
for row in cursor.fetchall():
    print(row)    