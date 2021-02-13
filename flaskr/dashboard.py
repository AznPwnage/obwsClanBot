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
    curr_dt = datetime.now(timezone.utc)
    week_start = score_gen.get_week_start(curr_dt)
    curr_week_folder = f'{week_start:%Y-%m-%d}'
    curr_file_path = path.join(curr_week_folder, clan_name + '.csv')
    with open(curr_file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for row in csv_reader:
            members.append(row)
    return render_template('dashboard/clan_view.html', members=members, clan_name=clan_name)


@dashboard.route('/generate')
def generate_scores():
    clan_name = request.args.get('clan_name', None)
    score_gen.get_scores(clan_name)
    members = []
    curr_dt = datetime.now(timezone.utc)
    week_start = score_gen.get_week_start(curr_dt)
    curr_week_folder = f'{week_start:%Y-%m-%d}'
    curr_file_path = path.join(curr_week_folder, clan_name + '.csv')
    with open(curr_file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for row in csv_reader:
            members.append(row)
    return render_template('dashboard/clan_view.html', members=members, clan_name=clan_name)
