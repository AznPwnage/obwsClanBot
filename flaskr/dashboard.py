import csv
import os.path as path
from datetime import datetime

from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from . import score_gen

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
def index():
    return render_template('dashboard/index.html')


@dashboard.route('/clan')
def clan_view():
    members = []

    clan_name = request.args.get('clan_name', None)
    sort_by = request.args.get('sort_by', None)
    reverse = request.args.get('reverse', None)
    col_type = request.args.get('col_type', None)
    selected_date = request.args.get('selected_date', None)

    file_path = get_file_path(clan_name, selected_date)
    with open(file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        if sort_by is not None:
            sort_by = int(sort_by)
            if reverse is None:
                if col_type == 'int':
                    members = sorted(csv_reader, key=lambda item: int(item[sort_by]))
                elif col_type == 'date':
                    members = sorted(csv_reader, key=lambda item: item[sort_by][:10])
                elif col_type == 'str':
                    members = sorted(csv_reader, key=lambda item: item[sort_by])
            else:
                if col_type == 'int':
                    members = sorted(csv_reader, key=lambda item: int(item[sort_by]), reverse=True)
                elif col_type == 'date':
                    members = sorted(csv_reader, key=lambda item: item[sort_by][:10], reverse=True)
                elif col_type == 'str':
                    members = sorted(csv_reader, key=lambda item: item[sort_by], reverse=True)
        else:
            for row in csv_reader:
                members.append(row)

    return render_template('dashboard/clan_view.html', members=members, clan_name=clan_name, selected_date=selected_date)


@dashboard.route('/generate')
def generate_scores():
    clan_name = request.args.get('clan_name', None)
    selected_date = request.args.get('selected_date', None)
    if clan_name == 'All':
        score_gen.generate_all_scores()
        return render_template('dashboard/index.html')
    else:
        score_gen.generate_scores(clan_name)
        return redirect(url_for('dashboard.clan_view', clan_name=clan_name, selected_date=selected_date))


@dashboard.route('/discord')
def discord_view():
    members = []

    clan_name = request.args.get('clan_name', None)
    sort_by = request.args.get('sort_by', None)
    reverse = request.args.get('reverse', None)
    col_type = request.args.get('col_type', None)
    selected_date = request.args.get('selected_date', None)

    file_path = get_file_path(clan_name, selected_date)
    with open(file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        if sort_by is not None:
            sort_by = int(sort_by)
            if reverse is None:
                if col_type == 'int':
                    members = sorted(csv_reader, key=lambda item: int(item[sort_by]))
                elif col_type == 'date':
                    members = sorted(csv_reader, key=lambda item: item[sort_by][:10])
                elif col_type == 'str':
                    members = sorted(csv_reader, key=lambda item: item[sort_by].upper())
            else:
                if col_type == 'int':
                    members = sorted(csv_reader, key=lambda item: int(item[sort_by]), reverse=True)
                elif col_type == 'date':
                    members = sorted(csv_reader, key=lambda item: item[sort_by][:10], reverse=True)
                elif col_type == 'str':
                    members = sorted(csv_reader, key=lambda item: item[sort_by].upper(), reverse=True)
        else:
            for row in csv_reader:
                members.append(row)
    return render_template('dashboard/discord_view.html', members=members, clan_name=clan_name, selected_date=selected_date)


@dashboard.route('/diff')
def diff_view():
    clan_name = request.args.get('clan_name', None)
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    sort_by = request.args.get('sort_by', None)
    reverse = request.args.get('reverse', None)
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    members_who_left, members_who_joined = score_gen.get_clan_member_diff(clan_name, start_date, end_date)
    if sort_by is not None:
        if reverse is None:
            members_who_left = members_who_left.sort_values(sort_by, ascending=True)
        else:
            members_who_left = members_who_left.sort_values(sort_by, ascending=False)

    return render_template('dashboard/diff_view.html', members_who_left=members_who_left, members_who_joined=members_who_joined, clan_name=clan_name,
                           start_date=start_date_str, end_date=end_date_str)


def get_file_path(clan_name, selected_date):
    dt = datetime.strptime(selected_date, '%Y-%m-%d')
    week_start = score_gen.get_week_start(dt)
    week_folder = f'{week_start:%Y-%m-%d}'
    return path.join(week_folder, clan_name + '.csv')
