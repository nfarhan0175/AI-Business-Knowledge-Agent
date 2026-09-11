import os
from dotenv import load_dotenv
from google import genai


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.6-flash"

def generate_answer(question, context):
    """
    Generate an answer using the user's question
    and retrieved context.
    """

    prompt = f"""
You are an AI business knowledge assistant for Olist.
Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context,
say that you could not find the information
in the available documents.

Do not make up information.

Context:
{context}

User Question:
{question}

Answer:
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text
