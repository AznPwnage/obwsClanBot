import csv
import os
import os.path as path
import urllib
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
        score_gen.generate_scores(clan_name)
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

    return render_template('dashboard/diff_view.html', members_who_left=members_who_left,
                           members_who_joined=members_who_joined, clan_name=clan_name,
                           start_date=start_date_str, end_date=end_date_str)


@dashboard.route('/save')
def save_to_csv():
    m = request.args.get('m', None).replace('%23', '#')
    clan = request.args.get('clan', None)
    date = request.args.get('date', None)
    url = request.args.get('old_url', None).replace('%26', '&')

    m = urllib.parse.unquote(m)

    file_path = get_file_path(clan, date)
    write_member_string_to_csv(file_path, m)

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


def get_file_path(clan_name, selected_date):
    dt = datetime.strptime(selected_date, '%Y-%m-%d')
    week_start = score_gen.get_week_start(dt)
    week_folder = f'{week_start:%Y-%m-%d}'
    return path.join(week_folder, clan_name + '.csv')


def write_member_string_to_csv(file_path, member_data):
    if path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write(
            'Name,Score,ScoreDelta,PreviousScore,DaysLastPlayed,DateLastPlayed,Id,Clan,MemberShipType,ClanType,Inactive,GOS_H,GOS_W,GOS_T,DSC_H,DSC_W,DSC_T,LW_H,LW_W,LW_T,ClanEngram_H,ClanEngram_W,ClanEngram_T,CrucibleEngram_H,CrucibleEngram_W,CrucibleEngram_T,ExoChallenge_H,ExoChallenge_W,ExoChallenge_T,SpareParts_H,SpareParts_W,SpareParts_T,ShadySchemes_H,ShadySchemes_W,ShadySchemes_T,VanguardServices_H,VanguardServices_W,VanguardServices_T,Variks_H,Variks_W,Variks_T,ExoStranger_H,ExoStranger_W,ExoStranger_T,EmpireHunt_H,EmpireHunt_W,EmpireHunt_T,NightFall_H,NightFall_W,NightFall_T,DeadlyVenatics_H,DeadlyVenatics_W,DeadlyVenatics_T,Strikes_H,Strikes_W,Strikes_T,Nightfall100k_H,Nightfall100k_W,Nightfall100k_T,Gambit_H,Gambit_W,Gambit_T,CruciblePlaylist_H,CruciblePlaylist_W,CruciblePlaylist_T,CrucibleGlory_H,CrucibleGlory_W,CrucibleGlory_T,Trials3_H,Trials3_W,Trials3_T,Trials5_H,Trials5_W,Trials5_T,Trials7_H,Trials7_W,Trials7_T,LowLight_H,LowLight_W,LowLight_T,PrivacyFlag,AccountExistsFlag,ExternalScore,Prophecy_H,Prophecy_W,Prophecy_T,Harbinger_H,Harbinger_W,Harbinger_T,GildLevel,Presage_H,Presage_W,Presage_T,POH_H,POH_W,POH_T,ST_H,ST_W,ST_T')
        csvfile.write('\r\n')
        csvfile.write(member_data)


def read_score_file(file_path, sort_by, reverse, col_type):
    members = []
    with open(file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        if sort_by is not None:
            sort_by = int(sort_by)
            if reverse is None:
                reverse = False
            else:
                reverse = True
            if col_type == 'int':
                members = sorted(csv_reader, key=lambda item: int(item[sort_by]), reverse=reverse)
            elif col_type == 'date':
                members = sorted(csv_reader, key=lambda item: item[sort_by][:10], reverse=reverse)
            elif col_type == 'str':
                members = sorted(csv_reader, key=lambda item: item[sort_by].lower(), reverse=reverse)
        else:
            for row in csv_reader:
                members.append(row)
    return members


def get_inactive_members(clan_name, selected_date):
    inactive_members = []

    file_path = get_file_path(clan_name, selected_date)
    members = read_score_file(file_path, None, None, None)

    for m in members:
        if m[10] == 'True':
            inactive_members.append(m)
    return inactive_members
