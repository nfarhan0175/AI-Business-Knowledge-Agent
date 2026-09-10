import chromadb
from app.rag.embedding import embed_text

# Connect to existing Chroma database
chroma_client = chromadb.PersistentClient(path="data/chroma_db" )
collection = chroma_client.get_collection(name="business_documents")

def search_documents(query, n_results=5, max_distance=0.80):
    query_embedding = embed_text(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    filtered_documents = [] 
    filtered_distances = [] 
    filtered_metadatas = [] 
    for document, distance, metadata in zip( documents, distances, metadatas ): 
        if distance <= max_distance: 
            filtered_documents.append(document) 
            filtered_distances.append(distance) 
            filtered_metadatas.append(metadata)

    return filtered_documents, filtered_distances, filtered_metadatas

if __name__ == "__main__":
    query = "Which products belong to the furniture category?"
    documents, distances, metadatas = search_documents(query,n_results=3,max_distance=0.80)

    print("\nQuery:")
    print(query)

    print("\nRetrieved Documents:")
    if not documents: 
        print( "No sufficiently relevant documents found." ) 
    else:
        for i, (document, distance, metadata) in enumerate(
            zip(documents, distances, metadatas),
            start=1):

            print(f"Result {i}")
            print("Distance:", distance)
            print("Metadata:", metadata)

            print("\nDocument:")
            print(document)