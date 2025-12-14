import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Rugby Performance Analytics Dashboard",
    layout="wide"
)

# ---------------------------------------------------------
# Base team list (Tier 1 + Tier 2)
# ---------------------------------------------------------
BASE_TEAMS = [
    # Tier 1
    "New Zealand", "South Africa", "England", "Wales",
    "Ireland", "France", "Australia",
    # Tier 2
    "Argentina", "Fiji", "Samoa", "Tonga", "Japan",
    "Georgia", "Italy", "USA", "Canada",
]

# ---------------------------------------------------------
# Data loading & preparation
# ---------------------------------------------------------
@st.cache_data
def load_match_data() -> pd.DataFrame:
    """
    Load international rugby match data, prefer a Kaggle-style dataset,
    and fall back to any local CSV or a tiny demo dataset if needed.

    Expected Kaggle-style columns:
    - date, home_team, away_team, home_score, away_score, tournament, ...

    We:
    - Filter to matches from 1987 onwards
    - Keep only matches where either team is in BASE_TEAMS
    - Expand each match into two rows (one per team perspective)
    """
    possible_paths = [
        "data/rugby_matches.csv",
        "data/international_rugby_union_results.csv",
        "data/results.csv",
    ]

    df_raw = None
    used_path = None

    for p in possible_paths:
        try:
            df_raw = pd.read_csv(p)
            used_path = p
            break
        except Exception:
            continue

    if df_raw is None:
        # Fallback demo dataset so the app always runs
        data = [
            {"date": "2015-10-31", "home_team": "New Zealand", "away_team": "Australia",
             "home_score": 34, "away_score": 17, "tournament": "Rugby World Cup",
             "city": "London", "country": "England", "neutral": True},
            {"date": "2019-11-02", "home_team": "South Africa", "away_team": "England",
             "home_score": 32, "away_score": 12, "tournament": "Rugby World Cup",
             "city": "Yokohama", "country": "Japan", "neutral": True},
            {"date": "2023-10-28", "home_team": "South Africa", "away_team": "New Zealand",
             "home_score": 12, "away_score": 11, "tournament": "Rugby World Cup",
             "city": "Paris", "country": "France", "neutral": True},
            {"date": "2022-07-09", "home_team": "New Zealand", "away_team": "Ireland",
             "home_score": 12, "away_score": 23, "tournament": "Test Series",
             "city": "Dunedin", "country": "New Zealand", "neutral": False},
            {"date": "2022-07-16", "home_team": "New Zealand", "away_team": "Ireland",
             "home_score": 22, "away_score": 32, "tournament": "Test Series",
             "city": "Wellington", "country": "New Zealand", "neutral": False},
        ]
        df_raw = pd.DataFrame(data)
        used_path = "demo_fallback"

    # If it looks like the Kaggle-style dataset
    if "home_team" in df_raw.columns and "away_team" in df_raw.columns:
        # Parse date
        df_raw["date"] = pd.to_datetime(df_raw["date"], errors="coerce")
        df_raw = df_raw.dropna(subset=["date"])
        df_raw["year"] = df_raw["date"].dt.year

        # Filter to 1987+ (modern World Cup era)
        df_raw = df_raw[df_raw["year"] >= 1987].copy()

        # Filter to Tier 1 + Tier 2
        mask = df_raw["home_team"].isin(BASE_TEAMS) | df_raw["away_team"].isin(BASE_TEAMS)
        df_filtered = df_raw[mask].copy()

        # Build team-perspective rows (two per match)
        home_df = df_filtered.rename(
            columns={
                "home_team": "team",
                "away_team": "opponent",
                "home_score": "team_score",
                "away_score": "opponent_score",
            }
        )
        away_df = df_filtered.rename(
            columns={
                "away_team": "team",
                "home_team": "opponent",
                "away_score": "team_score",
                "home_score": "opponent_score",
            }
        )
        # Keep date/year/tournament/venue-ish info
        keep_cols = [
            "date", "year", "team", "opponent", "team_score", "opponent_score",
            "tournament", "city", "country", "neutral"
        ]
        for col in keep_cols:
            if col not in home_df.columns:
                home_df[col] = np.nan
            if col not in away_df.columns:
                away_df[col] = np.nan

        df = pd.concat([home_df[keep_cols], away_df[keep_cols]], ignore_index=True)

    else:
        # Legacy-style dataset: try to adapt to the same schema
        df = df_raw.copy()
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])
            df["year"] = df["date"].dt.year
        elif "year" not in df.columns:
            df["year"] = pd.to_numeric(df.get("year", pd.Series([])), errors="coerce")

        # Ensure required columns exist
        for col in ["team", "opponent", "team_score", "opponent_score"]:
            if col not in df.columns:
                df[col] = np.nan

        # Filter to 1987+ if year exists
        if "year" in df.columns:
            df = df[df["year"] >= 1987].copy()

    # Result + margin
    if "team_score" in df.columns and "opponent_score" in df.columns:
        df["margin"] = df["team_score"] - df["opponent_score"]
        conditions = [
            df["team_score"] > df["opponent_score"],
            df["team_score"] < df["opponent_score"],
            df["team_score"] == df["opponent_score"],
        ]
        choices = ["Win", "Loss", "Draw"]
        df["result"] = np.select(conditions, choices, default="Unknown")

    # Stringify some columns if present
    for col in ["tournament", "city", "country", "team", "opponent"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    return df


df = load_match_data()

# Teams that actually appear in the data
teams_in_data = sorted(pd.unique(df[["team", "opponent"]].values.ravel()))

# Union of configured teams + those found in the dataset
teams = sorted(set(BASE_TEAMS) | set(teams_in_data))


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def team_summary(df_team: pd.DataFrame) -> dict:
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
    mask = (
        ((df_all["team"] == team_a) & (df_all["opponent"] == team_b)) |
        ((df_all["team"] == team_b) & (df_all["opponent"] == team_a))
    )
    return df_all[mask].copy()


def aggregate_rankings(df_all: pd.DataFrame) -> pd.DataFrame:
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

st.caption(
    "This dashboard uses real international rugby results. The selectors list all Tier 1 + Tier 2 nations, "
    "even if your current dataset only has matches for some of them. "
    "Teams with no rows in the data will show a 'No data available' message."
)

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
            st.warning(
                f"No data available for **{selected_team}** in the current dataset. "
                "Add matches for this team to your CSV to populate this view."
            )
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

            # Win % by year
            yearly = (
                team_df.groupby("year", as_index=False)
                .agg(
                    matches=("result", "count"),
                    wins=("result", lambda x: (x == "Win").sum())
                )
            )
            yearly["win_pct"] = yearly["wins"] / yearly["matches"] * 100

            st.markdown("**Win % by Year**")
            st.line_chart(yearly, x="year", y="win_pct")

            # Margin by match
            if "margin" in team_df.columns:
                st.markdown("**Score Margin by Match**")
                margin_df = team_df.sort_values("date" if "date" in team_df.columns else "year")
                x_col = "date" if "date" in margin_df.columns else "year"
                st.bar_chart(margin_df, x=x_col, y="margin")

# ---------------------------------------------------------
# TAB: Rankings
# ---------------------------------------------------------
with tab_rankings:
    st.header("Global Rankings (Simple Performance Model)")

    rankings_df = aggregate_rankings(df)

    if rankings_df.empty:
        st.info("Rankings require results and margin data.")
    else:
        rankings_display = rankings_df.rename(
            columns={
                "rank": "Rank",
                "team": "Team",
                "matches": "Matches",
                "wins": "Wins",
                "losses": "Losses",
                "draws": "Draws",
                "win_pct": "Win %",
                "avg_margin": "Avg Margin",
            }
        )

        st.markdown(
            "Teams are ranked by **Win %**, then **Average Score Margin**, "
            "then **Matches Played**."
        )

        styled_rankings = rankings_display.style.format(
            {"Win %": "{:.1f}", "Avg Margin": "{:.2f}"}
        ).set_properties(**{"text-align": "left"}).set_table_styles(
            [dict(selector="th", props=[("text-align", "left")])]
        )

        st.dataframe(
            styled_rankings,
            use_container_width=True,
            hide_index=True
        )

        # Static Top N bar chart using matplotlib (no zoom/scroll)
        top_n = min(10, len(rankings_display))
        top_df = rankings_display.head(top_n)

        st.subheader(f"Top {top_n} Teams by Win %")

        fig, ax = plt.subplots()
        ax.bar(top_df["Team"], top_df["Win %"])
        ax.set_xlabel("Team")
        ax.set_ylabel("Win %")
        ax.set_title(f"Top {top_n} Teams by Win %")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

# ---------------------------------------------------------
# TAB: Trends
# ---------------------------------------------------------
with tab_trends:
    st.header("Performance Trends")

    trend_team = st.selectbox("Select a team for trend analysis", teams, key="trend_team")
    trend_df = df[df["team"] == trend_team].copy()

    if trend_df.empty:
        st.warning(
            f"No match data found for **{trend_team}**. "
            "Add rows for this team to your dataset to see trend charts here."
        )
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Average Margin by Year")
            by_year = trend_df.groupby("year", as_index=False).agg(avg_margin=("margin", "mean"))
            st.line_chart(by_year, x="year", y="avg_margin")

        with col2:
            st.subheader("Win Rate vs Opponents")
            vs_opp = trend_df.groupby("opponent", as_index=False).agg(
                matches=("result", "count"),
                wins=("result", lambda x: (x == "Win").sum())
            )
            vs_opp["win_pct"] = vs_opp["wins"] / vs_opp["matches"] * 100
            vs_opp = vs_opp.sort_values("matches", ascending=False).head(12)
            st.bar_chart(vs_opp, x="opponent", y="win_pct")

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
        h2h_df = head_to_head(df, team_a, team_b)

        st.subheader("Head-to-Head Metrics")

        a_has_data = not df[df["team"] == team_a].empty
        b_has_data = not df[df["team"] == team_b].empty

        if not a_has_data or not b_has_data:
            st.warning(
                "One or both selected teams have no data in the current dataset. "
                "Add match rows for both teams to see a full comparison."
            )
        elif h2h_df.empty:
            st.info("These teams have no recorded head-to-head matches in the dataset.")
        else:
            a_as_team = h2h_df[h2h_df["team"] == team_a]
            a_as_opp = h2h_df[h2h_df["opponent"] == team_a]

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

            metrics_styled = metrics_table.style.set_properties(
                **{"text-align": "left"}
            ).set_table_styles(
                [dict(selector="th", props=[("text-align", "left")])]
            )

            st.dataframe(
                metrics_styled,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("Score Margin by Match (Team A Perspective)")
            a_norm_sorted = a_norm.sort_values("date" if "date" in a_norm.columns else "year")
            x_col = "date" if "date" in a_norm_sorted.columns else "year"
            st.bar_chart(a_norm_sorted, x=x_col, y="margin")

# ---------------------------------------------------------
# TAB: World Cups
# ---------------------------------------------------------
with tab_wc:
    st.header("Rugby World Cup History")

    wc_display = wc_df.copy()
    wc_display["Year"] = wc_display["year"].astype(str)
    wc_display = wc_display.rename(
        columns={
            "host": "Host",
            "winner": "Winner",
            "runner_up": "Runner-up",
        }
    )[["Year", "Host", "Winner", "Runner-up"]]

    wc_styled = wc_display.style.set_properties(
        **{"text-align": "left"}
    ).set_table_styles(
        [dict(selector="th", props=[("text-align", "left")])]
    )

    st.dataframe(
        wc_styled,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("World Cup Titles by Nation")

    nations = sorted(set(wc_df["winner"]) | set(wc_df["runner_up"]))
    title_counts = []
    for nation in nations:
        titles = (wc_df["winner"] == nation).sum()
        title_counts.append({"Nations": nation, "Titles": titles})

    titles_df = pd.DataFrame(title_counts).sort_values(
        by=["Titles", "Nations"], ascending=[False, True]
    )

    fig, ax = plt.subplots()
    ax.bar(titles_df["Nations"], titles_df["Titles"])
    ax.set_xlabel("Nation")
    ax.set_ylabel("Titles")
    ax.set_title("Rugby World Cup Titles by Nation")
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)

# ---------------------------------------------------------
# TAB: About
# ---------------------------------------------------------
with tab_about:
    st.header("About This Dashboard")
    st.markdown(
        """
        This dashboard is a **Rugby Performance Analytics** playground powered by real
        international match data.

        **Tabs overview**

        - **Team View** – One team at a time: Win %, score margins, and match-level performance.
        - **Rankings** – Simple global ranking table built from Wins, Losses, and Average Margin.
        - **Trends** – How performance evolves over time and against key opponents.
        - **Compare** – Side-by-side head-to-head comparison between any two teams.
        - **World Cups** – Quick reference of Rugby World Cup winners since 1987.

        To plug in your own data, drop a CSV into the `data/` folder with at least:
        `date`, `home_team`, `away_team`, `home_score`, `away_score`, and `tournament`.
        """
    )
