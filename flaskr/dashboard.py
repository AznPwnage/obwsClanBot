from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

import csv
from datetime import datetime, timezone, timedelta
from . import score_gen
import os.path as path

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

    curr_file_path = get_curr_file_path(clan_name)
    with open(curr_file_path, 'r', encoding='utf-8') as f:
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

    return render_template('dashboard/clan_view.html', members=members, clan_name=clan_name)


@dashboard.route('/generate')
def generate_scores():
    clan_name = request.args.get('clan_name', None)
    score_gen.get_scores(clan_name)
    return redirect(url_for('dashboard.clan_view', clan_name=clan_name))


@dashboard.route('/discord')
def discord_view():
    members = []

    clan_name = request.args.get('clan_name', None)
    sort_by = request.args.get('sort_by', None)
    reverse = request.args.get('reverse', None)
    col_type = request.args.get('col_type', None)

    curr_file_path = get_curr_file_path(clan_name)
    with open(curr_file_path, 'r', encoding='utf-8') as f:
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
    return render_template('dashboard/discord_view.html', members=members, clan_name=clan_name)


def get_curr_file_path(clan_name):
    curr_dt = datetime.now(timezone.utc)
    week_start = score_gen.get_week_start(curr_dt)
    curr_week_folder = f'{week_start:%Y-%m-%d}'
    return path.join(curr_week_folder, clan_name + '.csv')
