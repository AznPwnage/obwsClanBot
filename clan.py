import pandas as pd


class ClanGroup:
    def __init__(self):
        clan_list_df = pd.read_csv('clan_list.csv')
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
                 gos=None, dsc=None, lw=None, clan_engram=None, crucible_engram=None, exo_challenge=None, banshee=None,
                 drifter=None, zavala=None, variks=None, exo_stranger=None, trials3=None, empire_hunt=None,
                 nightfall=None, deadly_venatics=None, strikes=None, nightfall_100k=None, gambit=None,
                 crucible_playlist=None, crucible_glory=None, trials5=None, trials7=None, privacy=None,
                 account_not_exists=None, low_light=None):
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
        self.exo_challenge = exo_challenge
        self.banshee = banshee
        self.drifter = drifter
        self.zavala = zavala
        self.variks = variks
        self.exo_stranger = exo_stranger
        self.trials3 = trials3
        self.empire_hunt = empire_hunt
        self.nightfall = nightfall
        self.deadly_venatics = deadly_venatics
        self.strikes = strikes
        self.nightfall_100k = nightfall_100k
        self.gambit = gambit
        self.crucible_playlist = crucible_playlist
        self.crucible_glory = crucible_glory
        self.trials5 = trials5
        self.trials7 = trials7
        self.privacy = privacy
        self.account_not_exists = account_not_exists
        self.low_light = low_light
