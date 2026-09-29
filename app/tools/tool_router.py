import os
import json

from google import genai
from google.genai import types
from dotenv import load_dotenv

from app.tools.sql_pipeline import ask_database
from app.tools.analysis_tool import run_analysis
from app.rag.rag_pipeline import ask_question
from app.config import client, MODEL_NAME

# TOOL FUNCTIONS
def sql_tool(question: str) -> dict:
    return ask_database(question)


def analysis_tool(question: str) -> dict:
    return run_analysis(question)


def rag_tool(question: str) -> dict:
    return ask_question(question)


# GEMINI TOOL DECLARATIONS
tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="sql_tool",
                description=(
                    "Query the structured Olist business database. "
                    "Use this for factual database questions such as "
                    "totals, counts, filtering, joins, or retrieving "
                    "specific business records."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "question": types.Schema(
                            type="STRING",
                            description="The user's original business question."
                        )
                    },
                    required=["question"]
                )
            ),

            types.FunctionDeclaration(
                name="analysis_tool",
                description=(
                    "Perform data analysis using the business database. "
                    "Use this for growth, trends, percentages, comparisons, "
                    "distributions, rankings, and other calculations "
                    "that require analytical processing."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "question": types.Schema(
                            type="STRING",
                            description="The user's original analytical question."
                        )
                    },
                    required=["question"]
                )
            ),

            types.FunctionDeclaration(
                name="rag_tool",
                description=(
                    "Search the business knowledge documents using RAG. "
                    "Use this when the answer should come from the "
                    "business knowledge/document collection rather than "
                    "a direct database calculation."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "question": types.Schema(
                            type="STRING",
                            description="The user's original question."
                        )
                    },
                    required=["question"]
                )
            )
        ]
    )
]

# TOOL MAPPING
available_tools = {
    "sql_tool": sql_tool,
    "analysis_tool": analysis_tool,
    "rag_tool": rag_tool
}

# TOOL SELECTION
def select_tool(question):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=question,
        config=types.GenerateContentConfig(
            tools=tools,
            temperature=0
        )
    )
    # Check whether Gemini selected a tool
    if not response.function_calls: 
        return {
            "success": True,
            "tool": None,
            "answer": response.text
        }
    # Get selected function
    function_call = response.function_calls[0]
    tool_name = function_call.name
    tool_args = function_call.args
    print("\nSelected Tool:",tool_name)
    print("\nArguments:",tool_args)

    if tool_name not in available_tools:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
    # Execute selected tool
    tool_function = available_tools[tool_name]
    try:
        tool_result = tool_function(tool_args["question"])
    except Exception as error:
        return {
            "success": False,
            "tool": tool_name,
            "error": str(error)
        }
    print("\nTool Result:",tool_result)
    return {
        "success": True,
        "tool": tool_name,
        "question": question,
        "tool_result": tool_result
    }
    
# TEST
if __name__ == "__main__":
    test_questions = [
        # "hello",
        # "What is the total revenue?",
        # "What is the revenue growth by month?",
        "What is refund policy?",
        # "How many orders were placed in 2018?"
    ]
    for question in test_questions:
        print("\n" + "=" * 60)
        print("Question:",question)
        result = select_tool(question)
        print("\nFinal Result:")
        if result["success"]:
            print(result["tool_result"])
        else:
            print(result["error"])