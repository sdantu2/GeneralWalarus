import discord
from discord.ext.commands import Cog
from discord.ext import commands
import database as db
import os
from typing import List, Literal
from globals import vc_connections, servers
from models import VCConnection
from pydub import AudioSegment


class VoiceCog(Cog, name="Voice"):
    """ Class containing General Walarus' voice commands """

    # region Commands

    @commands.command(name="record", aliases=["startrecording", "join"])
    async def record(self, ctx: commands.Context) -> None:
        voice = ctx.author.voice

        if not voice:
            await ctx.send("You ain't even in a voice channel brotha")

        # Connect to the voice channel the author is in.
        voice_client = await voice.channel.connect()
        sink = discord.sinks.MP3Sink()

        voice_client.start_recording(
            sink,  # The sink type to use.
            VoiceCog.callback_func,  # What to do once done.
            ctx.channel,  # The channel to disconnect from.
            sync_start=True  # Everyone's audio is in sync
        )
        await ctx.send("***BE WARNED*** I'm recording you fuckers 🔴")

    @commands.command(name="clip", aliases=["clipit", "clipthat"])
    async def clip(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send("You're not even in a voice channel brotha")
            return

        if ctx.guild in vc_connections:  # Check if the guild is in the cache.
            vc = vc_connections[ctx.guild]
            # Stop recording, and call the callback function.
            vc.voice_client.stop_recording()
        else:
            # Respond with this if we aren't recording.
            await ctx.send("I am currently not recording here.")

    # endregion

    # region Helper Functions

    @staticmethod
    async def callback_func(sink: discord.sinks.MP3Sink, channel: discord.TextChannel):
        recorded_users = [  # A list of recorded users
            f"<@{user_id}>"
            for user_id, audio in sink.audio_data.items()
        ]
        await sink.vc.disconnect()  # Disconnect from the voice channel.

        # Combine individual users' audio recordings into into one file
        files = [audio.file for audio in sink.audio_data.values()]
        filename = 'combined.mp3'
        VoiceCog.combine_user_audios(audio_files=files, format='mp3', output_filepath=filename)
        combined_file = discord.File(filename, filename='clip.mp3')
        
        await channel.send('Here is your clip', files=[combined_file])
        os.remove(filename)

    @staticmethod
    def combine_user_audios(audio_files: List, format: Literal['wav', 'mp3'], output_filepath: str):
        audio_segments = [AudioSegment.from_file(file=file, format=format) for file in audio_files]
        duration = max(audio_segments, key=lambda audio: audio.duration_seconds).duration_seconds
        combined = AudioSegment.silent(duration=duration * 1000)
        for segment in audio_segments:
            combined = combined.overlay(segment)
        combined.export(output_filepath, format=format)

    # endregion
