import logging
from datetime import datetime

import pandas as pd
import yfinance as yf

from models.candle_interval import CandleInterval
from models.price_change import PriceChange
from models.stock import Stock

logger = logging.getLogger(__name__)


def _fetch_candles(ticker: str, start: datetime, end: datetime, interval: CandleInterval) -> pd.DataFrame:
    return yf.Ticker(ticker).history(start=start, end=end, interval=interval.yahoo_name)


def _containing_candle(candles: pd.DataFrame, timestamp: datetime, interval: CandleInterval) -> pd.Series | None:
    start = candles.index.asof(timestamp)

    if pd.isna(start) or timestamp >= start + interval.length:
        return None

    return candles.loc[start]


def _change_percent(candle: pd.Series) -> float:
    return (candle["Close"] - candle["Open"]) / candle["Open"] * 100


def fetch_price_changes(stock: Stock, timestamps: list[datetime], interval: CandleInterval) -> list[PriceChange]:
    if not timestamps:
        return []

    candles = _fetch_candles(
        stock.ticker, min(timestamps) - interval.length, max(timestamps) + interval.length, interval,
    )

    if candles.empty:
        logger.warning(f"{stock.name}: no candles returned for {stock.ticker}")
        return []

    # Candles which are monthly/daily come with second precision, and we can't compare them with microsecond precision timestamps
    candles.index = candles.index.as_unit("us")

    changes = []
    for timestamp in timestamps:
        candle = _containing_candle(candles, timestamp, interval)
        if candle is not None:
            changes.append(PriceChange(timestamp=timestamp, stock=stock.name, change_percent=_change_percent(candle)))

    skipped = len(timestamps) - len(changes)
    logger.info(f"{stock.name}: {len(changes)} of {len(timestamps)} timestamps have data, {skipped} skipped (no candle)")

    return changes
