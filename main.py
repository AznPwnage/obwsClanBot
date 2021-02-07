import request
import clan as clan_lib
import csv
from datetime import datetime, timezone, timedelta
import pytz


CLAN_ENGRAM_MS_HASH = '3603098564'
CLAN_ENGRAM_OBJ_HASH = '1001409310'
CRUCIBLE_MS_HASH = '2594202463'
CRUCIBLE_OBJ_HASH = '4026431786'

GOS_ACTIVITY_ID = 3458480158
DSC_ACTIVITY_ID = 910380154
LW_ACTIVITY_ID = 2122313384

EXO_CHALLENGE_HASHES = {1262994080, 2361093350, 3784931086}


def initialize_member():
    member = clan_lib.ClanMember(clan.memberList[j].name, clan.memberList[j].membership_id,
                                      clan.memberList[j].clan_name, clan.memberList[j].membership_type,
                                      clan.clan_type)
    member.privacy = False
    member.account_not_exists = False

    member.clan_engram = False
    member.crucible_engram = False

    member.h_gos = 0
    member.w_gos = 0
    member.t_gos = 0
    member.h_dsc = 0
    member.w_dsc = 0
    member.t_dsc = 0
    member.h_lw = 0
    member.w_lw = 0
    member.t_lw = 0

    member.score = 0

    return member


def check_milestone(ms_hash, obj_hash):
    if ms_hash in milestones.keys():  # not picked up
        if obj_hash == milestones[ms_hash]['availableQuests'][0]['status']['stepObjectives'][0]['objectiveHash']:  # completed
            return True
    else:  # picked up
        return True
    return False


def to_bool(val):
    return 'True' == val


def get_week_start(dt):
    day_number = dt.today().weekday()  # returns 0 for Mon, 6 for Sun
    if 1 <= day_number:  # diff from previous Tuesday
        return (dt - timedelta(days=day_number-1)).replace(hour=17, minute=00, second=0, microsecond=0)
    return (dt - timedelta(days=6)).replace(hour=17, minute=00, second=0, microsecond=0)  # case of Monday being current day


def str_to_time(time_str):
    date_format = "%Y-%m-%dT%XZ"
    return datetime.strptime(time_str, date_format)


def get_weekly_raid_count(member):
    character_raids = request.BungieApiCall().get_activity_history(member.membership_type, member.membership_id, character_id)
    for raid in character_raids:
        if utc.localize(str_to_time(raid['period'])) < week_start:  # exit if date is less than week start, as stats are in desc order (I hope)
            break
        ref_id = raid['activityDetails']['referenceId']
        if 0 == char_iterator:  # hunter
            if ref_id == GOS_ACTIVITY_ID:
                member.h_gos += 1
            elif ref_id == DSC_ACTIVITY_ID:
                member.h_dsc += 1
            elif ref_id == LW_ACTIVITY_ID:
                member.h_lw += 1
        elif 1 == char_iterator:  # warlock
            if ref_id == GOS_ACTIVITY_ID:
                member.w_gos += 1
            elif ref_id == DSC_ACTIVITY_ID:
                member.w_dsc += 1
            elif ref_id == LW_ACTIVITY_ID:
                member.w_lw += 1
        elif 2 == char_iterator:  # titan
            if ref_id == GOS_ACTIVITY_ID:
                member.t_gos += 1
            elif ref_id == DSC_ACTIVITY_ID:
                member.t_dsc += 1
            elif ref_id == LW_ACTIVITY_ID:
                member.t_lw += 1
    return member


def get_clan_and_crucible_engram(member):
    if not member.clan_engram or not member.crucible_engram:  # skip iteration if clan and crucible engrams already completed/claimed
        member.clan_engram = check_milestone(CLAN_ENGRAM_MS_HASH, CLAN_ENGRAM_OBJ_HASH)
        if 8 < len(milestones.keys()):  # require certain progression to have live-fire (crucible) available (see mod alt accounts) if we skip this check then the 'picked up' check below will pass
            member.crucible_engram = check_milestone(CRUCIBLE_MS_HASH, CRUCIBLE_OBJ_HASH)
    return member


def write_members_to_csv(mem_list):
    with open('members.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['Name', 'Id', 'Clan', 'MemberShipType', 'ClanType', 'Score', 'H_GOS', 'H_DSC', 'H_LW', 'W_GOS', 'W_DSC',
             'W_LW', 'T_GOS', 'T_DSC', 'T_LW', 'ClanEngram',
             'CrucibleEngram', 'PrivacyFlag', 'AccountExistsFlag'])
        for mem in mem_list:
            writer.writerow(
                [str(mem.name), str(mem.membership_id), str(mem.clan_name), str(mem.membership_type),
                 str(mem.clan_type), str(mem.score), str(mem.h_gos), str(mem.h_dsc), str(mem.h_lw),
                 str(mem.w_gos), str(mem.w_dsc), str(mem.w_lw), str(mem.t_gos), str(mem.t_dsc),
                 str(mem.t_lw),
                 str(mem.clan_engram), str(mem.crucible_engram), str(mem.privacy),
                 str(mem.account_not_exists)])


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

        for member in members:
            name = member['destinyUserInfo']['LastSeenDisplayName']
            membership_type = str(member['destinyUserInfo']['membershipType'])
            membership_id = str(member['destinyUserInfo']['membershipId'])
            clan.add_member(name, membership_type, membership_id)

        profile_responses = request.BungieApiCall().get_profile(clan.memberList)
        for j in range(len(profile_responses)):  # iterate over single clan's members

            curr_member = initialize_member()

            if clan.clan_type == 'Regional':
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

            character_progressions = profile['Response']['characterProgressions']['data']  # clan & crucible engrams
            char_iterator = 0
            print(curr_member.name)
            for character_id in character_progressions.keys():  # iterate over single member's characters
                milestones = character_progressions[character_id]['milestones']
                curr_member = get_weekly_raid_count(curr_member)
                curr_member = get_clan_and_crucible_engram(curr_member)
                char_iterator += 1
            curr_member_list.append(curr_member)

    write_members_to_csv(curr_member_list)
