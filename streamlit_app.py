import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Rugby Analytics Dashboard",
    page_icon="🏉",
    layout="wide",
)

# -------- ESPN-STYLE CUSTOM CSS --------
st.markdown(
    """
    <style>
    /* Tabs styling */
    .stTabs [role="tab"] {
        font-size: 1.05rem;
        padding: 10px 18px;
        font-weight: 600;
        border-bottom: 3px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        color: #e10600 !important;
        border-bottom: 3px solid #e10600 !important;
    }

    /* Headings stronger */
    h1, h2, h3, h4 {
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
    }

    /* Metric card container */
    .metric-card {
        background-color: #161a23;
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.06);
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------- TEAM LOGOS & COLORS --------
team_logos = {
    "New Zealand": "https://upload.wikimedia.org/wikipedia/en/thumb/8/81/All_Blacks_logo.svg/512px-All_Blacks_logo.svg.png",
    "South Africa": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e4/Springboks_logo.svg/512px-Springboks_logo.svg.png",
    "Australia": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3e/Wallabies_logo.svg/512px-Wallabies_logo.svg.png",
    "England": "https://upload.wikimedia.org/wikipedia/en/thumb/0/05/England_rugby_union_rose.svg/512px-England_rugby_union_rose.svg.png",
}

team_colors = {
    "New Zealand": "#ffffff",   # white on dark
    "South Africa": "#00b140",  # green
    "Australia": "#f2a900",     # gold
    "England": "#cc0000",       # red
}

# -------- HELPER: CHART STYLE --------
def style_chart(ax):
    """Apply consistent ESPN-style formatting to matplotlib axes."""
    ax.set_facecolor("#161a23")
    ax.grid(color="gray", linestyle="--", linewidth=0.3, alpha=0.35)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color("white")
    ax.title.set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")


# -------- LOAD DATA --------
df = pd.read_csv("team_stats.csv", index_col=0)
year_df = pd.read_csv("team_year_stats.csv")

# World Cup Winners dataset
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
wcs = pd.DataFrame(world_cups)

# -------- HEADER --------
st.markdown(
    """
    ### <span style="color:#e10600;font-weight:700;">
    Rugby Performance Analytics Dashboard
    </span>
    """,
    unsafe_allow_html=True,
)

# -------- SIDEBAR --------
team = st.sidebar.selectbox("Select a team:", df.index)

# -------- TABS --------
tab_team, tab_rankings, tab_trends, tab_compare, tab_worldcups, tab_about = st.tabs(
    ["Team View", "Rankings", "Trends", "Compare", "World Cups", "About"]
)


# ==========================
# TAB 1 — TEAM VIEW
# ==========================
with tab_team:
    st.subheader(f"Team Snapshot: {team}")
    team_data = df.loc[team]

    # Logo
    logo_url = team_logos.get(team)
    if logo_url:
        st.image(logo_url, width=160)

    # Metric cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Win %", f"{team_data['win_pct']:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Margin per Match", f"{team_data['margin_per_match']:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Defense (Pts Allowed/Match)",
            f"{team_data['points_allowed_per_match']:.2f}",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Seasonal Margin", f"{team_data['avg_season_margin']:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("World Cup Titles", int(team_data["world_cup_titles"]))
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================
# TAB 2 — RANKINGS
# ==========================
with tab_rankings:
    st.subheader("Rankings Overview")

    # Top by Win %
    st.markdown("#### Top 10 Teams by Win Percentage")
    top10_win = df.sort_values("win_pct", ascending=False).head(10)
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(
        top10_win.index,
        top10_win["win_pct"],
        color=[team_colors.get(t, "#e10600") for t in top10_win.index],
    )
    ax1.set_ylabel("Win %")
    ax1.set_title("Win Percentage (Top 10)")
    plt.xticks(rotation=45, ha="right")
    style_chart(ax1)
    st.pyplot(fig1)

    st.markdown("---")

    # Top by Dominance Score
    st.markdown("#### Top 10 Teams by Dominance Score")
    top10_dom = df.sort_values("dominance_score", ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(
        top10_dom.index,
        top10_dom["dominance_score"],
        color=[team_colors.get(t, "#e10600") for t in top10_dom.index],
    )
    ax2.set_ylabel("Dominance Score")
    ax2.set_title("Dominance Score (Top 10)")
    plt.xticks(rotation=45, ha="right")
    style_chart(ax2)
    st.pyplot(fig2)


# ==========================
# TAB 3 — TRENDS
# ==========================
with tab_trends:
    st.subheader("Performance Trends Over Time")

    available_teams = sorted(year_df["team"].unique())
    selected_teams = st.multiselect(
        "Compare teams:", options=available_teams, default=["New Zealand", "South Africa"]
    )

    metric_choice = st.radio(
        "Choose a metric to visualize:",
        ["Seasonal Point Margin", "Seasonal Win Percentage"],
    )

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
        subset = year_df[
            (year_df["team"].isin(selected_teams))
            & (year_df["year"] >= year_range[0])
            & (year_df["year"] <= year_range[1])
        ].copy()

        fig, ax = plt.subplots(figsize=(10, 5))

        for t in selected_teams:
            team_data = subset[subset["team"] == t].sort_values("year")
            color = team_colors.get(t, "#e10600")
            if metric_choice == "Seasonal Point Margin":
                y = team_data["margin_per_match_year"]
            else:
                y = team_data["win_pct_year"]

            ax.plot(
                team_data["year"],
                y,
                label=t,
                linewidth=2,
                marker="o",
                markersize=6,
                color=color,
            )

        ax.set_xlabel("Year")
        ylabel = (
            "Average Margin per Match (Season)"
            if metric_choice == "Seasonal Point Margin"
            else "Win Percentage (%)"
        )
        ax.set_ylabel(ylabel)
        ax.set_title(f"{metric_choice} Over Time")
        ax.legend()
        style_chart(ax)
        st.pyplot(fig)


# ==========================
# TAB 4 — TEAM COMPARISON
# ==========================
with tab_compare:
    st.subheader("Team Comparison")

    colA, colB = st.columns(2)
    with colA:
        teamA = st.selectbox("Team A:", df.index, key="teamA_select")
        logoA = team_logos.get(teamA)
        if logoA:
            st.image(logoA, width=130)
    with colB:
        # default index 1 just to avoid same team twice by default
        default_index_B = 1 if len(df.index) > 1 else 0
        teamB = st.selectbox("Team B:", df.index, index=default_index_B, key="teamB_select")
        logoB = team_logos.get(teamB)
        if logoB:
            st.image(logoB, width=130)

    if teamA == teamB:
        st.warning("Select two different teams to compare.")
    else:
        st.markdown("---")
        st.markdown("#### Head-to-Head Metrics")

        def metric_row(label, a_val, b_val):
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"**{label}**")
            c2.write(str(a_val))
            c3.write(str(b_val))

        a = df.loc[teamA]
        b = df.loc[teamB]

        metric_row("Win %", f"{a['win_pct']:.1f}%", f"{b['win_pct']:.1f}%")
        metric_row(
            "Avg Margin per Match",
            f"{a['margin_per_match']:.2f}",
            f"{b['margin_per_match']:.2f}",
        )
        metric_row(
            "Defense (Pts Allowed/Match)",
            f"{a['points_allowed_per_match']:.2f}",
            f"{b['points_allowed_per_match']:.2f}",
        )
        metric_row("World Cup Titles", int(a["world_cup_titles"]), int(b["world_cup_titles"]))

        st.markdown("---")
        st.markdown("#### Seasonal Margin Comparison")

        figC, axC = plt.subplots(figsize=(10, 5))
        for T in [teamA, teamB]:
            tdata = year_df[year_df["team"] == T].sort_values("year")
            axC.plot(
                tdata["year"],
                tdata["margin_per_match_year"],
                label=T,
                linewidth=2.5,
                marker="o",
                markersize=6,
                color=team_colors.get(T, "#e10600"),
            )

        axC.set_xlabel("Year")
        axC.set_ylabel("Average Margin per Match (Season)")
        axC.set_title("Seasonal Margin Comparison")
        axC.legend()
        style_chart(axC)
        st.pyplot(figC)


# ==========================
# TAB 5 — WORLD CUPS
# ==========================
with tab_worldcups:
    st.subheader("Rugby World Cup Winners (1987–2023)")

    # Clean formatted timeline table as Markdown (no index column)
    timeline_df = wcs[["year", "winner"]].copy()
    timeline_df.columns = ["Year", "Winner"]
    timeline_df["Year"] = timeline_df["Year"].astype(str)
    timeline_df = timeline_df.reset_index(drop=True)

    table_md = "| Year | Winner |\n|------|--------|\n"
    for _, row in timeline_df.iterrows():
        color = team_colors.get(row["Winner"], "#e10600")
        table_md += (
            f"| {row['Year']} | "
            f"<span style='color:{color};font-weight:600;'>{row['Winner']}</span> |\n"
        )

    st.markdown(table_md, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Total World Cup Titles")

    titles = wcs["winner"].value_counts()
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.bar(
        titles.index,
        titles.values,
        color=[team_colors.get(t, "#e10600") for t in titles.index],
    )
    ax3.set_xlabel("Team")
    ax3.set_ylabel("Titles")
    ax3.set_title("Total Rugby World Cup Titles (1987–2023)")
    plt.xticks(rotation=45, ha="right")
    style_chart(ax3)
    st.pyplot(fig3)


# ==========================
# TAB 6 — ABOUT
# ==========================
with tab_about:
    st.subheader("About This Project")
    st.write(
        """
        This dashboard explores international rugby dominance using:

        - Win percentage  
        - Scoring margins  
        - Defensive strength  
        - Seasonal trends  
        - Rugby World Cup history  

        Built with **Python**, **pandas**, **matplotlib**, and **Streamlit**.
        """
    )
