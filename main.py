import request
import clan


def check_milestone(ms_hash, obj_hash):
    if ms_hash in milestones.keys():  # not picked up
        if obj_hash == milestones[ms_hash]['availableQuests'][0]['status']['stepObjectives'][0]['objectiveHash']:  # completed
            return True
    else:  # picked up
        return True
    return False


CLAN_ENGRAM_MS_HASH = '3603098564'
CLAN_ENGRAM_OBJ_HASH = '1001409310'
CRUCIBLE_MS_HASH = '2594202463'
CRUCIBLE_OBJ_HASH = '4026431786'
GOS_MS_HASH = '1168279855'
DSC_MS_HASH = '954805812'
LW_MS_HASH = '3766204132'

if __name__ == '__main__':
    clan_group = clan.ClanGroup().get_clan_list()
    clanMembersResponses = request.BungieApiCall().get_clan_members(clan_group)

    for i in range(len(clan_group)):
        clan = clan_group[i]
        print(clan.name)
        clanMembersResponse = clanMembersResponses[i].json()['Response']
        clan.setTotalMember(clanMembersResponse['totalResults'])
        members = clanMembersResponse['results']

        for member in members:
            name = member['destinyUserInfo']['LastSeenDisplayName']
            membershipType = str(member['destinyUserInfo']['membershipType'])
            membershipId = str(member['destinyUserInfo']['membershipId'])
            clan.addMember(name, membershipType, membershipId)

        profile_responses = request.BungieApiCall().get_profile(clan.memberList)
        for i in range(len(profile_responses)):

            privacy_flag = False
            account_not_exists_flag = False

            clan_engram_flag = False
            crucible_flag = False

            curr_gos = 0
            curr_dsc = 0
            curr_lw = 0

            profile = profile_responses[i].json()

            if profile['ErrorStatus'] != 'Success':  # check for account existing or not, unsure of root cause
                account_not_exists_flag = True
                print(clan.memberList[i].name + ' account does not exist')
                continue
            if 'data' not in list(profile['Response']['metrics']) or 'data' not in list(profile['Response']['characterProgressions']):  # private profile
                privacy_flag = True
                print(clan.memberList[i].name + ' has their profile set to private')
                continue

            metrics = profile['Response']['metrics']['data']['metrics']

            if GOS_MS_HASH in metrics.keys():  # check to see if GOS completions is present, this fails if DLC is not owned (I think)
                curr_gos = metrics.get(GOS_MS_HASH)['objectiveProgress']['progress']
            if DSC_MS_HASH in metrics.keys():
                curr_dsc = metrics.get(DSC_MS_HASH)['objectiveProgress']['progress']
            if LW_MS_HASH in metrics.keys():
                curr_lw = metrics.get(LW_MS_HASH)['objectiveProgress']['progress']

            progression_data = profile['Response']['characterProgressions']['data']  # CLAN REWARD
            for j in range(len(progression_data)):  # iterate over characters
                if not clan_engram_flag or not crucible_flag:  # skip iteration if engram and live fire already completed/claimed
                    milestones = progression_data[list(progression_data)[j]]['milestones']
                    clan_engram_flag = check_milestone(CLAN_ENGRAM_MS_HASH, CLAN_ENGRAM_OBJ_HASH)
                    if 8 < len(milestones.keys()):  # require certain progression to have live-fire available (see mod alt accounts) if we skip this check then the 'picked up' check below will pass
                        crucible_flag = check_milestone(CRUCIBLE_MS_HASH, CRUCIBLE_OBJ_HASH)

            print(clan.memberList[i].name + ' || ID: ' + clan.memberList[i].membershipId + ' || GOS: ' + str(curr_gos) + ' || DSC: ' + str(curr_dsc) + ' || LW: '
                  + str(curr_lw) + ' || CLAN: ' + str(clan_engram_flag) + ' || CRUCIBLE: ' + str(crucible_flag))
