import urllib

import grequests
import requests as r


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

    def get_clan_members(self, clan):
        return r.get(self.get_api_root() + 'GroupV2/' + clan.group_id + '/Members', headers=self.get_header())

    def get_profiles(self, member_list):
        profile_requests = (
            self.api_call('Destiny2/', member.membership_type, '/Profile/', member.membership_id,
                          {'components': [100, 200, 202, 204, 1100]})
            for member in member_list)
        return grequests.map(profile_requests)

    def get_profile(self, membership_type, membership_id):
        return r.get(self.get_api_root() + 'Destiny2/' + membership_type + '/Profile/' + membership_id,
                     params={'components': [100, 200, 202, 204, 1100]}, headers=self.get_header()).json()

    def search_player(self, bungie_name):
        return r.post(self.get_api_root() + 'User/Search/GlobalName/-1/' + urllib.parse.quote(bungie_name), headers=self.get_header()).json()

    def get_activity_history(self, membership_type, membership_id, character_id, activity_type, page_limit):
        activities = []
        page = 0
        while True:
            response = r.get(
                self.get_api_root() + 'Destiny2/' + membership_type + '/Account/' + membership_id + '/Character/' + character_id + '/Stats/Activities',
                params={'page': page, 'mode': activity_type, 'count': 250}, headers=self.get_header()).json()
            if 'Response' not in response.keys():
                break
            if 'activities' in response['Response'].keys():
                activities.extend(response['Response']['activities'])
                if 250 > len(response['Response']['activities']):
                    break
            if page >= page_limit > 0:
                # We use page_limit = 2 for weekly score generation purposes since we assume that the activities are
                # returned in reverse chronological order, in which case it's safe to assume a player cannot have done
                # more than 500 (2 pages) dungeons or raids per character in a week. Number may vary if this method is
                # used for other activities.
                # page_limit = 0 just allows for the method to pull all activity history for the call.
                break
            page += 1
        return activities

    def get_aggregate_activity_stats(self, membership_type, membership_id, character_id):
        return r.get(self.get_api_root() + 'Destiny2/' + membership_type + '/Account/' + membership_id + '/Character/' + character_id + '/Stats/AggregateActivityStats/', headers=self.get_header()).json()

    def get_linked_profiles(self, membership_type, membership_id, get_all_memberships):
        return r.get(self.get_api_root() + 'Destiny2/' + membership_type + '/Profile/' + membership_id + '/LinkedProfiles/?getAllMemberships=' + get_all_memberships, headers=self.get_header()).json()

    def get_pgcr(self, activity_id):
        return r.get(self.get_api_root() + 'Destiny2/Stats/PostGameCarnageReport/' + activity_id, headers=self.get_header()).json()

    def get_public_milestones(self):
        return r.get(self.get_api_root() + 'Destiny2/Milestones/', headers=self.get_header()).json()
