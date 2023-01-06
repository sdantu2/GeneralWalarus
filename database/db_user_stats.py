import discord
from .db_globals import *

def inc_user_stat(discord_server: discord.Guild, user: discord.User | discord.Member, field: str, inc = 1) -> bool:
    user_stats = db.user_stats
    stats = ["mentioned", "sent_messages", "time_in_vc"]
    stats_data = {}
    for stat in stats:
        if stat == field:
            stats_data[stat] = inc
        else:
            stats_data[stat] = 0
    return user_stats.update_one({
                                    "_id": {
                                        "server_id": discord_server.id, 
                                        "user_id": user.id
                                    }
                                }, 
                                {
                                    "$set": {
                                        "server_name": discord_server.name, 
                                        "user_name": user.name
                                    },
                                    "$inc": stats_data
                                }, 
                                upsert = True).upserted_id != None

def update_user_stats(discord_server: discord.Guild, user: discord.User | discord.Member, **kwargs) -> bool:
    user_stats = db.user_stats
    set_fields: dict = { "server_name": discord_server.name, "user_name": user.name }
    set_fields.update(**kwargs)
    return user_stats.update_one({
                                    "_id": {
                                        "server_id": discord_server.id, 
                                        "user_id": user.id
                                    }
                                }, 
                                {
                                    "$set": set_fields
                                }, 
                                upsert = True).upserted_id != None

def get_user_stats(discord_server: discord.Guild, user_id: int, *fields):
    user_stats = db.user_stats
    projection: dict = {}
    for field in fields:
        projection[field] = 1
    return user_stats.find_one({
                                    "_id": {
                                        "server_id": discord_server.id, 
                                        "user_id": user_id
                                    }
                                }, projection)