import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "results.json"
SUMMARY_FILE = BASE_DIR / "evaluation_summary.json"


def load_results():
    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_summary(results):
    total_questions = len(results)

    successful_results = [
        result
        for result in results
        if result.get("status") == "success"
    ]

    failed_results = [
        result
        for result in results
        if result.get("status") == "failed"
    ]

    keyword_scores = [
        result["answer_evaluation"]["keyword_score"]
        for result in successful_results
        if result.get("answer_evaluation")
    ]

    average_keyword_score = (
        sum(keyword_scores) / len(keyword_scores)
        if keyword_scores
        else 0
    )

    retrieval_results = [
        result["retrieval_evaluation"]
        for result in successful_results
        if result.get("retrieval_evaluation")
    ]

    retrieval_successes = sum(
        1
        for result in retrieval_results
        if result.get("source_found") is True
    )

    retrieval_success_rate = (
        retrieval_successes / len(retrieval_results)
        if retrieval_results
        else 0
    )

    summary = {
        "total_questions": total_questions,
        "successful_questions": len(successful_results),
        "failed_questions": len(failed_results),

        "answer_evaluation": {
            "evaluated_questions": len(keyword_scores),
            "average_keyword_score": round(
                average_keyword_score,
                2
            )
        },

        "retrieval_evaluation": {
            "evaluated_questions": len(retrieval_results),
            "successful_retrievals": retrieval_successes,
            "retrieval_success_rate": round(
                retrieval_success_rate,
                2
            )
        },

        "failed_question_ids": [result["id"] for result in failed_results]
    }
    return summary


def main():
    results = load_results()
    summary = calculate_summary(results)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

    print("\n===== RAG EVALUATION SUMMARY =====")
    print(f"Total questions: {summary['total_questions']}")
    print(f"Successful: {summary['successful_questions']}")
    print(f"Failed: {summary['failed_questions']}")

    print(
        "Average keyword score:",
        summary["answer_evaluation"]["average_keyword_score"]
    )
    print(
        "Retrieval success rate:",
        summary["retrieval_evaluation"]["retrieval_success_rate"]
    )
    print("Failed question IDs:",summary["failed_question_ids"])
    print(f"\nSummary saved to: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()