# UK Retail Sales Analytics 🛒

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![DuckDB](https://img.shields.io/badge/SQL-DuckDB-yellow)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red?logo=streamlit)
![Plotly](https://img.shields.io/badge/Charts-Plotly-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

> **Business problem:** A UK-based e-commerce retailer wants to understand which customers, products, and regions are driving revenue — and how to act on that knowledge to increase retention and profitability.

---

## 🎯 Project Summary

This project delivers a full **end-to-end retail analytics pipeline** on the UCI Online Retail dataset (~500K transactions, 4,000+ customers, 37 countries). It combines **SQL-based analysis** using DuckDB with **RFM customer segmentation** and an interactive **Streamlit dashboard** — covering the core analytical workflow used by Data Analysts and BI Analysts in industry.

---

## 📁 Repository Structure

```
├── notebooks/
│   └── retail_analysis.ipynb       # Full EDA → SQL analysis → RFM insights
│
├── src/
│   ├── data_loader.py              # Data ingestion & cleaning pipeline
│   ├── sql_queries.py              # All business queries written in SQL (DuckDB)
│   └── rfm_analysis.py             # RFM scoring & customer segmentation
│
├── dashboard/
│   └── app.py                      # 3-page interactive Streamlit dashboard
│
├── requirements.txt
└── README.md
```

---

## 🔍 Key Business Findings

| Finding | Insight | Recommended Action |
|---|---|---|
| 82% of revenue from UK | Heavy geographic concentration | Diversify marketing to top EU markets |
| Thursday is peak revenue day | Mid-week buying behaviour | Schedule promotions for Wed–Thu |
| ~35% are one-time buyers | Retention gap | Launch post-purchase email sequence |
| Champions (top RFM) = 12% of customers, ~40% of revenue | Power law distribution | Prioritise loyalty rewards for this group |
| Month-on-month dip in Jan–Feb | Post-holiday slump | Introduce January loyalty incentives |

---

## 📊 Dashboard Pages

**1. Overview** — Headline KPIs, monthly revenue trend, MoM growth, country breakdown, day-of-week patterns

**2. Products** — Top 15 products by revenue, volume vs revenue scatter plot, product summary table

**3. Customer Segments** — Full RFM segmentation, segment revenue breakdown, repeat vs one-time buyer split, individual customer lookup with recommended action

---

## 🧠 RFM Segmentation Explained

**RFM** is a proven marketing analytics framework used across retail, fintech, and CRM:

| Dimension | Question | Scoring |
|---|---|---|
| **Recency** | How recently did they buy? | 5 = bought yesterday, 1 = bought a year ago |
| **Frequency** | How often do they buy? | 5 = very frequent, 1 = one-time |
| **Monetary** | How much do they spend? | 5 = high spender, 1 = low spender |

Customers are scored 1–5 on each dimension and mapped to 7 actionable segments:

| Segment | Profile | Action |
|---|---|---|
| **Champions** | Recent, frequent, high spend | Reward & upsell |
| **Loyal Customers** | Regular buyers, good spend | Loyalty programme |
| **At Risk** | Used to buy often — gone quiet | Win-back campaign |
| **Lost** | Low recency, low frequency | Strong reactivation offer |
| **Potential Loyalists** | Recent but infrequent | Convert with membership |

---

## 🔧 SQL Skills Demonstrated

All analysis is written in **SQL via DuckDB**, running directly on Pandas DataFrames — no database server required. Key SQL concepts used:

- `GROUP BY`, `ORDER BY`, aggregation functions
- `JOIN` (customer + transaction data)
- `CTEs` (`WITH` statements) for readable multi-step queries
- **Window functions** — `LAG()` for month-on-month growth, `RANK()` for product ranking
- `CASE WHEN` for conditional segmentation
- `NULLIF` for safe division

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/christina-kamble/uk-retail-analytics.git
cd uk-retail-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the notebook
jupyter notebook notebooks/retail_analysis.ipynb

# 4. Launch the dashboard
streamlit run dashboard/app.py
```

No data download needed — the dataset loads automatically from a public URL.

---

## 📦 Dataset

**UCI Online Retail Dataset** — real transaction data from a UK-based online gift retailer.

- ~500,000 transactions · ~4,000 customers · 37 countries
- Date range: December 2010 – December 2011
- Features: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country

---

## 🔮 Next Steps

- **Cohort retention analysis** — track what % of each monthly cohort returns in subsequent months, to quantify long-term loyalty trends
- **CLV (Customer Lifetime Value) modelling** — move from descriptive RFM to predictive CLV using BG/NBD model
- **Market basket analysis** — identify which products are frequently bought together using association rules (Apriori), to inform cross-sell recommendations
- **Anomaly detection on revenue** — flag unusual spikes/drops automatically to support business monitoring

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.
