from dotenv import load_dotenv
load_dotenv() # need to load environment variables before anything else
import os
import discord
from discord.ext import commands
import discord.utils
from cogs import (ArchiveCog, ElectionCog, EventsCog, 
    MiscellaneousCog, StatisticsCog, VoiceCog, OpenAICog)
from globals import start_mutex
import shell as sh
from threading import Thread
from utilities import get_server_prefix

def run_bot(bot: discord.Bot):
    bot.run(os.getenv("BOT_TOKEN"))

def main():    
    """ Setup bot intents and cogs and bring General Walarus to life """
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot: discord.Bot = commands.Bot(command_prefix=get_server_prefix(), intents=intents) # type: ignore
    bot.add_cog(EventsCog(bot))
    bot.add_cog(ArchiveCog(bot))
    bot.add_cog(ElectionCog())
    bot.add_cog(MiscellaneousCog())
    bot.add_cog(StatisticsCog())
    bot.add_cog(VoiceCog())
    bot.add_cog(OpenAICog())
    Thread(target=run_bot, name="cmd", args=[bot]).start()
    start_mutex.acquire()
    sh.run_walarus_shell()

if __name__ == "__main__":
    main()
