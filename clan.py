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
    def __init__(self, name, group_id, clan_type):
        self.name = name
        self.groupId = group_id
        self.clanType = clan_type
        self.totalMember = 0
        self.memberList = []

    def setTotalMember(self, total_member):
        self.totalMember = total_member

    def addMember(self, name, membership_type, membership_id):
        if self.clanType == 'Regional':
            clan_score_change = -10
        else:
            clan_score_change = 0
        self.memberList.append(ClanMember(name, membership_type, membership_id, clan_score_change))


class ClanMember:
    def __init__(self, name, membership_type, membership_id, clan_score_change):
        self.name = name
        self.membership_type = membership_type
        self.membership_id = membership_id
        self.clan_score_change = clan_score_change
