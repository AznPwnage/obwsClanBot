import enum

from . import request
from . import clan as clan_lib
import csv
from datetime import datetime, timezone, timedelta
import pytz
import os.path as path
import os
import pandas as pd


class DestinyClass(enum.Enum):
    Hunter = 1
    Warlock = 2
    Titan = 0


class DestinyRaid(enum.Enum):
    gos = 3458480158
    dsc = 910380154
    lw = 2122313384


MIN_LIGHT = 1200

CLAN_ENGRAM_MS_HASH = '3603098564'
CLAN_ENGRAM_OBJ_HASH = 1001409310
CRUCIBLE_MS_HASH = '2594202463'
CRUCIBLE_OBJ_HASH = 4026431786
EXO_CHALLENGE_POWERFUL_MS_HASH = '979073379'
EXO_CHALLENGE_PINNACLE_MS_HASH = '1713200903'
BANSHEE_ENGRAM_MS_HASH = '3899487295'
BANSHEE_ENGRAM_OBJ_HASH = 313458118
DRIFTER_ENGRAM_MS_HASH = '3802603984'
DRIFTER_ENGRAM_OBJ_HASH = 967175154
ZAVALA_ENGRAM_MS_HASH = '2709491520'
ZAVALA_ENGRAM_OBJ_HASH = 2338381314
VARIKS_ENGRAM_MS_HASH = '2540726600'
VARIKS_ENGRAM_OBJ_HASH = 1619867321
EXO_STRANGER_MS_HASH = '1424672028'
EXO_STRANGER_OBJ_HASH = 340542773
EMPIRE_HUNT_MS_HASH = '291895718'
NIGHTFALL_MS_HASH = '1942283261'
DEADLY_VENATICS_MS_HASH = '2406589846'
STRIKES_MS_HASH = '1437935813'
NIGHTFALL_100K_MS_HASH = '2029743966'
GAMBIT_MS_HASH = '3448738070'
CRUCIBLE_PLAYLIST_MS_HASH = '3312774044'
CRUCIBLE_GLORY_MS_HASH = '1368032265'
TRIALS3_MS_HASH = '3628293757'
TRIALS5_MS_HASH = '3628293755'
TRIALS7_MS_HASH = '3628293753'

EXO_CHALLENGE_HASHES = [1262994080, 2361093350, 3784931086]

clans = clan_lib.ClanGroup().get_clans()


def initialize_member(clan_member):
    member = clan_lib.ClanMember(clan_member.name, clan_member.membership_id, clan_member.clan_name,
                                 clan_member.membership_type, clan_member.clan_type)
    member.privacy = False
    member.account_not_exists = False

    member.clan_engram = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.crucible_engram = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}

    member.exo_challenge = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.banshee = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.drifter = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.zavala = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.variks = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.exo_stranger = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.empire_hunt = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.nightfall = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.deadly_venatics = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.strikes = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.nightfall_100k = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.gambit = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.crucible_playlist = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.crucible_glory = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.trials3 = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.trials5 = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.trials7 = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}

    member.raids = {DestinyRaid.gos.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
                    DestinyRaid.dsc.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
                    DestinyRaid.lw.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0}}

    member.low_light = {DestinyClass.Hunter.name: True, DestinyClass.Warlock.name: True, DestinyClass.Titan.name: True}

    member.score = 0
    member.score_delta = 0
    member.prev_score = 0
    member.date_last_played = ''
    member.days_last_played = -1

    return member


def get_low_light(member, member_class, char_to_check):
    if char_to_check['light'] >= MIN_LIGHT:
        member.low_light[member_class.name] = False
    return member


def get_prev_week_score(member, df):
    if df is not None:
        if int(member.membership_id) in df.index:
            member.prev_score = int(df.loc[int(member.membership_id)]['Score'])
    return member


def get_date_last_played(member, prof, dt):
    utc = pytz.UTC
    last_dt_str = prof['Response']['profile']['data']['dateLastPlayed']
    last_dt = utc.localize(datetime.strptime(last_dt_str, '%Y-%m-%dT%H:%M:%SZ'))
    member.date_last_played = last_dt_str
    member.days_last_played = (dt - last_dt).days
    return member


def get_week_start(dt):
    day_number = dt.weekday()  # returns 0 for Mon, 6 for Sun
    if 1 < day_number:  # diff from previous Tuesday
        return (dt - timedelta(days=day_number-1)).replace(hour=17, minute=00, second=0, microsecond=0)
    if 1 == day_number:  # check whether past reset or not
        if 17 <= dt.hour:  # past reset
            return dt.replace().replace(hour=17, minute=00, second=0, microsecond=0)
    return (dt - timedelta(days=6)).replace(hour=17, minute=00, second=0, microsecond=0)  # case of Monday being current day


def str_to_time(time_str):
    date_format = "%Y-%m-%dT%XZ"
    return datetime.strptime(time_str, date_format)


def get_weekly_raid_count(member, member_class, week_start, character_id):
    utc = pytz.UTC
    character_raids = request.BungieApiCall().get_activity_history(member.membership_type, member.membership_id, character_id)
    for raid in character_raids:
        if utc.localize(str_to_time(raid['period'])) < week_start:  # exit if date is less than week start, as stats are in desc order (I hope)
            break
        if 'No' == raid['values']['completed']['basic']['displayValue']:  # incomplete raids shouldn't be added to the counter
            continue
        ref_id = raid['activityDetails']['referenceId']
        if ref_id == 1661734046:  # Hack because Bungie API has 2 separate LW Raids. Bungie API is a mess.
            ref_id = 2122313384
        member.raids[DestinyRaid(ref_id).name][member_class.name] += 1
        if member.raids[DestinyRaid(ref_id).name][member_class.name] == 1:
            if member.clan_type == 'Raid':
                member.score += 2
            member.score += 5
    return member


def check_collectible_milestone(milestones_list, ms_hash, obj_hash):
    if ms_hash in milestones_list.keys():  # not picked up
        if obj_hash == milestones_list[ms_hash]['availableQuests'][0]['status']['stepObjectives'][0]['objectiveHash']:  # completed
            return True
    else:  # picked up
        return True
    return False


def milestone_not_in_list(milestones_list, ms_hash):
    if ms_hash not in milestones_list.keys():  # completed
        return True
    return False


def get_clan_engram(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if check_collectible_milestone(milestones_list, CLAN_ENGRAM_MS_HASH, CLAN_ENGRAM_OBJ_HASH):
            member.clan_engram[member_class.name] = True
            member.score += 4
    return member


def get_crucible_engram(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if check_collectible_milestone(milestones_list, CRUCIBLE_MS_HASH, CRUCIBLE_OBJ_HASH):
            member.crucible_engram[member_class.name] = True
            member.score += 4
    return member


def build_activity_hashes(activities_arr):
    activity_hash_arr = []
    for activity in activities_arr:
        activity_hash_arr.append(activity['activityHash'])
    return activity_hash_arr


def check_arr_contains(hash_arr, check_arr):
    for item in check_arr:
        if item in hash_arr:
            return True
    return False


def get_exo_challenge(member, member_class, milestones_list, activity_hash_arr):
    if not member.low_light[member_class.name] and check_arr_contains(activity_hash_arr, EXO_CHALLENGE_HASHES):
        if milestone_not_in_list(milestones_list, EXO_CHALLENGE_POWERFUL_MS_HASH) and milestone_not_in_list(milestones_list, EXO_CHALLENGE_PINNACLE_MS_HASH):
            member.exo_challenge[member_class.name] = True
            member.score += 1
    return member


def get_banshee(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if check_collectible_milestone(milestones_list, BANSHEE_ENGRAM_MS_HASH, BANSHEE_ENGRAM_OBJ_HASH):
            member.banshee[member_class.name] = True
            member.score += 2
    return member


def get_drifter(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if check_collectible_milestone(milestones_list, DRIFTER_ENGRAM_MS_HASH, DRIFTER_ENGRAM_OBJ_HASH):
            member.drifter[member_class.name] = True
            member.score += 2
    return member


def get_zavala(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if check_collectible_milestone(milestones_list, ZAVALA_ENGRAM_MS_HASH, ZAVALA_ENGRAM_OBJ_HASH):
            member.zavala[member_class.name] = True
            member.score += 2
    return member


def get_variks(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if check_collectible_milestone(milestones_list, VARIKS_ENGRAM_MS_HASH, VARIKS_ENGRAM_OBJ_HASH):
            member.variks[member_class.name] = True
            member.score += 2
    return member


def get_exo_stranger(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if check_collectible_milestone(milestones_list, EXO_STRANGER_MS_HASH, EXO_STRANGER_OBJ_HASH):
            member.exo_stranger[member_class.name] = True
            member.score += 2
    return member


def get_empire_hunt(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, EMPIRE_HUNT_MS_HASH):
            member.empire_hunt[member_class.name] = True
            member.score += 2
    return member


def get_nightfall(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, NIGHTFALL_MS_HASH):
            member.nightfall[member_class.name] = True
            member.score += 2
    return member


def get_deadly_venatics(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, DEADLY_VENATICS_MS_HASH):
            member.deadly_venatics[member_class.name] = True
            member.score += 2
    return member


def get_strikes(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, STRIKES_MS_HASH):
            member.strikes[member_class.name] = True
            member.score += 3
    return member


def get_nightfall_100k(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, NIGHTFALL_100K_MS_HASH):
            member.nightfall_100k[member_class.name] = True
            member.score += 3
    return member


def get_gambit(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, GAMBIT_MS_HASH):
            member.gambit[member_class.name] = True
            member.score += 3
    return member


def get_crucible_playlist(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, CRUCIBLE_PLAYLIST_MS_HASH):
            member.crucible_playlist[member_class.name] = True
            if 'PVP' == member.clan_type:
                member.score += 2
            member.score += 3
    return member


def get_crucible_glory(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, CRUCIBLE_GLORY_MS_HASH):
            member.crucible_glory[member_class.name] = True
            if 'PVP' == member.clan_type:
                member.score += 2
            member.score += 3
    return member


def get_trials(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, TRIALS3_MS_HASH):
            member.trials3[member_class.name] = True
            if 'PVP' == member.clan_type:
                member.score += 2
            member.score += 2
            if milestone_not_in_list(milestones_list, TRIALS5_MS_HASH):
                member.trials5[member_class.name] = True
                if 'PVP' == member.clan_type:
                    member.score += 2
                member.score += 3
                if milestone_not_in_list(milestones_list, TRIALS7_MS_HASH):
                    member.trials7[member_class.name] = True
                    if 'PVP' == member.clan_type:
                        member.score += 2
                    member.score += 4
    return member


def apply_score_cap_and_decay(member, clan_type):
    if member.score > 40:
        member.score = 40
    if clan_type == 'Regional':  # point decay for regional clan
        member.score -= 10
    if member.score > 30:  # max score post decay capped at 30 (specialized divisions as well)
        member.score = 30
    member.score_delta = member.score
    member.score += member.prev_score
    return member


def write_members_to_csv(mem_list, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['Name', 'Score', 'ScoreDelta', 'PreviousScore', 'DaysLastPlayed', 'DateLastPlayed', 'Id', 'Clan',
             'MemberShipType', 'ClanType',
             'GOS_H', 'GOS_W', 'GOS_T',
             'DSC_H', 'DSC_W', 'DSC_T',
             'LW_H', 'LW_W', 'LW_T',
             'ClanEngram_H', 'ClanEngram_W', 'ClanEngram_T',
             'CrucibleEngram_H', 'CrucibleEngram_W', 'CrucibleEngram_T',
             'ExoChallenge_H', 'ExoChallenge_W', 'ExoChallenge_T',
             'SpareParts_H', 'SpareParts_W', 'SpareParts_T',
             'ShadySchemes_H', 'ShadySchemes_W', 'ShadySchemes_T',
             'VanguardServices_H', 'VanguardServices_W', 'VanguardServices_T',
             'Variks_H', 'Variks_W', 'Variks_T',
             'ExoStranger_H', 'ExoStranger_W', 'ExoStranger_T',
             'EmpireHunt_H', 'EmpireHunt_W', 'EmpireHunt_T',
             'NightFall_H', 'NightFall_W', 'NightFall_T',
             'DeadlyVenatics_H', 'DeadlyVenatics_W', 'DeadlyVenatics_T',
             'Strikes_H', 'Strikes_W', 'Strikes_T',
             'Nightfall100k_H', 'Nightfall100k_W', 'Nightfall100k_T',
             'Gambit_H', 'Gambit_W', 'Gambit_T',
             'CruciblePlaylist_H', 'CruciblePlaylist_W', 'CruciblePlaylist_T',
             'CrucibleGlory_H', 'CrucibleGlory_W', 'CrucibleGlory_T',
             'Trials3_H', 'Trials3_W', 'Trials3_T',
             'Trials5_H', 'Trials5_W', 'Trials5_T',
             'Trials7_H', 'Trials7_W', 'Trials7_T',
             'LowLight_H', 'LowLight_W', 'LowLight_T',
             'PrivacyFlag', 'AccountExistsFlag'])
        for member in mem_list:
            writer.writerow(
                [str(member.name), str(member.score), str(member.score_delta), str(member.prev_score), str(member.days_last_played),
                 str(member.date_last_played), str(member.membership_id), str(member.clan_name), str(member.membership_type),
                 str(member.clan_type),
                 str(member.raids[DestinyRaid.gos.name][DestinyClass.Hunter.name]), str(member.raids[DestinyRaid.gos.name][DestinyClass.Warlock.name]), str(member.raids[DestinyRaid.gos.name][DestinyClass.Titan.name]),
                 str(member.raids[DestinyRaid.dsc.name][DestinyClass.Hunter.name]), str(member.raids[DestinyRaid.dsc.name][DestinyClass.Warlock.name]), str(member.raids[DestinyRaid.dsc.name][DestinyClass.Titan.name]),
                 str(member.raids[DestinyRaid.lw.name][DestinyClass.Hunter.name]), str(member.raids[DestinyRaid.lw.name][DestinyClass.Warlock.name]), str(member.raids[DestinyRaid.lw.name][DestinyClass.Titan.name]),
                 str(member.clan_engram[DestinyClass.Hunter.name]), str(member.clan_engram[DestinyClass.Warlock.name]), str(member.clan_engram[DestinyClass.Titan.name]),
                 str(member.crucible_engram[DestinyClass.Hunter.name]), str(member.crucible_engram[DestinyClass.Warlock.name]), str(member.crucible_engram[DestinyClass.Titan.name]),
                 str(member.exo_challenge[DestinyClass.Hunter.name]), str(member.exo_challenge[DestinyClass.Warlock.name]), str(member.exo_challenge[DestinyClass.Titan.name]),
                 str(member.banshee[DestinyClass.Hunter.name]), str(member.banshee[DestinyClass.Warlock.name]), str(member.banshee[DestinyClass.Titan.name]),
                 str(member.drifter[DestinyClass.Hunter.name]), str(member.drifter[DestinyClass.Warlock.name]), str(member.drifter[DestinyClass.Titan.name]),
                 str(member.zavala[DestinyClass.Hunter.name]), str(member.zavala[DestinyClass.Warlock.name]), str(member.zavala[DestinyClass.Titan.name]),
                 str(member.variks[DestinyClass.Hunter.name]), str(member.variks[DestinyClass.Warlock.name]), str(member.variks[DestinyClass.Titan.name]),
                 str(member.exo_stranger[DestinyClass.Hunter.name]), str(member.exo_stranger[DestinyClass.Warlock.name]), str(member.exo_stranger[DestinyClass.Titan.name]),
                 str(member.empire_hunt[DestinyClass.Hunter.name]), str(member.empire_hunt[DestinyClass.Warlock.name]), str(member.empire_hunt[DestinyClass.Titan.name]),
                 str(member.nightfall[DestinyClass.Hunter.name]), str(member.nightfall[DestinyClass.Warlock.name]), str(member.nightfall[DestinyClass.Titan.name]),
                 str(member.deadly_venatics[DestinyClass.Hunter.name]), str(member.deadly_venatics[DestinyClass.Warlock.name]), str(member.deadly_venatics[DestinyClass.Titan.name]),
                 str(member.strikes[DestinyClass.Hunter.name]), str(member.strikes[DestinyClass.Warlock.name]), str(member.strikes[DestinyClass.Titan.name]),
                 str(member.nightfall_100k[DestinyClass.Hunter.name]), str(member.nightfall_100k[DestinyClass.Warlock.name]), str(member.nightfall_100k[DestinyClass.Titan.name]),
                 str(member.gambit[DestinyClass.Hunter.name]), str(member.gambit[DestinyClass.Warlock.name]), str(member.gambit[DestinyClass.Titan.name]),
                 str(member.crucible_playlist[DestinyClass.Hunter.name]), str(member.crucible_playlist[DestinyClass.Warlock.name]), str(member.crucible_playlist[DestinyClass.Titan.name]),
                 str(member.crucible_glory[DestinyClass.Hunter.name]), str(member.crucible_glory[DestinyClass.Warlock.name]), str(member.crucible_glory[DestinyClass.Titan.name]),
                 str(member.trials3[DestinyClass.Hunter.name]), str(member.trials3[DestinyClass.Warlock.name]), str(member.trials3[DestinyClass.Titan.name]),
                 str(member.trials5[DestinyClass.Hunter.name]), str(member.trials5[DestinyClass.Warlock.name]), str(member.trials5[DestinyClass.Titan.name]),
                 str(member.trials7[DestinyClass.Hunter.name]), str(member.trials7[DestinyClass.Warlock.name]), str(member.trials7[DestinyClass.Titan.name]),
                 str(member.low_light[DestinyClass.Hunter.name]), str(member.low_light[DestinyClass.Warlock.name]), str(member.low_light[DestinyClass.Titan.name]),
                 str(member.privacy), str(member.account_not_exists)])


def get_scores(selected_clan):

    curr_dt = datetime.now(timezone.utc)
    week_start = get_week_start(curr_dt)
    prev_week = (week_start - timedelta(days=7))
    clan_member_response = request.BungieApiCall().get_clan_members(clans[selected_clan]).json()['Response']
    prev_df = None
    curr_member_list = []
    clan = clans[selected_clan]
    curr_week_folder = f'{week_start:%Y-%m-%d}'
    prev_file_path = path.join(f'{prev_week:%Y-%m-%d}', clan.name + '.csv')
    curr_file_path = path.join(curr_week_folder, clan.name + '.csv')
    if not path.exists(curr_week_folder):
        os.makedirs(curr_week_folder)
    if path.exists(curr_file_path):  # this week's data is already generated for this clan, delete it
        os.remove(curr_file_path)
    if path.exists(prev_file_path):
        prev_df = pd.read_csv(prev_file_path, usecols=['Score', 'Id'], index_col='Id')
    members = clan_member_response['results']

    for mem in members:
        name = mem['destinyUserInfo']['LastSeenDisplayName']
        membership_type = str(mem['destinyUserInfo']['membershipType'])
        membership_id = str(mem['destinyUserInfo']['membershipId'])
        clan.add_member(name, membership_type, membership_id)

    profile_responses = request.BungieApiCall().get_profile(clan.memberList)
    for j in range(len(profile_responses)):  # iterate over single clan's members

        curr_member = initialize_member(clan.memberList[j])
        profile = profile_responses[j].json()
        print(str(j+1) + '/' + str(len(profile_responses)) + ':' + curr_member.name)

        if profile['ErrorStatus'] != 'Success':  # check for account existing or not, unsure of root cause
            curr_member.account_not_exists = True
            curr_member_list.append(curr_member)
            continue
        if 'data' not in list(profile['Response']['metrics']) or 'data' not in list(profile['Response']['characterProgressions']):  # private profile
            curr_member.privacy = True
            curr_member_list.append(curr_member)
            continue

        curr_member = get_prev_week_score(curr_member, prev_df)
        curr_member = get_date_last_played(curr_member, profile, curr_dt)

        characters = profile['Response']['characters']['data']  # check light level
        character_progressions = profile['Response']['characterProgressions']['data']
        character_activities = profile['Response']['characterActivities']['data']
        for character_id in character_progressions.keys():  # iterate over single member's characters
            milestones = character_progressions[character_id]['milestones']
            activity_hashes = build_activity_hashes(character_activities[character_id]['availableActivities'])
            character = characters[character_id]
            curr_class = DestinyClass(character['classType'])
            curr_member = get_low_light(curr_member, curr_class, character)
            curr_member = get_weekly_raid_count(curr_member, curr_class, week_start, character_id)
            curr_member = get_clan_engram(curr_member, curr_class, milestones)
            curr_member = get_crucible_engram(curr_member, curr_class, milestones)
            curr_member = get_exo_challenge(curr_member, curr_class, milestones, activity_hashes)
            curr_member = get_banshee(curr_member, curr_class, milestones)
            curr_member = get_drifter(curr_member, curr_class, milestones)
            curr_member = get_zavala(curr_member, curr_class, milestones)
            curr_member = get_variks(curr_member, curr_class, milestones)
            curr_member = get_exo_stranger(curr_member, curr_class, milestones)
            curr_member = get_empire_hunt(curr_member, curr_class, milestones)
            curr_member = get_nightfall(curr_member, curr_class, milestones)
            curr_member = get_deadly_venatics(curr_member, curr_class, milestones)
            curr_member = get_strikes(curr_member, curr_class, milestones)
            curr_member = get_nightfall_100k(curr_member, curr_class, milestones)
            curr_member = get_gambit(curr_member, curr_class, milestones)
            curr_member = get_crucible_playlist(curr_member, curr_class, milestones)
            curr_member = get_crucible_glory(curr_member, curr_class, milestones)
            curr_member = get_trials(curr_member, curr_class, milestones)

        curr_member = apply_score_cap_and_decay(curr_member, clan.clan_type)
        curr_member_list.append(curr_member)

    write_members_to_csv(curr_member_list, curr_file_path)
