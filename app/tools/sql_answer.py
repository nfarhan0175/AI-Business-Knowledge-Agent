import os
from dotenv import load_dotenv
from google import genai


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-2.5-flash"


def generate_answer(question, sql, result):
    if not result["success"]:
        return f"Unable to answer the question because: {result['error']}"
    columns = result["columns"]
    rows = result["rows"]

    prompt = f"""
You are answering a user's business question using
the result of a SQL query.

User Question:
{question}

SQL Query:
{sql}

Database Result:
Columns: {columns}
Rows: {rows}

Instructions:
1. Answer the user's question directly.
2. Use only the information contained in the database result.
3. Do not invent or assume additional information.
4. Keep the answer concise and clear.
5. If the result contains a monetary value, format it to 2 decimal places.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text.strip()