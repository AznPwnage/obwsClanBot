from enum import Enum


class DestinyActivity(Enum):
    gos = (3458480158, 4, 40, 1200)
    dsc = (910380154, 4, 35, 1200)
    lw = (2122313384, 4, 45, 1500)
    vog = (3881495763, 4, 45, 1500)
    vog_master = (1681562271, 4, 45, 1500)
    vow = (1441982566, 4, 45, 1500)
    vow_master = (4217492330, 4, 45, 1500)
    kf = (1374392663, 4, 45, 1500)
    kf_master = (2964135793, 4, 45, 1500)
    ron = (2381413764, 4, 45, 1200)
    poh = (2582501063, 82, None, None)
    prophecy = (1077850348, 82, None, None)
    st = (2032534090, 2, None, None)
    goa = (4078656646, 82, None, None)
    goa_master = (3774021532, 82, None, None)
    duality = (2823159265, 82, None, None)
    duality_master = (1668217731, 82, None, None)
    spire = (1262462921, 82, None, None)
    spire_master = (1801496203, 82, None, None)

    def __init__(self, activity_hash, activity_mode, threshold_kill, threshold_time):
        self.activity_hash = activity_hash
        self.activity_mode = activity_mode
        self.threshold_kill = threshold_kill
        self.threshold_time = threshold_time

    def __new__(cls, activity_hash, activity_mode, threshold_kill, threshold_time):
        entry = object.__new__(cls)
        entry.activity_hash = entry._value_ = activity_hash  # set the value, and the extra attribute
        entry.activity_mode = activity_mode
        entry.threshold_kill = threshold_kill
        entry.threshold_time = threshold_time
        return entry

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: ({self.activity_hash!r}, {self.activity_mode!r}, {self.threshold_kill!r}, {self.threshold_time!r})>'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_