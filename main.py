import enum

import request
import clan as clan_lib
import csv
from datetime import datetime, timezone, timedelta
import pytz


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
EXO_CHALLENGE_MS_HASH = 979073379

EXO_CHALLENGE_HASHES = [1262994080, 2361093350, 3784931086]


def initialize_member(clan_member):
    member = clan_lib.ClanMember(clan_member.name, clan_member.membership_id, clan_member.clan_name,
                                 clan_member.membership_type, clan_member.clan_type)
    member.privacy = False
    member.account_not_exists = False

    member.clan_engram = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}
    member.crucible_engram = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}

    member.exo_challenge = {DestinyClass.Hunter.name: False, DestinyClass.Warlock.name: False, DestinyClass.Titan.name: False}

    member.raids = {DestinyRaid.gos.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
                    DestinyRaid.dsc.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0},
                    DestinyRaid.lw.name: {DestinyClass.Hunter.name: 0, DestinyClass.Warlock.name: 0, DestinyClass.Titan.name: 0}}

    member.low_light = {DestinyClass.Hunter.name: True, DestinyClass.Warlock.name: True, DestinyClass.Titan.name: True}

    member.score = 0

    return member


def get_low_light(member, member_class, char_to_check):
    if char_to_check['light'] >= MIN_LIGHT:
        member.low_light[member_class.name] = False
    return member


def get_week_start(dt):
    day_number = dt.today().weekday()  # returns 0 for Mon, 6 for Sun
    if 1 <= day_number:  # diff from previous Tuesday
        return (dt - timedelta(days=day_number-1)).replace(hour=17, minute=00, second=0, microsecond=0)
    return (dt - timedelta(days=6)).replace(hour=17, minute=00, second=0, microsecond=0)  # case of Monday being current day


def str_to_time(time_str):
    date_format = "%Y-%m-%dT%XZ"
    return datetime.strptime(time_str, date_format)


def get_weekly_raid_count(member, member_class):
    character_raids = request.BungieApiCall().get_activity_history(member.membership_type, member.membership_id, character_id)
    for raid in character_raids:
        if utc.localize(str_to_time(raid['period'])) < week_start:  # exit if date is less than week start, as stats are in desc order (I hope)
            break
        if 'No' == raid['values']['completed']['basic']['displayValue']:  # incomplete raids shouldn't be added to the counter
            continue
        ref_id = raid['activityDetails']['referenceId']
        member.raids[DestinyRaid(ref_id).name][member_class.name] += 1
    return member


def check_collectible_milestone(milestones_list, ms_hash, obj_hash):
    if ms_hash in milestones_list.keys():  # not picked up
        if obj_hash == milestones_list[ms_hash]['availableQuests'][0]['status']['stepObjectives'][0]['objectiveHash']:  # completed
            return True
    else:  # picked up
        return True
    return False


def check_auto_milestone(milestones_list, ms_hash):
    if ms_hash not in milestones_list.keys(): # completed
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
        if check_auto_milestone(milestones_list, EXO_CHALLENGE_MS_HASH):
            member.exo_challenge[member_class.name] = True
            member.score += 1
    return member


def write_members_to_csv(mem_list):
    with open('members.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['Name', 'Score', 'Id', 'Clan', 'MemberShipType', 'ClanType', 'GOS', 'DSC', 'LW', 'ExoChallenge',
             'ClanEngram', 'CrucibleEngram', 'LowLight', 'PrivacyFlag', 'AccountExistsFlag'])
        for member in mem_list:
            writer.writerow(
                [str(member.name), str(member.score), str(member.membership_id), str(member.clan_name), str(member.membership_type),
                 str(member.clan_type), str(member.raids[DestinyRaid.gos.name]), str(member.raids[DestinyRaid.dsc.name]),
                 str(member.raids[DestinyRaid.lw.name]), str(member.exo_challenge), str(member.clan_engram),
                 str(member.crucible_engram), str(member.low_light), str(member.privacy), str(member.account_not_exists)])


if __name__ == '__main__':

    curr_member_list = []  # member list compiled from Bungie API calls, reflects data from current week
    stored_member_dict = {}  # member dictionary from stored file, reflects data from past week
    curr_dt = datetime.now(timezone.utc)
    week_start = get_week_start(curr_dt)

    utc = pytz.UTC

    clan_group = clan_lib.ClanGroup().get_clan_list()
    clan_member_responses = request.BungieApiCall().get_clan_members(clan_group)

    for i in range(len(clan_group)):  # iterate over all clans in OBWS
        clan = clan_group[i]
        clan_member_response = clan_member_responses[i].json()['Response']
        members = clan_member_response['results']

        for mem in members:
            name = mem['destinyUserInfo']['LastSeenDisplayName']
            membership_type = str(mem['destinyUserInfo']['membershipType'])
            membership_id = str(mem['destinyUserInfo']['membershipId'])
            clan.add_member(name, membership_type, membership_id)

        profile_responses = request.BungieApiCall().get_profile(clan.memberList)
        for j in range(len(profile_responses)):  # iterate over single clan's members

            curr_member = initialize_member(clan.memberList[j])

            if clan.clan_type == 'Regional':  # point decay for regional clan
                curr_member.score -= 10

            profile = profile_responses[j].json()

            if profile['ErrorStatus'] != 'Success':  # check for account existing or not, unsure of root cause
                curr_member.account_not_exists = True
                curr_member_list.append(curr_member)
                continue
            if 'data' not in list(profile['Response']['metrics']) or 'data' not in list(profile['Response']['characterProgressions']):  # private profile
                curr_member.privacy = True
                curr_member_list.append(curr_member)
                continue

            characters = profile['Response']['characters']['data']  # check light level
            character_progressions = profile['Response']['characterProgressions']['data']
            character_activities = profile['Response']['characterActivities']['data']
            curr_class = None
            print(curr_member.name)
            for character_id in character_progressions.keys():  # iterate over single member's characters
                milestones = character_progressions[character_id]['milestones']
                activity_hashes = build_activity_hashes(character_activities[character_id]['availableActivities'])
                character = characters[character_id]
                curr_class = DestinyClass(character['classType'])
                curr_member = get_low_light(curr_member, curr_class, character)
                curr_member = get_weekly_raid_count(curr_member, curr_class)
                curr_member = get_clan_engram(curr_member, curr_class, milestones)
                curr_member = get_crucible_engram(curr_member, curr_class, milestones)
                curr_member = get_exo_challenge(curr_member, curr_class, milestones, activity_hashes)
            curr_member_list.append(curr_member)

    write_members_to_csv(curr_member_list)
