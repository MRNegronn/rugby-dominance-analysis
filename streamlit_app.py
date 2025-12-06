import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------- ESPN-STYLE CUSTOM CSS --------
st.markdown("""
    <style>

    /* Tabs styling */
    .stTabs [role="tab"] {
        font-size: 1.1rem;
        padding: 12px 20px;
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
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.08);
        margin-bottom: 12px;
    }

    </style>
""", unsafe_allow_html=True)


# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Rugby Analytics Dashboard",
    page_icon="🏉",
    layout="wide"
)


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
    {"year": 2015, "winner": "New Zealand"},   # ← fixed line
    {"year": 2019, "winner": "South Africa"},
    {"year": 2023, "winner": "South Africa"},
]
wcs = pd.DataFrame(world_cups)



# -------- HEADER --------
st.markdown("""
### <span style="color:#e10600;font-weight:700;">
Rugby Performance Analytics Dashboard
</span>
""", unsafe_allow_html=True)

# Sidebar
team = st.sidebar.selectbox("Select a team:", df.index)


# -------- TABS --------
tab_team, tab_rankings, tab_trends, tab_worldcups, tab_about = st.tabs(
    ["Team View", "Rankings", "Trends", "World Cups", "About"]
)


# ==========================
# TAB 1 — TEAM VIEW
# ==========================
with tab_team:
    st.subheader(f"Team Snapshot: {team}")
    team_data = df.loc[team]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Win %", f"{team_data['win_pct']:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Margin per Match", f"{team_data['margin_per_match']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Defense (Pts Allowed/Match)", f"{team_data['points_allowed_per_match']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    st.metric("Avg Seasonal Margin", f"{team_data['avg_season_margin']:.2f}")
    st.metric("World Cup Titles", int(team_data["world_cup_titles"]))


# ==========================
# TAB 2 — RANKINGS
# ==========================
with tab_rankings:

    # Chart style settings
    def style_chart(ax):
        ax.set_facecolor("#161a23")
        ax.grid(color="gray", linestyle="--", linewidth=0.3, alpha=0.35)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color("white")

    # Win Percentage Chart
    st.subheader("Top Teams — Win Percentage")
    top10 = df.sort_values("win_pct", ascending=False).head(10)
    fig1, ax1 = plt.subplots(figsize=(8,4))
    ax1.bar(top10.index, top10["win_pct"], color="#e10600")
    style_chart(ax1)
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    st.markdown("---")

    # Dominance Chart
    st.subheader("Top Teams — Dominance Score")
    top10_dom = df.sort_values("dominance_score", ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(8,4))
    ax2.bar(top10_dom.index, top10_dom["dominance_score"], color="#e10600")
    style_chart(ax2)
    plt.xticks(rotation=45)
    st.pyplot(fig2)


# ==========================
# TAB 3 — TRENDS
# ==========================
with tab_trends:
    st.subheader("Performance Trends Over Time")

    espn_colors = {
        "New Zealand": "#ffffff",
        "South Africa": "#00b140",
        "Australia": "#f2a900",
        "England": "#cc0000",
    }

    selected_teams = st.multiselect("Compare teams:", sorted(year_df["team"].unique()))
    metric_choice = st.radio("Choose metric:", ["Seasonal Point Margin", "Seasonal Win Percentage"])

    if selected_teams:
        fig, ax = plt.subplots(figsize=(10,5))

        for t in selected_teams:
            team_data = year_df[year_df["team"] == t]
            if metric_choice == "Seasonal Point Margin":
                ax.plot(team_data["year"], team_data["margin_per_match_year"],
                        label=t, linewidth=2, marker="o",
                        color=espn_colors.get(t, "#e10600"))
            else:
                ax.plot(team_data["year"], team_data["win_pct_year"],
                        label=t, linewidth=2, marker="o",
                        color=espn_colors.get(t, "#e10600"))

        style_chart(ax)
        ax.legend()
        st.pyplot(fig)


# ==========================
# TAB 4 — WORLD CUPS
# ==========================
with tab_worldcups:
    st.subheader("Rugby World Cup Winners (1987–2023)")

    # Timeline table (Markdown so NO index appears)
    timeline_df = wcs[["year", "winner"]].copy()
    timeline_df.columns = ["Year", "Winner"]
    timeline_df["Year"] = timeline_df["Year"].astype(str)
    timeline_df = timeline_df.reset_index(drop=True)

    table_md = "| Year | Winner |\n|------|--------|\n"
    for _, row in timeline_df.iterrows():
        table_md += f"| {row['Year']} | {row['Winner']} |\n"

    st.markdown(table_md)

    st.markdown("---")

    # Titles bar chart
    titles = wcs["winner"].value_counts()
    fig3, ax3 = plt.subplots(figsize=(8,4))
    ax3.bar(titles.index, titles.values, color="#e10600")
    style_chart(ax3)
    plt.xticks(rotation=45)
    st.pyplot(fig3)


# ==========================
# TAB 5 — ABOUT
# ==========================
with tab_about:
    st.subheader("About This Project")
    st.write("""
    This dashboard analyzes team performance, historical success,
    scoring trends, and Rugby World Cup results.
    Built using Python, Streamlit, and modern data visualization techniques.
    """)


