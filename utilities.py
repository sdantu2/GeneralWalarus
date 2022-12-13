from datetime import datetime
from pytz import timezone

def timef(dt: datetime) -> str:
    """ Format time of given datetime (ex. 02:47 PM CST) """
    return dt.strftime("%I:%M %p %Z")