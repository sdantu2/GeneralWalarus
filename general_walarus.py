import asyncio
from datetime import datetime, date, timedelta
from db_handler import DbHandler
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import os

# Setup
load_dotenv()
bot = commands.Bot(command_prefix="$")
db = DbHandler(os.getenv("DB_CONN_STRING"))
DATE_FILE = os.getenv("NEXT_ARCHIVE_DATE_FILE")

# Prints in console when bot is ready to be used
@bot.event
async def on_ready() -> None:
    print("General Walarus is up and ready in {} server(s)".format(len(bot.guilds)))
    if os.getenv("ENV_NAME") == "production":
        for server in bot.guilds:
            announce_chat: discord.TextChannel = discord.utils.get(server.text_channels, name="general")
            announce_chat = server.channels.pop(0) if announce_chat == None else announce_chat
            await announce_chat.send("A new version of me just rolled out @everyone")

@bot.event
async def on_message(message: discord.Message) -> None:
    db.log_user_stat(message.guild, message.author, "sent_messages")
    for user in message.mentions:
        db.log_user_stat(message.guild, user, "mentioned")
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    print('General Walarus joined guild "{}" (id: {})'.format(guild.name, guild.id))
    db.log_server(guild)
    await repeat_archive(guild)

# Command to manually run archive function for testing purposes
@bot.command(name="archivegeneral")
async def test_archive_general(ctx: commands.Context, general_cat_name=None, 
                               archive_cat_name="Archive", freq=2) -> None:
    if ctx.author.id == ctx.guild.owner_id:
        await archive_general(ctx.guild, general_cat_name=general_cat_name, 
                              archive_cat_name=archive_cat_name, freq=freq)
    else:
        await ctx.send("Only the owner can use this command")
        
# Dummy command
@bot.command(name="bruh")
async def bruh(ctx: commands.Context) -> None:
    await ctx.send("bruh")
    
@bot.command(name="echo")
async def echo(ctx: commands.Context, *words) -> None:
    message = ""
    for word in words:
        message += word + " "
    await ctx.send(message)
    
@bot.command(name="intodatabase", aliases=["intodb"])
async def log_server_into_database(ctx: commands.Context):
    if ctx.author.id == ctx.guild.owner_id:
        created_new = db.log_server(ctx.guild)
        if created_new:
            await ctx.send("Logged this server into the database") 
        else: 
            await ctx.send("Updated this server in database")
    else:
        await ctx.send("Only the owner can use this command")

@bot.command(name="join", aliases=["capture", "connect"])
async def join_vc(ctx: commands.Context):         
    voice_state: discord.VoiceState = ctx.author.voice
    voice_client: discord.VoiceClient
    if voice_state != None:
        voice_channel: discord.VoiceChannel = voice_state.channel
        try:
            voice_client = await voice_channel.connect()
        except:
            curr_voice_client: discord.VoiceClient = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            voice_client = await curr_voice_client.move_to(voice_channel)
    else:
        await ctx.send("You're not connected to a voice channel")
    
@bot.command(name="leave", aliases=["stopstalking"])
async def leave_vc(ctx: commands.Context):
    voice_client: discord.VoiceClient = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    if voice_client != None:
        await voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel")
        
@bot.command(name="nextarchivedate", aliases=["archivedate"])
async def next_archive_date_command(ctx: commands.Context) -> None:
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("Next archive date: " + 
                       str(get_next_archive_date(DATE_FILE)))
    else:
        await ctx.send("Only the owner can use this command")

# Get the current time that is being read
@bot.command(name="time")
async def time(ctx: commands.Context) -> None:
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("Current date/time on the server: " + str(datetime.now()))
    else:
        await ctx.send("Only the owner can use this command")

# Handles the actual archiving of general chat
async def archive_general(guild: discord.Guild, general_cat_name=None, 
                          archive_cat_name="Archive", freq=2) -> None:
    general_category = discord.utils.get(guild.categories, name=general_cat_name)
    archive_category = discord.utils.get(guild.categories, name="Archive")
    old_general_chat = discord.utils.get(guild.text_channels, name="general")
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
    then = get_next_archive_date(DATE_FILE)
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
        update_next_archive_date(DATE_FILE, now, weeks=2)
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
        
bot.run(os.getenv("BOT_TOKEN"))