import psycopg2
from config import DB_CONFIG


# ------------------------------------
# Database Connection
# ------------------------------------
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database Connected Successfully!")
        return conn

    except Exception as e:
        print("❌ Database Connection Failed!")
        print(e)
        raise


# ------------------------------------
# Dashboard KPIs
# ------------------------------------
def get_dashboard_kpis():

    conn = get_connection()

    try:
        cursor = conn.cursor()

        query = """
        SELECT
            SUM(payment_value),
            COUNT(DISTINCT order_id),
            COUNT(DISTINCT customer_unique_id),
            ROUND(
                AVG(
                    EXTRACT(
                        DAY FROM (
                            order_delivered_customer_date::timestamp -
                            order_purchase_timestamp::timestamp
                        )
                    )
                ),
                2
            )
        FROM retail_cleaned
        WHERE order_delivered_customer_date IS NOT NULL;
        """

        cursor.execute(query)

        result = cursor.fetchone()

        return {
            "total_revenue": float(result[0] or 0),
            "total_orders": result[1] or 0,
            "total_customers": result[2] or 0,
            "avg_delivery_days": float(result[3] or 0)
        }

    except Exception as e:
        print("Dashboard KPI Error:", e)
        raise

    finally:
        cursor.close()
        conn.close()


# ------------------------------------
# Run Any SQL Query
# ------------------------------------
def run_query(query):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        return {
            "columns": columns,
            "rows": rows
        }

    except Exception as e:
        print("SQL Error:", e)
        raise

    finally:
        cursor.close()
        conn.close()


# ------------------------------------
# Test
# ------------------------------------
if __name__ == "__main__":

    print(get_dashboard_kpis())