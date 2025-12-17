import pandas as pd
from collections import defaultdict
import math

BASE_ELO = 1500
K = 30

def expected_score(r_a, r_b):
    return 1 / (1 + 10 ** ((r_b - r_a) / 400))

def build_elo(
    input_path="data/rugby_matches.csv",
    output_path="data/rugby_matches_with_elo.csv",
):
    df = pd.read_csv(input_path)
    df.columns = [c.strip().lower() for c in df.columns]

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    ratings = defaultdict(lambda: BASE_ELO)

    elo_pre = []
    elo_post = []
    elo_delta = []

    for _, row in df.iterrows():
        team = row["team"]
        opp = row["opponent"]

        r_team = ratings[team]
        r_opp = ratings[opp]

        exp = expected_score(r_team, r_opp)

        if row["result"] == "Win":
            score = 1.0
        elif row["result"] == "Draw":
            score = 0.5
        else:
            score = 0.0

        new_rating = r_team + K * (score - exp)

        elo_pre.append(r_team)
        elo_post.append(new_rating)
        elo_delta.append(new_rating - r_team)

        ratings[team] = new_rating

    df["elo_pre"] = elo_pre
    df["elo_post"] = elo_post
    df["elo_delta"] = elo_delta

    df.to_csv(output_path, index=False)
    print(f"Elo file written to {output_path}")

if __name__ == "__main__":
    build_elo()
