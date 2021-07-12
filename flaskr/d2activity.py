class D2Activity:
    def __init__(self):
        self.ft_members = None
        self.pgcr_id = None
        self.mode = None
        self.date = None
        self.invalid_reason = None

    def ft_members_to_string(self):
        full_string = ''
        for ft_member in self.ft_members:
            if len(full_string) > 0:
                full_string += ', ' + ft_member.display_name
            else:
                full_string += ft_member.display_name
        return full_string


class D2ActivityPlayer:
    def __init__(self):
        self.membership_id = None
        self.display_name = None
        self.clan_name = None
        self.clan_id = None
