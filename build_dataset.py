import pandas as pd
import numpy as np
from pathlib import Path

# -------------------------------------------------
# Configuration
# -------------------------------------------------

OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "rugby_matches.csv"

MIN_YEAR = 1987  # Modern World Cup era

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

# -------------------------------------------------
# Load raw data
# -------------------------------------------------

print("Loading raw dataset...")
df = pd.read_csv("data/rugby_matches.csv")

# Normalize column names (defensive)
df.columns = [c.strip().lower() for c in df.columns]

# Handle dataset naming differences
if "competition" in df.columns and "tournament" not in df.columns:
    df = df.rename(columns={"competition": "tournament"})

required = {
    "date",
    "year",
    "team",
    "opponent",
    "team_score",
    "opponent_score",
    "result",
    "margin",
    "tournament",
}



missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# -------------------------------------------------
# Date handling & era filter
# -------------------------------------------------

print("Parsing dates...")
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])
df["year"] = df["date"].dt.year

print(f"Filtering to matches from {MIN_YEAR}+ ...")
df = df[df["year"] >= MIN_YEAR]

# -------------------------------------------------
# Team filter (Tier 1 + Tier 2)
# -------------------------------------------------

print("Filtering to Tier 1 + Tier 2 nations...")
df = df[df["team"].isin(TIER_1_2_TEAMS)].copy()

team_df = df.copy()

# -------------------------------------------------
# Derived analytics fields
# -------------------------------------------------

print("Computing derived metrics...")

team_df["margin"] = team_df["team_score"] - team_df["opponent_score"]

team_df["result"] = np.select(
    [
        team_df["margin"] > 0,
        team_df["margin"] < 0,
        team_df["margin"] == 0,
    ],
    ["Win", "Loss", "Draw"],
    default="Unknown",
)

team_df["result"] = np.select(

# -------------------------------------------------
# Final column selection (HARD DELETE others)
# -------------------------------------------------

FINAL_COLUMNS = [
    "date",
    "year",
    "team",
    "opponent",
    "team_score",
    "opponent_score",
    "margin",
    "result",
    "tournament",
]

team_df = team_df[FINAL_COLUMNS]

# Sort for sanity
team_df = team_df.sort_values(["date", "team"]).reset_index(drop=True)

# -------------------------------------------------
# Write output
# -------------------------------------------------

OUTPUT_DIR.mkdir(exist_ok=True)

print(f"Writing clean dataset to {OUTPUT_FILE} ...")
team_df.to_csv(OUTPUT_FILE, index=False)

print("Done.")
print(f"Final rows: {len(team_df):,}")
print(f"Teams represented: {team_df['team'].nunique()}")
