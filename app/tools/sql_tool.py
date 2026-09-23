import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "database" / "olist.db"

def validate_query(query):
    query = query.strip().lower()
    if not query.startswith("select"):
        return {
            "valid": False,
            "error": "Only SELECT queries are allowed."
        }
    forbidden_keywords = [
        "insert", "update", "delete", "drop",
        "alter", "create", "replace", "truncate"]
    for keyword in forbidden_keywords:
        if keyword in query:
            return {
                "valid": False,
                "error": f"Forbidden SQL operation: {keyword}"
            }
    return {"valid": True}

def execute_query(query):
    validation = validate_query(query)
    if not validation["valid"]:
        return {"success": False, "error": validation["error"]}
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [
            description[0]
            for description in cursor.description
        ]
        return {
            "success": True,
            "columns": columns,
            "rows": rows
        }
    except sqlite3.Error as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        connection.close()


if __name__ == "__main__":
    query = "SELECT abc FROM orders;"
#     query = """
# SELECT 
#     p.product_category_name,
#     SUM(oi.price) AS total_revenue
# FROM order_items oi
# JOIN products p
#     ON oi.product_id = p.product_id
# GROUP BY p.product_category_name
# ORDER BY total_revenue DESC
# LIMIT 5;
# """
    result = execute_query(query)
    print("Query result:")
    print(result)

