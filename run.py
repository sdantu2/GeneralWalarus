from dotenv import load_dotenv
load_dotenv() # need to load environment variables before anything else
import os
import discord
from discord.ext import commands
import discord.utils
from cogs import ArchiveCog, ElectionCog, EventsCog, MiscellaneousCog
import shell as sh

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
    bot.run(os.getenv("BOT_TOKEN"))
    sh.run_walarus_shell()

if __name__ == "__main__":
    main()