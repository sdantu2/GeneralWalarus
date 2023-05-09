import discord
from discord.ext.commands import Cog
from discord.ext import commands
import database as db
from typing import cast
        
class VoiceCog(Cog, name="Voice"):
    """ Class containing General Walarus' voice commands """
    
    #region Commands
    
    @commands.command(name="join", aliases=["joinvoice"])
    async def messages(self, ctx: commands.Context) -> None:
        pass
    
    #endregion
        


