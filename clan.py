import pandas as pd


class ClanGroup:
    def __init__(self):
        clan_list_df = pd.read_csv('test_clan_list2.csv')
        # clan_list_df = pd.read_csv('clan_list.csv')
        self.clan_list = []
        for index, row in clan_list_df.iterrows():
            self.clan_list.append(Clan(row['name'], str(row['groupId']), row['type']))

    def get_clan_list(self):
        return self.clan_list


class Clan:
    def __init__(self, name, group_id, clan_type):
        self.name = name
        self.group_id = group_id
        self.clan_type = clan_type
        self.memberList = []

    def add_member(self, name, membership_type, membership_id):
        self.memberList.append(ClanMember(name, membership_id, self.name, membership_type, self.clan_type))


class ClanMember:
    def __init__(self, name, membership_id, clan_name, membership_type, clan_type, score=None, gos=None, dsc=None, lw=None, clan_engram=None, crucible_engram=None, privacy=None, account_not_exists=None):
        self.name = name
        self.membership_id = membership_id
        self.clan_name = clan_name
        self.membership_type = membership_type
        self.clan_type = clan_type
        self.score = score
        self.gos = gos
        self.dsc = dsc
        self.lw = lw
        self.clan_engram = clan_engram
        self.crucible_engram = crucible_engram
        self.privacy = privacy
        self.account_not_exists = account_not_exists
