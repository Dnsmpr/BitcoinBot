import discord
import requests
from discord.ext import commands, tasks

import Scraper


class BitcoinAPI:
    def __init__(self, bot: discord.ext.commands.Bot, scraper: Scraper):
        self.bot = bot
        self.scraper = scraper
        self.bitcoin_prices = {}
        self.nodes_online = 0
        self.price_endpoint = "https://mempool.space/api/v1/prices"
        self.fees_endpoint = "https://mempool.space/api/v1/fees/recommended"

    @staticmethod
    def query_api(endpoint):
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            # Log the error
            print(e)

    def get_current_price(self, currency):
        return int(self.bitcoin_prices[currency])

    def update_prices(self):
        self.bitcoin_prices = self.query_api(self.price_endpoint)

    @tasks.loop(seconds=10)
    async def price_watch(self):
        try:
            self.update_prices()
            activity = discord.Activity(
                name=f"BTC: {self.get_current_price('USD')} USD",
                type=discord.ActivityType.watching)
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
        except Exception as e:
            # Log the error
            print(e)

    async def recommended_fees(self):
        return await self.query_api(self.fees_endpoint)

    async def start_tasks(self):
        self.price_watch.start()
        self.node_watch.start()

    def get_nodes_online(self):
        return self.nodes_online

    def update_node_count(self):
        self.nodes_online = self.scraper.get_running_nodes()

    @tasks.loop(seconds=30)
    async def node_watch(self):
        try:
            self.update_node_count()
        except Exception as e:
            # Log the error
            print(e)
