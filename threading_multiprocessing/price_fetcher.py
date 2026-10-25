import logging
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from pydantic import BaseModel, ConfigDict

from settings import Stock

logger = logging.getLogger(__name__)

# NOTE: I don't really like that we are fixed on hour here,
# i can couple the candle interval this way, but hourly change still hardcoded
class CandleInterval(BaseModel):
    model_config = ConfigDict(frozen=True)

    yahoo_name: str
    length: timedelta


HOURLY = CandleInterval(yahoo_name="1h", length=timedelta(hours=1))


class HourlyChange(BaseModel):
    model_config = ConfigDict(frozen=True)

    hour: datetime
    stock: str
    change_percent: float


def _fetch_candles(ticker: str, start: datetime, end: datetime) -> pd.DataFrame:
    return yf.Ticker(ticker).history(start=start, end=end, interval=HOURLY.yahoo_name)


def _containing_candle(candles: pd.DataFrame, hour: datetime) -> pd.Series | None:
    # Candles are indexed by their start time, so the only candidate is the last one starting at or before the hour.
    start = candles.index.asof(hour)

    if pd.isna(start) or hour >= start + HOURLY.length:
        return None

    return candles.loc[start]


def _change_percent(candle: pd.Series) -> float:
    return (candle["Close"] - candle["Open"]) / candle["Open"] * 100


def fetch_hourly_changes(stock: Stock, hours: list[datetime]) -> list[HourlyChange]:
    """Fetch the stock's hourly candles in one request and compute the % change for each hour.

    Hours with no candle (the market was closed) are skipped.
    """
    if not hours:
        return []

    # Widen by one candle, since the candle containing the first hour can start before it.
    candles = _fetch_candles(stock.ticker, min(hours) - HOURLY.length, max(hours) + HOURLY.length)

    if candles.empty:
        logger.warning("%s: no candles returned for %s", stock.name, stock.ticker)
        return []

    changes = []
    for hour in hours:
        candle = _containing_candle(candles, hour)
        if candle is not None:
            changes.append(HourlyChange(hour=hour, stock=stock.name, change_percent=_change_percent(candle)))

    logger.info(
        "%s: %d of %d hours have data, %d skipped (no candle)",
        stock.name, len(changes), len(hours), len(hours) - len(changes),
    )

    return changes
