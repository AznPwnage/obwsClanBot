from datetime import datetime, timedelta


def get_week_start_as_str(dt):
    dt = datetime.strptime(dt, '%Y-%m-%d')
    week_start = get_week_start(dt)
    return f'{week_start:%Y-%m-%d}'


def get_week_start(dt):
    day_number = dt.weekday()  # returns 0 for Mon, 6 for Sun
    if 1 < day_number:  # diff from previous Tuesday
        return (dt - timedelta(days=day_number-1)).replace(hour=17, minute=00, second=0, microsecond=0)
    if 1 == day_number:  # check whether past reset or not
        if 17 <= dt.hour:  # past reset
            return dt.replace().replace(hour=17, minute=00, second=0, microsecond=0)
        else:  # not past reset
            return (dt - timedelta(days=7)).replace(hour=17, minute=00, second=0, microsecond=0)
    return (dt - timedelta(days=6)).replace(hour=17, minute=00, second=0, microsecond=0)  # case of Monday being current day


def get_weeks_looked_back(old_date_str):
    old_week_start = datetime.strptime(old_date_str, '%Y-%m-%d')
    curr_week_start = get_week_start(datetime.now())
    return (curr_week_start - old_week_start).days / 7
