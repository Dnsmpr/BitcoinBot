import mplfinance as mpf
import pandas as pd
import io


class Graphing:
    def __init__(self):
        self.df = None

    def normalize_data(self, data):
        df = pd.DataFrame(data)
        df = df.iloc[-50:, 0:7]
        df.columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Close Time"]
        df["Open"] = df["Open"].astype(float)
        df["High"] = df["High"].astype(float)
        df["Low"] = df["Low"].astype(float)
        df["Close"] = df["Close"].astype(float)
        df["Volume"] = df["Volume"].astype(float)
        df["Date"] = pd.to_datetime(df["Date"], unit='ms')
        df["Close Time"] = pd.to_datetime(df["Close Time"], unit='ms')
        self.df = df.set_index("Date")

    def show(self, data, interval):
        self.normalize_data(data)
        buffer = io.BytesIO()
        kwargs = dict(type='candle',
                      volume=True,
                      figscale=0.75,
                      title=f"BTC/USD {interval} Kline",
                      ylabel='Price (USD)',
                      ylabel_lower='Volume', style='yahoo',
                      savefig=dict(fname=buffer, format='png'),
                      tight_layout=True,
                      figratio=(16, 9),
                      panel_ratios=(6, 2))
        mpf.plot(self.df, **kwargs)
        buffer.seek(0)
        return buffer
