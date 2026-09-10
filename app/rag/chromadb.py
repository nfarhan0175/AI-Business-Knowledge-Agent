import chromadb
import time
from app.rag.embedding import embed_text,embed_texts
from app.rag.documents import load_product_documents

# Create persistent Chroma client
chroma_client = chromadb.PersistentClient(path="data/chroma_db")
# Create or get collection
collection = chroma_client.get_or_create_collection(name="business_documents")
BATCH_SIZE = 50

def add_documents_to_chroma():
    documents = load_product_documents()
    total_documents = len(documents)
    print(f"\nTotal documents to process: {total_documents}")
    processed = 0

    for start in range(0,total_documents,BATCH_SIZE):
        end = min(start + BATCH_SIZE, total_documents)
        batch = documents[start:end]
        print(f"\nProcessing {start + 1} - {end} of {total_documents}")

        # Prepare batch
        ids = [document["id"] for document in batch]
        texts = [document["text"] for document in batch]
        metadatas = []
        for document in batch:
            metadata = document["metadata"].copy()
            metadata["chunk_index"] = 0
            metadatas.append(metadata)

        # Generate embeddings for entire batch
        embeddings = embed_texts(texts)
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        processed += len(batch)
        print(f"Saved: {processed}/{total_documents}")
        # Free tier rate limit protection
        if end < total_documents:
            print("Waiting 2 seconds before next batch...")
            time.sleep(2)

    print("Documents added to Chroma successfully!")
    print(f"Total processed: {processed}")
    print(f"Collection count: {collection.count()}")

if __name__ == "__main__":
    add_documents_to_chroma()