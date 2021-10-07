import csv
import os.path as path
from datetime import datetime, timezone

from flask import (
    Blueprint, redirect, render_template, request, url_for, flash
)

from . import clan as clan_lib
from . import score_gen

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
def index():
    return render_template('dashboard/index.html')


@dashboard.route('/clan')
def clan_view():
    clan_name = request.args.get('clan_name', None)
    sort_by = request.args.get('sort_by', None)
    reverse = request.args.get('reverse', None)
    col_type = request.args.get('col_type', None)
    selected_date = request.args.get('selected_date', None)
    file_path = get_file_path(clan_name, selected_date)

    members = read_score_file(file_path, sort_by, reverse, col_type)
    return render_template('dashboard/clan_view.html', members=members, clan_name=clan_name,
                           selected_date=selected_date)


@dashboard.route('/generate')
def generate_scores():
    clan_name = request.args.get('clan_name', None)
    selected_date = request.args.get('selected_date', None)
    if clan_name == 'All':
        score_gen.generate_all_scores()
        return render_template('dashboard/index.html')
    else:
        score_gen.generate_scores_for_clan(clan_name)
        return redirect(url_for('dashboard.clan_view', clan_name=clan_name, selected_date=selected_date))


@dashboard.route('/discord')
def discord_view():
    clan_name = request.args.get('clan_name', None)
    sort_by = request.args.get('sort_by', None)
    reverse = request.args.get('reverse', None)
    col_type = request.args.get('col_type', None)
    selected_date = request.args.get('selected_date', None)
    file_path = get_file_path(clan_name, selected_date)

    members = read_score_file(file_path, sort_by, reverse, col_type)
    return render_template('dashboard/discord_view.html', members=members, clan_name=clan_name,
                           selected_date=selected_date)


@dashboard.route('/diff')
def diff_view():
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    sort_by = request.args.get('sort_by', None)
    reverse = request.args.get('reverse', None)
    col_type = request.args.get('col_type', None)
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    members_who_left, members_who_joined = score_gen.get_clan_member_diff(start_date, end_date)
    if sort_by is not None:
        reverse = reverse is not None
        if col_type == 'int':
            members_who_left = sorted(members_who_left, key=lambda item: int(item[sort_by]), reverse=reverse)
            members_who_joined = sorted(members_who_joined, key=lambda item: int(item[sort_by]), reverse=reverse)
        elif col_type == 'str':
            members_who_left = sorted(members_who_left, key=lambda item: item[sort_by].lower(), reverse=reverse)
            members_who_joined = sorted(members_who_joined, key=lambda item: item[sort_by].lower(), reverse=reverse)

    return render_template('dashboard/diff_view.html', members_who_left=members_who_left, members_who_joined=members_who_joined, start_date=start_date_str, end_date=end_date_str)


@dashboard.route('/save')
def save_to_csv():
    m = request.args.get('m', None).replace('%23', '#')
    clan = request.args.get('clan', None)
    date = request.args.get('date', None)
    url = request.args.get('old_url', None).replace('%26', '&')

    mem_list = clan_lib.build_clan_members_from_json_string(m)

    file_path = get_file_path(clan, date)
    score_gen.write_members_to_csv(mem_list, file_path)

    return redirect(url)


@dashboard.route('/inactive')
def inactive_view():
    inactive_members = []

    clan_name = request.args.get('clan_name', None)
    selected_date = request.args.get('selected_date', None)

    if clan_name == 'All':
        for clan in score_gen.clans:
            inactive_members.extend(get_inactive_members(clan, selected_date))
    else:
        inactive_members = get_inactive_members(clan_name, selected_date)
    return render_template('dashboard/inactive_view.html', members=inactive_members, clan_name=clan_name,
                           selected_date=selected_date, clans=score_gen.clans)


@dashboard.route('/single')
def generate_single():
    bungie_name = request.args.get('bungie_name', None)
    clan_name = request.args.get('clan_name', None)
    output, member_found = score_gen.generate_scores_for_clan_member(bungie_name, clan_name)
    if not member_found:
        flash(output)
        redirect('/')
    return render_template('dashboard/single_player_view.html', member=output)


def get_week_start_as_str(dt):
    dt = datetime.strptime(dt, '%Y-%m-%d')
    week_start = score_gen.get_week_start(dt)
    return f'{week_start:%Y-%m-%d}'


def get_file_path(clan_name, selected_date):
    week_start_str = get_week_start_as_str(selected_date)
    week_folder = path.join('scoreData', week_start_str)
    return path.join(week_folder, clan_name + '.csv')


def read_score_file(file_path, sort_by, reverse, col_type):
    members = []
    with open(file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        headers = next(csv_reader)
        for row in csv_reader:
            members.append(row)
    mem_list = []
    for member in members:
        mem_as_json = {}
        for i in range(len(headers)):
            mem_as_json[headers[i]] = member[i]
        mem_list.append(mem_as_json)
    if sort_by is not None:
        reverse = reverse is not None
        if sort_by == 'inactive':
            reverse = not reverse

        if sort_by == 'clan_engram':
            reverse = not reverse
            mem_list = sorted(mem_list, key=lambda item: str(item[sort_by + '_hunter'] == 'True' or item[sort_by + '_warlock'] == 'True' or item[sort_by + '_titan'] == 'True'), reverse=reverse)
        elif col_type == 'int':
            mem_list = sorted(mem_list, key=lambda item: int(item[sort_by]), reverse=reverse)
        elif col_type == 'date':
            mem_list = sorted(mem_list, key=lambda item: item[sort_by][:10], reverse=reverse)
        elif col_type == 'str':
            mem_list = sorted(mem_list, key=lambda item: item[sort_by].lower(), reverse=reverse)
    return mem_list


def get_inactive_members(clan_name, selected_date):
    inactive_members = []

    file_path = get_file_path(clan_name, selected_date)
    members = read_score_file(file_path, None, None, None)

    for m in members:
        if m['inactive'] == 'True':
            inactive_members.append(m)
    return inactive_members
