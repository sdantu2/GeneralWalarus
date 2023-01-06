import discord
from datetime import datetime
from .db_globals import *

def log_server(discord_server: discord.Guild) -> bool:
    connected_servers = db.connected_servers
    server_exists = bool(connected_servers.find_one({"_id": discord_server.id}))
    icon_url = "" if discord_server.icon is None else discord_server.icon.url
    description_exists = bool(discord_server.description)
    server_data = {
        "_id": discord_server.id,
        "name": str(discord_server.name),
        "description": str(discord_server.description) if description_exists else "",
        "icon_url": icon_url,
        "creation_at": discord_server.created_at,
        "last_updated": datetime.now()
    }
    if not server_exists:
        server_data["joined"] = datetime.now()
    return log(discord_server, connected_servers, server_data)

def remove_discord_server(discord_server: discord.Guild) -> int:
    """Remove the given server from all relevant collections, returns the number of documenets deleted"""
    connected_servers = db.connected_servers
    user_stats = db.user_stats
    total = connected_servers.delete_many({"_id": discord_server.id}).deleted_count
    total += user_stats.delete_many({"_id.server_id": discord_server.id}).deleted_count
    return total