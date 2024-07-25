import discord
from .db_globals import *
from datetime import datetime
from typing import cast, Literal
from bson.timestamp import Timestamp

def get_current_sse_price(discord_server: discord.Guild) -> float:
    price_log = db.sse_price_log
    query = price_log.find_one({ "_id.server_id": discord_server.id }, { "_id": 0, "price": 1 }, 
                                    sort=[("_id.timestamp", -1)])
    query_dict = cast(dict, query) 
    price = float(query_dict["price"])
    return price

def set_current_sse_price(discord_server: discord.Guild, new_price: float) -> bool:
    price_log = db.sse_price_log
    timestamp = datetime.now()
    return price_log.insert_one({
                                    "_id": {
                                        "server_id": discord_server.id,
                                        "timestamp": timestamp
                                    },
                                    "price": new_price,
                                }).acknowledged

def get_prices(discord_server: discord.Guild):
    timestamps = []
    prices = []

    price_log = db.sse_price_log
    results = price_log.find({ "_id.server_id": discord_server.id }, { "_id.timestamp": 1, "price": 1 })

    for result in results:
        timestamps.append(str( result["_id"]["timestamp"].date()))
        prices.append(result["price"])

    return (timestamps, prices)

def set_transaction(member: discord.Member, curr_price: float, transaction_type: Literal["buy", "sell"]) -> bool:
    transaction_log = db.sse_transaction_log
    timestamp = datetime.now()
    guild = member.guild
    return transaction_log.insert_one({ 
                                        "server_id": guild.id,
                                        "server_name": guild.name,
                                        "user_id": member.id,
                                        "user_name": member.name,
                                        "timestamp": timestamp, 
                                        "action": transaction_type,
                                        "price": curr_price
                                      }).acknowledged

def get_last_transaction(member: discord.Member):
    transaction_log = db.sse_transaction_log
    guild = member.guild
    query = transaction_log.find_one({ "server_id": guild.id, "user_id": member.id }, sort=[("timestamp", -1)])
    query_dict = { "action": None } if query is None else cast(dict, query)
    return query_dict