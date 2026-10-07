from app.graph.state import AgentState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.graph.memory import rewrite_question_with_memory
from langchain_core.messages import HumanMessage, AIMessage
from app.graph.nodes import (router_node, sql_node, analysis_node, 
    rag_node, retry_node, error_node)


def route_after_router(state: AgentState):
    selected_tool = state["selected_tool"]
    if selected_tool == "sql_tool":
        return "sql"
    elif selected_tool == "analysis_tool":
        return "analysis"
    elif selected_tool == "rag_tool":
        return "rag"
    else:
        return "error"

def route_after_tool(state: AgentState):
    if not state["error"]:
        return "formatter"
    if state["retry_count"] < 2:
        return "retry"
    return "error"

def route_after_retry(state: AgentState):
    selected_tool = state["selected_tool"]
    if selected_tool == "sql_tool":
        return "sql"
    elif selected_tool == "analysis_tool":
        return "analysis"
    elif selected_tool == "rag_tool":
        return "rag"
    else:
        return "error"

# FORMATTER NODE
def formatter_node(state):
    tool = state.get("selected_tool")
    result = state.get("tool_result", {})
    # SQL TOOL
    if tool == "sql_tool":
        sql_result = result.get("result", {})
        if not sql_result.get("success"):
            error_message = sql_result.get("error", "Unknown SQL error")
            final_answer = (f"SQL query failed: {error_message}")
        else:
            columns = sql_result.get("columns", [])
            rows = sql_result.get("rows", [])
            if not rows:
                final_answer = "No matching records were found."
            elif len(rows) == 1 and len(rows[0]) == 1:
                value = rows[0][0]
                if isinstance(value, float):
                    value = round(value, 2)
                final_answer = (f"{columns[0]}: {value}")
            else:
                final_answer = str({
                    "columns": columns,
                    "rows": rows
                })
    # ANALYSIS TOOL
    elif tool == "analysis_tool":
        if not result.get("success"):
            error_message = result.get("error", "Unknown analysis error")
            final_answer = (f"Analysis failed: {error_message}")
        else:
            data = result.get("data")
            if data is None:
                final_answer = "Analysis completed, but no data was returned."
            else:
                final_answer = str(data)
    # RAG TOOL
    elif tool == "rag_tool":
        final_answer = result.get("answer", "No answer was generated.")
    # UNKNOWN TOOL
    else:
        final_answer = ("I could not determine which tool should answer this question.")
    return {
        "final_answer": final_answer,
        "messages": [
            HumanMessage(content=state["original_question"]),
            AIMessage(content=final_answer)
        ]
    }

graph_builder = StateGraph(AgentState)

graph_builder.add_node("memory", rewrite_question_with_memory)
graph_builder.add_node("router", router_node)
graph_builder.add_node("sql", sql_node)
graph_builder.add_node("analysis", analysis_node)
graph_builder.add_node("rag", rag_node)
graph_builder.add_node("retry", retry_node)
graph_builder.add_node("formatter", formatter_node)
graph_builder.add_node("error", error_node)

graph_builder.add_edge(START, "memory")
graph_builder.add_edge("memory", "router")
graph_builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "sql": "sql",
        "analysis": "analysis",
        "rag": "rag",
        "error": "error"
    }
)

def add_tool(node_name):
    graph_builder.add_conditional_edges(
        node_name,
        route_after_tool,
        {
            "formatter": "formatter",
            "retry": "retry",
            "error": "error"
        }
    )

graph_builder.add_conditional_edges(
    "retry",
    route_after_retry,
    {
        "sql": "sql",
        "analysis": "analysis",
        "rag": "rag",
        "error": "error"
    }
)
add_tool("sql")
add_tool("analysis")
add_tool("rag")
graph_builder.add_edge("formatter",END)
graph_builder.add_edge("error", END)
# graph = graph_builder.compile()
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# TEST
if __name__ == "__main__":
  for _ in range(3):  
    initial_state = {
        # "question":
        #     "How can i get refund?",
        #     "What is the revenue growth over the month?",
        #     "What are the top 5 product categories by revenue?",
        #     "What about their percentages?",
        "question": input("Enter your question: "),
        "original_question": "",
        "messages": [],
        "selected_tool": "",
        "tool_result": {},
        "final_answer": "",
        "error": "",
        "retry_count": 0
    }
    config = {"configurable": {"thread_id": "user_1"}}
    result = graph.invoke(initial_state, config=config)
    print("FINAL ANSWER")
    print(result["final_answer"])
    print("RETRY COUNT")
    print(result["retry_count"])
    # print("GRAPH")
    # print(graph.get_graph().draw_mermaid())