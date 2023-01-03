from bson import ObjectId
from datetime import datetime, timedelta
import discord
from discord.ext import commands
import os
from pymongo import MongoClient

CONNECTION_STRING: str = str(os.getenv("DB_CONN_STRING"))
db = MongoClient(CONNECTION_STRING).general_walarus
log = lambda discord_server, collection, data: collection.update_one({"_id": discord_server.id}, {"$set": data}, upsert = True).upserted_id != None
DATE_ID = ObjectId("62df0eeb1f3ca1fa0645aef0")
    
def log_user_stat(discord_server: discord.Guild, user: discord.User, target_stat: str, inc = 1) -> bool:
    user_stats = db.user_stats
    stats = ["mentioned", "sent_messages", "vc_time"]
    stats_data = {}
    for stat in stats:
        if stat == target_stat:
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

def get_next_archive_date() -> datetime:
    collection = db.next_archive_date
    data = collection.find_one({"_id": DATE_ID}, {"_id": 0})
    if data is None:
        raise Exception("Couldn't find document")
    return datetime(data["year"], data["month"], data["day"], data["hour"], data["minute"], data["second"])

def update_next_archive_date(archive_freq: timedelta) -> str:
    old_date = get_next_archive_date()
    new_date: datetime = old_date + archive_freq
    new_date_fields = {
        "year": new_date.year,
        "month": new_date.month,
        "day": new_date.day,
        "hour": new_date.hour,
        "minute": new_date.minute,
        "second": new_date.second
    }
    collection = db.next_archive_date
    collection.update_one({"_id": DATE_ID}, {"$set": new_date_fields}, upsert=True)
    month = str(new_date.month)
    day = str(new_date.day)
    year = str(new_date.year)
    return "general-" + month + "-" + day + "-" + year[len(year) - 2:]

def log_role_change(ctx: commands.Context):
    collection = db.role_changes
        

    
        
        