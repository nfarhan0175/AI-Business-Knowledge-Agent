from app.rag.documents import load_pdf_documents
from app.rag.chunker import sentence_chunker
from app.rag.embedding import embed_texts
from app.rag.chromadb import add_documents, get_collection_count

def prepare_chunks(documents):
    """
    Convert PDF pages into smaller chunks.
    """
    chunks = []
    for document in documents:
        page_id = document["id"]
        text = document["text"]
        metadata = document["metadata"]

        page_chunks = sentence_chunker(text, chunk_size=100, overlap=1)
        for chunk_number, chunk_text in enumerate(page_chunks,start=1):
            chunks.append({
                "id": f"{page_id}_chunk_{chunk_number}",
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk": chunk_number
                }
            })
    return chunks

def ingest_documents():
    print("Loading PDF...")
    documents = load_pdf_documents()

    print(f"Loaded {len(documents)} PDF pages.")

    print("\nCreating chunks...")
    chunks = prepare_chunks(documents)
    print(f"Created {len(chunks)} chunks.")

    print("\nCreating embeddings...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(texts)
    print(f"Created {len(embeddings)} embeddings.")

    print("\nStoring data in ChromaDB...")
    add_documents(documents=chunks, embeddings=embeddings)
    print(f"\nTotal documents in ChromaDB: {get_collection_count()}")

if __name__ == "__main__":
    ingest_documents()