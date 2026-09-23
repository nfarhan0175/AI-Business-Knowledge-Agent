from app.tools.sql_pipeline import ask_database
from app.tools.analysis_tool import run_analysis
from app.rag.rag_pipeline import ask_question

def route_question(question):
    """
    Decide which tool should handle the question.
    """
    question_lower = question.lower()
    # Analysis-related questions
    analysis_keywords = [
        "growth", "trend", "percentage", "percent",
        "average", "highest growth", "lowest growth",
        "top", "bottom","compare", "comparison", "distribution"]
    for keyword in analysis_keywords:
        if keyword in question_lower:
            return "analysis"

    # RAG-related questions
    rag_keywords = [
        "explain", "describe", "definition",
        "policy", "information about", "tell me about"]
    
    for keyword in rag_keywords:
        if keyword in question_lower:
            return "rag"

    # Default
    return "sql"


def call_tool(question):
    tool_name = route_question(question)
    print("\nSelected Tool:")
    print(tool_name)

    try:
        if tool_name == "sql":
            result = ask_database(question)
        elif tool_name == "analysis":
            result = run_analysis(question)
        elif tool_name == "rag":
            result = ask_question(question)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
            
        return {
            "success": True,
            "tool": tool_name,
            "question": question,
            "result": result
        }
    except Exception as error:
        return {
            "success": False,
            "tool": tool_name,
            "question": question,
            "error": str(error)
        }
# Test
if __name__ == "__main__":
    test_questions = [
        "What is the total revenue?",
        "What is the revenue growth by month?",
        "What information is available about the business?"
    ]
    for question in test_questions:
        print("Question:")
        print(question)

        result = call_tool(question)
        print("\nResult:")
        print(result["result"])