"""
sql_queries.py
--------------
All business analytics queries written in SQL using DuckDB.
DuckDB lets us run SQL directly on Pandas DataFrames — no database server needed.

This file demonstrates SQL skills clearly for DA/BI hiring managers.
"""

import duckdb
import pandas as pd


def _q(df: pd.DataFrame, sql: str) -> pd.DataFrame:
    """Run a SQL query against a Pandas DataFrame via DuckDB."""
    conn = duckdb.connect()
    conn.register("df", df)
    return conn.execute(sql).df()


# ─── OVERVIEW KPIs ───────────────────────────────────────────────────────────

def get_kpis(df: pd.DataFrame) -> dict:
    result = _q(df, """
        SELECT
            ROUND(SUM(revenue), 2)                          AS total_revenue,
            COUNT(DISTINCT invoice_no)                      AS total_orders,
            COUNT(DISTINCT customer_id)                     AS total_customers,
            ROUND(SUM(revenue) / COUNT(DISTINCT invoice_no), 2) AS avg_order_value
        FROM df
    """)
    return result.iloc[0].to_dict()


# ─── REVENUE TRENDS ───────────────────────────────────────────────────────────

def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return _q(df, """
        SELECT
            year_month,
            ROUND(SUM(revenue), 2)       AS revenue,
            COUNT(DISTINCT invoice_no)   AS orders,
            COUNT(DISTINCT customer_id)  AS customers
        FROM df
        GROUP BY year_month
        ORDER BY year_month
    """)


def revenue_by_country(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return _q(df, f"""
        SELECT
            country,
            ROUND(SUM(revenue), 2)      AS revenue,
            COUNT(DISTINCT customer_id) AS customers,
            COUNT(DISTINCT invoice_no)  AS orders
        FROM df
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT {top_n}
    """)


def revenue_by_day_of_week(df: pd.DataFrame) -> pd.DataFrame:
    return _q(df, """
        SELECT
            day_of_week,
            ROUND(SUM(revenue), 2)     AS revenue,
            COUNT(DISTINCT invoice_no) AS orders
        FROM df
        GROUP BY day_of_week
        ORDER BY revenue DESC
    """)


def mom_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Month-on-month revenue growth using window functions."""
    return _q(df, """
        WITH monthly AS (
            SELECT
                year_month,
                ROUND(SUM(revenue), 2) AS revenue
            FROM df
            GROUP BY year_month
        )
        SELECT
            year_month,
            revenue,
            LAG(revenue) OVER (ORDER BY year_month) AS prev_month_revenue,
            ROUND(
                (revenue - LAG(revenue) OVER (ORDER BY year_month))
                / NULLIF(LAG(revenue) OVER (ORDER BY year_month), 0) * 100,
            2) AS mom_growth_pct
        FROM monthly
        ORDER BY year_month
    """)


# ─── PRODUCT ANALYSIS ─────────────────────────────────────────────────────────

def top_products(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    return _q(df, f"""
        SELECT
            description,
            ROUND(SUM(revenue), 2)  AS revenue,
            SUM(quantity)           AS units_sold,
            COUNT(DISTINCT invoice_no) AS orders
        FROM df
        WHERE description IS NOT NULL
        GROUP BY description
        ORDER BY revenue DESC
        LIMIT {top_n}
    """)


def product_volume_vs_revenue(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """High volume vs high revenue products — useful for margin analysis."""
    return _q(df, f"""
        SELECT
            description,
            SUM(quantity)          AS units_sold,
            ROUND(SUM(revenue), 2) AS revenue,
            ROUND(AVG(unit_price), 2) AS avg_price
        FROM df
        WHERE description IS NOT NULL
        GROUP BY description
        ORDER BY units_sold DESC
        LIMIT {top_n}
    """)


# ─── CUSTOMER ANALYSIS ────────────────────────────────────────────────────────

def customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    return _q(df, """
        SELECT
            customer_id,
            COUNT(DISTINCT invoice_no)   AS total_orders,
            ROUND(SUM(revenue), 2)       AS total_spend,
            ROUND(AVG(revenue), 2)       AS avg_order_value,
            MIN(invoice_date)::DATE      AS first_order,
            MAX(invoice_date)::DATE      AS last_order
        FROM df
        GROUP BY customer_id
        ORDER BY total_spend DESC
    """)


def repeat_vs_onetime(df: pd.DataFrame) -> pd.DataFrame:
    """Split customers into one-time buyers vs repeat buyers."""
    return _q(df, """
        WITH customer_orders AS (
            SELECT
                customer_id,
                COUNT(DISTINCT invoice_no) AS num_orders
            FROM df
            GROUP BY customer_id
        )
        SELECT
            CASE WHEN num_orders = 1 THEN 'One-time' ELSE 'Repeat' END AS customer_type,
            COUNT(*)                       AS num_customers,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_customers
        FROM customer_orders
        GROUP BY customer_type
    """)


def cohort_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly order counts per acquisition cohort (first purchase month)."""
    return _q(df, """
        WITH first_purchase AS (
            SELECT
                customer_id,
                MIN(year_month) AS cohort_month
            FROM df
            GROUP BY customer_id
        ),
        cohort_data AS (
            SELECT
                f.cohort_month,
                d.year_month AS order_month,
                COUNT(DISTINCT d.customer_id) AS customers
            FROM df d
            JOIN first_purchase f ON d.customer_id = f.customer_id
            GROUP BY f.cohort_month, d.year_month
        )
        SELECT *
        FROM cohort_data
        ORDER BY cohort_month, order_month
    """)
