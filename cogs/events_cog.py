import discord
from discord.ext.commands import Cog
from discord.ext import commands
import discord.utils
import database as db
from datetime import timedelta
from typing import cast
from models import Server
from globals import servers

class EventsCog(Cog, name="Events"):
    """ Class containing implementations for Discord bot events """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Event that runs once General Walarus is up and running (v2) """
        rshuffle: list[str] = ["CEO of the Republic", 
                "Indian of the Republic",
                "The Softest of the Softest Carries", 
                "Chinese of the Republic", 
                "Economist of the Republic", 
                "Pope of the Republic"]
        ushuffle: list[discord.User] = []
        for guild in self.bot.guilds:
            servers[guild] = Server(guild, rshuffle, ushuffle)
        print(f"General Walarus active in {len(servers)} server(s)")
        await self.bot.get_cog("Archive").repeat_archive(timedelta(weeks=2)) # type: ignore
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """ Event that runs whenever a user sends something in a text channel (v2) """
        if message.guild is None:
            return
        db.log_user_stat(message.guild, cast(discord.User, message.author), "sent_messages")
        for user in message.mentions:
            db.log_user_stat(message.guild, cast(discord.User, user), "mentioned")
 
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """ Event that runs whenever General Walarus joins a new server\n 
            Servers information is added to the database (v2) """
        print(f"General Walarus joined guild '{guild.name}' (id: {guild.id})")
        db.log_server(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """ Event that runs when General Walarus gets removed from a server.\n
            Server information is deleted from database (v2) """
        print(f"General Walarus has been removed from guild '{guild.name}' (id: {guild.id})")
        print(f"{db.remove_discord_server(guild)} documents removed from database")

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        """ Event that runs when a server's information gets updated.\n
            Server information gets updated in the database (v2) """
        db.log_server(after)
        print(f"Server {before.id} was updated")
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, ex: commands.CommandError):
        if type(ex) == commands.CommandNotFound:
            await ctx.send("That ain't a command my brother in Christ")