from dotenv import load_dotenv
load_dotenv() # need to load environment variables before anything else
import os
import discord
from discord.ext import commands
import discord.utils
from cogs import ArchiveCog, ElectionCog, EventsCog, MiscellaneousCog, StatisticsCog, VoiceCog
from globals import start_mutex
import shell as sh
from threading import Thread

def run_bot(bot: discord.Bot):
    bot.run(os.getenv("BOT_TOKEN"))
    # bot.run(os.getenv("DEV_BOT_TOKEN"))

def main():    
    """ Setup General Walarus and run """
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot: discord.Bot = commands.Bot(command_prefix="$", intents=intents) # type: ignore
    bot.add_cog(EventsCog(bot))
    bot.add_cog(ArchiveCog(bot))
    bot.add_cog(ElectionCog())
    bot.add_cog(MiscellaneousCog())
    bot.add_cog(StatisticsCog())
    bot.add_cog(VoiceCog())
    Thread(target=run_bot, name="cmd", args=[bot]).start()
    start_mutex.acquire()
    sh.run_walarus_shell()

if __name__ == "__main__":
    main()