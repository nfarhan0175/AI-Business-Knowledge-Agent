import json
import time
from pathlib import Path
from app.rag.rag_pipeline import ask_question

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "rag_questions.json"
RESULTS_FILE = BASE_DIR / "results.json"

REQUEST_DELAY = 15 
MAX_RETRIES = 3

def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def evaluate_answer(answer, expected_keywords):
    answer_lower = answer.lower()
    matched_keywords = [
        keyword
        for keyword in expected_keywords
        if keyword.lower() in answer_lower
    ]
    score = len(matched_keywords) / len(expected_keywords)
    return {
        "matched_keywords": matched_keywords,
        "keyword_score": round(score, 2)
    }

def evaluate_retrieval(sources, expected_source):
    retrieved_sources = [
        source.get("source")
        for source in sources 
        if source.get("source")
    ]
    source_found = expected_source in retrieved_sources

    return {
        "expected_source": expected_source,
        "retrieved_sources": retrieved_sources,
        "source_found": source_found
    }

def ask_with_retry(question): 
    for attempt in range(MAX_RETRIES + 1): 
        try: 
            return ask_question(question, top_k=3) 
        except Exception as error: 
            error_message = str(error) 
            # Check whether this is a Gemini rate-limit error i
            if "429" not in error_message and "RESOURCE_EXHAUSTED" not in error_message: 
               raise 
            if attempt == MAX_RETRIES: 
               raise 
            wait_time = 60 
            print( f"Rate limit reached. " 
            f"Waiting {wait_time} seconds before retry " 
            f"({attempt + 1}/{MAX_RETRIES})..." ) 
            time.sleep(wait_time)
      
def run_evaluation():
    questions = load_questions()
    results = []
    print("\nStarting RAG evaluation...\n")

    for item in questions:
        question_id = item["id"]
        question = item["question"]

        print(f"Evaluating question {question_id}/{len(questions)}")
        print(f"Question: {question}")
        try:
            result = ask_with_retry(question)
            # result = ask_question(question, top_k=3)
            answer = result["answer"]
            sources = result["sources"]
            context = result.get("context", "")
            
            answer_evaluation = evaluate_answer(answer, item["expected_keywords"])
            retrieval_evaluation = evaluate_retrieval(sources, item["expected_source"])

            evaluation_result = {
                "id": question_id,
                "question": question,
                "answer": answer,
                "sources": sources,
                "context": context,
                "answer_evaluation": answer_evaluation,
                "retrieval_evaluation": retrieval_evaluation,
                "status": "success"
            }

            results.append(evaluation_result)
            print(f"Keyword score: {answer_evaluation['keyword_score']}")
            print(f"Source found: {retrieval_evaluation['source_found']}")
        except Exception as error:
            print(f"Evaluation failed: {error}") 
            evaluation_result = { 
                "id": question_id, 
                "question": question, 
                "answer": None, 
                "sources": [], 
                "answer_evaluation": None, 
                "retrieval_evaluation": None, 
                "status": "failed", 
                "error": str(error) } 
            results.append(evaluation_result)
        print("-" * 60)

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
    successful = sum( 
        1 for result in results 
        if result.get("status") == "success" ) 
    failed = len(results) - successful 
    print("\nEvaluation completed.") 
    print(f"Successful: {successful}") 
    print(f"Failed: {failed}") 
    print(f"Results saved to: {RESULTS_FILE}")

if __name__ == "__main__":
    run_evaluation()
