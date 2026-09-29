from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from app.tools.tool_router import select_tool
from app.tools.sql_pipeline import ask_database
from app.tools.analysis_tool import run_analysis
from app.rag.rag_pipeline import ask_question

class AgentState(TypedDict):
    question: str
    selected_tool: str
    tool_result: dict
    final_answer: str

# Router Node
def router_node(state: AgentState):
    question = state["question"]
    print("\n--- Router Node ---")
    print("Question:", question)
    result = select_tool(question)
    return {
        "selected_tool": result.get("tool", ""),
        "tool_result": result
    }

# SQL Node
def sql_node(state: AgentState):
    question = state["question"]
    print("\n--- SQL Node ---")
    result = ask_database(question)
    return {"tool_result": result}

# Analysis Node
def analysis_node(state: AgentState):
    question = state["question"]
    print("\n--- Analysis Node ---")
    result = run_analysis(question)
    return {"tool_result": result}

# RAG Node
def rag_node(state: AgentState):
    question = state["question"]
    print("\n--- RAG Node ---")
    result = ask_question(question)
    return {"tool_result": result}

# Conditional Router
def route_after_router(state: AgentState):
    selected_tool = state["selected_tool"]
    if selected_tool == "sql_tool":
        return "sql"
    elif selected_tool == "analysis_tool":
        return "analysis"
    elif selected_tool == "rag_tool":
       return "rag"
    else:
        raise ValueError(f"Unknown tool selected: {selected_tool}")

# Formatter Node
def formatter_node(state: AgentState):
    print("\n--- Formatter Node ---")
    tool = state["selected_tool"]
    result = state["tool_result"]

    # SQL
    if tool == "sql_tool":
        sql_result = result.get("result", {})
        if not sql_result.get("success"):
            final_answer = (
                f"SQL query failed: "
                f"{sql_result.get('error', 'Unknown error')}"
            )
        else:
            columns = sql_result.get("columns", [])
            rows = sql_result.get("rows", [])
            if not rows:
                final_answer = "No matching records were found."
            elif len(rows) == 1 and len(rows[0]) == 1:
                value = rows[0][0]
                # Format numeric values
                if isinstance(value, float):
                    value = round(value, 2)
                final_answer = f"{columns[0]}: {value}"
            else:
                final_answer = str({
                    "columns": columns,
                    "rows": rows
                })
    # Analysis
    elif tool == "analysis_tool":
        if not result.get("success"):
            final_answer = (
                f"Analysis failed: "
                f"{result.get('error', 'Unknown error')}"
            )
        else:
            data = result.get("data")
            if data is None:
                final_answer = (
                    "Analysis completed, "
                    "but no data was returned."
                )
            else:
                final_answer = data.to_string(index=False)
    # RAG
    elif tool == "rag_tool":
        if not result.get("answer"):
            final_answer = (
                "I could not generate an answer from "
                "the available documents."
            )
        else:
            final_answer = result["answer"]
    # Unknown tool
    else:
        final_answer = ("I could not determine how to answer the question.")
    return {"final_answer": final_answer}
# Build Graph
graph_builder = StateGraph(AgentState)

graph_builder.add_node("router", router_node)
graph_builder.add_node("sql", sql_node)
graph_builder.add_node("analysis", analysis_node)
graph_builder.add_node("rag", rag_node)
graph_builder.add_node("formatter", formatter_node)


graph_builder.add_edge(START, "router")
graph_builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "sql": "sql",
        "analysis": "analysis",
        "rag": "rag",
    }
)

graph_builder.add_edge("sql", "formatter")
graph_builder.add_edge("analysis", "formatter")
graph_builder.add_edge("rag", "formatter")
graph_builder.add_edge("formatter", END)

graph = graph_builder.compile()

# Test
if __name__ == "__main__":
    initial_state = {
        "question": "What is the revenue growth by month?",
        "selected_tool": "",
        "tool_result": {},
        "final_answer": ""
    }
    result = graph.invoke(initial_state)
    print("FINAL ANSWER")
    print(result["final_answer"])