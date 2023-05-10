from datetime import datetime
from models.server import Server
from pytz import timezone

def printlog(message: str) -> None:
    """ Prints input message to log file """
    log_file = open("log", "a")
    log_file.write(message + "\n")
    log_file.close()
    
def timef(dt: datetime) -> str:
    """ Format time of given datetime (ex. 02:47 PM CST) """
    return dt.strftime("%I:%M %p %Z")

def now_time(server: Server) -> datetime:
    """ Gives datetime.now() with timezone of given server """
    return datetime.now(tz=timezone(server.timezone))

def make_offset_aware(server: Server, dt: datetime) -> datetime:
    """ Getting datetime from DB gives offset-naive, by default, so 
    this function will convert it to offset-aware """
    result: datetime = dt.replace(tzinfo=timezone(server.timezone))
    return result

def get_server_prefix() -> str:
    """ Returns the given server's command prefix from DB 
    (this is just a placeholder for now) """
    result = "$"
    return result