import os.path as path

from flaskr.src.utils.date_utils import get_week_start_as_str


def get_file_path(clan_name, selected_date):
    week_start_str = get_week_start_as_str(selected_date)
    week_folder = path.join('scoreData', week_start_str)
    return path.join(week_folder, clan_name + '.csv')
