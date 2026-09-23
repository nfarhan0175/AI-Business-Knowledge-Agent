from app.tools.sql_generator import generate_sql
from app.tools.sql_tool import execute_query
from app.tools.sql_answer import generate_answer

def ask_database(question):
    sql = generate_sql(question)
    print("\nGenerated SQL:")
    print(sql)
    result = execute_query(sql)
    answer = generate_answer(question, sql, result)
    return {
        "question": question,
        "sql": sql,
        "result": result,
        "answer": answer
    }


if __name__ == "__main__":
    question = "What is the total revenue?"
    response = ask_database(question)

    print("\nFinal Result:")
    print(f"question: '{response['question']}',")
    print(f"sql: '{response['sql']}',")
    print(f"result: {response['result']},")
    print(f"answer: {response['answer']}")