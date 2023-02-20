from models import VCConnection, Election, Server
from discord import Guild
import threading

servers: dict[Guild, Server] = {}
""" Contains active server connections """

vc_connections: dict[Guild, VCConnection] = {} 
""" Contains active voice chat connections """

elections: dict[Guild, Election] = {}
""" Contains active elections """

start_mutex: threading.Semaphore = threading.Semaphore(0)
""" Mutex used to synchronize GW on_ready and shell start """