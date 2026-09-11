from app.rag.retriever import retrieve_documents
from app.rag.llm import generate_answer


def ask_question(question, top_k=3):
    print("\nSearching relevant information...")
    results = retrieve_documents(question,top_k=top_k)

    if not results:
        return {
            "answer": "I could not find relevant information in the available documents.",
            "sources": []
        }
    context_parts = []
    sources = []
    for result in results:
        context_parts.append(result["text"])
        sources.append({
            "source": result["metadata"].get("source"),
            "page": result["metadata"].get("page"),
            "chunk": result["metadata"].get("chunk")
        })

    context = "\n\n".join(context_parts)

    print("Generating answer...")
    answer = generate_answer(question=question, context=context)
    return {"answer": answer,"sources": sources}


if __name__ == "__main__":
    # Ask a question
    question = input("\nAsk a question about Olist: ")
    result = ask_question(question)

    print("ANSWER")
    print(result["answer"])

    print("SOURCES")
    for source in result["sources"]:
        print(
            f"- {source['source']} "
            f"(Page {source['page']}, "
            f"Chunk {source['chunk']})"
        )
