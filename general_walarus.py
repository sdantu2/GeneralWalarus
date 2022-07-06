import asyncio
import config as cfg
from datetime import datetime, date, timedelta
import discord
import json
from discord.ext import commands

client = commands.Bot(command_prefix="$")

# Prints in console when bot is ready to be used
@client.event
async def on_ready() -> None:
    print("General Walarus is up and ready")

@client.event
async def on_guild_join(guild: discord.Guild) -> None:
    print('General Walarus joined guild "{}" (id: {})'.format(guild.name, guild.id))
    await repeat_archive(guild)

# Dummy command
@client.command(name="bruh")
async def bruh(ctx: commands.Context) -> None:
    await ctx.send("bruh")
    
# Get the current time that is being read
@client.command(name="time")
async def time(ctx: commands.Context) -> None:
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("Current date/time: " + str(datetime.now()))
    else:
        await ctx.send("Only the owner can use this command")

# Command to manually run archive function for testing purposes
@client.command(name="archivegeneral")
async def test_archive_general(ctx: commands.Context, general_cat_name=None, 
                               archive_cat_name="Archive", freq=2) -> None:
    if ctx.author.id == ctx.guild.owner_id:
        await archive_general(ctx.guild, general_cat_name=general_cat_name, 
                              archive_cat_name=archive_cat_name, freq=freq)
    else:
        await ctx.send("Only the owner can use this command")
        
@client.command(name="nextarchivedate", aliases=["archivedate"])
async def next_archive_date_command(ctx: commands.Context) -> None:
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("Next archive date: " + 
                       str(get_next_archive_date(cfg.NEXT_ARCHIVE_DATE_FILE)))
    else:
        await ctx.send("Only the owner can use this command")

# Handles the actual archiving of general chat
async def archive_general(guild: discord.Guild, general_cat_name=None, 
                          archive_cat_name="Archive", freq=2) -> None:
    general_category = discord.utils.get(guild.categories, name=general_cat_name)
    archive_category = discord.utils.get(guild.categories, name="Archive")
    old_general_chat = discord.utils.get(guild.channels, name="general")
    try:
        await old_general_chat.move(beginning=True, category=archive_category, 
                                    sync_permissions=True)   
    except:
        print('Error moving general chat in {} (id: {})'.format(guild.name, 
                                                                guild.id))
    await old_general_chat.edit(name=get_archived_name())
    new_channel = await guild.create_text_channel("general", 
                                                  category=general_category)
    await new_channel.send("good morning @everyone")

# Returns the archived name of the archived general chat
def get_archived_name() -> str:
    today = date.today()
    month = str(today.month)
    day = str(today.day)
    year = str(today.year)
    return "general-" + month + "-" + day + "-" + year[len(year) - 2:]

# Handles repeatedly archiving general chat
async def repeat_archive(guild: discord.Guild) -> None:
    now = datetime.now()
    then = get_next_archive_date(cfg.NEXT_ARCHIVE_DATE_FILE)
    wait_time = (then - now).total_seconds()
    await asyncio.sleep(wait_time)
    while True:
        await archive_general(guild=guild)
        now = datetime.now()
        then = now + timedelta(weeks=2)
        wait_time = (then - now).total_seconds()
        if discord.utils.get(guild.channels, name=get_archived_name()):
            print(str(now) + ': general archived in "{}" (id: {})'.format(guild.name, guild.id))
        else:
            print(str(now) + ": there was an error archiving general")
        update_next_archive_date(cfg.NEXT_ARCHIVE_DATE_FILE, now, weeks=2)
        await asyncio.sleep(wait_time)

# Returns the next archive datetime from a file
def get_next_archive_date(filename: str) -> datetime:
    with open(filename, "r") as f:
        data = json.load(f)
        return datetime(data["year"], data["month"], data["day"], data["hour"], 
                        data["minute"], data["second"])

# Updates the file with the next archive date
def update_next_archive_date(filename, old_date, seconds=0, minutes=0, hours=0, 
                             days=0, weeks=0) -> None:
    new_date: datetime = old_date + timedelta(seconds=seconds, minutes=minutes, 
                                             hours=hours, days=days, weeks=weeks)
    date_json = {
        "year": new_date.year,
        "month": new_date.month,
        "day": new_date.day,
        "hour": new_date.hour,
        "minute": new_date.minute,
        "second": new_date.second
    }
    with open(filename, "w") as f:
        json.dump(date_json, f)
        
client.run(cfg.BOT_TOKEN)

