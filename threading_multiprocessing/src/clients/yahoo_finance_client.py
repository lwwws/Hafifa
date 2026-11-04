from datetime import datetime

import pandas as pd
import yfinance as yf

from src.models.candle_interval import CandleInterval


class YahooFinanceClient:
    def fetch_candles(self, ticker: str, start: datetime, end: datetime, interval: CandleInterval) -> pd.DataFrame:
        candles = yf.Ticker(ticker).history(start=start, end=end, interval=interval.yahoo_name)

        if candles.empty:
            return candles

        # Daily/monthly candles come with second precision, we can't compare them with microsecond timestamps
        candles.index = candles.index.as_unit("us")

        return candles
