import os
from dotenv import load_dotenv
from google import genai
from app.config import client

def embed_text(text):
    """ Generate embedding for a single text. """
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return response.embeddings[0].values

# Batch Text Embedding
def embed_texts(texts):
    """
    Generate embeddings for multiple texts in one API request.
    Parameters
    ----------
    texts : list[str]
        List of texts to embed.
    Returns
    -------
    list[list[float]]
        List of embedding vectors.
    """

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]