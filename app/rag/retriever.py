from app.rag.chromadb import get_collection
from app.rag.embedding import embed_text

def retrieve_documents(query,top_k=3,max_similarity=0.7):
    collection = get_collection()
    # Convert user query into embedding
    query_embedding = embed_text(query)
    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved_documents = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    ids = results.get("ids", [[]])[0]
    for doc_id, document, metadata, distance in zip(ids,documents,metadatas,distances):
        if distance <= max_similarity:
            retrieved_documents.append({
                "id": doc_id,
                "text": document,
                "metadata": metadata,
                "distance": distance
            })
    return retrieved_documents

if __name__ == "__main__":
    query = "What is olist?"
    results = retrieve_documents(query, top_k=3, max_similarity=0.8)

    print(f"\nQuery: {query}")
    print(f"Retrieved documents: {len(results)}")

    for i, result in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print("ID:", result["id"])
        print("Distance:", result["distance"])
        print("Metadata:", result["metadata"])

        # print("Text:")
        # print(result["text"])
