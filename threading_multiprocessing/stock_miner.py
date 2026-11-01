import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import pandas as pd
import yfinance as yf

from dates_reader import read_dates
from models.stock import Stock
from models.stock_mining_job import StockMiningJob
from models.stock_snapshot import StockSnapshot
from settings import MinerSettings

logger = logging.getLogger(__name__)


def _change_percent(candle: pd.Series) -> float:
    return (candle["Close"] - candle["Open"]) / candle["Open"] * 100


class StockMiner:
    def __init__(self, settings: MinerSettings):
        self._candle_interval = settings.candle_interval
        self._default_timezone = settings.default_dates_timezone
        self._max_workers = settings.max_workers

    def mine_stocks(self, jobs: list[StockMiningJob]) -> list[StockSnapshot]:
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_job = {executor.submit(self._mine_stock, job): job for job in jobs}

            snapshots = []
            for future in as_completed(future_to_job):
                try:
                    snapshots.extend(future.result())
                except Exception:
                    logger.exception(f"{future_to_job[future].stock.name}: failed, skipping")

        return snapshots

    def _mine_stock(self, job: StockMiningJob) -> list[StockSnapshot]:
        timestamps = read_dates(job.dates_file, self._default_timezone)
        if not timestamps:
            return []

        candles = self._fetch_candles(job.stock, min(timestamps), max(timestamps))
        if candles.empty:
            logger.warning(f"{job.stock.name}: no candles returned for {job.stock.ticker}")
            return []

        snapshots = []
        for timestamp in timestamps:
            candle = self._containing_candle(candles, timestamp)
            if candle is not None:
                snapshots.append(
                    StockSnapshot(
                        timestamp=timestamp, stock_name=job.stock.name, price_change_percent=_change_percent(candle),
                    )
                )

        found, skipped = len(snapshots), len(timestamps) - len(snapshots)
        logger.info(
            f"{job.stock.name}: {found} of {len(timestamps)} timestamps have data, {skipped} skipped (no candle)"
        )

        return snapshots

    def _fetch_candles(self, stock: Stock, first: datetime, last: datetime) -> pd.DataFrame:
        candles = yf.Ticker(stock.ticker).history(
            start=first - self._candle_interval.length,
            end=last + self._candle_interval.length,
            interval=self._candle_interval.yahoo_name,
        )
        if candles.empty:
            return candles

        # Daily/monthly candles come with second precision, we can't compare them with microsecond timestamps
        candles.index = candles.index.as_unit("us")

        return candles

    def _containing_candle(self, candles: pd.DataFrame, timestamp: datetime) -> pd.Series | None:
        start = candles.index.asof(timestamp)

        if pd.isna(start) or timestamp >= start + self._candle_interval.length:
            return None

        return candles.loc[start]
