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
    def __init__(self, name, membership_id, clan_name, membership_type, clan_type, score=None,
                 h_gos=None, w_gos=None, t_gos=None, h_dsc=None, w_dsc=None, t_dsc=None, h_lw=None, w_lw=None, t_lw=None,
                 clan_engram=None, crucible_engram=None, privacy=None, account_not_exists=None):
        self.name = name
        self.membership_id = membership_id
        self.clan_name = clan_name
        self.membership_type = membership_type
        self.clan_type = clan_type
        self.score = score
        self.h_gos = h_gos
        self.w_gos = w_gos
        self.t_gos = t_gos
        self.h_dsc = h_dsc
        self.w_dsc = w_dsc
        self.t_dsc = t_dsc
        self.h_lw = h_lw
        self.w_lw = w_lw
        self.t_lw = t_lw
        self.clan_engram = clan_engram
        self.crucible_engram = crucible_engram
        self.privacy = privacy
        self.account_not_exists = account_not_exists
