import json

import pandas as pd


class ClanGroup:
    def __init__(self):
        clan_list_df = pd.read_csv('clan_list.csv')
        self.clans = {}
        for index, row in clan_list_df.iterrows():
            self.clans[row['name']] = (Clan(row['name'], str(row['groupId']), row['type'], bool(row['lookback_only'])))

    def get_clans(self):
        return self.clans


class Clan:
    def __init__(self, name, group_id, clan_type, lookback_only):
        self.name = name
        self.group_id = group_id
        self.clan_type = clan_type
        self.lookback_only = lookback_only
        self.memberList = []

    def add_member(self, name, membership_type, membership_id, bungie_name):
        self.memberList.append(ClanMember(name, membership_id, self.name, membership_type, self.clan_type, bungie_name))


class ClanMember:
    def __init__(self, name, membership_id, clan_name, membership_type, clan_type, bungie_name):
        self.name = name
        self.membership_id = membership_id
        self.clan_name = clan_name
        self.membership_type = membership_type
        self.clan_type = clan_type
        self.bungie_name = bungie_name

    def get(self, attr_name):
        return getattr(self, attr_name)

    def set(self, attr_name, attr_val):
        return setattr(self, attr_name, attr_val)

    def flatten(self):
        attrs = self.__dict__
        header = []
        values = []
        for key, value in attrs.items():
            header, value = recursive_flatten(header, values, key, value)
        return header, value

    def to_json(self):
        attr_dict = {}
        h, v = self.flatten()
        for i in range(len(h)):
            attr_dict[h[i]] = v[i]
        return attr_dict


def recursive_flatten(header, values, key, value):
    if type(value) == dict:
        for k, v in value.items():
            recursive_flatten(header, values, key + '_' + k, v)
    else:
        header.append(key)
        values.append(value)
    return header, values


def build_clan_members_from_json_string(json_string):
    json_strings = json_string.split('\r\n')[:-1]
    mem_list = []
    for json_string in json_strings:
        json_obj = json.loads(json_string)
        m = ClanMember(None, None, None, None, None, None)
        for k, v in json_obj.items():
            m.set(k, v)
        mem_list.append(m)
    return mem_list
