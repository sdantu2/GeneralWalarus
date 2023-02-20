import discord
from discord.ext.commands import Cog
from discord.ext import commands
import database as db
from typing import cast
from utilities import printlog

class _TimeSpan():
    def __init__(self, seconds: int):
        self.days = seconds // 86400
        self.days_unit = "day" if self.days == 1 else "days"
        seconds -= self.days * 86400
        self.hours = seconds // 3600
        self.hours_unit = "hour" if self.hours == 1 else "hours"
        seconds -= self.hours * 3600
        self.minutes = seconds // 60
        self.minutes_unit = "minute" if self.minutes == 1 else "minutes"
        seconds -= self.minutes * 60
        self.seconds = seconds
        self.seconds_unit = "second" if self.seconds == 1 else "seconds"
        
class StatisticsCog(Cog, name="Statistics"):
    """ Class containing General Walarus' statistics commands """
    
    @commands.command(name="messages", aliases=["mymessages"])
    async def messages(self, ctx: commands.Context, user: discord.User = None) -> None: #type: ignore
        """ Command that sends back how many messages user has sent (v2) """
        try:
            guild = ctx.guild
            user = cast(discord.User, ctx.author) if user is None else user
            if guild != None:
                query = cast(dict, db.get_user_stats(guild, user.id, "sent_messages"))
                messages = int(query["sent_messages"])
                if user.id == ctx.author.id:
                    await ctx.send(f"You've sent {messages:,} messages")
                else:
                    await ctx.send(f"{user.name} has sent {messages:,} messages")
        except Exception as e:
            printlog(str(e))
            await ctx.send("I pooped my pants...try again")
            
        
    @commands.command(name="vctime", aliases=["timeinvc"])
    async def vctime(self, ctx: commands.Context, user: discord.User = None) -> None: #type: ignore
        """ Command that sends back how much time user has spent in VC (v2) """
        try:
            guild = ctx.guild
            user = cast(discord.User, ctx.author) if user is None else user 
            if guild != None:
                query = cast(dict, db.get_user_stats(guild, user.id, "time_in_vc"))
                seconds = int(query["time_in_vc"])
                time: _TimeSpan = _TimeSpan(seconds)
                msg = f"You've spent" if user.id == ctx.author.id else f"{user.name} has spent"
                if time.days > 0:
                    msg += (f" {time.days} {time.days_unit}, {time.hours} {time.hours_unit}, "
                            f"{time.minutes} {time.minutes_unit}, and {time.seconds} "
                            f"{time.seconds_unit} in voice channel")
                elif time.hours > 0:
                    msg += (f" {time.hours} {time.hours_unit}, {time.minutes} "
                            f"{time.minutes_unit}, and {time.seconds} "
                            f"{time.seconds_unit} in voice channel")
                elif time.minutes > 0:
                    msg += (f" {time.minutes} {time.minutes_unit}, and {time.seconds} "
                            f"{time.seconds_unit} in voice channel")
                else:
                    msg += f" {time.seconds} {time.seconds_unit} in voice channel"
                await ctx.send(msg)
        except Exception as e:
            printlog(str(e))
            await ctx.send("I pooped my pants...try again")

