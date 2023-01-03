from discord import VoiceClient
from datetime import datetime
from models.server import Server
from utilities import now_time, timef

class VCConnection:
    """ Class that encapsulates information about active voice channel connections """
    def __init__(self, server: Server, voice_client: VoiceClient) -> None:
        self.server: Server = server
        """Server that voice connection associated with"""
        self.connected: datetime = now_time(server)
        """Time that Walarus connected to voice chat"""
        self.voice_client: VoiceClient = voice_client
        """Pycord Voice Client associated with VC connection"""
    
    def __str__(self) -> str:
        return f"VCConnection: server='{self.server.guild.name}', connected='{timef(self.connected)}'"