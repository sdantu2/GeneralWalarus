import discord
from discord.ext.commands import Cog
from discord.ext import commands
import database as db
from typing import cast

class StatisticsCog(Cog, name="Statistics"):
    """ Class containing General Walarus' statistics commands """
    
    @commands.command(name="messages", aliases=["mymessages"])
    async def messages(self, ctx: commands.Context, user: discord.User = None) -> None:
        """ Command that sends back how many messages user has sent (v2) """
        try:
            guild = ctx.guild
            user = cast(discord.User, ctx.author) if user is None else user
            if guild != None:
                query = cast(dict, db.get_user_stats(guild, user.id, "sent_messages"))
                messages = int(query["sent_messages"])
                await ctx.send(f"You've sent {messages:,} messages")
        except Exception as e:
            print(str(e))
            await ctx.send("I pooped my pants...try again")
            
        
    @commands.command(name="vctime", aliases=["timeinvc"])
    async def vctime(self, ctx: commands.Context, user: discord.User = None) -> None:
        """ Command that sends back how much time user has spent in VC (v2) """
        try:
            guild = ctx.guild
            user = cast(discord.User, ctx.author) if user is None else user 
            if guild != None:
                query = cast(dict, db.get_user_stats(guild, user.id, "time_in_vc"))
                seconds = int(query["time_in_vc"])
                days = seconds // 86400
                seconds -= days * 86400
                hours = seconds // 3600
                seconds -= hours * 3600
                minutes = seconds // 60
                seconds -= minutes * 60
                unit: dict = {
                    days: "days" if days > 1 else "day",
                    hours: "hours" if hours > 1 else "hour",
                    minutes: "minutes" if minutes > 1 else "minute",
                    seconds: "seconds" if seconds > 1 or seconds == 0 else "second"
                }
                msg = f"You've spent" if user.id == ctx.author.id else f"{user.name} has spent"
                if days > 0:
                    msg += (f" {days} {unit[days]}, {hours} {unit[hours]}, {minutes} {unit[minutes]}, "
                            f"and {seconds} {unit[seconds]} in voice channel")
                elif hours > 0:
                    msg += (f" {hours} {unit[hours]}, {minutes} {unit[minutes]}, and {seconds} " 
                            f"{unit[seconds]} in voice channel")
                elif minutes > 0:
                    msg += (f" {minutes} {unit[minutes]}, and {seconds} {unit[seconds]} in "
                            f"voice channel")
                else:
                    msg += f" {seconds} {unit[seconds]} in voice channel"
                await ctx.send(msg)
        except Exception as e:
            print(str(e))
            await ctx.send("I pooped my pants...try again")
    