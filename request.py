import grequests


class BungieApiCall:
    def __init__(self):
        with open('key.txt', 'r') as apiKey:
            self.headers = {"X-API-Key": apiKey.read()}
        self.api_root = 'https://www.bungie.net/Platform/'

    def get_header(self):
        return self.headers

    def get_api_root(self):
        return self.api_root

    def api_call(self, url_string_1, url_param_1, url_string_2, url_param_2="", params={}):
        return grequests.get(self.get_api_root() + url_string_1 + url_param_1 + url_string_2 + url_param_2,
                             params=params, headers=self.get_header())

    def get_clan_members(self, clan_group):
        clan_members_requests = (self.api_call('GroupV2/', clan.groupId, '/Members') for clan in clan_group)
        return grequests.map(clan_members_requests)

    def get_profile(self, member_list):
        profile_requests = (
            self.api_call('Destiny2/', member.membershipType, '/Profile/', member.membershipId,
                          {'components': [202, 1100]})
            for member in member_list)
        return grequests.map(profile_requests)
