from datetime import datetime
import discord

class Server:
    def __init__(self, guild: discord.Guild) -> None:
        self.__server_id = guild.id
        self.__bot_join_datetime = datetime.now()
        
        
        
        
        