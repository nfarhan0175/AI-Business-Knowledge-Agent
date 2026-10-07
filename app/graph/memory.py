from app.config import client, MODEL_NAME
from langchain_core.messages import HumanMessage, AIMessage

def build_contextual_question(state):
    messages = state.get("messages", [])
    current_question = state["question"]
    if not messages:
        return current_question
    conversation = []
    for message in messages:
        if isinstance(message, HumanMessage):
            conversation.append(f"User: {message.content}")
        elif isinstance(message, AIMessage):
            conversation.append(f"Assistant: {message.content}")
    conversation_text = "\n".join(conversation)
    return f"""
Previous conversation:
{conversation_text}
Current question:
{current_question}

Rewrite the current question as a standalone business question using
the necessary context from the previous conversation.
Examples:
Previous:
User: What are the top 5 product categories by revenue?
Assistant: ...
Current:
What about their percentages?
Rewritten:
What are the percentages of the top 5 product categories by revenue?
Previous:
User: What was the total revenue in 2018?
Assistant: ...
Current:
What about 2017?
Rewritten:
What was the total revenue in 2017?
If the current question is already standalone, return it unchanged.
Return ONLY the rewritten question.
"""

def rewrite_question_with_memory(state):
    original_question = state["question"]
    messages = state.get("messages", [])
    if not messages:
        return {
            "original_question": original_question,
            "question": original_question
        }
    prompt = build_contextual_question(state)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "temperature": 0
        }
    )
    rewritten_question = response.text.strip()
    print("\n--- Memory ---")
    print("Original Question:", original_question)
    print("Contextual Question:", rewritten_question)
    return {
        "original_question": original_question,
        "question": rewritten_question
    }
