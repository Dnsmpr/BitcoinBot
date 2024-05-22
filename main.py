import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import BitcoinAPI
import Scraper
import Graphing as g

load_dotenv()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), description="BTC Bot")
scaper = Scraper.Scaper()
api = BitcoinAPI.BitcoinAPI(bot, scaper)
g = g.Graphing()
token = str(os.getenv("DISCORD_TOKEN"))


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    await api.start_tasks()


@bot.command(name="nodes", description="Get total amount of nodes.")
async def nodes(ctx: commands.Context):
    await ctx.send(f'{api.get_nodes_online()}')


@bot.command(name="graph")
async def graph(ctx: commands.Context, interval: str):
    await ctx.send(file=discord.File(g.show(api.get_kline(interval), interval), filename='graph.png'))


@bot.command(name="fees", description="Get recommended fees.", aliases=["fee"])
async def fee(ctx: commands.Context):
    fees = api.recommended_fees()
    embed = discord.Embed(title="Recommended Fees", color=discord.Color.green())
    embed.add_field(name="Fastest Fee", value=f"{fees['fastestFee']} sats/vByte", inline=True)
    embed.add_field(name="Half Hour Fee", value=f"{fees['halfHourFee']} sats/vByte", inline=True)
    embed.add_field(name="Hour Fee", value=f"{fees['hourFee']} sats/vByte", inline=True)
    embed.add_field(name="Economy Fee", value=f"{fees['economyFee']} sats/vByte", inline=True)
    embed.add_field(name="Minimum Fee", value=f"{fees['minimumFee']} sats/vByte", inline=True)
    await ctx.send(embed=embed)


@bot.command(name="price",
             description="Get the current price of bitcoin in specified currency",
             aliases=["prices", "p"])
async def price(ctx: commands.Context, currency: str):
    currency = currency.upper()
    embed = discord.Embed(title="Current price of Bitcoin", color=discord.Color.green())
    embed.add_field(name=f"Current price in {currency}: ", value=f"{api.get_current_price(currency)}", inline=True)
    await ctx.send(embed=embed)


@bot.command(name="height", description="Get the current block height.")
async def height(ctx: commands.Context):
    await ctx.send(f"Current block height: {api.get_height()}")


bot.run(token)
