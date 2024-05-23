import discord
import requests
from discord.ext import commands, tasks

import Scraper

ONE_MB = 1000000


class BitcoinAPI:
    def __init__(self, bot: discord.ext.commands.Bot, scraper: Scraper):
        self.bot = bot
        self.scraper = scraper
        self.bitcoin_prices = {}
        self.nodes_online = 0
        self.price_endpoint = "https://mempool.space/api/v1/prices"
        self.fees_endpoint = "https://mempool.space/api/v1/fees/recommended"
        self.kline_endpoint = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval="
        self.height_endpoint = "https://mempool.space/api/blocks/tip/height"
        self.mempool_endpoint = "https://mempool.space/api/mempool"
        self.long_short_endpoint = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1"
        self.open_interest_endpoint = "https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&limit=1"

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

    def recommended_fees(self):
        return self.query_api(self.fees_endpoint)

    async def start_tasks(self):
        self.price_watch.start()
        self.node_watch.start()

    def get_nodes_online(self):
        return self.nodes_online

    def update_node_count(self):
        self.nodes_online = self.scraper.get_running_nodes()

    @tasks.loop(minutes=30)
    async def node_watch(self):
        try:
            self.update_node_count()
        except Exception as e:
            # Log the error
            print(e)

    def get_kline(self, interval: str):
        kline_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
        if interval not in kline_intervals:
            return "Invalid interval."
        return self.query_api(self.kline_endpoint + interval)

    def get_height(self):
        return self.query_api(self.height_endpoint)

    def get_mempool(self):
        data = self.query_api(self.mempool_endpoint)
        fee_hist = data["fee_histogram"]
        mb_range = [ONE_MB, 4 * ONE_MB, 12 * ONE_MB, 20 * ONE_MB, 28 * ONE_MB, 36 * ONE_MB]
        mempool = [(data["count"], data["vsize"], data["total_fee"])]
        fee_range = []
        index = 0
        for s in mb_range:
            min_range, max_range, index = self.get_mempool_size(fee_hist[index:], s, index)
            fee_range.append((int(min_range), int(max_range)))

        mempool.append(fee_range)

        return mempool


    def get_mempool_size(self, fee_hist, mb_range, index):

        acc = 0
        tx = []
        for entry in fee_hist:
            index += 1
            if acc + entry[1] <= mb_range:
                acc = acc + entry[1]
                tx.append(entry)
            else:
                return min(tx, key=lambda x: x[0])[0], max(tx, key=lambda x: x[0])[0], index

    def get_long_short_ratio(self):
        ls = self.query_api(self.long_short_endpoint)[0]
        return ls["longAccount"], ls["shortAccount"]

    def get_open_interest(self):
        oi = self.query_api(self.open_interest_endpoint)[0]
        return oi["sumOpenInterest"], oi["sumOpenInterestValue"]

    def get_market_data(self):
        long, short = self.get_long_short_ratio()
        interest_btc, interest_usd = self.get_open_interest()

        return long, short, interest_btc, interest_usd



