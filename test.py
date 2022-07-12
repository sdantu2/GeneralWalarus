from datetime import datetime
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from discord.sinks import WaveSink, Sink, MP3Sink

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
load_dotenv()
connections = {}

@bot.event
async def on_ready() -> None:
    print("test walarus is up and ready")

@bot.command(name="herro")
async def herro(ctx: commands.Context) -> None:
    await ctx.send("Hello there!")

@bot.command()
async def record(ctx):  # If you're using commands.Bot, this will also work.
    voice = ctx.author.voice

    if not voice:
        await ctx.respond("You aren't in a voice channel!")

    vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
    connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

    vc.start_recording(
        WaveSink(),  # The sink type to use.
        once_done,  # What to do once done.
        ctx.channel  # The channel to disconnect from.
    )
    await ctx.send("Started recording!")

async def once_done(sink: Sink, channel: discord.TextChannel, *args):  # Our voice client already passes these in.
    recorded_users = [  # A list of recorded users
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    now = datetime.now()
    timestamp = f"{str(now.date())}_{now.hour}-{now.minute}-{now.second}"
    files = [discord.File(audio.file, f"vcclip_{timestamp}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
    await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.", files=files)  # Send a message with the accumulated files.

@bot.command(name="stop")
async def stop_recording(ctx: commands.Context):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        del connections[ctx.guild.id]  # Remove the guild from the cache.
    else:
        await ctx.send("I am currently not recording here.")  # Respond with this if we aren't recording.

print(os.getenv("BOT_TOKEN"))
bot.run(os.getenv("BOT_TOKEN"))