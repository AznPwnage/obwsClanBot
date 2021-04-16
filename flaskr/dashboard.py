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
        print(members)

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
    m = request.args.get('m', None)
    clan = request.args.get('clan', None)
    date = request.args.get('date', None)
    url = request.args.get('old_url', None).replace('%26', '&')

    m = urllib.parse.unquote(m)

    file_path = get_file_path(clan, date)

    write_member_string_to_csv(file_path, m)

    return redirect(url)


def get_file_path(clan_name, selected_date):
    dt = datetime.strptime(selected_date, '%Y-%m-%d')
    week_start = score_gen.get_week_start(dt)
    week_folder = f'{week_start:%Y-%m-%d}'
    return path.join(week_folder, clan_name + '.csv')


def write_member_string_to_csv(file_path, member_data):
    if path.exists(file_path):  # this week's data is already generated for this clan, delete it
        os.remove(file_path)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write('Name,Score,ScoreDelta,PreviousScore,DaysLastPlayed,DateLastPlayed,Id,Clan,MemberShipType,ClanType,Inactive,GOS_H,GOS_W,GOS_T,DSC_H,DSC_W,DSC_T,LW_H,LW_W,LW_T,ClanEngram_H,ClanEngram_W,ClanEngram_T,CrucibleEngram_H,CrucibleEngram_W,CrucibleEngram_T,ExoChallenge_H,ExoChallenge_W,ExoChallenge_T,SpareParts_H,SpareParts_W,SpareParts_T,ShadySchemes_H,ShadySchemes_W,ShadySchemes_T,VanguardServices_H,VanguardServices_W,VanguardServices_T,Variks_H,Variks_W,Variks_T,ExoStranger_H,ExoStranger_W,ExoStranger_T,EmpireHunt_H,EmpireHunt_W,EmpireHunt_T,NightFall_H,NightFall_W,NightFall_T,DeadlyVenatics_H,DeadlyVenatics_W,DeadlyVenatics_T,Strikes_H,Strikes_W,Strikes_T,Nightfall100k_H,Nightfall100k_W,Nightfall100k_T,Gambit_H,Gambit_W,Gambit_T,CruciblePlaylist_H,CruciblePlaylist_W,CruciblePlaylist_T,CrucibleGlory_H,CrucibleGlory_W,CrucibleGlory_T,Trials3_H,Trials3_W,Trials3_T,Trials5_H,Trials5_W,Trials5_T,Trials7_H,Trials7_W,Trials7_T,LowLight_H,LowLight_W,LowLight_T,PrivacyFlag,AccountExistsFlag,ExternalScore')
        csvfile.write('\r\n')
        csvfile.write(member_data)
