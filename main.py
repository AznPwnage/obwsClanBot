import request
import clan

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
            profile = profile_responses[i].json()
            if profile['ErrorStatus'] != 'Success':
                account_not_exists_flag = True
                print(clan.memberList[i].name + ' account does not exist')
                continue
            if 'data' not in list(profile['Response']['metrics']) or 'data' not in list(profile['Response']['characterProgressions']):
                privacy_flag = True
                print(clan.memberList[i].name + ' has their profile set to private')
                continue
            metrics = profile['Response']['metrics']['data']['metrics']
            clan_reward_completed_flag = False
            curr_gos = 0
            curr_dsc = 0
            curr_lw = 0
            if '1168279855' in metrics.keys():
                curr_gos = metrics.get('1168279855')['objectiveProgress']['progress']  # GOS
            if '954805812' in metrics.keys():
                curr_dsc = metrics.get('954805812')['objectiveProgress']['progress']  # DSC
            if '3766204132' in metrics.keys():
                curr_lw = metrics.get('3766204132')['objectiveProgress']['progress']  # LW

            progression_data = profile['Response']['characterProgressions']['data']  # CLAN REWARD
            for j in range(len(progression_data)):
                if not clan_reward_completed_flag:
                    milestones = progression_data[list(progression_data)[j]]['milestones']
                    if '3603098564' in milestones.keys():  # not picked up
                        if '4258517136' == milestones['3603098564']['availableQuests'][0]['status']:  # completed clan xp
                            clan_reward_completed_flag = True
                    else:  # picked up
                        clan_reward_completed_flag = True

            print(clan.memberList[i].name + '|| GOS: ' + str(curr_gos) + ' || DSC: ' + str(curr_dsc) + ' || LW: '
                  + str(curr_lw) + ' || CLAN: ' + str(clan_reward_completed_flag))
