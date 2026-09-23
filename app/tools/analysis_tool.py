import pandas as pd
from app.tools.sql_generator import generate_sql
from app.tools.sql_tool import execute_query


# Step 1: SQL Result → Pandas DataFrame
def result_to_dataframe(result):
    if not result["success"]:
        raise ValueError(result["error"])
    df = pd.DataFrame(result["rows"], columns=result["columns"])
    return df

# Step 2: Basic Summary
def calculate_summary(df):
    summary = {
        "row_count": len(df),
        "column_count": len(df.columns)
    }
    return summary

# Step 3: Percentage Analysis
def calculate_percentage(df, value_column):
    if value_column not in df.columns:
        raise ValueError(f"Column '{value_column}' not found in DataFrame.")
    total = df[value_column].sum()
    if total == 0:
        raise ValueError("Total value is zero.")
    df = df.copy()
    df["percentage"] = (df[value_column] / total) * 100
    return df

# Step 4: Growth Analysis
def calculate_growth(df, value_column):
    if value_column not in df.columns:
        raise ValueError(f"Column '{value_column}' not found in DataFrame.")
    df = df.copy()
    df["growth"] = (df[value_column].pct_change()) * 100
    return df

# Step 5: Highest Growth
def find_highest_growth(df, growth_column="growth"):
    if growth_column not in df.columns:
        raise ValueError(f"Column '{growth_column}' not found in DataFrame.")
    df = df.dropna(subset=[growth_column])
    if df.empty:
        raise ValueError("No valid growth data available.")
    highest_row = df.loc[df[growth_column].idxmax()]
    return highest_row

# Step 6: Top N
def get_top_n(df, column, n=5):
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    return (df.sort_values(by=column, ascending=False).head(n))

# Step 7: Bottom N
def get_bottom_n(df, column, n=5):
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    return (df.sort_values(by=column, ascending=True).head(n))

# Step 8: Detect Numeric Value Column
def detect_value_column(df, exclude_columns=None):
    if exclude_columns is None:
        exclude_columns = []
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    numeric_columns = [
        column
        for column in numeric_columns
        if column not in exclude_columns
    ]
    if not numeric_columns:
        raise ValueError("No numeric column found for analysis.")
    return numeric_columns[0]

# Step 9: Run SQL + Analysis
def run_analysis(question):
    sql = generate_sql(question)
    print("\nGenerated SQL:")
    print(sql)

    result = execute_query(sql)
    if not result["success"]:
        return {"success": False, "error": result["error"]}

    df = result_to_dataframe(result)
    return {
        "success": True,
        "question": question,
        "sql": sql,
        "data": df
    }

# Step 10: Final Analysis Pipeline
def analyze_revenue_by_category():
    question = "Show me revenue by product category."
    result = run_analysis(question)

    if not result["success"]:
        return result

    df = result["data"]
    value_column = detect_value_column(df,exclude_columns=[])
    
    percentage_df = calculate_percentage(df,value_column)
    top_categories = get_top_n(percentage_df,value_column,5)

    return {
        "success": True,
        "analysis_type": "top_n",
        "question": question,
        "sql": result["sql"],
        "value_column": value_column,
        "total_rows": len(df),
        "top_results": top_categories.to_dict(
            orient="records"
        )
    }

# Test
if __name__ == "__main__":
    result = analyze_revenue_by_category()
    if result["success"]:
        print("FINAL ANALYSIS RESULT")
        print("\nQuestion:")
        print(result["question"])

        print("\nValue Column:")
        print(result["value_column"])

        print("\nTotal Rows:")
        print(result["total_rows"])

        print("\nTop 5 Categories:")
        for row in result["top_results"]:
            print(row)
    else:
        print("\nAnalysis Error:")
        print(result["error"])