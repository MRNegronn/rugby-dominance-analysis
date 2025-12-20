import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# Page config
# =========================================================
st.set_page_config(
    page_title="Rugby Performance Analytics Dashboard",
    layout="wide",
)

st.title("Rugby Performance Analytics Dashboard")

MIN_YEAR = 1987

# =========================================================
# Data Loading
# =========================================================
@st.cache_data
def load_data(path="data/rugby_matches_with_elo.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    required = {
        "date", "year", "team", "opponent",
        "team_score", "opponent_score",
        "margin", "result", "tournament",
        "dominance_score",
        "elo_pre", "elo_post", "elo_delta",
    }

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    return df[df["year"] >= MIN_YEAR].copy()

df = load_data()

# =========================================================
# Sidebar Filters
# =========================================================
with st.sidebar:
    st.header("Filters")

    year_range = st.slider(
        "Year range",
        int(df["year"].min()),
        int(df["year"].max()),
        (int(df["year"].min()), int(df["year"].max())),
    )

    tournaments = sorted(
        df["tournament"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_tournaments = st.multiselect(
        "Tournaments",
        tournaments,
        default=[]
    )

df_filtered = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
].copy()

if selected_tournaments:
    df_filtered = df_filtered[
        df_filtered["tournament"].astype(str).isin(selected_tournaments)
    ]

teams = sorted(df["team"].dropna().unique())

# =========================================================
# Shared Aggregations
# =========================================================
dominance_by_team = (
    df_filtered
    .groupby("team", as_index=False)
    .agg(
        dominance=("dominance_score", "sum"),
        matches=("dominance_score", "count"),
        avg_margin=("margin", "mean"),
    )
    .sort_values("dominance", ascending=False)
)

# =========================================================
# Tabs
# =========================================================
tab_team, tab_rankings, tab_elo, tab_trends, tab_compare, tab_wc, tab_about = st.tabs(
    ["Team View", "Rankings", "Elo", "Trends", "Compare", "World Cups", "About"]
)

# =========================================================
# Team View
# =========================================================
with tab_team:
    st.header("Team Performance Overview")

    team = st.selectbox("Select team", teams, key="team_view")

    tdf = df_filtered[df_filtered["team"] == team]

    col1, col2, col3 = st.columns(3)

    col1.metric("Matches", len(tdf))
    col2.metric("Total Dominance", int(tdf["dominance_score"].sum()))
    col3.metric("Avg Margin", round(tdf["margin"].mean(), 2))

    st.subheader("Recent Matches")
    st.dataframe(
        tdf.sort_values("date", ascending=False).head(10),
        use_container_width=True,
        hide_index=True,
    )

# =========================================================
# Rankings
# =========================================================
with tab_rankings:
    st.header("Dominance Rankings")

    rankings = dominance_by_team.reset_index(drop=True)
    rankings["rank"] = rankings.index + 1

    st.dataframe(
        rankings[["rank", "team", "dominance", "matches", "avg_margin"]],
        use_container_width=True,
        hide_index=True,
    )

# =========================================================
# Elo
# =========================================================
with tab_elo:
    st.header("Elo Ratings")

    elo_leader = (
        df_filtered.sort_values("date")
        .groupby("team", as_index=False)
        .agg(
            current_elo=("elo_post", "last"),
            peak_elo=("elo_post", "max"),
            matches=("elo_post", "count"),
        )
        .sort_values("current_elo", ascending=False)
        .reset_index(drop=True)
    )

    elo_leader["rank"] = elo_leader.index + 1
    elo_leader["current_elo"] = elo_leader["current_elo"].round(1)

    st.subheader("Elo Leaderboard")
    st.dataframe(
        elo_leader[["rank", "team", "current_elo", "peak_elo", "matches"]],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    team = st.selectbox("Select team", teams, key="elo_team")

    tdf = df[df["team"] == team].sort_values("date")

    fig, ax = plt.subplots()
    ax.plot(tdf["date"], tdf["elo_post"])
    ax.set_title(f"{team} Elo Over Time")
    ax.set_ylabel("Elo")
    ax.set_xlabel("Year")
    st.pyplot(fig, use_container_width=True)

# =========================================================
# Trends
# =========================================================
with tab_trends:
    st.header("Dominance Over Time")

    trend_df = (
        df_filtered
        .groupby(["year", "team"], as_index=False)
        .agg(dominance=("dominance_score", "sum"))
    )

    team = st.selectbox("Select team", teams, key="trend_team")

    tdf = trend_df[trend_df["team"] == team]

    fig, ax = plt.subplots()
    ax.plot(tdf["year"], tdf["dominance"])
    ax.set_title(f"{team} — Annual Dominance")
    ax.set_ylabel("Dominance")
    ax.set_xlabel("Year")
    st.pyplot(fig, use_container_width=True)

# =========================================================
# Compare
# =========================================================
with tab_compare:
    st.header("Team Comparison")

    team_a, team_b = st.multiselect(
        "Select two teams",
        teams,
        default=teams[:2],
        max_selections=2,
    )

    if len(team_a := [team_a, team_b]) == 2:
        comp = dominance_by_team[
            dominance_by_team["team"].isin([team_a[0], team_a[1]])
        ]
        st.dataframe(comp, use_container_width=True, hide_index=True)

# =========================================================
# World Cups
# =========================================================
with tab_wc:
    st.header("World Cups")

    st.markdown(
        """
This tab will later include:
- World Cup–only dominance
- Tournament-weighted Elo
- Era comparisons
"""
    )

# =========================================================
# About
# =========================================================
with tab_about:
    st.header("About This Project")

    st.markdown(
        """
**Rugby Performance Analytics Dashboard**

- Match-level dataset (1987+)
- Dominance Index v1
- Elo ratings (explanatory)
- Tier 1 & 2 nations

Built for clarity, not prediction.
"""
    )
