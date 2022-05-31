import discord
from discord.ext import commands
import config as cfg

client = commands.Bot(command_prefix="$")

@client.event
async def on_ready():
    print("General Walarus is up and ready")

@client.command(name="archivegeneral")
async def biweekly_general(ctx, general_cat_name=None, archive_cat_name="Archive", freq=2):
    guild = ctx.guild
    general_category = discord.utils.get(guild.categories, name=general_cat_name)
    archive_category = discord.utils.get(guild.categories, name="Archive")
    old_general_chat = discord.utils.get(guild.channels, name="general")
    await old_general_chat.move(beginning=True, category=archive_category, sync_permissions=True)
    await guild.create_text_channel("general", category=general_category)

client.run(cfg.BOT_TOKEN)
