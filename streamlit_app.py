import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# World Cup Winners Data (1987–2023)
world_cups = [
    {"year": 1987, "winner": "New Zealand"},
    {"year": 1991, "winner": "Australia"},
    {"year": 1995, "winner": "South Africa"},
    {"year": 1999, "winner": "Australia"},
    {"year": 2003, "winner": "England"},
    {"year": 2007, "winner": "South Africa"},
    {"year": 2011, "winner": "New Zealand"},
    {"year": 2015, "winner": "New Zealand"},
    {"year": 2019, "winner": "South Africa"},
    {"year": 2023, "winner": "South Africa"},
]

import pandas as pd
wcs = pd.DataFrame(world_cups)

st.set_page_config(
    page_title="Rugby Dominance Dashboard",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load data
df = pd.read_csv("team_stats.csv", index_col=0)
year_df = pd.read_csv("team_year_stats.csv")


# Title and intro
st.title("🏉 Rugby Dominance Dashboard")
st.write("""
Explore international rugby dominance using win percentages, scoring margins,
defensive strength, and Rugby World Cup titles.
""")

# Sidebar controls
team = st.sidebar.selectbox("Select a team:", df.index)

# ----- TABS -----
tab_team, tab_rankings, tab_trends, tab_worldcups, tab_about = st.tabs(
    ["Team View", "Rankings", "Trends", "World Cups", "About"]
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
# TAB 3 — TRENDS
# =========================
with tab_trends:
    st.subheader("Performance Trends Over Time")

    # Team selector
    available_teams = sorted(year_df["team"].unique())
    selected_teams = st.multiselect(
        "Compare teams:",
        options=available_teams,
        default=["New Zealand", "South Africa"]
    )

    # Metric selector
    metric_choice = st.radio(
        "Choose a metric to visualize:",
        ["Seasonal Point Margin", "Seasonal Win Percentage"]
    )

    # Year slider
    min_year = int(year_df["year"].min())
    max_year = int(year_df["year"].max())
    year_range = st.slider(
        "Year range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
    )

    if not selected_teams:
        st.info("Select at least one team to see trends.")
    else:
        # Filter for teams & year
        subset = year_df[
            (year_df["team"].isin(selected_teams)) &
            (year_df["year"] >= year_range[0]) &
            (year_df["year"] <= year_range[1])
        ].copy().sort_values(["team", "year"])

        # Choose which metric to plot
        fig, ax = plt.subplots()

        if metric_choice == "Seasonal Point Margin":
            for t in selected_teams:
                team_data = subset[subset["team"] == t]
                ax.plot(
                    team_data["year"],
                    team_data["margin_per_match_year"],
                    label=t
                )
            ax.set_ylabel("Margin per Match (Season)")

        else:  # Win %
            for t in selected_teams:
                team_data = subset[subset["team"] == t]
                ax.plot(
                    team_data["year"],
                    team_data["win_pct_year"],
                    label=t
                )
            ax.set_ylabel("Win Percentage (%)")

        ax.axhline(0, linestyle="--", linewidth=1)
        ax.set_title(f"{metric_choice} Over Time")
        ax.set_xlabel("Year")
        ax.legend()
        st.pyplot(fig)

        st.markdown(
            """
This chart shows how teams have performed year-by-year.
Choose between point margin or win percentage to explore dominance trends.
"""
        )
        
with tab_worldcups:
    st.subheader("Rugby World Cup Timeline (1987–2023)")

    st.write("A clean timeline showing each Rugby World Cup winner:")

    # Assign colors to teams
    team_colors = {
        "New Zealand": "#000000",   # black
        "South Africa": "#006400",  # green
        "Australia": "#ffcc00",     # gold
        "England": "#cc0000",       # red
    }

    fig, ax = plt.subplots(figsize=(10, 4))

    # Plot one point per tournament
    ax.scatter(
        wcs["year"],
        [1] * len(wcs),                  # all points on a flat horizontal line
        s=300,
        color=[team_colors[t] for t in wcs["winner"]],
    )

    # Add text labels above each dot
    for i, row in wcs.iterrows():
        ax.text(
            row["year"],
            1.05,
            row["winner"],
            ha='center',
            va='bottom',
            fontsize=9,
            color=team_colors[row["winner"]],
            fontweight="bold"
        )

    ax.set_yticks([])  # remove the y-axis
    ax.set_xlabel("Year")
    ax.set_title("World Cup Winners by Year")
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    st.pyplot(fig)

    st.markdown("---")

    st.subheader("Total World Cup Titles")

    titles = wcs["winner"].value_counts()

    fig2, ax2 = plt.subplots()
    ax2.bar(
        titles.index,
        titles.values,
        color=[team_colors[t] for t in titles.index]
    )
    ax2.set_xlabel("Team")
    ax2.set_ylabel("Titles")
    ax2.set_title("Total Rugby World Cup Titles (1987–2023)")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    st.markdown("---")

    st.subheader("World Cup Winners Table")
    st.dataframe(wcs)


# =========================
# TAB 5 — ABOUT
# =========================
with tab_about:
    st.subheader("About This Project")
    st.write("""
This dashboard summarizes international rugby performance across multiple metrics,
including win percentage, scoring margin, defensive strength, and championship success.
It is part of a portfolio demonstrating data analysis and web app deployment using Python and Streamlit.
""")





