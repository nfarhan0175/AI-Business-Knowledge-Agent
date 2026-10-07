from app.tools.sql_generator import generate_sql, correct_sql
from app.tools.sql_tool import execute_query
from app.tools.sql_answer import generate_answer

def ask_database(question, failed_sql=None, sql_error=None):
    if failed_sql is None:
        sql = generate_sql(question)
    else:
        print("\nCorrecting failed SQL...")
        sql = correct_sql(
            question=question,
            failed_sql=failed_sql,
            error_message=sql_error
        )
    print("\nGenerated SQL:")
    print(sql)
    result = execute_query(sql)

    return {
        "question": question,
        "sql": sql,
        "result": result
    }

if __name__ == "__main__":
    question = "What is the total revenue?"
    response = ask_database(question)

    print("\nFinal Result:")
    print(f"question: '{response['question']}',")
    print(f"sql: '{response['sql']}',")
    print(f"result: {response['result']},")
    # print(f"answer: {response['answer']}")