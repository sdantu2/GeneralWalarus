from models import VCConnection, Election, Server
from discord import Guild

servers: dict[Guild, Server] = {}
""" Contains active server connections """

vc_connections: dict[Guild, VCConnection] = {} 
""" Contains active voice chat connections """

elections: dict[Guild, Election] = {}
""" Contains active elections """