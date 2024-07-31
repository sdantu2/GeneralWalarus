import discord
from discord.ext.commands import Cog
from discord.ext import commands
import database as db
import os
import time
from typing import List, Literal
from globals import vc_connections, servers
from models import VCConnection
from pydub import AudioSegment
from datetime import datetime


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
            VoiceCog.clip_callback,  # What to do once done.
            ctx.channel,  # The channel to disconnect from.
            sync_start=True  # Everyone's audio is in sync
        )
        # VoiceCog.save_clip(ctx)
        await ctx.send("***BE WARNED*** I'm recording you fuckers 🔴")

        guild: discord.Guild | None = ctx.guild # type: ignore  
        if guild is None:
            raise Exception("record(): guild is None")
        server = servers[guild]
        if isinstance(voice_client, discord.VoiceClient):
            # Updating the cache with the guild and channel.
            vc_connections.update({guild: VCConnection(server, voice_client)})


    @commands.command(name="clip", aliases=["clipit", "clipthat"])
    async def clip(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send("You're not even in a voice channel brotha")
            return

        if ctx.guild in vc_connections:  # Check if the guild is in the cache.
            vc = vc_connections[ctx.guild]
            del vc_connections[ctx.guild]
            # Stop recording, and call the callback function.
            vc.voice_client.stop_recording()
        else:
            # Respond with this if we aren't recording.
            await ctx.send("I am currently not recording here.")

    # endregion

    # region Helper Functions

    @staticmethod
    def save_clip(ctx: commands.Context):
        while True:
            time.sleep(10)
            if ctx.guild in vc_connections:
                voice_client = vc_connections[ctx.guild].voice_client
                voice_client.stop_recording()   
                voice_client.start_recording(
                    discord.sinks.MP3Sink(),
                    VoiceCog.clip_callback,
                    ctx.channel,
                    sync_start=True
                )
            else:
                raise Exception(f'{ctx.guild.name} has no connection in vc_connections')


    @staticmethod
    async def clip_callback(sink: discord.sinks.MP3Sink, channel: discord.TextChannel):
        recorded_users = [  # A list of recorded users
            f"<@{user_id}>"
            for user_id, audio in sink.audio_data.items()
        ]

        user_initiated = True if vc_connections.get(channel.guild) is None else False

        # Combine individual users' audio recordings into into one file
        files = [audio.file for audio in sink.audio_data.values()]
        filename = f'combined-{datetime.now()}.mp3'
        VoiceCog.combine_user_audios(audio_files=files, format='mp3', output_filepath=filename)
        combined_file = discord.File(filename, filename='clip.mp3')
        
        if user_initiated:
            await sink.vc.disconnect()  # Disconnect from the voice channel.
            await channel.send('Here is your clip', files=[combined_file])
            os.remove(filename)


    @staticmethod
    def combine_user_audios(audio_files: List, format: Literal['wav', 'mp3'], output_filepath: str, 
                            max_length_ms: int = 30000):
        """ Splices the given audio files into one """
        audio_segments = [AudioSegment.from_file(file=file, format=format) for file in audio_files]
        max_audio_length = max(audio_segments, key=lambda audio: audio.duration_seconds).duration_seconds
        max_audio_length_ms = max_audio_length * 1000  # x1000 to convert seconds to ms
        duration = min(max_audio_length_ms, max_length_ms)
        combined = AudioSegment.silent(duration=duration)
        for segment in audio_segments:
            combined = combined.overlay(segment)
        combined.export(output_filepath, format=format)

    # endregion
