import copy
import enum
from collections import OrderedDict

from . import request
from . import clan as clan_lib
import csv
from datetime import datetime, timezone, timedelta
import pytz
import os.path as path
import os
import pandas as pd
from configparser import ConfigParser

from .clan import ClanMember


class DestinyClass(enum.Enum):
    hunter = 1
    warlock = 2
    titan = 0


class DestinyActivity(enum.Enum):
    gos = (3458480158, 4, 40, 1200)
    dsc = (910380154, 4, 35, 1200)
    lw = (2122313384, 4, 45, 1500)
    vog = (3881495763, 4, 45, 1500)
    vog_challenge = (1485585878, 4, 45, 1500)
    vog_master = (1681562271, 4, 45, 1500)
    poh = (2582501063, 82, None, None)
    prophecy = (1077850348, 82, None, None)
    st = (2032534090, 2, None, None)
    presage = (2124066889, 2, None, None)
    presage_master = (4212753278, 2, None, None)
    harbinger = (1738383283, 2, None, None)

    def __init__(self, activity_hash, activity_mode, threshold_kill, threshold_time):
        self.activity_hash = activity_hash
        self.activity_mode = activity_mode
        self.threshold_kill = threshold_kill
        self.threshold_time = threshold_time

    def __new__(cls, activity_hash, activity_mode, threshold_kill, threshold_time):
        entry = object.__new__(cls)
        entry.activity_hash = entry._value_ = activity_hash  # set the value, and the extra attribute
        entry.activity_mode = activity_mode
        entry.threshold_kill = threshold_kill
        entry.threshold_time = threshold_time
        return entry

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: ({self.activity_hash!r}, {self.activity_mode!r}, {self.threshold_kill!r}, {self.threshold_time!r})>'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class DestinyMilestone:
    def __init__(self, name, ms_hash, obj_hash, score, collectible):
        self.name = name
        self.ms_hash = ms_hash
        self.obj_hash = obj_hash
        self.score = score
        self.collectible = collectible


parser = ConfigParser()
parser.read('configs.ini')


def build_milestones_from_config(section_name):
    milestones_dict = {}
    for x in parser.items(section_name):
        config = x[1].split(',')
        config[1] = int(config[1]) if config[1] != 'None' else None
        config[2] = int(config[2]) if config[2] != 'None' else None
        config[3] = True if config[3] == 'True' else False
        milestones_dict[x[0]] = (DestinyMilestone(x[0], config[0], config[1], config[2], config[3]))
    return milestones_dict


current_season_hash = parser.getint('seasonal_variables', 'current_season_hash')
season_splicer_hash = parser.getint('seasonal_variables', 'season_splicer_hash')
season_chosen_hash = parser.getint('seasonal_variables', 'season_chosen_hash')
current_expansion_value = parser.getint('seasonal_variables', 'current_expansion_value')

min_light = parser.getint('seasonal_variables', 'min_light')

mod_alts = dict(parser.items('mod_alts')).values()

mods = dict(parser.items('mods')).values()

gild_level_thresholds = dict([(int(x[0]), int(x[1])) for x in parser.items('gild_level_thresholds')])
rejoin_lookback_map = dict([(int(x[0]), int(x[1])) for x in parser.items('rejoin_lookback')])

exo_challenge_hashes = dict([(x[0], int(x[1])) for x in parser.items('exo_challenge_hashes')]).values()
empire_hunt_hashes = dict([(x[0], int(x[1])) for x in parser.items('empire_hunt_hashes')]).values()
battleground_hashes = dict([(x[0], int(x[1])) for x in parser.items('battleground_hashes')]).values()
override_hashes = dict([(x[0], int(x[1])) for x in parser.items('override_hashes')]).values()
shattered_realms_hashes = dict([(x[0], int(x[1])) for x in parser.items('shattered_realms_hashes')]).values()

destiny_activity_mode_type = dict([(x[0], int(x[1])) for x in parser.items('destiny_activity_mode_type')])

activities_to_track_by_history = [DestinyActivity.poh, DestinyActivity.st, DestinyActivity.presage, DestinyActivity.presage_master]

clans = clan_lib.ClanGroup().get_clans()

prev_df = pd.DataFrame()
lookback_df = pd.DataFrame()

milestones = build_milestones_from_config('milestones')
milestones_seasonal = build_milestones_from_config('milestones_seasonal')
milestones_splicer = build_milestones_from_config('milestones_splicer')
milestones_chosen = build_milestones_from_config('milestones_chosen')
milestones_special = build_milestones_from_config('milestones_special')


def initialize_member(clan_member):
    member = clan_lib.ClanMember(clan_member.name, clan_member.membership_id, clan_member.clan_name,
                                 clan_member.membership_type, clan_member.clan_type)
    member.privacy = False
    member.account_not_exists = False

    destiny_class_bool_dict = {DestinyClass.hunter.name: False, DestinyClass.warlock.name: False, DestinyClass.titan.name: False}
    destiny_class_count_dict = {DestinyClass.hunter.name: 0, DestinyClass.warlock.name: 0, DestinyClass.titan.name: 0}

    for m in milestones.values():
        member.set(m.name, copy.copy(destiny_class_bool_dict))

    for m in milestones_chosen.values():
        member.set(m.name, copy.copy(destiny_class_bool_dict))

    for m in milestones_splicer.values():
        member.set(m.name, copy.copy(destiny_class_bool_dict))

    for m in milestones_seasonal.values():
        member.set(m.name, copy.copy(destiny_class_bool_dict))

    for m in milestones_special.values():
        member.set(m.name, copy.copy(destiny_class_bool_dict))
    member.set('exo_challenge', copy.copy(destiny_class_count_dict))
    member.set('clan_xp', copy.copy(destiny_class_count_dict))

    member.set(DestinyActivity.gos.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.dsc.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.lw.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.vog.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.vog_challenge.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.vog_master.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.prophecy.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.harbinger.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.presage.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.poh.name, copy.copy(destiny_class_count_dict))
    member.set(DestinyActivity.st.name, copy.copy(destiny_class_count_dict))

    member.low_light = {DestinyClass.hunter.name: True, DestinyClass.warlock.name: True, DestinyClass.titan.name: True}

    member.score = 0
    member.score_delta = 0
    member.prev_score = 0
    member.date_last_played = ''
    member.days_last_played = -1

    member.inactive = False

    member.external_score = 0

    member.gild_level = 0

    return member


def get_low_light(member, member_class, char_to_check):
    if char_to_check['light'] >= min_light:
        member.low_light[member_class.name] = False
    return member


def get_prev_week_score(member, df):
    if df is not None:
        if int(member.membership_id) in df.index:
            member.prev_score = int(df.loc[int(member.membership_id)]['score'])
    return member


def get_prev_gild_level(member, df):
    if df is not None:
        if int(member.membership_id) in df.index:
            if 'gild_level' in df.columns:
                member.gild_level = int(df.loc[int(member.membership_id)]['gild_level'])
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
        else:  # not past reset
            return (dt - timedelta(days=7)).replace(hour=17, minute=00, second=0, microsecond=0)
    return (dt - timedelta(days=6)).replace(hour=17, minute=00, second=0, microsecond=0)  # case of Monday being current day


def str_to_time(time_str):
    date_format = "%Y-%m-%dT%XZ"
    return datetime.strptime(time_str, date_format)


def get_raids(member, member_class, week_start, character_id, completion_counter):
    utc = pytz.UTC
    character_raids = request.BungieApiCall().get_activity_history(member.membership_type, member.membership_id, character_id, 4)
    for raid in character_raids:
        if utc.localize(str_to_time(raid['period'])) < week_start:  # exit if date is less than week start, as stats are in desc order (I hope)
            break
        ref_id = get_activity_ref_id(raid)
        if not DestinyActivity.has_value(ref_id):
            continue
        activity_enum = DestinyActivity(ref_id)
        if activity_invalid(raid, activity_enum):
            continue

        member.get(activity_enum.name)[member_class.name] += 1
        if member.get(activity_enum.name)[member_class.name] == 1:    # only award points for first unique completion of the raid
            if member.clan_type == 'Raid':
                member.score += 2
            member.score += 5
        completion_counter += 1
    return member, completion_counter


def get_dungeons(member, member_class, week_start, character_id):

    member = process_dungeons(member, member_class, week_start, character_id, destiny_activity_mode_type['dungeon'])
    member = process_dungeons(member, member_class, week_start, character_id, destiny_activity_mode_type['story_activity'])

    return member


def process_dungeons(member, member_class, week_start, character_id, activity_mode_type):
    character_dungeons = request.BungieApiCall().get_activity_history(member.membership_type, member.membership_id, character_id, activity_mode_type)
    utc = pytz.UTC
    for dungeon in character_dungeons:
        if utc.localize(str_to_time(dungeon['period'])) < week_start:  # exit if date is less than week start, as stats are in desc order (I hope)
            break

        ref_id = get_activity_ref_id(dungeon)
        if not DestinyActivity.has_value(ref_id):
            continue
        activity_enum = DestinyActivity(ref_id)
        if activity_enum not in activities_to_track_by_history:
            continue
        if activity_invalid(dungeon, activity_enum):
            continue
        if activity_enum == DestinyActivity.presage_master:
            activity_enum = DestinyActivity.presage

        member.get(activity_enum.name)[member_class.name] += 1
        if member.get(activity_enum.name)[member_class.name] == 1:  # only award points for first unique completion of the dungeon
            member.score += 2
    return member


def activity_invalid(activity, activity_enum):
    if 'No' == activity['values']['completed']['basic']['displayValue']:  # incomplete raids shouldn't be added to the counter
        return True

    kills = activity['values']['kills']['basic']['value']
    completion_time_in_seconds = activity['values']['timePlayedSeconds']['basic']['value']
    kill_check_fail = False
    time_check_fail = False
    if activity_enum.threshold_kill is not None:
        kill_check_fail = kills < activity_enum.threshold_kill
    if activity_enum.threshold_time is not None:
        time_check_fail = completion_time_in_seconds < activity_enum.threshold_time
    if kill_check_fail and time_check_fail:
        return True
    return False


def get_activity_ref_id(activity):
    ref_id = activity['activityDetails']['referenceId']
    if ref_id == 1661734046:  # Hack because Bungie API has 2 separate LW Raids. Bungie API is a mess.
        ref_id = 2122313384
    if ref_id == 3976949817:  # Hack because Bungie API has 2 separate DSC Raids. This one is for guided games.
        ref_id = 910380154
    if ref_id == 3711931140:  # Hack for guided games VOG.
        ref_id = 3881495763
    return ref_id


def check_aggregate_stats(aggregate_stats, activity_hashes):
    if 'activities' not in aggregate_stats['Response']:
        return False
    for activity in aggregate_stats['Response']['activities']:
        if activity['activityHash'] in activity_hashes:
            if activity['values']['activityCompletions']['basic']['value'] > 0:
                return True
    return False


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


def get_collectible_milestone_completion_status(member, member_class, milestones_list, milestone):
    if not member.low_light[member_class.name]:
        if check_collectible_milestone(milestones_list, milestone.milestone_hash, milestone.objective_hash):
            return True
    return False


def get_milestone_completion_status(member, member_class, milestones_list, milestone):
    if not member.low_light[member_class.name]:
        if milestone.collectible:
            if check_collectible_milestone(milestones_list, milestone.ms_hash, milestone.obj_hash):
                return True
        else:
            if milestone_not_in_list(milestones_list, milestone.ms_hash):
                return True
    return False


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
    if not member.low_light[member_class.name] and check_arr_contains(activity_hash_arr, exo_challenge_hashes):
        m1 = milestones_special.get('exo_challenge_powerful')
        m2 = milestones_special.get('exo_challenge_pinnacle')
        m1_not_in_list = milestone_not_in_list(milestones_list, m1.ms_hash)
        m2_not_in_list = milestone_not_in_list(milestones_list, m2.ms_hash)
        if m1_not_in_list and m2_not_in_list:
            member.get('exo_challenge')[member_class.name] = True
            member.score += m1.score
    return member


def get_clan_xp(member, member_class, uninstanced_item_objectives):
    if not member.low_light[member_class.name]:
        m = milestones_special.get('clan_xp')
        if not milestone_not_in_list(uninstanced_item_objectives, m.ms_hash):
            for objective in uninstanced_item_objectives[m.ms_hash]:
                if objective['objectiveHash'] == m.obj_hash:
                    member.get(m.name)[member_class.name] = objective['progress']
                    if objective['progress'] >= 5000:
                        member.score += m.score
    return member


def get_astral_alignment(curr_member, curr_class, milestones_list):
    m = milestones_seasonal.get('astral_alignment1')
    curr_member = check_milestone_and_add_score(curr_member, curr_class, milestones_list, m)
    if curr_member.get(m.name)[curr_class.name]:
        m = milestones_seasonal.get('astral_alignment2')
        curr_member = check_milestone_and_add_score(curr_member, curr_class, milestones_list, m)
        if curr_member.get(m.name)[curr_class.name]:
            m = milestones_seasonal.get('astral_alignment3')
            curr_member = check_milestone_and_add_score(curr_member, curr_class, milestones_list, m)
    return curr_member


def get_trials(curr_member, curr_class, milestones_list, milestone, clan_type):
    if get_milestone_completion_status(curr_member, curr_class, milestones_list, milestone):
        curr_member.get(milestone.name)[curr_class.name] = True
        curr_member.score += milestone.score
        if clan_type == 'PVP':
            curr_member.score += 2
    return curr_member


def iterate_over_milestones(curr_member, curr_class, milestones_list, milestones_to_iterate_over):
    for m in milestones_to_iterate_over.values():
        curr_member = check_milestone_and_add_score(curr_member, curr_class, milestones_list, m)
    return curr_member


def check_milestone_and_add_score(curr_member, curr_class, milestones_list, milestone):
    if get_milestone_completion_status(curr_member, curr_class, milestones_list, milestone):
        curr_member.get(milestone.name)[curr_class.name] = True
        curr_member.score += milestone.score
    return curr_member


def apply_score_cap_and_decay(member, clan_type):
    if member.score > 40:
        member.score = 40
    if clan_type == 'Regional':  # point decay for regional clan
        member.score -= 10

    member = apply_gild_cap(member)

    member.score_delta = member.score
    member.score += member.prev_score
    if member.score < 0:
        member.score = 0
    return member


def apply_gild_cap(member):
    potential_score = member.score + member.prev_score
    gild_level_threshold = gild_level_thresholds.get(member.gild_level)

    if potential_score > gild_level_threshold:
        member.score = gild_level_threshold - member.prev_score

    return member


def check_inactive(member, clan_type, completion_counter, clan_level):
    if member.membership_id in mods:
        return member
    if clan_level == 6:
        if member.days_last_played > 5:
            member.inactive = True
    else:
        total_xp = 0
        member.inactive = True
        for xp in member.clan_xp.values():
            total_xp += xp
        if total_xp >= 5000:
            member.inactive = False
    if clan_type == 'Regional':
        return member
    if clan_type == 'PVP':
        for char_completion in member.crucible_engram:
            if member.crucible_engram[char_completion]:
                return member
        member.inactive = True
    if clan_type == 'Raid':
        if completion_counter < 3:
            member.inactive = True
    return member


def perform_lookback(member, df):
    if df is not None:
        if int(member.membership_id) in df.index:
            latest_row = lookback_df.loc[int(member.membership_id)].sort_values('date', ascending=False).head(1)
            latest_row.reset_index(inplace=True)
            lookback_score = int(latest_row.values[0][2])
            lookback_date_str = str(latest_row.values[0][4])

            lookback_weeks = get_lookback_weeks(lookback_score)
            weeks_looked_back = get_weeks_looked_back(lookback_date_str)

            if weeks_looked_back <= lookback_weeks:
                member.prev_score += lookback_score
                if 'gild_level' in df.columns:
                    member.gild_level = int(latest_row['gild_level'])
    return member


def get_lookback_weeks(score):
    lookback_weeks = 0
    score_thresholds = list(rejoin_lookback_map.keys())
    for i in range(len(score_thresholds)):
        if i == len(score_thresholds):
            if score_thresholds[i] <= score:
                lookback_weeks = rejoin_lookback_map.get(score_thresholds[i])
            return lookback_weeks
        if score_thresholds[i] <= score < score_thresholds[i + 1]:
            return rejoin_lookback_map.get(score_thresholds[i])
        if score < score_thresholds[i]:
            return 0


def get_weeks_looked_back(old_date_str):
    old_week_start = datetime.strptime(old_date_str, '%Y-%m-%d')
    curr_week_start = get_week_start(datetime.now())
    return (curr_week_start - old_week_start).days / 7


def write_members_to_csv(mem_list, file_path):
    if path.exists(file_path):  # this week's data is already generated for this clan, delete it
        os.remove(file_path)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        h, v = mem_list[0].flatten()
        writer.writerow(h)
        for member in mem_list:
            h, v = member.flatten()
            writer.writerow(v)


def build_prev_df(prev_week):
    global prev_df
    if prev_df.empty:
        for prev_week_clan in clans:
            prev_file_path = path.join('scoreData', f'{prev_week:%Y-%m-%d}', clans[prev_week_clan].name + '.csv')
            if path.exists(prev_file_path):
                prev_df = prev_df.append(
                    pd.read_csv(prev_file_path, usecols=['score', 'membership_id', 'name', 'gild_level', 'clan_name'],
                                index_col='membership_id'))


def build_lookback_df(week_start):
    global lookback_df
    if lookback_df.empty:
        max_lookback = max(rejoin_lookback_map.values())
        for i in range(1, max_lookback):
            lookback_week = (week_start - timedelta(days=i * 7))
            for lookback_clan in clans:
                lookback_file_path = path.join('scoreData', f'{lookback_week:%Y-%m-%d}',
                                               clans[lookback_clan].name + '.csv')
                if path.exists(lookback_file_path):
                    temp_df = pd.read_csv(lookback_file_path, usecols=['score', 'membership_id', 'name', 'gild_level'],
                                          index_col='membership_id')
                    temp_df['date'] = f'{lookback_week:%Y-%m-%d}'
                    lookback_df = lookback_df.append(temp_df)


def build_score_for_clan_member(clan_member, profile, clan_type):
    curr_dt = datetime.now(timezone.utc)
    clan_level = 0
    completion_counter = 0
    clan_xp = 0

    curr_week = get_week_start(curr_dt)

    curr_member = initialize_member(clan_member)

    if profile['ErrorStatus'] != 'Success':  # check for account existing or not, unsure of root cause
        curr_member.account_not_exists = True
        return curr_member
    if 'data' not in list(profile['Response']['metrics']) or 'data' not in list(
            profile['Response']['characterProgressions']):  # private profile
        curr_member.privacy = True
        return curr_member

    member_joined_this_week = int(curr_member.membership_id) not in prev_df.index

    curr_member = get_prev_week_score(curr_member, prev_df)
    curr_member = get_date_last_played(curr_member, profile, curr_dt)
    curr_member = get_prev_gild_level(curr_member, prev_df)

    characters = profile['Response']['characters']['data']  # check light level
    character_progressions = profile['Response']['characterProgressions']['data']
    character_activities = profile['Response']['characterActivities']['data']

    owns_current_season = current_season_hash in profile['Response']['profile']['data']['seasonHashes']
    owns_season_splicer = season_splicer_hash in profile['Response']['profile']['data']['seasonHashes']
    owns_season_chosen = season_chosen_hash in profile['Response']['profile']['data']['seasonHashes']
    owns_current_expansion = profile['Response']['profile']['data']['versionsOwned'] > current_expansion_value

    for character_id in character_progressions.keys():  # iterate over single member's characters
        milestones_list = character_progressions[character_id]['milestones']
        activity_hashes = build_activity_hashes(character_activities[character_id]['availableActivities'])
        uninstanced_item_objectives = character_progressions[character_id]['uninstancedItemObjectives']
        progressions = character_progressions[character_id]['progressions']
        character = characters[character_id]
        curr_class = DestinyClass(character['classType'])
        aggregate_activity_stats = None

        if '584850370' not in progressions.keys():
            # Member left clan within the time that it took to reach their profile in the code
            break
        clan_level = progressions['584850370']['level']

        curr_member = get_low_light(curr_member, curr_class, character)
        curr_member, completion_counter = get_raids(curr_member, curr_class, curr_week, character_id,
                                                    completion_counter)
        curr_member = get_dungeons(curr_member, curr_class, curr_week, character_id)
        curr_member = get_exo_challenge(curr_member, curr_class, milestones_list, activity_hashes)
        curr_member = get_clan_xp(curr_member, curr_class, uninstanced_item_objectives)

        aggregate_activity_stats = request.BungieApiCall().get_aggregate_activity_stats(curr_member.membership_type,
                                                                                        curr_member.membership_id,
                                                                                        character_id)
        unlocked_empire_hunt_milestones = check_aggregate_stats(aggregate_activity_stats, empire_hunt_hashes)
        if unlocked_empire_hunt_milestones:
            curr_member = check_milestone_and_add_score(curr_member, curr_class, milestones_list,
                                                        milestones_special.get('empire_hunt'))

        curr_member = iterate_over_milestones(curr_member, curr_class, milestones_list, milestones)

        if owns_season_chosen:
            if aggregate_activity_stats is None:
                aggregate_activity_stats = request.BungieApiCall().get_aggregate_activity_stats(
                    curr_member.membership_type, curr_member.membership_id, character_id)
            unlocked_battleground_milestones = check_aggregate_stats(aggregate_activity_stats, battleground_hashes)
            if unlocked_battleground_milestones:
                curr_member = iterate_over_milestones(curr_member, curr_class, milestones_list, milestones_chosen)

        if owns_season_splicer:
            if aggregate_activity_stats is None:
                aggregate_activity_stats = request.BungieApiCall().get_aggregate_activity_stats(
                    curr_member.membership_type, curr_member.membership_id, character_id)
            unlocked_override_milestones = check_aggregate_stats(aggregate_activity_stats, override_hashes)
            if unlocked_override_milestones:
                curr_member = iterate_over_milestones(curr_member, curr_class, milestones_list, milestones_splicer)

        if owns_current_season:
            curr_member = check_milestone_and_add_score(curr_member, curr_class, milestones_list,
                                                        milestones_seasonal.get('wf_compass'))

            curr_member = get_astral_alignment(curr_member, curr_class, milestones_list)

            if aggregate_activity_stats is None:
                aggregate_activity_stats = request.BungieApiCall().get_aggregate_activity_stats(
                    curr_member.membership_type, curr_member.membership_id, character_id)
            unlocked_shattered_realms = check_aggregate_stats(aggregate_activity_stats, shattered_realms_hashes)
            if unlocked_shattered_realms:
                curr_member = check_milestone_and_add_score(curr_member, curr_class, milestones_list,
                                                            milestones_seasonal.get('shattered_champions'))

        if owns_current_expansion:
            curr_member = get_trials(curr_member, curr_class, milestones_list, milestones_special.get('trials50'),
                                     clan_type)
            curr_member = get_trials(curr_member, curr_class, milestones_list, milestones_special.get('trials7'),
                                     clan_type)

    if member_joined_this_week:
        curr_member = perform_lookback(curr_member, lookback_df)
    else:
        curr_member = check_inactive(curr_member, clan_type, completion_counter, clan_level)

    curr_member = apply_score_cap_and_decay(curr_member, clan_type)

    return curr_member


def generate_scores_for_clan(selected_clan):
    prev_week, curr_week = get_prev_and_curr_weeks()
    clan_member_response = request.BungieApiCall().get_clan_members(clans[selected_clan]).json()['Response']
    curr_member_list = []
    clan = clans[selected_clan]

    curr_week_folder = path.join('scoreData', f'{curr_week:%Y-%m-%d}')
    curr_file_path = path.join(curr_week_folder, clan.name + '.csv')
    if not path.exists(curr_week_folder):
        os.makedirs(curr_week_folder)

    build_prev_df(prev_week)

    build_lookback_df(curr_week)

    members = clan_member_response['results']
    clan.memberList = []

    for mem in members:
        name = mem['destinyUserInfo']['bungieGlobalDisplayName'] \
            if mem['destinyUserInfo']['bungieGlobalDisplayName'] != '' \
            else mem['destinyUserInfo']['LastSeenDisplayName']
        membership_type = str(mem['destinyUserInfo']['membershipType'])
        membership_id = str(mem['destinyUserInfo']['membershipId'])
        if membership_id not in mod_alts:
            clan.add_member(name, membership_type, membership_id)

    profile_responses = request.BungieApiCall().get_profiles(clan.memberList)
    for j in range(len(profile_responses)):  # iterate over single clan's members

        print(str(j + 1) + '/' + str(len(profile_responses)) + ':' + clan.memberList[j].name)

        curr_member = build_score_for_clan_member(clan.memberList[j], profile_responses[j].json(), clan.clan_type)

        curr_member_list.append(curr_member)

    write_members_to_csv(curr_member_list, curr_file_path)


def generate_all_scores():
    for clan in clans:
        print(clan)
        generate_scores_for_clan(clan)


def generate_scores_for_clan_member(bungie_name, selected_clan):
    print(bungie_name, selected_clan)
    clan = clans[selected_clan]
    clan_member_response = request.BungieApiCall().get_clan_members(clans[selected_clan]).json()['Response']
    members = clan_member_response['results']
    member_in_clan_flag = False
    for mem in members:
        if 'bungieGlobalDisplayName' in mem['destinyUserInfo'] and 'bungieGlobalDisplayNameCode' in mem['destinyUserInfo']:
            name = '{0}#{1}'.format(mem['destinyUserInfo']['bungieGlobalDisplayName'],  mem['destinyUserInfo']['bungieGlobalDisplayNameCode'])
            if bungie_name == name:
                member_in_clan_flag = True
    if not member_in_clan_flag:
        return 'No such member found', False

    search_response = request.BungieApiCall().search_player(bungie_name)['Response'][0]
    if not search_response:
        return 'No such member found', False
    membership_id = search_response['membershipId']
    membership_type = search_response['membershipType']
    profile_response = request.BungieApiCall().get_profile(str(membership_type), membership_id)

    prev_week, curr_week = get_prev_and_curr_weeks()

    build_prev_df(prev_week)

    build_lookback_df(curr_week)

    profile_user_info = profile_response['Response']['profile']['data']['userInfo']

    name = profile_user_info['bungieGlobalDisplayName'] \
        if profile_user_info['bungieGlobalDisplayName'] != '' \
        else profile_user_info['LastSeenDisplayName']
    membership_type = str(profile_user_info['membershipType'])

    clan_member = ClanMember(name, membership_id, name, membership_type, clan.clan_type)
    clan_member = build_score_for_clan_member(clan_member, profile_response, clan.clan_type)
    return clan_member, True


def get_prev_and_curr_weeks():
    curr_dt = datetime.now(timezone.utc)
    curr_week = get_week_start(curr_dt)
    prev_week = (curr_week - timedelta(days=7))

    return prev_week, curr_week


def get_file_path(selected_clan, date):
    week_start = get_week_start(date)
    week_folder = path.join('scoreData', f'{week_start:%Y-%m-%d}')
    return path.join(week_folder, selected_clan + '.csv')


def get_left_diff_df(left_df, right_df):
    diff_index = left_df.index.difference(right_df.index)
    return left_df[left_df.index.isin(diff_index.tolist())].reset_index()


def get_clan_member_diff(start_date, end_date):
    start_df = pd.DataFrame()
    end_df = pd.DataFrame()
    for clan in clans:
        clan = clans[clan]
        start_file_path = get_file_path(clan.name, start_date)
        end_file_path = get_file_path(clan.name, end_date)
        if start_df.empty:
            start_df = pd.read_csv(start_file_path, usecols=['score', 'membership_id', 'name', 'clan_name'], index_col='membership_id')
        else:
            start_df = pd.concat([start_df, pd.read_csv(start_file_path, usecols=['score', 'membership_id', 'name', 'clan_name'], index_col='membership_id')])
        if end_df.empty:
            end_df = pd.read_csv(end_file_path, usecols=['score', 'membership_id', 'name', 'clan_name'], index_col='membership_id')
        else:
            end_df = pd.concat([end_df, pd.read_csv(end_file_path, usecols=['score', 'membership_id', 'name', 'clan_name'], index_col='membership_id')])

    diff_date_iterator = get_week_start(start_date)
    mid_df = pd.DataFrame()
    while diff_date_iterator <= get_week_start(end_date):
        for clan in clans:
            clan = clans[clan]
            file_path = get_file_path(clan.name, diff_date_iterator)
            temp_df = pd.read_csv(file_path, usecols=['score', 'membership_id', 'name', 'clan_name'])
            temp_df['date'] = datetime.strftime(diff_date_iterator, '%Y-%m-%d')
            if mid_df.empty:
                mid_df = temp_df
            else:
                mid_df = pd.concat([mid_df, temp_df])
        diff_date_iterator = diff_date_iterator + timedelta(days=7)
    idx_left = mid_df.groupby(['membership_id'], sort=False)['date'].transform(max) == mid_df['date']
    idx_joined = mid_df.groupby(['membership_id'], sort=False)['date'].transform(min) == mid_df['date']
    mid_df_left = mid_df[idx_left]
    mid_df_joined = mid_df[idx_joined]

    members_who_left = get_left_diff_df(start_df, end_df)
    members_who_joined = get_left_diff_df(end_df, start_df)

    members_who_left = mid_df_left.loc[mid_df_left['membership_id'].isin(members_who_left['membership_id'].tolist())]
    members_who_joined = mid_df_joined.loc[mid_df_joined['membership_id'].isin(members_who_joined['membership_id'].tolist())]

    return members_who_left.to_dict(orient='records'), members_who_joined.to_dict(orient='records')
