import discord
from datetime import datetime
from .db_globals import *
from typing import cast

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
        "last_updated": datetime.now(),
        "rshuffle": list(map(_role_name, discord_server.roles)),
        "ushuffle": list(map(_member_name, discord_server.members))
    }
    if not server_exists:
        server_data["joined"] = datetime.now()
    return log(discord_server, connected_servers, server_data)

def _role_name(role: discord.Role) -> str:
    return role.name

def _member_name(member: discord.Member) -> str:
    return member.name

def remove_discord_server(discord_server: discord.Guild) -> int:
    """Remove the given server from all relevant collections, returns the number of documenets deleted"""
    connected_servers = db.connected_servers
    user_stats = db.user_stats
    total = connected_servers.delete_many({"_id": discord_server.id}).deleted_count
    # total += user_stats.delete_many({"_id.server_id": discord_server.id}).deleted_count
    return total

def get_rshuffle(guild: discord.Guild) -> list[str]:
    connected_servers = db.connected_servers
    query = connected_servers.find_one({
                                            "name": guild.name
                                       },
                                       {
                                           "rshuffle": 1
                                       })
    query_dict: dict = cast(dict, query)
    return [] if query_dict.get("rshuffle") == None else query_dict["rshuffle"]

def get_ushuffle(guild: discord.Guild) -> list[str]:
    connected_servers = db.connected_servers
    query = connected_servers.find_one({ "name": guild.name },
                                       { "ushuffle": 1 })
    query_dict: dict = cast(dict, query)
    return [] if query_dict.get("ushuffle") == None else query_dict["ushuffle"]