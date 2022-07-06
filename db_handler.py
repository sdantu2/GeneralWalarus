from datetime import datetime
import discord
from pymongo import MongoClient

class DbHandler:
    def __init__(self, db_conn_string: str) -> None:
        self.__db = MongoClient(db_conn_string).general_walarus
    
    # Returns true if new document added
    def log(self, server: discord.Guild) -> bool:
        connected_servers = self.__db.connected_servers
        server_data = {
            "_id": server.id,
            "name": str(server.name),
            "description": str(server.description),
            "icon_url": str(server.icon_url),
            "creation_at": server.created_at,
            "last_updated": datetime.now()
        }
        return self.__db.connected_servers.update_one({"_id": server.id}, 
                                                      {"$set": server_data},
                                                      upsert = True).upserted_id != None
        
        