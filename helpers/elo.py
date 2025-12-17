import pandas as pd
from collections import defaultdict

BASE_ELO = 1500

K_FACTORS = {
    "World Cup": 40,
    "Tier1_Tier1": 30,
    "Tier1_Tier2": 25,
    "Tier2_Tier2": 20,
}

def expected_score(r_a, r_b):
    return 1 / (1 + 10 ** ((r_b - r_a) / 400))


def get_k_factor(row):
    if row["competition"] == "World Cup":
        return K_FACTORS["World Cup"]

    t1 = row["home_tier"]
    t2 = row["away_tier"]

    if t1 == 1 and t2 == 1:
        return K_FACTORS["Tier1_Tier1"]
    if t1 != t2:
        return K_FACTORS["Tier1_Tier2"]
    return K_FACTORS["Tier2_Tier2"]


def compute_elo(df):
    df = df.sort_values("date").copy()

    ratings = defaultdict(lambda: BASE_ELO)

    elo_pre_home = []
    elo_pre_away = []
    elo_post_home = []
    elo_post_away = []
    elo_delta_home = []
    elo_delta_away = []

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]

        r_home = ratings[home]
        r_away = ratings[away]

        e_home = expected_score(r_home, r_away)
        e_away = 1 - e_home

        if row["home_score"] > row["away_score"]:
            s_home, s_away = 1, 0
        elif row["home_score"] < row["away_score"]:
            s_home, s_away = 0, 1
        else:
            s_home = s_away = 0.5

        k = get_k_factor(row)

        new_home = r_home + k * (s_home - e_home)
        new_away = r_away + k * (s_away - e_away)

        elo_pre_home.append(r_home)
        elo_pre_away.append(r_away)
        elo_post_home.append(new_home)
        elo_post_away.append(new_away)
        elo_delta_home.append(new_home - r_home)
        elo_delta_away.append(new_away - r_away)

        ratings[home] = new_home
        ratings[away] = new_away

    df["elo_pre_home"] = elo_pre_home
    df["elo_pre_away"] = elo_pre_away
    df["elo_post_home"] = elo_post_home
    df["elo_post_away"] = elo_post_away
    df["elo_delta_home"] = elo_delta_home
    df["elo_delta_away"] = elo_delta_away

    return df
