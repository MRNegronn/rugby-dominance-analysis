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
        "date","year","team","opponent",
        "team_score","opponent_score",
        "margin","result","tournament",
        "elo_pre","elo_post","elo_delta"
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


df_filtered = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

if selected_tournaments:
    df_filtered = df_filtered[df_filtered["tournament"].isin(selected_tournaments)]

teams = sorted(df["team"].unique())

# =========================================================
# Tabs
# =========================================================
tab_team, tab_rankings, tab_elo = st.tabs(
    ["Team View", "Rankings", "Elo"]
)

# =========================================================
# Elo Tab
# =========================================================
with tab_elo:
    st.header("Elo Ratings")

    st.markdown(
        """
Elo shows **relative team strength over time**.
Beating strong teams matters more than beating weak ones.
This version is explanatory only — not predictive.
"""
    )

    # Leaderboard
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
    elo_leader["peak_elo"] = elo_leader["peak_elo"].round(1)

    st.subheader("Elo Leaderboard")
    st.dataframe(
        elo_leader[["rank","team","current_elo","peak_elo","matches"]],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # Timeline (full history, not filtered)
    team = st.selectbox("Select team", teams)

    tdf = df[df["team"] == team].sort_values("date")

    st.subheader(f"{team} — Elo Over Time")
    fig, ax = plt.subplots()
    ax.plot(tdf["date"], tdf["elo_post"])
    ax.set_ylabel("Elo")
    ax.set_xlabel("Year")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)

    st.subheader("Recent Elo Changes")
    recent = tdf.sort_values("date", ascending=False).head(10)
    recent["date"] = recent["date"].dt.strftime("%Y-%m-%d")
    st.table(
        recent[["date","opponent","result","elo_delta","elo_post"]]
    )

