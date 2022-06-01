import discord
from discord.ext import commands
import config as cfg
from datetime import datetime, date, timedelta
import asyncio

client = commands.Bot(command_prefix="$")

# Prints in console when bot is ready to be used
@client.event
async def on_ready():
    print("General Walarus is up and ready")

@client.event
async def on_guild_join(guild):
    print('General Walarus joined guild "{}" (id: {})'.format(guild.name, guild.id))
    await repeat_archive(guild)

# Dummy command
@client.command(name="bruh")
async def bruh(ctx):
    await ctx.send("bruh")
    
# Get the current time that is being read
@client.command(name="time")
async def time(ctx):
    await ctx.send("Current date/time: " + str(datetime.now()))

# Command to manually run archive function for testing purposes
@client.command(name="archivegeneral")
async def test_archive_general(ctx, general_cat_name=None, archive_cat_name="Archive", freq=2):
    if ctx.author == ctx.guild.owner:
        await archive_general(ctx.guild, general_cat_name=general_cat_name, archive_cat_name=archive_cat_name, freq=freq)
    else:
        ctx.channel.send("You don't have access to that command")

# Handles the actual archiving of general chat
async def archive_general(guild, general_cat_name=None, archive_cat_name="Archive", freq=2):
    general_category = discord.utils.get(guild.categories, name=general_cat_name)
    archive_category = discord.utils.get(guild.categories, name="Archive")
    old_general_chat = discord.utils.get(guild.channels, name="general")
    await old_general_chat.move(beginning=True, category=archive_category, sync_permissions=True)
    await old_general_chat.edit(name=get_archived_name())
    new_channel = await guild.create_text_channel("general", category=general_category)
    await new_channel.send("good morning @everyone")

# Returns the archived name of the archived general chat
def get_archived_name() -> str:
    today = date.today()
    month = str(today.month)
    day = str(today.day)
    year = str(today.year)
    return "general-" + month + "-" + day + "-" + year[len(year) - 2:]

# Handles repeatedly archiving general chat
async def repeat_archive(guild):
    NEXT_DATE_FILENAME = "next_archive_date.txt"
    now = datetime.now()
    then = get_next_archive_date(NEXT_DATE_FILENAME)
    wait_time = (then - now).total_seconds()
    await asyncio.sleep(wait_time)
    while True:
        await archive_general(guild=guild)
        now = datetime.now()
        then = now + timedelta(weeks=2)
        wait_time = (then - now).total_seconds()
        update_next_archive_date(NEXT_DATE_FILENAME, now, weeks=2)
        await asyncio.sleep(wait_time)

# Returns the next archive datetime from a file
def get_next_archive_date(filename) -> datetime:
    lines = []
    with open(filename, "r") as f:
        lines = f.readlines()
    return datetime(int(lines[0]), int(lines[1]), int(lines[2]), hour=int(lines[3]),
                    minute=int(lines[4]), second=int(lines[5]))

# Updates the file with the next archive date
def update_next_archive_date(filename, old_date, seconds=0, minutes=0, hours=0, 
                             days=0, weeks=0):
    new_date = old_date + timedelta(seconds=seconds, minutes=minutes, 
                                             hours=hours, days=days, weeks=weeks)
    with open(filename, "w") as f:
        f.write("{}\n{}\n{}\n{}\n{}\n{}".format(str(new_date.year), str(new_date.month), 
                                        str(new_date.day), str(new_date.hour), 
                                        str(new_date.minute), str(new_date.second)))
        
client.run(cfg.BOT_TOKEN)
