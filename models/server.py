from discord import Guild, User

class Server:
    """ Class that encapsulates a Guild object and additional info about a server """
    
    def __init__(self, guild: Guild, rshuffle: list[str], ushuffle: list[User]) -> None:
        self.guild: Guild = guild
        """ Pycord Guild object associated with this server """
        self.rshuffle: list[str] = rshuffle
        """ String list of roles involved in role change """
        self.ushuffle: list[User] = ushuffle
        """ List of users involved in role change """
        self.archive_int: int = 2
        """ General chat archive interval (in weeks) """
        self.rc_int: int = 3
        """ Role change interval (in minutes) """
        self.timezone: str = "US/Eastern"
        """ Timezone of server """