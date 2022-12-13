from models.vc_connection import VCConnection
from models.election import Election
from models.server import Server
from discord import Guild

servers: dict[Guild, Server] = {}
""" Contains active server connections """

vc_connections: dict[Guild, VCConnection] = {} 
""" Contains active voice chat connections """

elections: dict[Guild, Election] = {}
""" Contains active elections """