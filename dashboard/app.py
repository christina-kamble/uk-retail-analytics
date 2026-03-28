"""
dashboard/app.py
----------------
Interactive Streamlit dashboard for UK Retail Sales Analytics.

Three pages:
  1. Overview      — headline KPIs, revenue trends, geographic breakdown
  2. Products      — top products, volume vs revenue scatter
  3. Customers     — RFM segmentation, repeat vs one-time buyers

Run with: streamlit run dashboard/app.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.data_loader import load_data
from src.sql_queries import (
    get_kpis, monthly_revenue, revenue_by_country,
    revenue_by_day_of_week, mom_growth, top_products,
    product_volume_vs_revenue, repeat_vs_onetime,
)
from src.rfm_analysis import compute_rfm, segment_summary

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UK Retail Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Clean light theme CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #eef2ff;
        border-radius: 14px;
        padding: 24px 20px;
        text-align: center;
        border-left: 5px solid #4f6ef7;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1a202c;
        letter-spacing: -0.5px;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #4a5568;
        margin-top: 6px;
        font-weight: 500;
    }
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a202c;
        margin: 1.5rem 0 0.4rem;
        padding-bottom: 6px;
        border-bottom: 2px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data (cached) ─────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading retail data...")
def get_data():
    return load_data()

df = get_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/shopping-cart.png", width=60)
st.sidebar.title("UK Retail Analytics")
st.sidebar.markdown("*UK E-commerce · 2010–2011*")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["📊 Overview", "📦 Products", "👥 Customer Segments"],
)

countries = ["All Countries"] + sorted(df["country"].unique().tolist())
selected_country = st.sidebar.selectbox("Filter by Country", countries)

if selected_country != "All Countries":
    df = df[df["country"] == selected_country]

st.sidebar.divider()
st.sidebar.markdown(f"**{len(df):,}** transactions · **{df['customer_id'].nunique():,}** customers")

# ── Shared Plotly layout ───────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="#1a202c", size=13),
    margin=dict(t=30, b=30),
)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("📊 Sales Overview")
    st.markdown("High-level business performance across revenue, orders, and customers.")
    st.divider()

    kpis = get_kpis(df)
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{kpis['total_revenue']:,.0f}</div>
            <div class="metric-label">Total Revenue</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{int(kpis['total_orders']):,}</div>
            <div class="metric-label">Total Orders</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{int(kpis['total_customers']):,}</div>
            <div class="metric-label">Unique Customers</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{kpis['avg_order_value']:,.2f}</div>
            <div class="metric-label">Avg Order Value</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📈 Monthly Revenue Trend</div>', unsafe_allow_html=True)
    monthly = monthly_revenue(df)
    fig_trend = px.area(
        monthly, x="year_month", y="revenue",
        labels={"year_month": "Month", "revenue": "Revenue (£)"},
        color_discrete_sequence=["#4f6ef7"],
    )
    fig_trend.update_layout(
        **PLOT_LAYOUT,
        xaxis=dict(showgrid=False, tickfont=dict(color="#1a202c")),
        yaxis=dict(showgrid=True, gridcolor="#e2e8f0", tickfont=dict(color="#1a202c")),
        hovermode="x unified",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">📉 Month-on-Month Growth (%)</div>', unsafe_allow_html=True)
        growth = mom_growth(df).dropna()
        colors = ["#e53e3e" if v < 0 else "#38a169" for v in growth["mom_growth_pct"]]
        fig_growth = go.Figure(go.Bar(
            x=growth["year_month"], y=growth["mom_growth_pct"],
            marker_color=colors,
            text=growth["mom_growth_pct"].apply(lambda x: f"{x:+.1f}%"),
            textposition="outside",
            textfont=dict(color="#1a202c", size=11),
        ))
        fig_growth.update_layout(
            **PLOT_LAYOUT,
            xaxis=dict(showgrid=False, tickfont=dict(color="#1a202c")),
            yaxis=dict(showgrid=True, gridcolor="#e2e8f0", tickfont=dict(color="#1a202c")),
            showlegend=False,
        )
        st.plotly_chart(fig_growth, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">🌍 Revenue by Country (Top 10)</div>', unsafe_allow_html=True)
        by_country = revenue_by_country(df)
        fig_country = px.bar(
            by_country, x="revenue", y="country", orientation="h",
            labels={"revenue": "Revenue (£)", "country": ""},
            color="revenue", color_continuous_scale="Blues",
        )
        fig_country.update_layout(
            **PLOT_LAYOUT,
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed", tickfont=dict(color="#1a202c")),
            xaxis=dict(tickfont=dict(color="#1a202c")),
        )
        st.plotly_chart(fig_country, use_container_width=True)

    st.markdown('<div class="section-header">📅 Revenue by Day of Week</div>', unsafe_allow_html=True)
    dow = revenue_by_day_of_week(df)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow["day_of_week"] = pd.Categorical(dow["day_of_week"], categories=day_order, ordered=True)
    dow = dow.sort_values("day_of_week")
    fig_dow = px.bar(
        dow, x="day_of_week", y="revenue",
        labels={"day_of_week": "Day", "revenue": "Revenue (£)"},
        color="revenue", color_continuous_scale="Purples",
    )
    fig_dow.update_layout(
        **PLOT_LAYOUT,
        coloraxis_showscale=False,
        xaxis=dict(tickfont=dict(color="#1a202c")),
        yaxis=dict(tickfont=dict(color="#1a202c"), gridcolor="#e2e8f0"),
    )
    st.plotly_chart(fig_dow, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Products":
    st.title("📦 Product Analysis")
    st.markdown("Identify top performers and understand volume vs revenue trade-offs.")
    st.divider()

    st.markdown('<div class="section-header">🏆 Top 15 Products by Revenue</div>', unsafe_allow_html=True)
    top = top_products(df)
    fig_top = px.bar(
        top, x="revenue", y="description", orientation="h",
        labels={"revenue": "Revenue (£)", "description": ""},
        color="revenue", color_continuous_scale="Teal",
        hover_data=["units_sold", "orders"],
    )
    fig_top.update_layout(
        **PLOT_LAYOUT,
        height=550,
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed", tickfont=dict(color="#1a202c", size=12)),
        xaxis=dict(tickfont=dict(color="#1a202c")),
    )
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown('<div class="section-header">🔍 Volume vs Revenue — Product Positioning</div>', unsafe_allow_html=True)
    st.caption("Products in the top-right corner are both high-volume and high-revenue — your star products.")
    scatter = product_volume_vs_revenue(df, top_n=50)
    fig_scatter = px.scatter(
        scatter, x="units_sold", y="revenue",
        hover_name="description", size="avg_price",
        labels={"units_sold": "Units Sold", "revenue": "Revenue (£)", "avg_price": "Avg Price (£)"},
        color="avg_price", color_continuous_scale="Viridis",
    )
    fig_scatter.update_layout(
        **PLOT_LAYOUT,
        xaxis=dict(tickfont=dict(color="#1a202c"), gridcolor="#e2e8f0"),
        yaxis=dict(tickfont=dict(color="#1a202c"), gridcolor="#e2e8f0"),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown('<div class="section-header">📋 Product Summary Table</div>', unsafe_allow_html=True)
    top_display = top.copy()
    top_display["revenue"] = top_display["revenue"].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(top_display, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CUSTOMER SEGMENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Customer Segments":
    st.title("👥 Customer Segmentation — RFM Analysis")
    st.markdown(
        "**RFM** (Recency · Frequency · Monetary) is a proven framework used in retail, fintech, "
        "and CRM to segment customers by purchasing behaviour and target them with the right actions."
    )
    st.divider()

    with st.spinner("Computing RFM scores..."):
        rfm = compute_rfm(df)
        seg_sum = segment_summary(rfm)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="section-header">🍩 Customer Distribution by Segment</div>', unsafe_allow_html=True)
        fig_donut = px.pie(
            seg_sum, names="segment", values="num_customers",
            hole=0.45, color="segment",
            color_discrete_map=seg_sum.set_index("segment")["color"].to_dict(),
        )
        fig_donut.update_traces(
            textposition="inside", textinfo="percent+label",
            textfont=dict(size=13, color="white"),
        )
        fig_donut.update_layout(showlegend=False, paper_bgcolor="white", font=dict(color="#1a202c"))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">💰 Revenue by Segment</div>', unsafe_allow_html=True)
        fig_rev = px.bar(
            seg_sum.sort_values("total_revenue", ascending=True),
            x="total_revenue", y="segment", orientation="h",
            color="segment",
            color_discrete_map=seg_sum.set_index("segment")["color"].to_dict(),
            labels={"total_revenue": "Total Revenue (£)", "segment": ""},
        )
        fig_rev.update_layout(
            **PLOT_LAYOUT,
            showlegend=False,
            yaxis=dict(tickfont=dict(color="#1a202c", size=13)),
            xaxis=dict(tickfont=dict(color="#1a202c")),
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    st.markdown('<div class="section-header">📋 Segment Detail & Recommended Actions</div>', unsafe_allow_html=True)
    display = seg_sum[["segment", "num_customers", "pct_customers", "avg_recency", "avg_frequency", "avg_monetary", "total_revenue"]].copy()
    display.columns = ["Segment", "Customers", "% of Base", "Avg Recency (days)", "Avg Orders", "Avg Spend (£)", "Total Revenue (£)"]
    display["Total Revenue (£)"] = display["Total Revenue (£)"].apply(lambda x: f"£{x:,.0f}")
    display["Avg Spend (£)"]     = display["Avg Spend (£)"].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">🔁 Repeat vs One-Time Buyers</div>', unsafe_allow_html=True)
    repeat = repeat_vs_onetime(df)
    col3, col4 = st.columns(2)
    with col3:
        fig_repeat = px.pie(
            repeat, names="customer_type", values="num_customers",
            color_discrete_sequence=["#4f6ef7", "#e53e3e"],
            hole=0.4,
        )
        fig_repeat.update_traces(textfont=dict(size=14, color="white"))
        fig_repeat.update_layout(paper_bgcolor="white", font=dict(color="#1a202c"))
        st.plotly_chart(fig_repeat, use_container_width=True)
    with col4:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for _, row in repeat.iterrows():
            icon = "🔄" if row["customer_type"] == "Repeat" else "1️⃣"
            st.metric(
                f"{icon} {row['customer_type']} Buyers",
                f"{int(row['num_customers']):,} customers",
                f"{row['pct_customers']}% of base"
            )

    st.markdown('<div class="section-header">🔍 Look Up a Customer</div>', unsafe_allow_html=True)
    customer_ids = sorted(rfm["customer_id"].unique().tolist())
    selected = st.selectbox("Select Customer ID", customer_ids)
    if selected:
        row = rfm[rfm["customer_id"] == selected].iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Segment",     row["segment"])
        c2.metric("Recency",     f"{row['recency']} days")
        c3.metric("Frequency",   f"{row['frequency']} orders")
        c4.metric("Monetary",    f"£{row['monetary']:,.2f}")
        c5.metric("RFM Score",   row["rfm_score"])
        st.info(f"💡 **Recommended action:** {row['recommended_action']}")
