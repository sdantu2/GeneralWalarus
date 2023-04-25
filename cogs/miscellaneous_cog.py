from discord.ext.commands import Cog
from discord.ext import commands
import database as db
from datetime import datetime
from globals import servers
from models import Server
from utilities import now_time, timef
from typing import cast

class MiscellaneousCog(Cog, name="Miscellaneous"):
    """ Class containing General Walarus' miscellaneous commands """
    
    @commands.command(name="bruh")
    async def bruh(self, ctx: commands.Context) -> None:
        """ Stupid command that just has General Walarus send 'bruh' """
        await ctx.send("bruh")
        
    @commands.command(name="echo", aliases=["say"])
    async def echo(self, ctx: commands.Context, *words) -> None:
        """ Command that has General Walarus repeat back command args """
        message = ""
        for word in words:
            message += word + " "
        await ctx.send(message)
        
    @commands.command(name="intodatabase", aliases=["intodb"])
    async def log_server_into_database(self, ctx: commands.Context):
        """ Command to manually log a server into the database """
        if ctx.guild is None: 
            raise Exception("ctx.guild is None")
        if ctx.author.id == ctx.guild.owner_id:
            created_new = db.log_server(ctx.guild)
            if created_new:
                await ctx.send("Logged this server into the database") 
            else: 
                await ctx.send("Updated this server in database")
        else:
            await ctx.send("Only the owner can use this command")
            
    @commands.command(name="datetime", aliases=["date", "time"])
    async def time(self, ctx: commands.Context) -> None:
        """ Get the current datetime in the timezone of the given server """
        if ctx.guild is None:
            raise Exception("ctx.guild is None")
        server: Server = cast(Server, servers.get(ctx.guild))
        now: datetime = now_time(server)
        await ctx.send(f"It is {now.date()}, {timef(now)}")

    @commands.command(name="test")
    async def test(self, ctx: commands.Context) -> None:
        """ Command reserved for testing purposes """
        if ctx.guild is None:
            raise Exception("ctx.guild is None")
        # if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Boi wat you tryna test 🫱")