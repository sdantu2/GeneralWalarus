from datetime import datetime
import discord
from pymongo import MongoClient

class DbHandler:
    def __init__(self, db_conn_string: str) -> None:
        self.__db = MongoClient(db_conn_string).general_walarus
    
    def log_user_stat(self, discord_server: discord.Guild, user: discord.User, target_stat: str,
                      inc = 1) -> bool:
        user_stats = self.__db.user_stats
        stat_names = ["mentioned", "sent_messages", "vc_time"]
        stats_data = {}
        for stat in stat_names:
            if stat == target_stat:
                stats_data[stat] = inc
            else:
                stats_data[stat] = 0
        return user_stats.update_one({
                                        "_id": {
                                            "server_id": discord_server.id, 
                                            "user_id": user.id, 
                                            "server_name": discord_server.name, 
                                            "user_name": user.name
                                        }
                                    }, 
                                    {
                                        "$inc": stats_data
                                    }, 
                                    upsert = True).upserted_id != None
    
    def log_server(self, discord_server: discord.Guild) -> bool:
        connected_servers = self.__db.connected_servers
        server_data = {
            "_id": discord_server.id,
            "name": str(discord_server.name),
            "description": str(discord_server.description),
            "icon_url": str(discord_server.icon_url),
            "creation_at": discord_server.created_at,
            "last_updated": datetime.now()
        }
        return self.__log(discord_server, "connected_servers", server_data)
    
    # Returns true if new document added
    def __log(self, discord_server: discord.Guild, collection_name: str, data: dict) -> bool:
        collection = self.__db.get_collection(collection_name)
        return collection.update_one({
                                        "_id": discord_server.id
                                    }, 
                                    {
                                        "$set": data
                                    }, 
                                     upsert = True).upserted_id != None
        
        