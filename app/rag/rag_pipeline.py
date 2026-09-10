from app.rag.retriever import search_documents
from app.rag.llm import generate_answer

def build_context(documents, metadatas):
    context_parts = []
    for i, (document, metadata) in enumerate(zip(documents, metadatas),
    start=1):
        context = f"""
Document {i}
Product ID: {metadata.get("product_id")}
Category: {metadata.get("category")}
{document}
""".strip()
        context_parts.append(context)
    return "\n\n".join(context_parts)

def rag_answer(question, n_results=5,max_distance=0.80):
    # Step 1: Retrieve relevant documents
    documents, distances, metadatas = search_documents(
        question, n_results=n_results, max_distance=max_distance)
    if not documents: 
        return ( "I could not find sufficiently relevant " 
                "information in the product knowledge base.", 
                documents, distances, metadatas )    
    # Step 2: Build context
    context = build_context(documents,metadatas)
    # Step 3: Generate final answer
    answer = generate_answer(question,context)
    return answer, documents, distances, metadatas

if __name__ == "__main__":
    question = input("\nAsk your question: ")
    answer, documents, distances, metadatas = rag_answer(question,n_results=3,max_distance=0.80)
    print("FINAL ANSWER")
    print(answer)

    print("RETRIEVED DOCUMENTS")
    if not metadatas: 
        print("No sources found.") 
    else:
        for i, (distance, metadata) in enumerate(zip(distances, metadatas),start=1):
            print(
                f"\n{i}. "
                f"Category: {metadata.get('category')} | "
                f"Distance: {distance}"
            )