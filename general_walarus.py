import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import random
from db_handler import DbHandler
import discord
from discord.ext import commands
from discord.sinks import WaveSink
from dotenv import load_dotenv
import json
import os

# Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
load_dotenv()
bot = commands.Bot(command_prefix="$", intents=intents)
db = DbHandler(str(os.getenv("DB_CONN_STRING")))
vc_connections = {}
election_active = False
next_election_result = None

# Prints in console when bot is ready to be used
@bot.event
async def on_ready() -> None:
    print("General Walarus is up and ready in {} server(s)".format(len(bot.guilds)))
    await repeat_archive(timedelta(weeks=2))
    
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

@bot.event
async def on_guild_remove(guild: discord.Guild) -> None:
    print('General Walarus has been removed from guild "{}" (id: {})'.format(guild.name, guild.id))
    print(f"{db.remove_discord_server(guild)} documents removed from database")

@bot.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    db.log_server(after)
    print('Server {} was updated'.format(before.id))

# Command to manually run archive function for testing purposes
@bot.command(name="archivegeneral", aliases=["archive"])
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

# @bot.command(name="join", aliases=["connect", "startstalking"])
# async def join_vc(ctx: commands.Context):    
#     voice_state: discord.VoiceState = ctx.author.voice
#     voice_client: discord.VoiceClient
#     if voice_state != None:
#         voice_channel: discord.VoiceChannel = voice_state.channel
#         try:
#             voice_client = await voice_channel.connect()
#         except:
#             curr_voice_client: discord.VoiceClient = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
#             voice_client = await curr_voice_client.move_to(voice_channel)
#         vc_connections.update({ctx.guild.id: voice_client})
#         voice_client.start_recording(WaveSink(), once_stop_recording, voice_client.channel, ctx.channel)
#         print(f"started recording for {voice_client.channel.name}")
#     else:
#         await ctx.send("You're not connected to a voice channel")

# @bot.command(name="clip", aliases=["capture", "clipthatshit"])
# async def clip_vc(ctx: commands.Context, *args):
#     voice_client: discord.VoiceClient = vc_connections[ctx.guild.id]
#     if voice_client != None:
#         voice_client.stop_recording()
#         voice_client.start_recording(WaveSink(), once_stop_recording, voice_client.channel, ctx.channel)
#     else:
#         await ctx.send(f"I need to be in a voice channel {ctx.author}")

# @bot.command(name="leave", aliases=["disconnect", "stopstalking"])
# async def leave_vc(ctx: commands.Context):
#     voice_client: discord.VoiceClient = vc_connections[ctx.guild.id]
#     if voice_client != None:
#         del vc_connections[ctx.guild.id]
#         await voice_client.disconnect()
#         voice_client.stop_recording()
#     else:
#         await ctx.send("I'm not in a voice channel")
        
@bot.command(name="nextarchivedate", aliases=["archivedate"])
async def next_archive_date_command(ctx: commands.Context) -> None:
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("Next archive date: " + str(db.get_next_archive_date()))
    else:
        await ctx.send("Only the owner can use this command")

@bot.command(name="nextresult", aliases=["nextelectionresult"])
async def next_election(ctx: commands.Context):
    if election_active:
        await ctx.send(f"The next election result will be announced at {next_election_result}")
    else:
        await ctx.send("There is no election currently active")

@bot.command(name="startelection", aliases=["initiateelection", "beginelection"])
async def start_election(ctx: commands.Context, arg="default"):
    global election_active
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Only the Supreme Leader can use this command")
        return
    elif election_active:
        if str(arg).lower() == "cancel":
            await ctx.send("Stopping current election...")
            election_active = False
        else:
            await ctx.send("An election is already active")
        return
    await carry_out_elections(ctx, timedelta(minutes=3))

# Get the current time that is being read
@bot.command(name="time")
async def time(ctx: commands.Context) -> None:
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("Current date/time on the server: " + str(datetime.now()))
    else:
        await ctx.send("Only the owner can use this command")

@bot.command(name="test")
async def test(ctx: commands.Context) -> None:
    """Command reserved for testing purposes"""
    await ctx.send("Boi wat you tryna test 🫱")

async def archive_general(guild: discord.Guild, general_cat_name=None, archive_cat_name="Archive", freq=2) -> None:
    """Handles the actual archiving of general chat"""
    try:
        general_category = discord.utils.get(guild.categories, name=general_cat_name)
        archive_category = discord.utils.get(guild.categories, name="Archive")
        chat_to_archive = discord.utils.get(guild.text_channels, name="general")
        await chat_to_archive.move(beginning=True, category=archive_category, sync_permissions=True)
        await chat_to_archive.edit(name=db.get_archived_name())
        new_channel = await guild.create_text_channel("general", category=general_category)
        await new_channel.send("good morning @everyone")   
    except Exception as ex:
        raise Exception(str(ex))

async def carry_out_elections(ctx: commands.Context, freq: timedelta):
    """Handles repeatedly carrying out elections until finished"""
    global election_active
    election_active = True
    global next_election_result
    members = list(filter(lambda member: not member.bot, ctx.guild.members))
    members.remove(discord.utils.get(ctx.guild.members, id=ctx.guild.owner_id))
    positions = ["CEO of the Republic", 
             "Indian of the Republic",
             "The Softest of the Softest Carries", 
             "Chinese of the Republic", 
             "Economist of the Republic", 
             "Pope of the Republic"]
    positions_assigned = []
    start = datetime.now() - timedelta(hours=5) # set to EST
    next = (start + freq).time()
    next_election_result = datetime.strptime(f"{next.hour}:{next.minute}","%H:%M").strftime("%I:%M %p")
    await ctx.send(f"Elections have begun @everyone. The first election result will be announced at {next_election_result} EST")
    while len(members) > 0 and election_active:
        await asyncio.sleep(freq.total_seconds())
        member_num = random.randint(0, len(members) - 1)
        index = random.randint(0, len(positions_assigned) - 1) if len(positions) == 0 else random.randint(0, len(positions) - 1)
        chosen_one = members[member_num]
        chosen_position = positions[index]
        await ctx.send(f"Election result @everyone: {chosen_one.name}'s new position will be {chosen_position}")
        next = datetime.now() + freq - timedelta(hours=5)
        next_election_result = datetime.strptime(f"{next.hour}:{next.minute}","%H:%M").strftime("%I:%M %p")
        await next_election(ctx)
        positions.remove(chosen_position)
        if len(positions) == 0:
            positions = deepcopy(positions_assigned)
        positions_assigned.append(chosen_position)
        members.remove(chosen_one)
    await ctx.send("Election results finalized!")
    election_active = False
    next_election_result = None

# Handles repeatedly archiving general chat
async def repeat_archive(freq: timedelta) -> None:
    await sleep_until_archive()
    while True:
        db.update_next_archive_date(freq)
        for guild in bot.guilds:
            now = datetime.now()
            try:
                await archive_general(guild=guild)
                discord.utils.get(guild.channels, name=db.get_archived_name())
                print(str(now) + ': general archived in "{}" (id: {})'.format(guild.name, guild.id))
            except Exception as ex:
                print(str(now) + ': there was an error archiving general in "{}" (id: {}): {}'.format(guild.name, guild.id, str(ex)))
        await sleep_until_archive()

# Handles waiting for the next archive date
async def sleep_until_archive() -> None:
    now = datetime.now()
    then = db.get_next_archive_date()
    wait_time = (then - now).total_seconds()
    await asyncio.sleep(wait_time)

async def once_stop_recording(sink: WaveSink, vc: discord.VoiceChannel, tc: discord.TextChannel) -> None:
    print(f"{len(vc_connections)} connections:\n{str(vc_connections)}")
    if len(vc_connections) == 0:
        print("went here")
        return
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    now = datetime.now()
    timestamp = f"{str(now.date())}_{now.hour}-{now.minute}-{now.second}"
    files = [discord.File(audio.file, f"vcclip_{timestamp}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
    await tc.send(f"Clipped all audio from the \"{vc.name}\" voice chat:", files=files) 

bot.run(os.getenv("BOT_TOKEN"))