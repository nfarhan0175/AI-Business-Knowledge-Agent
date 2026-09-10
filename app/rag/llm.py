import os
from dotenv import load_dotenv
from google import genai


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")
client = genai.Client(api_key=api_key)


def generate_answer(question, context):
    prompt = f"""
Your task is to answer the user's question using 
ONLY the information provided in the context. 
Important rules: 
1. Do not invent facts. 
2. Do not use outside knowledge. 
3. If the context does not contain enough information, 
say that the available product information is not sufficient. 
4. Keep the answer clear and concise. 
5. Mention relevant product IDs when appropriate. 
6. When useful, mention the product category. 
7. Do not claim that a product belongs to a category unless the context supports it.
Context:
{context}

User Question:
{question}
Now provide the best answer based only on the retrieved context.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text