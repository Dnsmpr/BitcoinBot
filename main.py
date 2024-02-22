import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import BitcoinAPI

load_dotenv()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), description="BTC Bot")
api = BitcoinAPI.BitcoinAPI(bot)
token = str(os.getenv("DISCORD_TOKEN"))


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    await api.start_price_watch()


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

bot.run(token)
