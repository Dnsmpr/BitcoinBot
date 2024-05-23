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


@bot.command(name="nodes", description="Get the total amount of nodes.")
async def nodes(ctx: commands.Context):
    nodes_online = api.get_nodes_online()  # Retrieve the total amount of nodes
    embed = discord.Embed(
        title="🌐 Total Nodes Online",
        description="The current total number of active nodes in the network is displayed below:",
        color=discord.Color.orange()  # You can choose a color that fits your bot's theme
    )
    embed.add_field(name="Nodes Online:", value=f"**{nodes_online}**", inline=False)
    await ctx.send(embed=embed)


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
    embed = discord.Embed(
        title="📈 Current Bitcoin Price",
        description=f"The latest price of Bitcoin (BTC) in **{currency}** is provided below:",
        color=discord.Color.green()
    )
    current_price = api.get_current_price(currency)
    embed.add_field(name=f"Price in {currency}:", value=f"**{current_price}** {currency}", inline=False)
    await ctx.send(embed=embed)


@bot.command(name="height", description="Get the current block height.")
async def height(ctx: commands.Context):
    block_height = api.get_height()
    embed = discord.Embed(
        title="🏗️ Current Block Height",
        description="The current height of the blockchain is shown below:",
        color=discord.Color.green()
    )
    embed.add_field(name="Block Height:", value=f"**{block_height}**", inline=False)
    await ctx.send(embed=embed)


@bot.command(name="mempool", description="Get the current block height.")
async def mempool(ctx: commands.Context):
    mempool_data, mempool_fee = api.get_mempool()
    embed = discord.Embed(
        title=(
            f"Mempool Summary: {mempool_data[0]} transactions, "
            f"totaling {int(mempool_data[1] / 1_000_000)} MB, "
            f"with {int(mempool_data[2] / 100_000_000)} BTC in fees"
        ),
        color=discord.Color.green()
    )

    embed.add_field(name="0MB  - 1MB", value=f"{mempool_fee[0]} sats/vbyte", inline=True)
    embed.add_field(name="1MB  - 4MB", value=f"{mempool_fee[1]} sats/vbyte", inline=True)
    embed.add_field(name="4MB  - 12MB", value=f"{mempool_fee[2]} sats/vbyte", inline=True)
    embed.add_field(name="12MB - 20MB", value=f"{mempool_fee[3]} sats/vbyte", inline=True)
    embed.add_field(name="20MB - 28MB", value=f"{mempool_fee[4]} sats/vbyte", inline=True)
    embed.add_field(name="28MB - 36MB", value=f"{mempool_fee[5]} sats/vbyte", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="ls", description="Long short ratio")
async def ls(ctx: commands.Context):
    long, short, interest_btc, interest_usd = api.get_market_data()
    interest_btc = float(interest_btc)
    interest_usd = float(interest_usd)
    long = float(long)
    short = float(short)
    embed = discord.Embed(
        title="📊 Market Position Ratios",
        description=(
            "Here's the current long and short ratio for Bitcoin futures in both BTC and USD, "
            "along with the open interest data:"
        ),
        color=discord.Color.dark_green()
    )
    embed.add_field(name="📈 Long Ratio (%)", value=f"{long * 100:.3f}%", inline=True)
    embed.add_field(name="💵 Long Ratio (USD)", value=f"${long * interest_usd:,.0f}", inline=True)
    embed.add_field(name="₿ Long Ratio (BTC)", value=f"{long * interest_btc:,.0f} BTC", inline=True)
    embed.add_field(name="📉 Short Ratio (%)", value=f"{short * 100:,.3f}%", inline=True)
    embed.add_field(name="💵 Short Ratio (USD)", value=f"${short * interest_usd:,.0f}", inline=True)
    embed.add_field(name="₿ Short Ratio (BTC)", value=f"{short * interest_btc:,.0f} BTC", inline=True)


    await ctx.send(embed=embed)


bot.run(token)
