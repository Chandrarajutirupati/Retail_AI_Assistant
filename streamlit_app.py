import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Retail AI Assistant",
    page_icon="🛒",
    layout="wide"
)
# -------------------------------
# Session State
# -------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

API_URL = "http://127.0.0.1:8001/ask"

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.title("🛒 Retail AI Assistant")

    st.markdown("---")

    st.subheader("💡 Sample Questions")

    questions = [
        "What is total revenue?",
        "Monthly sales",
        "Top 10 product categories",
        "Top states by sales",
        "Average delivery time",
        "Highest payment type",
        "Top sellers",
        "Cancelled orders",
        "Weekend vs Weekday sales",
        "Highest freight charges"
    ]

    for q in questions:
        st.markdown(f"• {q}")

    st.markdown("---")
    st.info("Ask business questions in plain English.")

# -------------------------------
# Title
# -------------------------------
st.title("🛒 Retail AI Assistant")

st.caption("Ask business questions and get SQL + AI Insights")


# ==========================
# Dashboard KPIs
# ==========================

try:
    kpi_response = requests.get("http://127.0.0.1:8001/dashboard")
    kpis = kpi_response.json()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Revenue", f"₹ {kpis['total_revenue']:,.2f}")
    col2.metric("📦 Orders", f"{kpis['total_orders']:,}")
    col3.metric("👥 Customers", f"{kpis['total_customers']:,}")
    col4.metric("🚚 Avg Delivery", f"{kpis['avg_delivery_days']} Days")

    st.divider()

except:
    st.warning("Unable to load dashboard KPIs.")

# -------------------------------
# User Input
# -------------------------------
question = st.text_input(
    "Ask a business question",
    placeholder="Example: Show monthly sales"
)

# -------------------------------
# Ask Button
# -------------------------------
if st.button("🚀 Ask AI"):

    start = time.time()

    response = requests.post(
        API_URL,
        json={"question": question},
        timeout=120
    )

    end = time.time()

    data = response.json()

    st.caption(f"⏱ Query executed in {end - start:.2f} seconds")

    # Check for API errors first
    if response.status_code != 200:
        st.error(data.get("detail", "Unknown error"))
        st.stop()

    # Save only successful responses
    st.session_state.history.append({
        "question": question,
        "sql": data["sql"],
        "result": data["result"],
        "explanation": data["explanation"]
    })

    # -----------------------------
    # Generated SQL
    # -----------------------------
    with st.expander("📝 Generated SQL"):
        st.code(data["sql"], language="sql")

    st.subheader("📊 Query Result")

    result = data["result"]
    columns = data["columns"]

    # Single numeric value
    if (
        isinstance(result, list)
        and len(result) == 1
        and len(result[0]) == 1
    ):

        value = result[0][0]

        if isinstance(value, (int, float)):
            st.metric("Result", f"{value:,.2f}")
        else:
            st.metric("Result", str(value))

    # Table
    else:

        df = pd.DataFrame(result, columns=columns)

        st.dataframe(df, use_container_width=True)
        # -----------------------------
        # Download CSV
        # -----------------------------
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="query_results.csv",
            mime="text/csv"
            )

    # -------------------------------
    # Automatic Visualization
    # -------------------------------
    if "df" in locals() and len(df.columns) == 2:

        x = df.columns[0]
        y = df.columns[1]

        x_name = x.lower()

        # Line Chart
        if "month" in x_name or "date" in x_name or "year" in x_name:
            fig = px.line(df, x=x, y=y, markers=True)

        # Pie Chart
        elif (
            "payment" in x_name
            or "status" in x_name
            or "sales_day" in x_name
            or "weekday" in x_name
            or "weekend" in x_name
        ):
            fig = px.pie(df, names=x, values=y)

        # Bar Chart
        elif (
            "category" in x_name
            or "state" in x_name
            or "city" in x_name
            or "seller" in x_name
            or df[x].dtype == object
        ):
            fig = px.bar(df,x=y,y=x,orientation="h")

        # Scatter Chart
        else:
            fig = px.scatter(df, x=x, y=y)

        st.plotly_chart(fig, use_container_width=True)
        # -----------------------------
    # Business Insight
    # -----------------------------
    if data.get("explanation"):

        st.markdown("---")
        st.subheader("💡 Business Insight")

        st.info(data["explanation"])
        st.markdown("---")
        st.subheader("🕒 Chat History")

        if len(st.session_state.history) == 0:
            st.info("No questions asked yet.")

        for i, item in enumerate(reversed(st.session_state.history), start=1):
            with st.expander(f"Question {i}: {item['question']}"):
                st.write("**SQL:**")
                st.code(item["sql"], language="sql")

                st.write("**Business Insight:**")
                st.write(item["explanation"])