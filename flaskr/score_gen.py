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


class DestinyActivity(enum.Enum):
    gos = (3458480158, 4, 40, 1200)
    dsc = (910380154, 4, 35, 1200)
    lw = (2122313384, 4, 45, 1500)
    vog = (3881495763, 4, 45, 1500)
    vog_challenge = (1485585878, 4, 45, 1500)
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


activities_to_track_by_history = [DestinyActivity.poh, DestinyActivity.st, DestinyActivity.presage]


gild_level_thresholds = {
    0: 720,
    1: 2160,
    2: 4320,
    3: 7920,
    4: 99999
}


class DestinyMilestone(enum.Enum):
    clan_engram = ('3603098564', 1001409310, 4)
    crucible = ('2594202463', 4026431786, 4)
    exo_challenge_powerful = ('979073379', None, 1)
    exo_challenge_pinnacle = ('1713200903', None, 1)
    banshee_engram = ('3899487295', 313458118, 2)
    drifter_engram = ('3802603984', 967175154, 2)
    zavala_engram = ('2709491520', 2338381314, 2)
    variks_engram = ('2540726600', 1619867321, 2)
    exo_stranger = ('1424672028', 340542773, 2)
    empire_hunt = ('291895718', None, 2)
    nightfall = ('1942283261', None, 2)
    deadly_venatics = ('2406589846', None, 2)
    strikes = ('1437935813', None, 3)
    nightfall_100k = ('2029743966', None, 3)
    gambit = ('3448738070', None, 3)
    crucible_playlist = ('3312774044', None, 3)
    crucible_glory = ('1368032265', None, 3)
    trials3 = ('3628293757', None, 2)
    trials5 = ('3628293755', None, 3)
    trials7 = ('3628293753', None, 5)
    prophecy = ('825965416', None, 2)
    harbinger = ('1086730368', None, 2)
    presage = ('3927548661', None, 2)
    digital_trove = ('1684722553 ', None, 2)
    net_crasher = ('966446952', None, 2)
    rewiring_the_light = ('3341030123', 594674637, 2)

    def __init__(self, milestone_hash, objective_hash, clan_score):
        self.milestone_hash = milestone_hash
        self.objective_hash = objective_hash
        self.clan_score = clan_score

    def __new__(cls, milestone_hash, objective_hash, clan_score):
        entry = object.__new__(cls)
        entry.milestone_hash = entry._value_ = milestone_hash  # set the value, and the extra attribute
        entry.objective_hash = objective_hash
        entry.clan_score = clan_score
        return entry

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: ({self.milestone_hash!r}, {self.objective_hash!r}, {self.clan_score!r})>'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


CURRENT_SEASON_HASH = 2809059429

MIN_LIGHT = 1200

CLAN_ENGRAM_MS_HASH = '3603098564'  #
CLAN_ENGRAM_OBJ_HASH = 1001409310  #
CRUCIBLE_MS_HASH = '2594202463'  #
CRUCIBLE_OBJ_HASH = 4026431786  #
EXO_CHALLENGE_POWERFUL_MS_HASH = '979073379'  #
EXO_CHALLENGE_PINNACLE_MS_HASH = '1713200903'  #
BANSHEE_ENGRAM_MS_HASH = '3899487295'  #
BANSHEE_ENGRAM_OBJ_HASH = 313458118  #
DRIFTER_ENGRAM_MS_HASH = '3802603984'  #
DRIFTER_ENGRAM_OBJ_HASH = 967175154  #
ZAVALA_ENGRAM_MS_HASH = '2709491520'  #
ZAVALA_ENGRAM_OBJ_HASH = 2338381314  #
VARIKS_ENGRAM_MS_HASH = '2540726600'  #
VARIKS_ENGRAM_OBJ_HASH = 1619867321  #
EXO_STRANGER_MS_HASH = '1424672028'  #
EXO_STRANGER_OBJ_HASH = 340542773  #
EMPIRE_HUNT_MS_HASH = '291895718'  #
NIGHTFALL_MS_HASH = '1942283261'  #
DEADLY_VENATICS_MS_HASH = '2406589846'
STRIKES_MS_HASH = '1437935813'
NIGHTFALL_100K_MS_HASH = '2029743966'
GAMBIT_MS_HASH = '3448738070'
CRUCIBLE_PLAYLIST_MS_HASH = '3312774044'
CRUCIBLE_GLORY_MS_HASH = '1368032265'
TRIALS3_MS_HASH = '3628293757'
TRIALS5_MS_HASH = '3628293755'
TRIALS7_MS_HASH = '3628293753'
PROPHECY_MS_HASH = '825965416'
HARBINGER_MS_HASH = '1086730368'
PRESAGE_MS_HASH = '3927548661'

EXO_CHALLENGE_HASHES = [1262994080, 2361093350, 3784931086]

OVERRIDE_HASHES = [25688104, 2865532048, 3933916447, 612985278]

MEMBERSHIP_IDS_TO_IGNORE = ['4611686018468017900',  # Renk
                            '4611686018467476681',  # Daramir
                            '4611686018467377928',  # Halioon
                            '4611686018511983802',  # Bena's alt
                            '4611686018512061584',  # Jjljunkins0101
                            '4611686018513522502',  # Fencervenser
                            '4611686018512275371',  # PGDR
                            '4611686018508301419',  # obwsperidot
                            '4611686018505313756',  # Ell3mental
                            '4611686018508326111',  # FizbanTWO
                            '4611686018508299936',  # VoluspaTheSeer
                            '4611686018508327663',  # Petidor
                            '4611686018506792489',  # Nar2n
                            '4611686018511981905',  # AltPwnage
                            '4611686018490231638',  # Распутин
                            '4611686018509035256',  # CalusPerfected,
                            '4611686018492000698',  # Renk6
                            '4611686018490330934',  # Renk3
                            '4611686018490255441',  # Renk2
                            '4611686018490338905',  # Renk5
                            '4611686018508286343',  # Rarinredbull6
                            '4611686018471980460',  # Renk4
                            '4611686018508307348',  # Renk8
                            '4611686018506086618',  # Renk-6
                            ]

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
    member.rewiring_the_light = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.digital_trove = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.net_crasher = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}

    member.activities = {
        DestinyActivity.gos.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.dsc.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.lw.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.vog.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.vog_challenge.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.prophecy.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.harbinger.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.presage.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.poh.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
        DestinyActivity.st.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0}
    }

    member.low_light = {DestinyClass.Hunter.name: True, DestinyClass.Warlock.name: True, DestinyClass.Titan.name: True}

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
    if char_to_check['light'] >= MIN_LIGHT:
        member.low_light[member_class.name] = False
    return member


def get_prev_week_score(member, df):
    if df is not None:
        if int(member.membership_id) in df.index:
            member.prev_score = int(df.loc[int(member.membership_id)]['Score'])
    return member


def get_prev_gild_level(member, df):
    if df is not None:
        if int(member.membership_id) in df.index:
            if 'GildLevel' in df.columns:
                member.gild_level = int(df.loc[int(member.membership_id)]['GildLevel'])
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
        activity_enum = DestinyActivity(ref_id)
        if activity_invalid(raid, activity_enum):
            continue

        member.activities[activity_enum.name][member_class.name] += 1
        if member.activities[activity_enum.name][member_class.name] == 1:    # only award points for first unique completion of the raid
            if member.clan_type == 'Raid':
                member.score += 2
            member.score += 5
        completion_counter += 1
    return member, completion_counter


def get_dungeons(member, member_class, week_start, character_id):
    utc = pytz.UTC
    character_dungeons = request.BungieApiCall().get_activity_history(member.membership_type, member.membership_id, character_id, 82)
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

        member.activities[activity_enum.name][member_class.name] += 1
        if member.activities[activity_enum.name][member_class.name] == 1:  # only award points for first unique completion of the raid
            member.score += 2
    return member


def get_story_activities(member, member_class, week_start, character_id):
    utc = pytz.UTC
    character_dungeons = request.BungieApiCall().get_activity_history(member.membership_type, member.membership_id, character_id, 2)
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

        member.activities[activity_enum.name][member_class.name] += 1
        if member.activities[activity_enum.name][member_class.name] == 1:  # only award points for first unique completion of the raid
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
    return ref_id


def check_aggregate_stats(aggregate_stats, activity_hashes):
    if 'activities' not in aggregate_stats['Response']:
        print('No activities')
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
        if milestone_not_in_list(milestones_list, milestone.milestone_hash):
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
                    member.score += 5
    return member


def get_prophecy(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, PROPHECY_MS_HASH):
            member.activities[DestinyActivity.prophecy.name][member_class.name] = True
            member.score += 2
    return member


def get_harbinger(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, HARBINGER_MS_HASH):
            member.activities[DestinyActivity.harbinger.name][member_class.name] = True
            member.score += 2
    return member


def get_presage(member, member_class, milestones_list):
    if not member.low_light[member_class.name]:
        if milestone_not_in_list(milestones_list, PRESAGE_MS_HASH):
            member.activities[DestinyActivity.presage.name][member_class.name] = True
            member.score += 2
    return member


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


def check_inactive(member, clan_type, completion_counter):
    # if member.days_last_played > 5:
    #     member.inactive = True
    #     return member
    for char_completion in member.clan_engram:
        member.inactive = True
        if member.clan_engram[char_completion]:
            member.inactive = False
            break
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


def write_members_to_csv(mem_list, file_path):
    if path.exists(file_path):  # this week's data is already generated for this clan, delete it
        os.remove(file_path)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # 114 columns
        writer.writerow(
            ['Name', 'Score', 'ScoreDelta', 'PreviousScore', 'DaysLastPlayed', 'DateLastPlayed', 'Id', 'Clan',
             'MemberShipType', 'ClanType', 'Inactive',
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
             'PrivacyFlag', 'AccountExistsFlag', 'ExternalScore',
             'Prophecy_H', 'Prophecy_W', 'Prophecy_T',
             'Harbinger_H', 'Harbinger_W', 'Harbinger_T',
             'GildLevel',
             'Presage_H', 'Presage_W', 'Presage_T',
             'POH_H', 'POH_W', 'POH_T',
             'ST_H', 'ST_W', 'ST_T',
             'RewiringTheLight_H', 'RewiringTheLight_W', 'RewiringTheLight_T',
             'DigitalTrove_H', 'DigitalTrove_W', 'DigitalTrove_T',
             'NetCrasher_H', 'NetCrasher_W', 'NetCrasher_T',
             'VOG_H', 'VOG_W', 'VOG_T',
             'VOGC_H', 'VOGC_W', 'VOGC_T'])
        for member in mem_list:
            writer.writerow(
                [
                    str(member.name), str(member.score), str(member.score_delta), str(member.prev_score),
                    str(member.days_last_played),
                    str(member.date_last_played), str(member.membership_id), str(member.clan_name),
                    str(member.membership_type),
                    str(member.clan_type), str(member.inactive),

                    str(member.activities[DestinyActivity.gos.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.gos.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.gos.name][DestinyClass.Titan.name]),

                    str(member.activities[DestinyActivity.dsc.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.dsc.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.dsc.name][DestinyClass.Titan.name]),

                    str(member.activities[DestinyActivity.lw.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.lw.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.lw.name][DestinyClass.Titan.name]),

                    str(member.clan_engram[DestinyClass.Hunter.name]),
                    str(member.clan_engram[DestinyClass.Warlock.name]),
                    str(member.clan_engram[DestinyClass.Titan.name]),

                    str(member.crucible_engram[DestinyClass.Hunter.name]),
                    str(member.crucible_engram[DestinyClass.Warlock.name]),
                    str(member.crucible_engram[DestinyClass.Titan.name]),

                    str(member.exo_challenge[DestinyClass.Hunter.name]),
                    str(member.exo_challenge[DestinyClass.Warlock.name]),
                    str(member.exo_challenge[DestinyClass.Titan.name]),

                    str(member.banshee[DestinyClass.Hunter.name]),
                    str(member.banshee[DestinyClass.Warlock.name]),
                    str(member.banshee[DestinyClass.Titan.name]),

                    str(member.drifter[DestinyClass.Hunter.name]),
                    str(member.drifter[DestinyClass.Warlock.name]),
                    str(member.drifter[DestinyClass.Titan.name]),

                    str(member.zavala[DestinyClass.Hunter.name]),
                    str(member.zavala[DestinyClass.Warlock.name]),
                    str(member.zavala[DestinyClass.Titan.name]),

                    str(member.variks[DestinyClass.Hunter.name]),
                    str(member.variks[DestinyClass.Warlock.name]),
                    str(member.variks[DestinyClass.Titan.name]),

                    str(member.exo_stranger[DestinyClass.Hunter.name]),
                    str(member.exo_stranger[DestinyClass.Warlock.name]),
                    str(member.exo_stranger[DestinyClass.Titan.name]),

                    str(member.empire_hunt[DestinyClass.Hunter.name]),
                    str(member.empire_hunt[DestinyClass.Warlock.name]),
                    str(member.empire_hunt[DestinyClass.Titan.name]),

                    str(member.nightfall[DestinyClass.Hunter.name]),
                    str(member.nightfall[DestinyClass.Warlock.name]),
                    str(member.nightfall[DestinyClass.Titan.name]),

                    str(member.deadly_venatics[DestinyClass.Hunter.name]),
                    str(member.deadly_venatics[DestinyClass.Warlock.name]),
                    str(member.deadly_venatics[DestinyClass.Titan.name]),

                    str(member.strikes[DestinyClass.Hunter.name]),
                    str(member.strikes[DestinyClass.Warlock.name]),
                    str(member.strikes[DestinyClass.Titan.name]),

                    str(member.nightfall_100k[DestinyClass.Hunter.name]),
                    str(member.nightfall_100k[DestinyClass.Warlock.name]),
                    str(member.nightfall_100k[DestinyClass.Titan.name]),

                    str(member.gambit[DestinyClass.Hunter.name]),
                    str(member.gambit[DestinyClass.Warlock.name]),
                    str(member.gambit[DestinyClass.Titan.name]),

                    str(member.crucible_playlist[DestinyClass.Hunter.name]),
                    str(member.crucible_playlist[DestinyClass.Warlock.name]),
                    str(member.crucible_playlist[DestinyClass.Titan.name]),

                    str(member.crucible_glory[DestinyClass.Hunter.name]),
                    str(member.crucible_glory[DestinyClass.Warlock.name]),
                    str(member.crucible_glory[DestinyClass.Titan.name]),

                    str(member.trials3[DestinyClass.Hunter.name]),
                    str(member.trials3[DestinyClass.Warlock.name]),
                    str(member.trials3[DestinyClass.Titan.name]),

                    str(member.trials5[DestinyClass.Hunter.name]),
                    str(member.trials5[DestinyClass.Warlock.name]),
                    str(member.trials5[DestinyClass.Titan.name]),

                    str(member.trials7[DestinyClass.Hunter.name]),
                    str(member.trials7[DestinyClass.Warlock.name]),
                    str(member.trials7[DestinyClass.Titan.name]),

                    str(member.low_light[DestinyClass.Hunter.name]),
                    str(member.low_light[DestinyClass.Warlock.name]),
                    str(member.low_light[DestinyClass.Titan.name]),

                    str(member.privacy), str(member.account_not_exists), str(member.external_score),

                    str(member.activities[DestinyActivity.prophecy.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.prophecy.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.prophecy.name][DestinyClass.Titan.name]),

                    str(member.activities[DestinyActivity.harbinger.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.harbinger.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.harbinger.name][DestinyClass.Titan.name]),

                    str(member.gild_level),

                    str(member.activities[DestinyActivity.presage.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.presage.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.presage.name][DestinyClass.Titan.name]),

                    str(member.activities[DestinyActivity.poh.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.poh.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.poh.name][DestinyClass.Titan.name]),

                    str(member.activities[DestinyActivity.st.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.st.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.st.name][DestinyClass.Titan.name]),

                    str(member.rewiring_the_light[DestinyClass.Hunter.name]),
                    str(member.rewiring_the_light[DestinyClass.Warlock.name]),
                    str(member.rewiring_the_light[DestinyClass.Titan.name]),

                    str(member.digital_trove[DestinyClass.Hunter.name]),
                    str(member.digital_trove[DestinyClass.Warlock.name]),
                    str(member.digital_trove[DestinyClass.Titan.name]),

                    str(member.net_crasher[DestinyClass.Hunter.name]),
                    str(member.net_crasher[DestinyClass.Warlock.name]),
                    str(member.net_crasher[DestinyClass.Titan.name]),

                    str(member.activities[DestinyActivity.vog.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.vog.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.vog.name][DestinyClass.Titan.name]),

                    str(member.activities[DestinyActivity.vog_challenge.name][DestinyClass.Hunter.name]),
                    str(member.activities[DestinyActivity.vog_challenge.name][DestinyClass.Warlock.name]),
                    str(member.activities[DestinyActivity.vog_challenge.name][DestinyClass.Titan.name])
                ]
            )


def generate_scores(selected_clan):

    curr_dt = datetime.now(timezone.utc)
    week_start = get_week_start(curr_dt)
    prev_week = (week_start - timedelta(days=7))
    clan_member_response = request.BungieApiCall().get_clan_members(clans[selected_clan]).json()['Response']
    prev_df = None
    curr_member_list = []
    clan = clans[selected_clan]
    curr_week_folder = f'{week_start:%Y-%m-%d}'
    curr_file_path = path.join(curr_week_folder, clan.name + '.csv')
    if not path.exists(curr_week_folder):
        os.makedirs(curr_week_folder)
    prev_df = pd.DataFrame()
    for prev_week_clan in clans:
        prev_file_path = path.join(f'{prev_week:%Y-%m-%d}', clans[prev_week_clan].name + '.csv')
        if path.exists(prev_file_path):
            prev_df = prev_df.append(pd.read_csv(prev_file_path, usecols=['Score', 'Id', 'Name', 'GildLevel'], index_col='Id'))
    members = clan_member_response['results']
    clan.memberList = []

    for mem in members:
        name = mem['destinyUserInfo']['LastSeenDisplayName']
        membership_type = str(mem['destinyUserInfo']['membershipType'])
        membership_id = str(mem['destinyUserInfo']['membershipId'])
        if membership_id not in MEMBERSHIP_IDS_TO_IGNORE:
            clan.add_member(name, membership_type, membership_id)

    profile_responses = request.BungieApiCall().get_profile(clan.memberList)
    for j in range(len(profile_responses)):  # iterate over single clan's members

        completion_counter = 0
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
        curr_member = get_prev_gild_level(curr_member, prev_df)

        characters = profile['Response']['characters']['data']  # check light level
        character_progressions = profile['Response']['characterProgressions']['data']
        character_activities = profile['Response']['characterActivities']['data']
        owns_current_season = CURRENT_SEASON_HASH in profile['Response']['profile']['data']['seasonHashes']
        for character_id in character_progressions.keys():  # iterate over single member's characters
            aggregate_activity_stats = request.BungieApiCall().get_aggregate_activity_stats(curr_member.membership_type, curr_member.membership_id, character_id)
            unlocked_override_milestones = check_aggregate_stats(aggregate_activity_stats, OVERRIDE_HASHES)
            milestones = character_progressions[character_id]['milestones']
            activity_hashes = build_activity_hashes(character_activities[character_id]['availableActivities'])
            character = characters[character_id]
            curr_class = DestinyClass(character['classType'])
            curr_member = get_low_light(curr_member, curr_class, character)
            curr_member, completion_counter = get_raids(curr_member, curr_class, week_start, character_id, completion_counter)
            curr_member = get_dungeons(curr_member, curr_class, week_start, character_id)
            curr_member = get_story_activities(curr_member, curr_class, week_start, character_id)
            curr_member = get_exo_challenge(curr_member, curr_class, milestones, activity_hashes)
            curr_member = get_trials(curr_member, curr_class, milestones)
            curr_member = get_prophecy(curr_member, curr_class, milestones)
            curr_member = get_harbinger(curr_member, curr_class, milestones)
            # curr_member = get_presage(curr_member, curr_class, milestones)

            use_milestone_enum = True
            if use_milestone_enum:
                if get_collectible_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.clan_engram):
                    curr_member.clan_engram[curr_class.name] = True
                    curr_member.score += DestinyMilestone.clan_engram.clan_score
                if get_collectible_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.crucible):
                    curr_member.crucible_engram[curr_class.name] = True
                    curr_member.score += DestinyMilestone.crucible.clan_score
                if get_collectible_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.banshee_engram):
                    curr_member.banshee[curr_class.name] = True
                    curr_member.score += DestinyMilestone.banshee_engram.clan_score
                if get_collectible_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.drifter_engram):
                    curr_member.drifter[curr_class.name] = True
                    curr_member.score += DestinyMilestone.drifter_engram.clan_score
                if get_collectible_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.zavala_engram):
                    curr_member.zavala[curr_class.name] = True
                    curr_member.score += DestinyMilestone.zavala_engram.clan_score
                if get_collectible_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.variks_engram):
                    curr_member.variks[curr_class.name] = True
                    curr_member.score += DestinyMilestone.variks_engram.clan_score
                if get_collectible_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.exo_stranger):
                    curr_member.exo_stranger[curr_class.name] = True
                    curr_member.score += DestinyMilestone.exo_stranger.clan_score

                if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.empire_hunt):
                    curr_member.empire_hunt[curr_class.name] = True
                    curr_member.score += DestinyMilestone.empire_hunt.clan_score
                if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.nightfall):
                    curr_member.nightfall[curr_class.name] = True
                    curr_member.score += DestinyMilestone.nightfall.clan_score
                if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.deadly_venatics):
                    curr_member.deadly_venatics[curr_class.name] = True
                    curr_member.score += DestinyMilestone.deadly_venatics.clan_score
                if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.strikes):
                    curr_member.strikes[curr_class.name] = True
                    curr_member.score += DestinyMilestone.strikes.clan_score
                if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.nightfall_100k):
                    curr_member.nightfall_100k[curr_class.name] = True
                    curr_member.score += DestinyMilestone.nightfall_100k.clan_score
                if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.gambit):
                    curr_member.gambit[curr_class.name] = True
                    curr_member.score += DestinyMilestone.gambit.clan_score
                if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.crucible_playlist):
                    curr_member.crucible_playlist[curr_class.name] = True
                    curr_member.score += DestinyMilestone.crucible_playlist.clan_score
                if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.crucible_glory):
                    curr_member.crucible_glory[curr_class.name] = True
                    curr_member.score += DestinyMilestone.crucible_glory.clan_score

                if owns_current_season:
                    if unlocked_override_milestones:
                        if get_collectible_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.rewiring_the_light):
                            curr_member.rewiring_the_light[curr_class.name] = True
                            curr_member.score += DestinyMilestone.rewiring_the_light.clan_score
                        if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.digital_trove):
                            curr_member.digital_trove[curr_class.name] = True
                            curr_member.score += DestinyMilestone.digital_trove.clan_score
                        if get_milestone_completion_status(curr_member, curr_class, milestones, DestinyMilestone.net_crasher):
                            curr_member.net_crasher[curr_class.name] = True
                            curr_member.score += DestinyMilestone.net_crasher.clan_score
            else:
                curr_member = get_clan_engram(curr_member, curr_class, milestones)
                curr_member = get_crucible_engram(curr_member, curr_class, milestones)
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

        curr_member = apply_score_cap_and_decay(curr_member, clan.clan_type)
        curr_member = check_inactive(curr_member, clan.clan_type, completion_counter)
        curr_member_list.append(curr_member)

    write_members_to_csv(curr_member_list, curr_file_path)


def generate_all_scores():
    for clan in clans:
        print(clan)
        generate_scores(clan)


def get_file_path(selected_clan, date):
    week_start = get_week_start(date)
    week_folder = f'{week_start:%Y-%m-%d}'
    return path.join(week_folder, selected_clan + '.csv')


def get_left_diff_df(left_df, right_df):
    diff_index = left_df.index.difference(right_df.index)
    return left_df[left_df.index.isin(diff_index.tolist())].reset_index()


def get_clan_member_diff(selected_clan, start_date, end_date):
    start_file_path = get_file_path(selected_clan, start_date)
    end_file_path = get_file_path(selected_clan, end_date)
    start_df = pd.read_csv(start_file_path, usecols=['Score', 'Id', 'Name'], index_col='Id')
    end_df = pd.read_csv(end_file_path, usecols=['Score', 'Id', 'Name'], index_col='Id')
    members_who_left = get_left_diff_df(start_df, end_df)
    members_who_joined = get_left_diff_df(end_df, start_df)
    return members_who_left.to_dict(orient='records'), members_who_joined.to_dict(orient='records')
