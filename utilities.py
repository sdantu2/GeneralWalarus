from datetime import datetime
from models.server import Server
from pytz import timezone

def timef(dt: datetime) -> str:
    """ Format time of given datetime (ex. 02:47 PM CST) """
    return dt.strftime("%I:%M %p %Z")

def now_time(server: Server) -> datetime:
    """Gives datetime.now() with timezone of given server"""
    return datetime.now(tz=timezone(server.timezone))