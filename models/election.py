from datetime import datetime, timedelta
import discord
from utilities import timef
from server import Server

class Election:
    """ Class that encapsulates election info per guild """
    def __init__(self, server: Server, start: datetime, roles: list[str], members: list[discord.User]) -> None:
        self.server: Server = server
        """ Server that election is occurring in """
        self.next_time: datetime = start + timedelta(minutes=server.rc_int)
        """ Datetime of next election """
        self.roles = roles
        """ List of roles that are to be shuffled """
        self.members = members
        """ List of members whose roles are to be shuffled """
        
    def __str__(self) -> str:
        guild: discord.Guild = self.server.guild
        return f"Guild '{guild.name}' (id: {guild.id}), next_time at {timef(self.next_time)}"