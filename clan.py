import pandas as pd


class ClanGroup:
    def __init__(self):
        clan_list_df = pd.read_csv('clan_list.csv')
        self.clan_list = []
        for index, row in clan_list_df.iterrows():
            self.clan_list.append(Clan(row['name'], str(row['groupId']), row['type']))

    def get_clan_list(self):
        return self.clan_list


class Clan:
    def __init__(self, name, groupId, clanType):
        self.name = name
        self.groupId = groupId
        self.clanType = clanType
        self.totalMember = 0
        self.memberList = []

    def setTotalMember(self, totalMember):
        self.totalMember = totalMember

    def addMember(self, name, membershipType, membershipId):
        if self.clanType == 'Regional':
            clanScoreGained = -10
        else:
            clanScoreGained = 0
        self.memberList.append(ClanMember(name, membershipType, membershipId, clanScoreGained))


class ClanMember:
    def __init__(self, name, membershipType, membershipId, clanScoreGained):
        self.name = name
        self.membershipType = membershipType
        self.membershipId = membershipId
        self.clanScoreGained = clanScoreGained
