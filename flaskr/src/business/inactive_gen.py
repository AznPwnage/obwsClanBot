import os
import os.path as path
import pandas as pd

from ..model import clan as clan_lib
from flaskr.src.utils.date_utils import get_week_start_as_str
from flaskr.src.utils.file_utils import get_file_path
from flaskr.src.utils.score_utils import read_score_file

clans = clan_lib.ClanGroup().get_clans()


def generate_inactive_file(selected_date):
    df = pd.DataFrame()
    week_start = get_week_start_as_str(selected_date)
    for clan in clans:
        df = get_inactive_members_for_file(clans[clan].name, week_start, df)
    write_to_csv(df)


def get_inactive_members(clan_name, selected_date):
    inactive_members = []

    file_path = get_file_path(clan_name, selected_date)
    members = read_score_file(file_path, None, None, None)

    for m in members:
        if m['inactive'] == 'True':
            inactive_members.append(m)
    return inactive_members


def get_inactive_members_for_file(clan_name, week_start, df):
    file_path = path.join('scoreData', week_start, clan_name + '.csv')
    if path.exists(file_path):
        raw = pd.read_csv(file_path, usecols=['bungie_name', 'clan_name', 'inactive'])
        filtered = raw[raw['inactive']]
        df = df.append(filtered)
    return df


def write_to_csv(df):
    file_path = path.join('output/inactiveFile', 'inactive_file.csv')
    if path.exists(file_path):  # delete old file for current week
        os.remove(file_path)
    df.to_csv(file_path, columns=["bungie_name", "clan_name"], header=False, index=False, encoding='utf-8', sep=',')
