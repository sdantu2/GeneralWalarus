import asyncio
import discord
from discord.ext.commands import Cog
from discord.ext import commands
import discord.utils
import database as db
from datetime import timedelta, datetime
from typing import cast
from utilities import printlog

class ArchiveCog(Cog, name="Archive"):
    """ Class containing commands pertaining to archiving general chat """
   
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
   
    @commands.command(name="archivegeneral", aliases=["archive"])
    async def test_archive_general(self, ctx: commands.Context, general_cat_name=None, archive_cat_name="Archive", freq=2) -> None:
        """ Command that manually runs archive function for testing purposes """
        if ctx.guild is None: 
            raise Exception("ctx.guild is None")
        if ctx.author.id == ctx.guild.owner_id:
            archive_name = db.update_next_archive_date(timedelta(weeks=2))
            await self.archive_general(ctx.guild, archive_name, general_cat_name=general_cat_name, archive_cat_name=archive_cat_name)
        else:
            await ctx.send("Only the owner can use this command")
            
    @commands.command(name="nextarchivedate", aliases=["nextarchive"])
    async def next_archive_date_command(self, ctx: commands.Context) -> None:
        """ Command that sends the date of the next general chat archive. 
            Assumes global archive date """
        if ctx.guild is None: 
            raise Exception("ctx.guild is None")
        await ctx.send("Next archive date: " + str(db.get_next_archive_date()))
        
    async def archive_general(self, guild: discord.Guild, archive_name: str, general_cat_name=None, archive_cat_name="Archive") -> None:
        """ Houses the actual logic of archiving general chat """
        try:
            general_category = cast(discord.CategoryChannel, discord.utils.get(guild.categories, name=general_cat_name))
            archive_category = cast(discord.CategoryChannel, discord.utils.get(guild.categories, name=archive_cat_name))
            chat_to_archive = cast(discord.TextChannel, discord.utils.get(guild.text_channels, name="general"))
            await chat_to_archive.move(beginning=True, category=archive_category, sync_permissions=True)
            await chat_to_archive.edit(name=archive_name)
            new_channel = await guild.create_text_channel("general", category=general_category)
            await new_channel.send("good morning @everyone")   
        except Exception as ex:
            printlog(str(ex))
            
    async def repeat_archive(self, freq: timedelta) -> None:
        """ Handles repeatedly archiving general chat """
        await self.sleep_until_archive()
        while True:
            archive_name: str = db.update_next_archive_date(freq)
            for guild in self.bot.guilds:
                now = datetime.now()
                try:
                    await self.archive_general(guild=guild, archive_name=archive_name)
                    printlog(str(now) + f": general archived in '{guild.name}' (id: {guild.id})")
                except Exception as ex:
                    printlog(str(now) + f": there was an error archiving general in '{guild.name}' (id: {guild.id}): {str(ex)}")
            await self.sleep_until_archive()

    async def sleep_until_archive(self) -> None:
        """ Handles waiting for the next archive date """
        now = datetime.now()
        then = db.get_next_archive_date()
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)