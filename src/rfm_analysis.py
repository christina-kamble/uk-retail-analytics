"""
rfm_analysis.py
---------------
RFM (Recency, Frequency, Monetary) customer segmentation.

RFM is a proven marketing analytics framework used in CRM, retail,
and fintech to segment customers by behaviour. It's a core interview topic
for DA and BI roles.

  Recency   — How recently did the customer buy?
  Frequency — How often do they buy?
  Monetary  — How much do they spend in total?
"""

import pandas as pd
import numpy as np


SEGMENT_MAP = {
    "Champions":          {"r": (4, 5), "f": (4, 5), "color": "#2ecc71"},
    "Loyal Customers":    {"r": (3, 5), "f": (3, 5), "color": "#27ae60"},
    "Potential Loyalists":{"r": (3, 5), "f": (1, 3), "color": "#1abc9c"},
    "Recent Customers":   {"r": (4, 5), "f": (1, 1), "color": "#3498db"},
    "At Risk":            {"r": (1, 2), "f": (3, 5), "color": "#e67e22"},
    "Lost":               {"r": (1, 2), "f": (1, 2), "color": "#e74c3c"},
    "Need Attention":     {"r": (2, 3), "f": (2, 3), "color": "#f39c12"},
}

SEGMENT_ACTIONS = {
    "Champions":           "Reward them. Ask for reviews. Upsell premium products.",
    "Loyal Customers":     "Offer loyalty programme. Recommend new products.",
    "Potential Loyalists": "Offer membership or loyalty programme to convert.",
    "Recent Customers":    "Provide onboarding support. Build early relationship.",
    "At Risk":             "Send win-back campaigns. Offer discounts urgently.",
    "Lost":                "Reactivation campaign with strong incentive.",
    "Need Attention":      "Send limited-time offers. Reconnect with relevant content.",
}


def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute RFM scores for each customer.

    Steps:
    1. Calculate raw R, F, M values per customer
    2. Score each metric 1–5 using quintiles
    3. Assign business segment based on score combination
    """
    snapshot_date = df["invoice_date"].max() + pd.Timedelta(days=1)

    # ── Step 1: Raw RFM values ──
    rfm = (
        df.groupby("customer_id")
        .agg(
            recency   = ("invoice_date", lambda x: (snapshot_date - x.max()).days),
            frequency = ("invoice_no",   "nunique"),
            monetary  = ("revenue",      "sum"),
        )
        .reset_index()
    )

    rfm["monetary"] = rfm["monetary"].round(2)

    # ── Step 2: Score 1–5 (5 = best) ──
    rfm["r_score"] = pd.qcut(rfm["recency"],   5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"],  5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)

    # ── Step 3: Assign segment ──
    rfm["segment"] = rfm.apply(_assign_segment, axis=1)
    rfm["segment_color"] = rfm["segment"].map(lambda s: SEGMENT_MAP.get(s, {}).get("color", "#95a5a6"))
    rfm["recommended_action"] = rfm["segment"].map(SEGMENT_ACTIONS)

    return rfm


def _assign_segment(row) -> str:
    r, f = row["r_score"], row["f_score"]
    for segment, rules in SEGMENT_MAP.items():
        r_min, r_max = rules["r"]
        f_min, f_max = rules["f"]
        if r_min <= r <= r_max and f_min <= f <= f_max:
            return segment
    return "Others"


def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Aggregate RFM results by segment for dashboard display."""
    summary = (
        rfm.groupby("segment")
        .agg(
            num_customers   = ("customer_id", "count"),
            avg_recency     = ("recency",     "mean"),
            avg_frequency   = ("frequency",   "mean"),
            avg_monetary    = ("monetary",    "mean"),
            total_revenue   = ("monetary",    "sum"),
        )
        .reset_index()
    )

    summary["avg_recency"]   = summary["avg_recency"].round(0).astype(int)
    summary["avg_frequency"] = summary["avg_frequency"].round(1)
    summary["avg_monetary"]  = summary["avg_monetary"].round(2)
    summary["total_revenue"] = summary["total_revenue"].round(2)
    summary["pct_customers"] = (summary["num_customers"] / summary["num_customers"].sum() * 100).round(1)
    summary["color"]         = summary["segment"].map(lambda s: SEGMENT_MAP.get(s, {}).get("color", "#95a5a6"))

    return summary.sort_values("total_revenue", ascending=False)
