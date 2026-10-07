from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage#, HumanMessage, AIMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    question: str
    original_question: str
    messages: Annotated[list[BaseMessage], add_messages]
    selected_tool: str
    tool_result: dict
    final_answer: str
    error: str
    retry_count: int