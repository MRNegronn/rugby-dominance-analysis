import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Rugby Dominance Dashboard",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load data
df = pd.read_csv("team_stats.csv", index_col=0)

# Title and intro
st.title("🏉 Rugby Dominance Dashboard")
st.write("""
Explore international rugby dominance using win percentages, scoring margins,
defensive strength, and Rugby World Cup titles.
""")

# Sidebar controls
team = st.sidebar.selectbox("Select a team:", df.index)

# ----- TABS -----
tab_team, tab_rankings, tab_about = st.tabs(
    ["Team View", "Rankings", "About"]
)

# =========================
# TAB 1 — TEAM VIEW
# =========================
with tab_team:
    st.subheader(f"Team Snapshot: {team}")
    team_data = df.loc[team]

    col1, col2, col3 = st.columns(3)
    col1.metric("Win %", f"{team_data['win_pct']:.1f}%")
    col2.metric("Avg Margin per Match", f"{team_data['margin_per_match']:.2f}")
    col3.metric(
        "Defense (pts allowed / match)",
        f"{team_data['points_allowed_per_match']:.2f}",
    )

    st.metric("Avg Seasonal Margin", f"{team_data['avg_season_margin']:.2f}")
    st.metric("World Cup Titles", int(team_data["world_cup_titles"]))


# =========================
# TAB 2 — RANKINGS
# =========================
with tab_rankings:
    st.subheader("Top 10 Teams — Win Percentage")
    top10 = df.sort_values("win_pct", ascending=False).head(10)
    fig1, ax1 = plt.subplots()
    ax1.bar(top10.index, top10["win_pct"])
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig1)

    st.markdown("---")

    st.subheader("Top 10 Teams — Dominance Score")
    top10_dom = df.sort_values("dominance_score", ascending=False).head(10)
    fig2, ax2 = plt.subplots()
    ax2.bar(top10_dom.index, top10_dom["dominance_score"])
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig2)

    st.markdown("---")

    # Auto summary
    top_dom = df.sort_values("dominance_score", ascending=False).head(3)
    dom1, dom2, dom3 = top_dom.index

    st.write(
        f"Most dominant teams overall: **{dom1}**, **{dom2}**, **{dom3}**."
    )


# =========================
# TAB 3 — ABOUT
# =========================
with tab_about:
    st.subheader("About This Project")
    st.write("""
This dashboard summarizes international rugby performance across multiple metrics,
including win percentage, scoring margin, defensive strength, and championship success.
It is part of a portfolio demonstrating data analysis and web app deployment using Python and Streamlit.
""")
