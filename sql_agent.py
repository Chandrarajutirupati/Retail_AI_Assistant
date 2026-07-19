from ai import ask_llm
from database import run_query


def clean_sql(sql):
    sql = sql.replace("```sql", "")
    sql = sql.replace("```SQL", "")
    sql = sql.replace("```", "")
    return sql.strip()


def ask_database(question):

    print("\n========== SQL AGENT ==========")

    # -----------------------------
    # Generate SQL
    # -----------------------------
    print("Step 1: Generating SQL...")

    sql_query = ask_llm(question)

    sql_query = clean_sql(sql_query)

    # Automatically limit large queries
    if (
        "limit" not in sql_query.lower()
        and "count(" not in sql_query.lower()
        and "sum(" not in sql_query.lower()
        and "avg(" not in sql_query.lower()
        and "max(" not in sql_query.lower()
        and "min(" not in sql_query.lower()
    ):
        sql_query += "\nLIMIT 100;"

    print("Generated SQL:")
    print(sql_query)

    # -----------------------------
    # Execute SQL
    # -----------------------------
    print("Step 2: Running SQL...")

    db_result = run_query(sql_query)

    columns = db_result["columns"]
    rows = db_result["rows"]

    print("Database Result:")
    print(rows)

    # -----------------------------
    # Limit rows sent to the LLM
    # -----------------------------
    if len(rows) > 10:
        preview = rows[:10]
    else:
        preview = rows

    # -----------------------------
    # Generate Explanation
    # -----------------------------
    print("Step 3: Generating Explanation...")

    explanation_prompt = f"""
You are a senior Retail Business Analyst.

User Question:
{question}

SQL Query:
{sql_query}

Database Result:
{preview}

Write the answer in this EXACT format:

📊 Key Insight
- ...

💡 Recommendation
- ...

⚠ Business Impact
- ...

Keep each point short.

Do NOT generate SQL.
Do NOT repeat the table values.
"""

    explanation = ask_llm(
        explanation_prompt,
        system_prompt="""
You are an expert Retail Business Analyst.

Give concise executive-level business insights.

Always respond using this format:

📊 Key Insight
- ...

💡 Recommendation
- ...

⚠ Business Impact
- ...

Keep each point short.

Never generate SQL.
Never explain the SQL.
"""
)


    
    print("Explanation Generated.")
    print("========== FINISHED ==========\n")

    return {
        "sql": sql_query,
        "columns": columns,
        "result": rows,
        "explanation": explanation
    }