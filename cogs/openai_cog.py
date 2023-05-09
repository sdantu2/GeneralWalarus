import discord
from discord.ext.commands import Cog
from discord.ext import commands
import database as db
from typing import cast
from utilities import printlog
import openai
import os
        
class OpenAICog(Cog, name="OpenAI"):
    """ Class containing General Walarus' OpenAI commands """
    
    def __init__(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    #region Commands
    
    @commands.command(name="gpt", aliases=["ai", "chatgpt"])
    async def chat_gpt(self, ctx: commands.Context, *message_input) -> None:
        """ Command to chat with ChatGPT """
        waiting_msg = await ctx.send("ChatGPT is thinking...")
        try:
            messages = []
            messages.append({ "role": "user", "content": " ".join(message_input) })
            chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            await waiting_msg.delete()
            await ctx.send(f"ChatGPT says: ```{chat.choices[0].message.content}```") #type: ignore    
        except Exception as e:
            printlog(str(e))
            await waiting_msg.delete()
            await ctx.send("ChatGPT died trying to talk to you...")
    
    #endregion 