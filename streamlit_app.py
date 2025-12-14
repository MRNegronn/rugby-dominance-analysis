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


# =========================================================
# Constants
# =========================================================
MIN_YEAR = 1987

TIER_1_2_TEAMS = [
    # Tier 1
    "New Zealand",
    "South Africa",
    "England",
    "Wales",
    "Ireland",
    "France",
    "Australia",
    # Tier 2
    "Argentina",
    "Fiji",
    "Samoa",
    "Tonga",
    "Japan",
    "Georgia",
    "Italy",
    "USA",
    "Canada",
]

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


# =========================================================
# Data Loading
# =========================================================
@st.cache_data
def load_data(path: str = "data/rugby_matches.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # Defensive cleanup
    df.columns = [c.strip().lower() for c in df.columns]

    # Required columns from build_dataset.py output
    required = {
        "date",
        "year",
        "team",
        "opponent",
        "team_score",
        "opponent_score",
        "margin",
        "result",
        "tournament",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()

    # Ensure types
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["team_score"] = pd.to_numeric(df["team_score"], errors="coerce")
    df["opponent_score"] = pd.to_numeric(df["opponent_score"], errors="coerce")
    df["margin"] = pd.to_numeric(df["margin"], errors="coerce")

    # Normalize strings
    df["team"] = df["team"].astype(str)
    df["opponent"] = df["opponent"].astype(str)
    df["tournament"] = df["tournament"].astype(str)
    df["result"] = df["result"].astype(str)

    # Keep modern era (should already be filtered, but keep it safe)
    df = df[df["year"] >= MIN_YEAR].copy()

    return df


try:
    df = load_data()
except Exception as e:
    st.error("App failed to load the dataset.")
    st.code(str(e))
    st.stop()


# =========================================================
# Helpers
# =========================================================
def team_summary(df_team: pd.DataFrame) -> dict:
    total = len(df_team)
    wins = int((df_team["result"] == "Win").sum())
    losses = int((df_team["result"] == "Loss").sum())
    draws = int((df_team["result"] == "Draw").sum())

    win_pct = (wins / total * 100) if total else 0.0
    avg_margin = float(df_team["margin"].mean()) if total else 0.0
    avg_for = float(df_team["team_score"].mean()) if total else 0.0
    avg_against = float(df_team["opponent_score"].mean()) if total else 0.0

    return {
        "matches": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_pct": win_pct,
        "avg_margin": avg_margin,
        "avg_for": avg_for,
        "avg_against": avg_against,
    }


def compute_rankings(df_all: pd.DataFrame) -> pd.DataFrame:
    grouped = df_all.groupby("team", as_index=False).agg(
        matches=("result", "count"),
        wins=("result", lambda x: int((x == "Win").sum())),
        losses=("result", lambda x: int((x == "Loss").sum())),
        draws=("result", lambda x: int((x == "Draw").sum())),
        avg_margin=("margin", "mean"),
        avg_points_for=("team_score", "mean"),
        avg_points_against=("opponent_score", "mean"),
    )
    grouped["win_pct"] = grouped["wins"] / grouped["matches"] * 100
    ranked = grouped.sort_values(
        by=["win_pct", "avg_margin", "matches"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
    return ranked


def static_bar_chart(categories, values, title, xlabel=None, ylabel=None, rotate_x=45):
    fig, ax = plt.subplots()
    ax.bar(categories, values)
    ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=rotate_x, labelsize=8)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)


def static_line_chart(x, y, title, xlabel=None, ylabel=None):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)


def static_margin_bar_by_date(df_rows: pd.DataFrame, title: str):
    # Bar chart of margin vs date (static)
    df_plot = df_rows.sort_values("date").copy()
    fig, ax = plt.subplots()
    ax.bar(df_plot["date"].dt.strftime("%Y-%m-%d"), df_plot["margin"])
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Margin")
    ax.tick_params(axis="x", rotation=90, labelsize=6)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)


# =========================================================
# Sidebar controls (global)
# =========================================================
with st.sidebar:
    st.header("Filters")
    year_min = int(df["year"].min()) if df["year"].notna().any() else MIN_YEAR
    year_max = int(df["year"].max()) if df["year"].notna().any() else MIN_YEAR

    year_range = st.slider(
        "Year range",
        min_value=year_min,
        max_value=year_max,
        value=(max(MIN_YEAR, year_min), year_max),
        step=1,
    )

    tournaments = sorted(df["tournament"].dropna().unique().tolist())
    selected_tournaments = st.multiselect(
        "Tournaments (optional)",
        options=tournaments,
        default=[],
    )

    st.caption("Tip: leave tournaments empty to include everything.")


df_filtered = df[
    (df["year"] >= year_range[0]) & (df["year"] <= year_range[1])
].copy()

if selected_tournaments:
    df_filtered = df_filtered[df_filtered["tournament"].isin(selected_tournaments)].copy()


# Build team list from filtered data (still allow Tier list ordering)
teams_in_data = sorted(set(df_filtered["team"].unique().tolist()) | set(df_filtered["opponent"].unique().tolist()))
teams_ordered = [t for t in TIER_1_2_TEAMS if t in teams_in_data] + [t for t in teams_in_data if t not in TIER_1_2_TEAMS]


# =========================================================
# Tabs
# =========================================================
tab_team, tab_rankings, tab_trends, tab_compare, tab_wc, tab_about = st.tabs(
    ["Team View", "Rankings", "Trends", "Compare", "World Cups", "About"]
)

# ---------------------------------------------------------
# Team View
# ---------------------------------------------------------
with tab_team:
    st.header("Team View")

    col1, col2 = st.columns([1, 2], vertical_alignment="top")

    with col1:
        team = st.selectbox("Select a team", options=teams_ordered, index=0)

        team_df = df_filtered[df_filtered["team"] == team].copy()

        if team_df.empty:
            st.warning("No matches found for this team with the current filters.")
        else:
            s = team_summary(team_df)

            st.subheader("Summary")
            a, b, c = st.columns(3)
            a.metric("Matches", s["matches"])
            b.metric("Win %", f"{s['win_pct']:.1f}%")
            c.metric("Avg Margin", f"{s['avg_margin']:.2f}")

            d, e, f = st.columns(3)
            d.metric("Wins", s["wins"])
            e.metric("Losses", s["losses"])
            f.metric("Draws", s["draws"])

            st.caption(f"Avg Points For: {s['avg_for']:.1f}  |  Avg Points Against: {s['avg_against']:.1f}")

    with col2:
        if not team_df.empty:
            st.subheader("Win % by Year (Static)")

            by_year = team_df.groupby("year", as_index=False).agg(
                matches=("result", "count"),
                wins=("result", lambda x: int((x == "Win").sum())),
            )
            by_year["win_pct"] = by_year["wins"] / by_year["matches"] * 100
            by_year = by_year.sort_values("year")

            static_line_chart(
                x=by_year["year"].astype(int).tolist(),
                y=by_year["win_pct"].tolist(),
                title=f"{team} – Win % by Year",
                xlabel="Year",
                ylabel="Win %",
            )

            st.subheader("Score Margin by Match (Static)")
            # limit bars to keep it readable
            recent_n = st.slider("Show last N matches", min_value=10, max_value=80, value=30, step=5, key="teamview_n")
            recent = team_df.sort_values("date").tail(recent_n)
            static_margin_bar_by_date(recent, title=f"{team} – Margin (Last {recent_n} Matches)")

            st.subheader("Recent Matches (Non-editable)")
            show_cols = ["date", "opponent", "team_score", "opponent_score", "margin", "result", "tournament"]
            table_df = team_df.sort_values("date", ascending=False)[show_cols].head(15).copy()
            table_df["date"] = table_df["date"].dt.strftime("%Y-%m-%d")
            st.table(table_df)

# ---------------------------------------------------------
# Rankings
# ---------------------------------------------------------
with tab_rankings:
    st.header("Rankings")

    rankings = compute_rankings(df_filtered)

    if rankings.empty:
        st.warning("No ranking data available with the current filters.")
    else:
        # Full table: keep it readable; static would be painful at this size
        display = rankings.copy()
        display["win_pct"] = display["win_pct"].map(lambda v: round(float(v), 1))
        display["avg_margin"] = display["avg_margin"].map(lambda v: round(float(v), 2))
        display["avg_points_for"] = display["avg_points_for"].map(lambda v: round(float(v), 1))
        display["avg_points_against"] = display["avg_points_against"].map(lambda v: round(float(v), 1))

        st.caption("Sorted by Win %, then Avg Margin, then Matches.")
        st.dataframe(
            display[["rank", "team", "matches", "wins", "losses", "draws", "win_pct", "avg_margin"]],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader("Top 3 (Non-editable)")
        top3 = display.head(3)[["rank", "team", "matches", "win_pct", "avg_margin"]].copy()
        st.table(top3)

        st.subheader("Top 10 by Win % (Static)")
        top10 = display.head(10).copy()
        static_bar_chart(
            categories=top10["team"].tolist(),
            values=top10["win_pct"].tolist(),
            title="Top 10 Teams by Win %",
            xlabel="Team",
            ylabel="Win %",
            rotate_x=45,
        )

# ---------------------------------------------------------
# Trends
# ---------------------------------------------------------
with tab_trends:
    st.header("Trends")

    team = st.selectbox("Select a team", options=teams_ordered, index=0, key="trends_team")

    tdf = df_filtered[df_filtered["team"] == team].copy()
    if tdf.empty:
        st.warning("No matches found for this team with the current filters.")
    else:
        c1, c2 = st.columns(2, vertical_alignment="top")

        with c1:
            st.subheader("Average Margin by Year (Static)")
            by_year = tdf.groupby("year", as_index=False).agg(avg_margin=("margin", "mean")).sort_values("year")
            static_line_chart(
                x=by_year["year"].astype(int).tolist(),
                y=by_year["avg_margin"].tolist(),
                title=f"{team} – Avg Margin by Year",
                xlabel="Year",
                ylabel="Avg Margin",
            )

        with c2:
            st.subheader("Win % vs Opponents (Top 12 by Matches)")
            vs = tdf.groupby("opponent", as_index=False).agg(
                matches=("result", "count"),
                wins=("result", lambda x: int((x == "Win").sum())),
            )
            vs["win_pct"] = vs["wins"] / vs["matches"] * 100
            vs = vs.sort_values("matches", ascending=False).head(12)
            vs = vs.sort_values("win_pct", ascending=False)

            # Static bar chart
            static_bar_chart(
                categories=vs["opponent"].tolist(),
                values=vs["win_pct"].tolist(),
                title=f"{team} – Win % vs Opponents (Top 12 by Matches)",
                xlabel="Opponent",
                ylabel="Win %",
                rotate_x=60,
            )

# ---------------------------------------------------------
# Compare
# ---------------------------------------------------------
with tab_compare:
    st.header("Compare")

    colA, colB = st.columns(2, vertical_alignment="top")
    with colA:
        team_a = st.selectbox("Team A", options=teams_ordered, index=0, key="compare_a")
    with colB:
        team_b = st.selectbox("Team B", options=teams_ordered, index=1 if len(teams_ordered) > 1 else 0, key="compare_b")

    if team_a == team_b:
        st.warning("Pick two different teams.")
    else:
        # Head-to-head in team-centric dataset is easy:
        h2h_a = df_filtered[(df_filtered["team"] == team_a) & (df_filtered["opponent"] == team_b)].copy()
        h2h_b = df_filtered[(df_filtered["team"] == team_b) & (df_filtered["opponent"] == team_a)].copy()

        st.subheader("Head-to-Head Summary")

        if h2h_a.empty and h2h_b.empty:
            st.info("No head-to-head matches found with current filters.")
        else:
            # Build one combined view, but keep team A perspective for consistent reading
            # If we have A rows, use those; else convert B rows into A perspective
            if not h2h_a.empty:
                a_view = h2h_a.copy()
            else:
                # Convert B rows into A perspective
                a_view = h2h_b.rename(
                    columns={
                        "team": "opponent",
                        "opponent": "team",
                        "team_score": "opponent_score",
                        "opponent_score": "team_score",
                        "margin": "margin",
                        "result": "result",
                    }
                ).copy()
                a_view["team"] = team_a
                a_view["opponent"] = team_b
                a_view["margin"] = a_view["team_score"] - a_view["opponent_score"]
                a_view["result"] = np.select(
                    [a_view["margin"] > 0, a_view["margin"] < 0, a_view["margin"] == 0],
                    ["Win", "Loss", "Draw"],
                    default="Unknown",
                )

            a_summary = team_summary(a_view)

            # Show metrics side-by-side (non-editable table)
            metrics = pd.DataFrame(
                {
                    "Metric": ["Matches", "Wins", "Losses", "Draws", "Win %", "Avg Margin", "Avg PF", "Avg PA"],
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
                }
            )
            st.table(metrics)

            st.subheader("Head-to-Head Margin by Match (Static)")
            recent_n = st.slider("Show last N head-to-head matches", min_value=5, max_value=50, value=15, step=5, key="h2h_n")
            recent = a_view.sort_values("date").tail(recent_n)
            static_margin_bar_by_date(recent, title=f"{team_a} vs {team_b} – Margin (Last {recent_n})")

            st.subheader("Recent Head-to-Head Matches (Non-editable)")
            show_cols = ["date", "team_score", "opponent_score", "margin", "result", "tournament"]
            recent_tbl = a_view.sort_values("date", ascending=False)[show_cols].head(15).copy()
            recent_tbl["date"] = recent_tbl["date"].dt.strftime("%Y-%m-%d")
            st.table(recent_tbl)

# ---------------------------------------------------------
# World Cups
# ---------------------------------------------------------
with tab_wc:
    st.header("Rugby World Cups")

    wc_df = pd.DataFrame(WORLD_CUPS)
    wc_display = wc_df.rename(columns={"year": "Year", "host": "Host", "winner": "Winner", "runner_up": "Runner-up"})[
        ["Year", "Host", "Winner", "Runner-up"]
    ]

    st.subheader("Winners by Year (Non-editable)")
    st.table(wc_display)

    st.subheader("Titles by Nation (Static)")
    titles = wc_df.groupby("winner", as_index=False).size().rename(columns={"winner": "Nation", "size": "Titles"})
    titles = titles.sort_values(["Titles", "Nation"], ascending=[False, True])

    static_bar_chart(
        categories=titles["Nation"].tolist(),
        values=titles["Titles"].tolist(),
        title="Rugby World Cup Titles by Nation",
        xlabel="Nation",
        ylabel="Titles",
        rotate_x=45,
    )

# ---------------------------------------------------------
# About
# ---------------------------------------------------------
with tab_about:
    st.header("About")

    st.markdown(
        f"""
**Data Source:** `data/rugby_matches.csv` (team-centric match rows)

**Dataset rules (current build):**
- Modern era only: {MIN_YEAR}+  
- Tier 1 + Tier 2 nations  
- Each match is represented twice (one row per team perspective)

**What this enables:**
- Rankings based on real match volume
- Meaningful trends across decades
- Clean head-to-head comparisons without fragile home/away logic
"""
    )
