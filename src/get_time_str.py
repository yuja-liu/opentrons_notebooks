import pytz, datetime

def get_time_str(tz_str = "America/Chicago"):
    "Return the time str for current time of given time zone"
    
    tz = pytz.timezone(tz_str)
    tz_now = datetime.datetime.now(tz)
    return tz_now.strftime("%m/%d/%y %H:%M:%S")