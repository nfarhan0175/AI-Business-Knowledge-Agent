import json
import time
import os
from dotenv import load_dotenv
from pathlib import Path
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "results.json"
FAITHFULNESS_FILE = BASE_DIR / "faithfulness_results.json"

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.6-flash"
REQUEST_DELAY = 15


def load_results():
    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_faithfulness(client, question, answer, context):
    prompt = f"""
You are evaluating a RAG system.
Determine whether the answer is fully supported by the retrieved context.

Question:
{question}

Retrieved Context:
{context}

Generated Answer:
{answer}

Evaluate the answer using these criteria:
1. grounded:
   - true if the answer is supported by the retrieved context
   - false if the answer contains unsupported claims
2. score:
   - 1.0 = fully supported
   - 0.5 = partially supported
   - 0.0 = unsupported
3. explanation:
   - briefly explain your decision
Return ONLY valid JSON in this format:

{{    "grounded": true,
    "score": 1.0,
    "explanation": "The answer is fully supported by the retrieved context."
}}
"""

    response = client.models.generate_content( 
        model=MODEL_NAME, contents=prompt ) 
    text = response.text.strip()

    # Remove markdown code fences if Gemini adds them
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()
    return json.loads(text)


def main():
    results = load_results()

    faithfulness_results = []
    successful_results = [
        result
        for result in results
        if result.get("status") == "success"
        and result.get("context")
    ]

    print("\nStarting faithfulness evaluation...\n")

    for index, result in enumerate(successful_results):
        question_id = result["id"]
        question = result["question"]
        answer = result["answer"]
        context = result["context"]

        print(
            f"Evaluating faithfulness "
            f"{index + 1}/{len(successful_results)}"
        )
        print(f"Question: {question}")

        try:
            evaluation = evaluate_faithfulness(
                client,question,answer,context)

            faithfulness_result = {
                "id": question_id,
                "question": question,
                "grounded": evaluation["grounded"],
                "score": evaluation["score"],
                "explanation": evaluation["explanation"],
                "status": "success"
            }

            faithfulness_results.append(faithfulness_result)

            print(f"Grounded: {evaluation['grounded']}")
            print(f"Score: {evaluation['score']}")

        except Exception as error:
            print(f"Evaluation failed: {error}")

            faithfulness_results.append({
                "id": question_id,
                "question": question,
                "grounded": None,
                "score": None,
                "explanation": None,
                "status": "failed",
                "error": str(error)
            })

        print("-" * 60)

        if index < len(successful_results) - 1:
            print(
                f"Waiting {REQUEST_DELAY} seconds..."
            )
            time.sleep(REQUEST_DELAY)

    with open(FAITHFULNESS_FILE, "w",  encoding="utf-8") as file:
        json.dump( faithfulness_results,  file, indent=4, ensure_ascii=False)

    successful = sum(
        1
        for result in faithfulness_results
        if result["status"] == "success"
    )

    failed = len(faithfulness_results) - successful

    print("\nFaithfulness evaluation completed.")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(
        f"Results saved to: {FAITHFULNESS_FILE}"
    )

if __name__ == "__main__":
    main()

