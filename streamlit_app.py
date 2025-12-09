import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Rugby Performance Analytics Dashboard",
    layout="wide"
)

# ---------------------------------------------------------
# Data loading & preparation
# ---------------------------------------------------------
@st.cache_data
def load_match_data(path: str = "data/rugby_matches.csv") -> pd.DataFrame:
    """
    Try to load a matches CSV.
    If not found, fall back to a small demo dataset so the app still runs.
    Expected columns if using your own data:
      - date (or year)
      - team
      - opponent
      - team_score
      - opponent_score
      - tournament
      - venue
    """
    try:
        df = pd.read_csv(path)
    except Exception:
        # Fallback demo dataset
        data = [
            {"date": "2015-10-31", "team": "New Zealand", "opponent": "Australia",
             "team_score": 34, "opponent_score": 17, "tournament": "Rugby World Cup",
             "venue": "Twickenham"},
            {"date": "2019-11-02", "team": "South Africa", "opponent": "England",
             "team_score": 32, "opponent_score": 12, "tournament": "Rugby World Cup",
             "venue": "Yokohama"},
            {"date": "2023-10-28", "team": "South Africa", "opponent": "New Zealand",
             "team_score": 12, "opponent_score": 11, "tournament": "Rugby World Cup",
             "venue": "Paris"},
            {"date": "2022-07-09", "team": "Ireland", "opponent": "New Zealand",
             "team_score": 23, "opponent_score": 12, "tournament": "Test Series",
             "venue": "Dunedin"},
            {"date": "2022-07-16", "team": "Ireland", "opponent": "New Zealand",
             "team_score": 32, "opponent_score": 22, "tournament": "Test Series",
             "venue": "Wellington"},
        ]
        df = pd.DataFrame(data)

    # Basic derived columns
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["year"] = df["date"].dt.year
    elif "year" not in df.columns:
        # If the user only has a year column, that's fine
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    if "team_score" in df.columns and "opponent_score" in df.columns:
        df["margin"] = df["team_score"] - df["opponent_score"]
        conditions = [
            df["team_score"] > df["opponent_score"],
            df["team_score"] < df["opponent_score"],
            df["team_score"] == df["opponent_score"]
        ]
        choices = ["Win", "Loss", "Draw"]
        df["result"] = np.select(conditions, choices, default="Unknown")

    # Normalize some expected columns
    for col in ["tournament", "venue", "team", "opponent"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    return df


df = load_match_data()

# Precomputed list of teams for selectors
teams = sorted(pd.unique(df[["team", "opponent"]].values.ravel()))


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def team_summary(df_team: pd.DataFrame) -> dict:
    """Compute core metrics for one team."""
    total_matches = len(df_team)
    wins = (df_team["result"] == "Win").sum()
    losses = (df_team["result"] == "Loss").sum()
    draws = (df_team["result"] == "Draw").sum()

    win_pct = wins / total_matches * 100 if total_matches > 0 else 0.0
    avg_margin = df_team["margin"].mean() if "margin" in df_team.columns else 0.0
    avg_points_for = df_team["team_score"].mean() if "team_score" in df_team.columns else 0.0
    avg_points_against = df_team["opponent_score"].mean() if "opponent_score" in df_team.columns else 0.0

    return {
        "matches": total_matches,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_pct": win_pct,
        "avg_margin": avg_margin,
        "avg_for": avg_points_for,
        "avg_against": avg_points_against,
    }


def head_to_head(df_all: pd.DataFrame, team_a: str, team_b: str) -> pd.DataFrame:
    """Filter matches where team_a plays team_b (either home or away)."""
    mask = (
        ((df_all["team"] == team_a) & (df_all["opponent"] == team_b)) |
        ((df_all["team"] == team_b) & (df_all["opponent"] == team_a))
    )
    return df_all[mask].copy()


def aggregate_rankings(df_all: pd.DataFrame) -> pd.DataFrame:
    """Create a simple ranking table by win percentage & average margin."""
    if "result" not in df_all.columns:
        return pd.DataFrame()

    grouped = df_all.groupby("team", as_index=False).agg(
        matches=("result", "count"),
        wins=("result", lambda x: (x == "Win").sum()),
        losses=("result", lambda x: (x == "Loss").sum()),
        draws=("result", lambda x: (x == "Draw").sum()),
        avg_margin=("margin", "mean"),
    )
    grouped["win_pct"] = grouped["wins"] / grouped["matches"] * 100
    ranked = grouped.sort_values(
        by=["win_pct", "avg_margin", "matches"],
        ascending=[False, False, False]
    ).reset_index(drop=True)
    ranked["rank"] = ranked.index + 1
    cols = ["rank", "team", "matches", "wins", "losses", "draws", "win_pct", "avg_margin"]
    return ranked[cols]


# Static World Cup history for the World Cups tab
WORLD_CUPS = [
    {"year": 1987, "host": "New Zealand & Australia", "winner": "New Zealand", "runner_up": "France"},
    {"year": 1991, "host": "UK, France & Ireland", "winner": "Australia", "runner_up": "England"},
    {"year": 1995, "host": "South Africa", "winner": "South Africa", "runner_up": "New Zealand"},
    {"year": 1999, "host": "Wales", "winner": "Australia", "runner_up": "France"},
    {"year": 2003, "host": "Australia", "winner": "England", "runner_up": "Australia"},
    {"year": 2007, "host": "France", "winner": "South Africa", "runner_up": "England"},
    {"year": 2011, "host": "New Zealand", "winner": "New Zealand", "runner_up": "France"},
    {"year": 2015, "host": "England", "winner": "New Zealand", "runner_up": "Australia"},
    {"year": 2019, "host": "Japan", "winner": "South Africa", "runner_up": "England"},
    {"year": 2023, "host": "France", "winner": "South Africa", "runner_up": "New Zealand"},
]
wc_df = pd.DataFrame(WORLD_CUPS)

# ---------------------------------------------------------
# Layout – main title and tabs
# ---------------------------------------------------------
st.title("Rugby Performance Analytics Dashboard")

tab_team, tab_rankings, tab_trends, tab_compare, tab_wc, tab_about = st.tabs(
    ["Team View", "Rankings", "Trends", "Compare", "World Cups", "About"]
)

# ---------------------------------------------------------
# TAB: Team View
# ---------------------------------------------------------
with tab_team:
    st.header("Team View")

    col1, col2 = st.columns([2, 3])

    with col1:
        selected_team = st.selectbox("Select a team", teams, key="team_view_team")
        team_df = df[df["team"] == selected_team].copy()

        if team_df.empty:
            st.warning("No data found for this team.")
        else:
            summary = team_summary(team_df)

            st.subheader(f"{selected_team} – Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Matches", summary["matches"])
            c2.metric("Win %", f"{summary['win_pct']:.1f}%")
            c3.metric("Avg Margin", f"{summary['avg_margin']:.2f}")

            c4, c5, c6 = st.columns(3)
            c4.metric("Avg Points For", f"{summary['avg_for']:.1f}")
            c5.metric("Avg Points Against", f"{summary['avg_against']:.1f}")
            c6.metric("Draws", summary["draws"])

    with col2:
        if not team_df.empty:
            st.subheader("Results Over Time")

            # Win rate per year
            yearly = (
                team_df.groupby("year", as_index=False)
                .agg(
                    matches=("result", "count"),
                    wins=("result", lambda x: (x == "Win").sum())
                )
            )
            yearly["win_pct"] = yearly["wins"] / yearly["matches"] * 100

            fig_win = px.line(
                yearly,
                x="year",
                y="win_pct",
                markers=True,
                title=f"{selected_team} Win % by Year",
            )
            fig_win.update_layout(
                xaxis_title="Year",
                yaxis_title="Win Percentage",
            )
            st.plotly_chart(fig_win, use_container_width=True)

            if "margin" in team_df.columns:
                fig_margin = px.bar(
                    team_df.sort_values("date"),
                    x="date" if "date" in team_df.columns else "year",
                    y="margin",
                    title=f"{selected_team} Score Margin by Match",
                )
                fig_margin.update_layout(
                    xaxis_title="Match Date" if "date" in team_df.columns else "Year",
                    yaxis_title="Score Margin (Team - Opponent)",
                )
                st.plotly_chart(fig_margin, use_container_width=True)

# ---------------------------------------------------------
# TAB: Rankings
# ---------------------------------------------------------
with tab_rankings:
    st.header("Global Rankings (Simple Performance Model)")

    rankings_df = aggregate_rankings(df)

    if rankings_df.empty:
        st.info("Rankings require results and margin data.")
    else:
        st.markdown("Teams are ranked by **win percentage**, then **average score margin**, then **matches played**.")

        st.dataframe(
            rankings_df.style.format(
                {"win_pct": "{:.1f}", "avg_margin": "{:.2f}"}
            ),
            use_container_width=True,
            hide_index=True
        )

        fig_rank = px.bar(
            rankings_df.head(10),
            x="team",
            y="win_pct",
            title="Top 10 Teams by Win Percentage",
        )
        fig_rank.update_layout(
            xaxis_title="Team",
            yaxis_title="Win Percentage",
        )
        st.plotly_chart(fig_rank, use_container_width=True)

# ---------------------------------------------------------
# TAB: Trends
# ---------------------------------------------------------
with tab_trends:
    st.header("Performance Trends")

    trend_team = st.selectbox("Select a team for trend analysis", teams, key="trend_team")
    trend_df = df[df["team"] == trend_team].copy()

    if trend_df.empty:
        st.warning("No data for this team.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Average Margin by Year")
            by_year = trend_df.groupby("year", as_index=False).agg(avg_margin=("margin", "mean"))
            fig_trend_margin = px.line(
                by_year,
                x="year",
                y="avg_margin",
                markers=True,
                title=f"{trend_team} – Avg Score Margin by Year",
            )
            fig_trend_margin.update_layout(
                xaxis_title="Year",
                yaxis_title="Average Score Margin",
            )
            st.plotly_chart(fig_trend_margin, use_container_width=True)

        with col2:
            st.subheader("Win Rate vs Opponents")
            vs_opp = trend_df.groupby("opponent", as_index=False).agg(
                matches=("result", "count"),
                wins=("result", lambda x: (x == "Win").sum())
            )
            vs_opp["win_pct"] = vs_opp["wins"] / vs_opp["matches"] * 100
            vs_opp = vs_opp.sort_values("matches", ascending=False).head(12)

            fig_opp = px.bar(
                vs_opp,
                x="opponent",
                y="win_pct",
                title=f"{trend_team} – Win % vs Top Opponents",
            )
            fig_opp.update_layout(
                xaxis_title="Opponent",
                yaxis_title="Win Percentage",
            )
            st.plotly_chart(fig_opp, use_container_width=True)

# ---------------------------------------------------------
# TAB: Compare
# ---------------------------------------------------------
with tab_compare:
    st.header("Team Comparison")

    col_a, col_b = st.columns(2)
    with col_a:
        team_a = st.selectbox("Team A", teams, key="compare_team_a")
    with col_b:
        team_b = st.selectbox("Team B", teams, key="compare_team_b")

    if team_a == team_b:
        st.warning("Select two different teams to compare.")
    else:
        # Head-to-head data
        h2h_df = head_to_head(df, team_a, team_b)

        st.subheader("Head-to-Head Metrics")

        if h2h_df.empty:
            st.info("These teams have no recorded matches in the dataset.")
        else:
            # From perspective of Team A
            a_as_team = h2h_df[h2h_df["team"] == team_a]
            a_as_opp = h2h_df[h2h_df["opponent"] == team_a]

            # Normalize so that A is always the "team" column
            a_norm = pd.concat(
                [
                    a_as_team,
                    a_as_opp.rename(
                        columns={
                            "team": "opponent",
                            "opponent": "team",
                            "team_score": "opponent_score",
                            "opponent_score": "team_score",
                        }
                    )
                ],
                ignore_index=True
            )

            a_summary = team_summary(a_norm)
            b_summary = team_summary(
                pd.concat(
                    [
                        h2h_df[h2h_df["team"] == team_b],
                        h2h_df[h2h_df["opponent"] == team_b].rename(
                            columns={
                                "team": "opponent",
                                "opponent": "team",
                                "team_score": "opponent_score",
                                "opponent_score": "team_score",
                            }
                        )
                    ],
                    ignore_index=True
                )
            )

            metrics_table = pd.DataFrame(
                {
                    "Metric": [
                        "Matches Played",
                        "Wins",
                        "Losses",
                        "Draws",
                        "Win %",
                        "Avg Margin",
                        "Avg Points For",
                        "Avg Points Against",
                    ],
                    team_a: [
                        a_summary["matches"],
                        a_summary["wins"],
                        a_summary["losses"],
                        a_summary["draws"],
                        f"{a_summary['win_pct']:.1f}%",
                        f"{a_summary['avg_margin']:.2f}",
                        f"{a_summary['avg_for']:.1f}",
                        f"{a_summary['avg_against']:.1f}",
                    ],
                    team_b: [
                        b_summary["matches"],
                        b_summary["wins"],
                        b_summary["losses"],
                        b_summary["draws"],
                        f"{b_summary['win_pct']:.1f}%",
                        f"{b_summary['avg_margin']:.2f}",
                        f"{b_summary['avg_for']:.1f}",
                        f"{b_summary['avg_against']:.1f}",
                    ],
                }
            )

            st.dataframe(
                metrics_table,
                use_container_width=True,
                hide_index=True,
            )

            # Simple labeled chart – margin by match
            st.subheader("Score Margin by Match (Team A Perspective)")

            a_norm_sorted = a_norm.sort_values("date" if "date" in a_norm.columns else "year")
            fig_h2h_margin = px.bar(
                a_norm_sorted,
                x="date" if "date" in a_norm_sorted.columns else "year",
                y="margin",
                title=f"{team_a} Score Margin vs {team_b} by Match",
            )
            fig_h2h_margin.update_layout(
                xaxis_title="Match Date" if "date" in a_norm_sorted.columns else "Year",
                yaxis_title="Score Margin (Team A - Team B)",
            )
            st.plotly_chart(fig_h2h_margin, use_container_width=True)

        # NOTE:
        # No stray st.image(), no bare 'fig' objects,
        # so the little broken-image icon should be gone.

# ---------------------------------------------------------
# TAB: World Cups
# ---------------------------------------------------------
with tab_wc:
    st.header("Rugby World Cup History")

    st.dataframe(
        wc_df,
        use_container_width=True,
        hide_index=True
    )

    fig_wc = px.bar(
        wc_df,
        x="year",
        y="winner",
        title="Rugby World Cup Winners by Year",
    )
    fig_wc.update_layout(
        xaxis_title="Year",
        yaxis_title="Winning Nation",
    )
    st.plotly_chart(fig_wc, use_container_width=True)

# ---------------------------------------------------------
# TAB: About
# ---------------------------------------------------------
with tab_about:
    st.header("About This Dashboard")
    st.markdown(
        """
        This dashboard is a **Rugby Performance Analytics** playground.

        **Tabs overview**

        - **Team View** – Dive into one team at a time, with win %, score margins,
          and match-level performance.
        - **Rankings** – Simple global ranking table built from wins, losses, and
          average margin.
        - **Trends** – How performance evolves over time and against key opponents.
        - **Compare** – Side-by-side head-to-head comparison between any two teams.
        - **World Cups** – Quick reference of Rugby World Cup winners since 1987.

        To plug in your own data, point `load_match_data()` to your CSV and make sure
        it includes at least:
        `team`, `opponent`, `team_score`, `opponent_score`, and `date` or `year`.
        """
    )

