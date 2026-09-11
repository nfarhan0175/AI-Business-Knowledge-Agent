import chromadb
import time
from pathlib import Path
from app.rag.embedding import embed_text,embed_texts
from app.rag.documents import load_pdf_documents

CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "olist_business_knowledge"
BATCH_SIZE = 50

def get_chroma_client():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client

def get_collection():
    client = get_chroma_client()
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection

def add_documents(documents,embeddings):
    collection = get_collection()
    ids = [doc["id"] for doc in documents]
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    print(f"Added {len(documents)} documents to ChromaDB.")

def get_collection_count():
    collection = get_collection()
    return collection.count()
    
if __name__ == "__main__":
    collection = get_collection()

    print("Collection:", collection.name)
    print("Documents stored:", collection.count())