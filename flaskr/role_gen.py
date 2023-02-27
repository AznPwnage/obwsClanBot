import csv
import os
from datetime import datetime, timezone

from . import clan as clan_lib
import os.path as path
import pandas as pd

from .score_gen import get_week_start

clans = clan_lib.ClanGroup().get_clans()


def generate_role_file():
    curr_week_start = get_curr_week_start()
    df = build_score_df(curr_week_start)
    df = add_roles_to_df(df)
    write_to_csv(df)


def build_score_df(week_start):
    df = pd.DataFrame()
    for clan in clans:
        prev_file_path = path.join('scoreData', f'{week_start:%Y-%m-%d}', clans[clan].name + '.csv')
        if path.exists(prev_file_path):
            df = df.append(
                pd.read_csv(prev_file_path,
                            usecols=['score', 'bungie_name', 'gild_level']))
    return df


def get_curr_week_start():
    curr_dt = datetime.now(timezone.utc)
    return get_week_start(curr_dt)


def get_role_name_from_score(score, gild_level):
    if score < 60 and gild_level == 0:
        return "Guardian"
    elif score < 120 and gild_level == 0:
        return "Brave"
    elif score < 240 and gild_level == 0:
        return "Heroic"
    elif score < 480 and gild_level == 0:
        return "Fabled"
    elif score < 720 and gild_level == 0:
        return "Mythic"
    elif score == 720 and gild_level == 0:
        return "Legend"
    elif score < 2160 and gild_level == 1:
        return "Gilded Legend"
    elif score == 2160 and gild_level == 1:
        return "Iron Wolf"
    elif score < 4320 and gild_level == 2:
        return "Gilded Iron Wolf"
    elif score == 4320 and gild_level == 2:
        return "Iron Lord"
    elif score < 7920 and gild_level >= 3:
        return "Gilded Iron Lord"
    elif score == 7920 and gild_level >= 3:
        return "Iron Will"
    else:
        return "Iron Will"


def add_roles_to_df(df):
    df['role_name'] = df.apply(lambda row: get_role_name_from_score(row['score'], row['gild_level']), axis=1)
    return df


def write_to_csv(df: pd.DataFrame):
    file_path = path.join('roleFile', 'role_file.csv')
    if path.exists(file_path):  # delete old file for current week
        os.remove(file_path)
    df.to_csv(file_path, columns=["bungie_name", "role_name"], header=False, index=False, encoding='utf-8', sep=',')
