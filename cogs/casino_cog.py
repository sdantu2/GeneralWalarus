from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
from discord.ext.commands import Cog
from discord.ext import commands
import database as db
import random
import matplotlib
import matplotlib.pyplot as plt
import os

class CasinoCog(Cog, name="Casino"):
    """ Class containing commands pertaining to elections """

    #region Commands
    
    @commands.command(name="sse", aliases=["currentstockprice", "currentprice", "price"])
    async def sse_details(self, ctx: commands.Context):
        """ Displays details about current state of Srinath Stock Exchange """
        sse_status = db.get_sse_status(ctx.guild)

        if not sse_status:
            await ctx.send("The Srinath Stock Exchange is not currently open")
            return

        price = db.get_current_sse_price(ctx.guild)
        await ctx.send(f"**Price**: ${round(price, 2):,.2f}\n"
                       f"**Next Price Update**: {self.__job.next_run_time}\n"
                       f"**Stock Price Graph**:")
        await self.__show_graph(ctx)

    @commands.command(name="ssebuy", aliases=["buy", "buyin", "buystock"])
    async def sse_buy(self, ctx: commands.Context):
        """ Buy into the Srinath Stock Exchange at the current stock price """
        sse_status = db.get_sse_status(ctx.guild)

        if not sse_status:
            await ctx.send("The Srinath Stock Exchange is not currently open")
            return
        
        last_transaction = db.get_last_transaction(ctx.author)["action"]
        
        if last_transaction == "buy": 
            await ctx.send("You are already bought into the SSE!")
            return
        
        curr_price = db.get_current_sse_price(ctx.guild)
        db.set_transaction(member=ctx.author, curr_price=curr_price, transaction_type="buy")
        await ctx.send(f"{ctx.author.name} just bought into the Srinath Stock Exchange for "
                       f"${round(curr_price, 2):,.2f}")

    @commands.command(name="ssesell", aliases=["sell", "sellstock"])
    async def sse_sell(self, ctx: commands.Context):
        """ Sell your share of the Srinath Stock Exchange at the current stock price """
        sse_status = db.get_sse_status(ctx.guild)

        if not sse_status:
            await ctx.send("The Srinath Stock Exchange is not currently open")
            return
        
        last_transaction = db.get_last_transaction(ctx.author)["action"]

        if last_transaction == "sell":
            await ctx.send("You haven't bought into the SSE yet!")
            return

        curr_price = db.get_current_sse_price(ctx.guild)
        db.set_transaction(member=ctx.author, curr_price=curr_price, transaction_type="sell")
        await ctx.send(f"{ctx.author.name} just sold share in the Srinath Stock Exchange for "
                       f"${round(curr_price, 2):,.2f}")

    @commands.command(name="sseopen", aliases=["ssestart"])
    async def sse_start(self, ctx: commands.Context):
        """ Open the Srinath Stock Exchange for business """
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.send("Only the server owner can use this command")
            return 
        
        sse_status = db.get_sse_status(ctx.guild)

        if sse_status:
            await ctx.send("The Srinath Stock Exchange is already open!")
            return

        OPENING_PRICE = 1.00
        db.set_sse_status(ctx.guild, status=True)
        db.set_current_sse_price(ctx.guild, OPENING_PRICE)
        price = db.get_current_sse_price(ctx.guild)
        await ctx.send("@everyone The Srinath Stock Exchange is now open for business at "
                       f"price of ${round(price, 2):,.2f}!")
        
        cron_trigger = CronTrigger.from_crontab("0 9 * * *")
        scheduler = BackgroundScheduler()
        self.__job = scheduler.add_job(self.__get_new_sse_price, cron_trigger, args=[ctx.guild, True])
        scheduler.start()


    @commands.command(name="sseclose", aliases=["ssestop", "sseend"])
    async def sse_end(self, ctx: commands.Context):
        """ Close the Srinath Stock Exchange """
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.send("Only the server owner can use this command")
            return

        sse_status = db.get_sse_status(ctx.guild)
        
        if not sse_status:
            await ctx.send("The Srinath Stock Exchange is not currently open")
            return
        
        db.set_sse_status(ctx.guild, status=False)
        await ctx.send("@everyone The Srinath Stock Exchange is now closed")
        
    @commands.command(name="lasttransaction")
    async def sse_last_transaction(self, ctx: commands.Context, member: discord.Member | None = None):
        """ View details about your last SSE transaction """
        if member is None:
            member = ctx.author
        transaction = db.get_last_transaction(member)
        if transaction is None:
            await ctx.send(f"{"You haven't" if member.id == ctx.author.id else f'{member.name} hasn\'t'} made "
                           "any transactions yet. Try the 'ssebuy' or 'ssesell' commands.")
            return
        await ctx.send(f"Here are the details of {"your" if member.id == ctx.author.id else f'{member.name}\'s '} "
                       "last transaction:\n"
                       f"\t**Timestamp**: {transaction['timestamp']}\n"
                       f"\t**Transaction Type**: {transaction['action']}\n"
                       f"\t**Price**: ${round(transaction['price'], 2):,.2f}")

    # @commands.command(name="ssetest")
    # async def sse_test(self, ctx: commands.Context):
    #     """ Test command for the Srinath Stock Exchange """
    #     self.__get_new_sse_price(ctx.guild, write=True)
    
    #endregion

    #region Helper Functions

    def __get_new_sse_price(self, guild: discord.Guild, write: bool = False) -> float:
        old_price = db.get_current_sse_price(guild)
        rate = random.randint(-200, 700) / 10000
        delta = old_price * rate
        new_price = old_price + delta
        if write:
            db.set_current_sse_price(guild, new_price)
        return new_price
    
    async def __show_graph(self, ctx: commands.Context):
        matplotlib.use('Agg')
        timestamps, prices = db.get_prices(ctx.guild)

        fig, ax = plt.subplots()
        fig.set_figwidth(15)
        ax.set_ylabel("Price", labelpad=25)
        ax.yaxis.set_major_formatter('${x:1.2f}')
        ax.set_xlabel("Date", labelpad=25)
        ax.tick_params(axis='x', labelrotation=90)
        ax.plot(timestamps, prices, marker="o")

        image_name = "prices.jpg"        
        plt.savefig(image_name, bbox_inches='tight')
        plt.close()
        await ctx.send(file=discord.File(image_name))
        os.remove(image_name)

    #endregion