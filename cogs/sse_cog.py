import discord
from discord import utils
from discord.ext.commands import Cog
from discord.ext import commands
import database as db
from models import SSESession
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from globals import live_sse_sessions

class SSECog(Cog, name="Chris Stock Exchange"):
    """ Class containing commands pertaining to Chris Stock Exchange """

    #region Commands
    
    @commands.command(name="cse", aliases=["currentstockprice", "currentprice", "price"])
    async def sse_details(self, ctx: commands.Context):
        """ Displays details about current state of Chris Stock Exchange """
        guild: discord.Guild | None = ctx.guild # type: ignore
        if guild is None:
            raise Exception("sse_details(): guild is None")
        sse_status = db.get_sse_status(guild)

        if not sse_status:
            await ctx.send("The Chris Stock Exchange is not currently open")
            return

        price = db.get_current_sse_price(guild)
        job = live_sse_sessions[guild].job
        await ctx.send(f"**Price**: ${round(price, 2):,.2f}\n"
                       f"**Next Price Update**: {job.next_run_time}\n"
                       f"**Stock Price Graph**:")
        await self.__show_graph(ctx)


    @commands.command(name="csebuy", aliases=["buy", "buyin", "buystock"])
    async def sse_buy(self, ctx: commands.Context):
        """ Buy into the Chris Stock Exchange at the current stock price """
        guild: discord.Guild | None = ctx.guild # type: ignore
        if guild is None:
            raise Exception("sse_buy(): guild is None")
        sse_status = db.get_sse_status(guild)

        if not sse_status:
            await ctx.send("The Chris Stock Exchange is not currently open")
            return
        
        author: discord.Member = ctx.author # type: ignore
        last_transaction = db.get_last_transaction(author)["action"]
        
        if last_transaction == "buy": 
            await ctx.send("You are already bought into the SSE!")
            return
        
        curr_price = db.get_current_sse_price(guild)
        db.set_transaction(member=author, curr_price=curr_price, transaction_type="buy")
        await ctx.send(f"{ctx.author.name} just bought into the Chris Stock Exchange for "
                       f"${round(curr_price, 2):,.2f}")


    @commands.command(name="csesell", aliases=["sell", "sellstock"])
    async def sse_sell(self, ctx: commands.Context):
        """ Sell your share of the Chris Stock Exchange at the current stock price """
        guild: discord.Guild | None = ctx.guild # type: ignore
        if guild is None:
            raise Exception("sse_sell(): guild is None")
        sse_status = db.get_sse_status(guild)

        if not sse_status:
            await ctx.send("The Chris Stock Exchange is not currently open")
            return
        
        author: discord.Member = ctx.author # type: ignore
        last_transaction = db.get_last_transaction(author)["action"]

        if last_transaction == "sell":
            await ctx.send("You haven't bought into the SSE yet!")
            return

        curr_price = db.get_current_sse_price(guild)
        db.set_transaction(member=author, curr_price=curr_price, transaction_type="sell")
        await ctx.send(f"{ctx.author.name} just sold share in the Chris Stock Exchange for "
                       f"${round(curr_price, 2):,.2f}")


    @commands.command(name="cseopen", aliases=["csestart"])
    async def sse_start(self, ctx: commands.Context):
        """ Open the Chris Stock Exchange for business """
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.send("Only the server owner can use this command")
            return 
        
        guild: discord.Guild | None = ctx.guild # type: ignore
        if guild is None:
            raise Exception("sse_start(): guild is None")
        sse_status = db.get_sse_status(guild)

        if sse_status:
            await ctx.send("The Chris Stock Exchange is already open!")
            return

        OPENING_PRICE = 1.00
        db.set_sse_status(guild, status=True)
        db.set_current_sse_price(guild, OPENING_PRICE)
        price = db.get_current_sse_price(guild)
        await ctx.send("@everyone The Chris Stock Exchange is now open for business at "
                       f"price of ${round(price, 2):,.2f}!")
        
        live_sse_sessions[guild] = SSESession(guild, "0 9 * * *")


    @commands.command(name="cseclose", aliases=["csestop", "cseend"])
    async def sse_end(self, ctx: commands.Context):
        """ Close the Chris Stock Exchange """
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.send("Only the server owner can use this command")
            return

        guild: discord.Guild | None = ctx.guild # type: ignore
        if guild is None:
            raise Exception("sse_end(): guild is None")
        sse_status = db.get_sse_status(guild)
        
        if not sse_status:
            await ctx.send("The Chris Stock Exchange is not currently open")
            return
        
        db.set_sse_status(guild, status=False)
        await ctx.send("@everyone The Chris Stock Exchange is now closed")

        del live_sse_sessions[guild]
        

    @commands.command(name="lasttransaction")
    async def sse_last_transaction(self, ctx: commands.Context, member: discord.Member | None = None):
        """ View details about your last SSE transaction """
        if member is None:
            member = ctx.author
        transaction = db.get_last_transaction(member)
        if transaction is None:
            who = "You haven't" if member.id == ctx.author.id else f"{member.name} hasn't"
            await ctx.send(f"{who} made any transactions yet. Try the 'ssebuy' or 'ssesell' commands.")
            return
        who = "your" if member.id == ctx.author.id else f"{member.name}'s"
        await ctx.send(f"Here are the details of {who} last transaction:\n"
                       f"\t**Timestamp**: {transaction['timestamp']}\n"
                       f"\t**Transaction Type**: {transaction['action']}\n"
                       f"\t**Price**: ${round(transaction['price'], 2):,.2f}")
        

    @commands.command(name="cseportfolio", aliases=["myportfolio", "seeportfolio", "portfolio"])
    async def sse_portfolio(self, ctx: commands.Context, member: discord.Member | None = None):
        """ View details about your SSE portfolio """
        if member is None:
            member = ctx.author

        transaction = db.get_last_transaction(member)
        curr_price = db.get_current_sse_price(ctx.guild)
        stock = curr_price if transaction["action"] == "buy" else 0
        cash = transaction["cash_value"]
        total = stock + cash
        who = "Your" if member.id == ctx.author.id else f"{member.name}'s"

        await ctx.send(f"```{who} Portfolio Breakdown:\n"
                       f"\tStock Value: ${round(stock, 2):,.2f}\n"
                       f"\tCash Value: ${round(cash, 2):,.2f}\n"
                       f"\tTotal Portfolio Value: ${round(total, 2):,.2f}\n"
                       f"\tOverall Net: ${round(total - 1, 2):,.2f}```")


    @commands.command(name="cseleaderboard")
    async def sse_leaderboard(self, ctx: commands.Context):
        """ View the SSE leaderboard """
        transactions = db.get_transactions(guild=ctx.guild)
        participants = np.unique([transaction["user_id"] for transaction in transactions])
        curr_price = db.get_current_sse_price(ctx.guild)
        portfolios = []

        for participant in participants:
            member = utils.find(lambda m: m.id == participant, ctx.guild.members)
            last_transaction = db.get_last_transaction(member)
            name = last_transaction["user_name"]
            stock = curr_price if last_transaction["action"] == "buy" else 0
            cash = last_transaction["cash_value"]
            portfolio = {
                "name": name,
                "stock_value": stock,
                "cash_value": cash,
                "total": stock + cash,
                "net": (stock + cash) - 1
            }
            portfolios.append((last_transaction, portfolio))

        message = "```CHRIS STOCK EXCHANGE LEADERBOARD\n\n"
        portfolios = sorted(portfolios, key=lambda p: (-p[1]["total"], p[1]["name"]))
        for item in portfolios:
            last_transaction = item[0]
            portfolio = item[1]
            message += (f"{last_transaction["user_name"]}\n"
                        f"\tStock Value: ${round(portfolio["stock_value"], 2):,.2f}\n"
                        f"\tCash Value: ${round(portfolio["cash_value"], 2):,.2f}\n"
                        f"\tTotal Portfolio Value: ${round(portfolio["total"], 2):,.2f}\n"
                        f"\tOverall Net: ${round(portfolio["net"], 2):,.2f}\n")   
        message += "```"

        await ctx.send(message)

    # @commands.command(name="ssetest")
    # async def sse_test(self, ctx: commands.Context, member: discord.Member | None):
    #     """ Test command for the Chris Stock Exchange """
    #     db.get_transactions(member)
    
    #endregion

    #region Helper Functions
    
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