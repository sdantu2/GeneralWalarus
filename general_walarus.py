import asyncio
from copy import deepcopy
from datetime import datetime, timedelta
import random
from typing import cast
import discord
from discord.ext import commands
from discord.sinks import WaveSink
import database as db
import discord.utils
from models import Server, Election, VCConnection
from globals import servers, vc_connections, elections
from utilities import timef, now_time
from cogs import ArchiveCog, ElectionCog, EventsCog, MiscellaneousCog

print("general_walarus.py")
# Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot: discord.Bot = commands.Bot(command_prefix="$", intents=intents) # type: ignore
bot.add_cog(EventsCog(bot))
bot.add_cog(ArchiveCog(bot))
bot.add_cog(ElectionCog())
bot.add_cog(MiscellaneousCog())

# @bot.command(name="stalk", aliases=["join", "connect"])
# async def join_vc(ctx: commands.Context):
#     try:
#         author: discord.Member = cast(discord.Member, ctx.author)
#         if author.voice == None:
#             await ctx.send("You're not connected to a voice chat")
#             return
#         voice_state: discord.VoiceState = author.voice
#         voice_channel: discord.VoiceChannel = cast(discord.VoiceChannel, voice_state.channel)
#         voice_client: discord.VoiceClient
#         try: 
#             voice_client = await voice_channel.connect()
#         except: # already connected to a different VC, move them to the author's VC
#             curr_voice_client: discord.VoiceClient = cast(discord.VoiceClient, discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild))
#             voice_client = cast(discord.VoiceClient, await curr_voice_client.move_to(voice_channel))
#         server: Server = servers[cast(discord.Guild, ctx.guild)]
#         vc_connections[cast(discord.Guild, ctx.guild)] = VCConnection(server, voice_client)
#         voice_client.start_recording(WaveSink(), once_done, ctx.channel)
#     except Exception as ex:
#         print(str(ex))
        
# @bot.command(name="stop")
# async def stop(ctx: commands.Context):
#     vc_connection: VCConnection = vc_connections[cast(discord.Guild, ctx.guild)]
#     voice_client: discord.VoiceClient = vc_connection.voice_client
#     voice_client.stop_recording()
#     del vc_connection
#     print("done recording")
    
# async def once_done(sink: WaveSink, send_to_channel: discord.TextChannel, *args):
#     voice_client: discord.VoiceClient = vc_connections[cast(discord.Guild, send_to_channel.guild)].voice_client
#     sink.write()
#     await voice_client.disconnect()
#     files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
#     await send_to_channel.send("Clipped the last 30 seconds", files=files)  # Send a message with the accumulated files.

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