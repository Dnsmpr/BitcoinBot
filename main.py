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


bot.run(token)
