from google.genai import types
from app.config import MODEL_NAME, client

# TOOL DECLARATIONS
tools = [
    types.Tool(
        function_declarations=[
            # SQL TOOL
            types.FunctionDeclaration(
                name="sql_tool",
                description=(
                    "Query the structured Olist business database. "
                    "Use this for direct database questions such as "
                    "totals, counts, sums, averages, filtering, sorting, "
                    "top-N results, rankings, GROUP BY queries, JOINs, "
                    "and retrieving specific business records."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "question": types.Schema(
                            type="STRING",
                            description=(
                                "The user's original business question."
                            )
                        )
                    },
                    required=["question"]
                )
            ),

            # ANALYSIS TOOL
            types.FunctionDeclaration(
                name="analysis_tool",
                description=(
                    "Perform data analysis using the business database. "
                    "Use this for growth rates, percentage changes, "
                    "trends over time, distributions, statistical summaries, "
                    "and other calculations that require analytical processing."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "question": types.Schema(
                            type="STRING",
                            description=(
                                "The user's original analytical question."
                            )
                        )
                    },
                    required=["question"]
                )
            ),

            # RAG TOOL
            types.FunctionDeclaration(
                name="rag_tool",
                description=(
                    "Search the business knowledge documents using RAG. "
                    "Use this when the answer should come from business "
                    "knowledge documents rather than a direct database "
                    "calculation."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "question": types.Schema(
                            type="STRING",
                            description=(
                                "The user's original question."
                            )
                        )
                    },
                    required=["question"]
                )
            )
        ]
    )
]


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
    # No function call
    if not response.function_calls:
        return {
            "success": True,
            "tool": None,
            "question": question,
            "answer": response.text
        }
    # Get selected function
    function_call = response.function_calls[0]
    tool_name = function_call.name
    tool_args = function_call.args

    print("\nSelected Tool:", tool_name)
    print("\nArguments:", tool_args)
    # Validate tool name
    valid_tools = ["sql_tool", "analysis_tool", "rag_tool"]
    if tool_name not in valid_tools:
        return {
            "success": False,
            "tool": None,
            "question": question,
            "error": f"Unknown tool: {tool_name}"
        }
    return {
        "success": True,
        "tool": tool_name,
        "question": question,
        "arguments": tool_args
    }