import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Rugby Dominance Dashboard", layout="wide")

# Load team stats
df = pd.read_csv("team_stats.csv", index_col=0)

st.title("🏉 Rugby Dominance Dashboard")
st.write("""
Explore international rugby dominance using win percentages, scoring margins,
defensive strength, and Rugby World Cup titles.
""")

# Sidebar team selector
st.sidebar.header("Select a Team")
team = st.sidebar.selectbox("Team:", df.index)

# Team snapshot
st.subheader(f"Team Snapshot: {team}")

team_data = df.loc[team]

col1, col2, col3 = st.columns(3)
col1.metric("Win %", f"{team_data['win_pct']:.1f}%")
col2.metric("Avg Margin", f"{team_data['margin_per_match']:.2f}")
col3.metric("Defense (pts allowed)", f"{team_data['points_allowed_per_match']:.2f}")

st.metric("Avg Seasonal Margin", f"{team_data['avg_season_margin']:.2f}")
st.metric("World Cup Titles", int(team_data["world_cup_titles"]))

st.divider()

# Top 10 by win percentage
st.subheader("Top Teams: Win Percentage")
top10 = df.sort_values("win_pct", ascending=False).head(10)

fig, ax = plt.subplots()
ax.bar(top10.index, top10["win_pct"])
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

# Top 10 by dominance score
st.subheader("Top Teams: Dominance Score")
top10_dom = df.sort_values("dominance_score", ascending=False).head(10)

fig2, ax2 = plt.subplots()
ax2.bar(top10_dom.index, top10_dom["dominance_score"])
plt.xticks(rotation=45, ha="right")
st.pyplot(fig2)

st.divider()

# Auto summary
st.subheader("Auto-Generated Summary")

top_dom = df.sort_values("dominance_score", ascending=False).head(3)
dom1, dom2, dom3 = top_dom.index

st.write(
    f"**Top Dominant Teams:** {dom1}, {dom2}, and {dom3}. "
    f"{dom1} ranks #1 overall according to win %, scoring margin, defense, and World Cup titles."
)
