import os
import json
from dotenv import load_dotenv
from google import genai
from app.tools.schemas import get_database_schema

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-flash"

def clean_sql(text):
    text = text.strip()
    # Remove markdown code fences
    text = text.replace("```sql", "")
    text = text.replace("```", "")
    text = text.strip()
    # Find the beginning of the SQL query
    select_position = text.lower().find("select")
    if select_position == -1:
        raise ValueError("No SELECT query found in LLM response.")
    # Remove anything before SELECT
    text = text[select_position:]
    return text.strip()

def format_schema(schema):
    formatted_schema = ""
    for table_name, columns in schema.items():
        formatted_schema += f"Table: {table_name}\n"
        for column in columns:
            formatted_schema += (
                f"  - {column['name']} "
                f"({column['type']})\n"
            )
        formatted_schema += "\n"
    return formatted_schema


def generate_sql(question):
    schema = get_database_schema()
    schema_text = format_schema(schema)

    prompt = f"""
You are a SQL query generator for an e-commerce business database.
Your task is to convert the user's natural language question
into a valid SQLite SQL query.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

Rules:
1. Generate only a valid SQLite SQL query.
2. Do not explain the query.
3. Use only tables and columns that exist in the schema.
4. Use appropriate JOINs when information is distributed across tables.
5. Do not modify the database.
6. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE.
7. Only generate SELECT queries.
8. Give meaningful aliases when appropriate.

Return ONLY the SQL query.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    sql = response.text.strip()
    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")
        sql = sql.strip()
    sql = clean_sql(response.text)
    return sql


if __name__ == "__main__":
    question = "What are the top 5 product categories by revenue?"
    sql = generate_sql(question)
    print("\nUSER QUESTION:")
    print(question)
    print("\nGENERATED SQL:")
    print(sql)