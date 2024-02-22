import discord
import requests
from discord.ext import commands, tasks


class BitcoinAPI:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.bitcoin_prices = {}
        self.price_endpoint = "https://mempool.space/api/v1/prices"
        self.update_prices()

    def get_current_price(self, currency):
        return int(self.bitcoin_prices[currency])

    def update_prices(self):
        try:
            response = requests.get(self.price_endpoint)
            response.raise_for_status()
            data = response.json()
            self.bitcoin_prices = data
        except requests.exceptions.RequestException as e:
            # Log the error
            print(e)

    @tasks.loop(seconds=10)
    async def price_watch(self):
        try:
            activity = discord.Activity(
                name=f"BTC: {self.get_current_price('USD')} USD",
                type=discord.ActivityType.watching)
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
        except Exception as e:
            # Log the error
            print(e)

    async def start_price_watch(self):
        self.price_watch.start()
