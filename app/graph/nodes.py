from app.graph.state import AgentState

from app.tools.tool_router import select_tool
from app.tools.sql_pipeline import ask_database
from app.tools.analysis_tool import run_analysis
from app.rag.rag_pipeline import ask_question

def router_node(state: AgentState):   
    print("\n--- Router Node ---")
    question = state["question"]
    print("Question:", question)
    result = select_tool(question)
    if not result["success"]:
        return {
            "selected_tool": "",
            "tool_result": {},
            "error": result["error"]
        }
    selected_tool = result.get("tool")
    print("Selected Tool:", selected_tool)
    return {
        "selected_tool": selected_tool,
        "tool_result": {},
        "error": ""
    }

def sql_node(state: AgentState):
    print("\n--- SQL Node ---")
    question = state["question"]
    try:
        if state["retry_count"] == 0:
            result = ask_database(question)
        else:
            previous_result = state["tool_result"]
            failed_sql = previous_result.get("sql","")
            sql_result = previous_result.get("result",{})
            sql_error = sql_result.get("error",state["error"])
            result = ask_database(
                question=question,
                failed_sql=failed_sql,
                sql_error=sql_error
            )
        if not result["result"]["success"]:
            return {
                "tool_result": result,
                "error": result["result"].get(
                    "error",
                    "Unknown SQL error"
                )
            }
        return {"tool_result": result,"error": ""}
    except Exception as error:
        return {"tool_result": state.get("tool_result",{}),"error": str(error)}

def analysis_node(state: AgentState):
    print("\n--- Analysis Node ---")
    question = state["question"]
    try:
        result = run_analysis(question)
        return {
            "tool_result": result,
            "error": ""
        }
    except Exception as error:
        return {
            "tool_result": {},
            "error": str(error)
        }

def rag_node(state: AgentState):
    print("\n--- RAG Node ---")
    question = state["question"]
    try:
        result = ask_question(question)
        return {"tool_result": result,"error": ""}
    except Exception as error:
        return {"tool_result": {}, "error": str(error)}

def retry_node(state: AgentState):
    print("\n--- Retry Node ---")
    new_retry_count = (state["retry_count"] + 1)
    print("Retry attempt:",new_retry_count)
    return {"retry_count": new_retry_count,"error": ""}

def error_node(state: AgentState):
    print("\n--- Error Node ---")
    error = state["error"]
    return {
        "final_answer": (
            "I could not complete the request.\n"
            f"Error: {error}"
        )
    }
