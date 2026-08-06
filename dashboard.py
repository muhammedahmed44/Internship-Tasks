"""
Week 3 - Program Performance Dashboard
Run with: streamlit run dashboard.py
"""

import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="NextGen Program Performance", layout="wide")

# ---------- Load data ----------
conn = sqlite3.connect("nextgen.db")
applicants = pd.read_sql("SELECT * FROM applicants;", conn)
interns = pd.read_sql("SELECT * FROM interns;", conn)
scores = pd.read_sql("SELECT * FROM hackathon_scores;", conn)
conn.close()

st.title("📊 NextGen Program Performance Dashboard")
st.caption("Applicant -> Intern -> Hackathon funnel, filterable by domain.")

# ---------- Domain filter (the "interactive" requirement) ----------
domain_list = ["All"] + sorted(applicants["domain"].unique().tolist())
selected_domain = st.selectbox("Filter by Domain", domain_list)

if selected_domain != "All":
    applicants_filtered = applicants[applicants["domain"] == selected_domain]
    interns_filtered = interns[interns["domain"] == selected_domain]
    scores_filtered = scores[scores["domain"] == selected_domain]
else:
    applicants_filtered = applicants
    interns_filtered = interns
    scores_filtered = scores

completed_filtered = interns_filtered[interns_filtered["completion_status"] == "Completed"]

# ---------- 1. Funnel: total applicants vs total interns ----------
st.subheader("Funnel: Applicants → Interns → Completed")
col1, col2, col3 = st.columns(3)
col1.metric("Total Applicants", len(applicants_filtered))
col2.metric("Became Interns", len(interns_filtered))
col3.metric("Completed Program", len(completed_filtered))

st.divider()

# ---------- 2. Completion rate per domain ----------
st.subheader("Completion Rate per Domain")
completion_by_domain = (
    interns[interns["completion_status"] == "Completed"]
    .groupby("domain")
    .size()
    .reindex(sorted(applicants["domain"].unique()), fill_value=0)
    .rename("completed_count")
)
st.bar_chart(completion_by_domain)

st.divider()

# ---------- 3. Average hackathon score per domain ----------
st.subheader("Average Hackathon Score per Domain")
avg_score_by_domain = (
    scores.groupby("domain")["score"]
    .mean()
    .round(2)
    .reindex(sorted(applicants["domain"].unique()))
)
st.bar_chart(avg_score_by_domain)

st.divider()

# ---------- 4. Leaderboard of top 10 performers (respects the domain filter) ----------
st.subheader(f"🏆 Top 10 Leaderboard{'' if selected_domain == 'All' else f' — {selected_domain}'}")
leaderboard = (
    interns_filtered.merge(scores_filtered, on=["intern_id", "domain"], how="inner")
    [["intern_id", "domain", "score"]]
    .sort_values("score", ascending=False)
    .head(10)
    .reset_index(drop=True)
)
st.dataframe(leaderboard, width="stretch")

st.caption(
    "Data source: nextgen.db (applicants, interns, hackathon_scores). "
    "Completion rate and average score charts always show all domains for comparison; "
    "the funnel metrics and leaderboard respect the domain filter above."
)
