"""
STEP 9: Visual dashboard.

Turns your CSV results into an interactive web dashboard -- much more
demo-friendly than reading a terminal report or a spreadsheet.

HOW TO RUN:
    py -m pip install streamlit pandas
    py main.py                          (make sure audit_log.csv is fresh)
    streamlit run dashboard.py

This opens automatically in your browser at http://localhost:8501
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Revenue Recovery Dashboard", layout="wide")

st.title("💰 Revenue Recovery Dashboard")
st.caption("AI agent for recovering failed payments and abandoned checkouts")


@st.cache_data
def load_data():
    return pd.read_csv("audit_log.csv")


try:
    df = load_data()
except FileNotFoundError:
    st.error("audit_log.csv not found. Run 'py main.py' first to generate results.")
    st.stop()

# ---------- Headline metrics ----------
total_at_risk = df["amount"].sum()
total_recovered = df["amount_recovered"].sum()
recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk else 0
escalation_rate = (df["action_taken"] == "escalate_to_human").mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total At Risk", f"Rs {total_at_risk:,.0f}")
col2.metric("Total Recovered", f"Rs {total_recovered:,.0f}")
col3.metric("Recovery Rate", f"{recovery_rate:.1f}%")
col4.metric("Escalated to Human", f"{escalation_rate:.1f}%")

st.divider()

# ---------- Chart: recovery by action ----------
st.subheader("Amount Recovered by Action Type")
by_action = df.groupby("action_taken")["amount_recovered"].sum().sort_values(ascending=False)
st.bar_chart(by_action)

# ---------- Chart: recovery by failure reason ----------
st.subheader("Amount Recovered by Failure Reason")
by_reason = df.groupby("classified_reason")["amount_recovered"].sum().sort_values(ascending=False)
st.bar_chart(by_reason)

st.divider()

# ---------- Filterable table ----------
st.subheader("Full Audit Trail")

col_a, col_b = st.columns(2)
with col_a:
    action_filter = st.multiselect(
        "Filter by action", options=sorted(df["action_taken"].unique())
    )
with col_b:
    recovered_filter = st.selectbox(
        "Filter by outcome", options=["All", "Recovered only", "Not recovered only"]
    )

filtered = df.copy()
if action_filter:
    filtered = filtered[filtered["action_taken"].isin(action_filter)]
if recovered_filter == "Recovered only":
    filtered = filtered[filtered["recovered"] == True]
elif recovered_filter == "Not recovered only":
    filtered = filtered[filtered["recovered"] == False]

st.dataframe(filtered, use_container_width=True)
st.caption(f"Showing {len(filtered)} of {len(df)} transactions")
