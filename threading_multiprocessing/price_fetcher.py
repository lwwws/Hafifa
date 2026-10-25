import logging
from datetime import datetime

import pandas as pd
import yfinance as yf
from pydantic import BaseModel, ConfigDict

from candle_interval import CandleInterval
from stocks import Stock

logger = logging.getLogger(__name__)


class PriceChange(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    stock: str
    change_percent: float


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
    """Fetch the stock's candles in one request and compute the % change of the candle containing each timestamp.

    Timestamps with no candle (the market was closed) are skipped.
    """
    if not timestamps:
        return []

    candles = _fetch_candles(
        stock.ticker, min(timestamps) - interval.length, max(timestamps) + interval.length, interval,
    )

    if candles.empty:
        logger.warning("%s: no candles returned for %s", stock.name, stock.ticker)
        return []

    changes = []
    for timestamp in timestamps:
        candle = _containing_candle(candles, timestamp, interval)
        if candle is not None:
            changes.append(PriceChange(timestamp=timestamp, stock=stock.name, change_percent=_change_percent(candle)))

    logger.info(
        "%s: %d of %d timestamps have data, %d skipped (no candle)",
        stock.name, len(changes), len(timestamps), len(timestamps) - len(changes),
    )

    return changes
