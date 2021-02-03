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

        profileResponses = request.BungieApiCall().get_profile(clan.memberList)

        for i in range(len(clan.memberList)):
            member = clan.memberList[i]
            print(member.name)
            profileResponse = profileResponses[i].json()['Response']['characterProgressions']['data']
            for character in profileResponse.keys():
                characterMilestones = profileResponse[character]['milestones']
                print(len(characterMilestones))

