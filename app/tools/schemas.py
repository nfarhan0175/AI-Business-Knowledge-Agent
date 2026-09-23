import sqlite3
from pathlib import Path
from app.tools.sql_tool import DB_PATH

def get_database_schema():
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name;
        """)
        tables = cursor.fetchall()
        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            schema[table_name] = [
                {"name": column[1], "type": column[2]}
                for column in columns
            ]
        return schema
    finally:
        connection.close()

if __name__ == "__main__":
    schema = get_database_schema()
    print("\nDATABASE SCHEMA")
    for table_name, columns in schema.items():
        print(f"\nTable: {table_name}")
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")