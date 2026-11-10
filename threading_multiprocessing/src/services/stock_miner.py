import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import pandas as pd

from src.clients.yahoo_finance_client import YahooFinanceClient
from src.configs.settings import MinerSettings
from src.file_io.dates_reader import read_dates
from src.models.stock import Stock
from src.models.stock_mining_job import StockMiningJob
from src.models.stock_snapshot import StockSnapshot

logger = logging.getLogger(__name__)


def _change_percent(candle: pd.Series) -> float:
    return (candle["Close"] - candle["Open"]) / candle["Open"] * 100


class StockMiner:
    def __init__(self, settings: MinerSettings, yahoo_finance_client: YahooFinanceClient):
        self._yahoo_finance_client = yahoo_finance_client
        self._candle_interval = settings.candle_interval
        self._default_timezone = settings.default_dates_timezone
        self._max_workers = settings.max_workers

    def mine_stocks_concurrently(self, jobs: list[StockMiningJob]) -> list[StockSnapshot]:
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_job = {executor.submit(self._collect_stock_snapshots, job): job for job in jobs}

            snapshots = []

            for future in as_completed(future_to_job):
                try:
                    snapshots.extend(future.result())
                except Exception:
                    logger.exception(f"{future_to_job[future].stock.name}: failed, skipping")

        return snapshots

    def _collect_stock_snapshots(self, job: StockMiningJob) -> list[StockSnapshot]:
        timestamps = read_dates(job.dates_file, self._default_timezone)

        if not timestamps:
            return []

        candles = self._fetch_candles(job.stock, min(timestamps), max(timestamps))

        if candles.empty:
            logger.warning(f"{job.stock.name}: no candles returned for {job.stock.ticker}")

            return []

        snapshots = self._snapshots_at_timestamps(job.stock, candles, timestamps)
        self._log_coverage(job.stock, len(snapshots), len(timestamps))

        return snapshots

    def _snapshots_at_timestamps(
        self, stock: Stock, candles: pd.DataFrame, timestamps: list[datetime]
    ) -> list[StockSnapshot]:
        snapshots = []

        for timestamp in timestamps:
            candle = self._containing_candle(candles, timestamp)

            if candle is not None:
                price_change_percent = _change_percent(candle)
                snapshots.append(
                    StockSnapshot(timestamp=timestamp, stock_name=stock.name, price_change_percent=price_change_percent)
                )

        return snapshots

    def _log_coverage(self, stock: Stock, found: int, total: int):
        logger.info(f"{stock.name}: {found} of {total} timestamps have data, {total - found} skipped (no candle)")

    def _fetch_candles(self, stock: Stock, first: datetime, last: datetime) -> pd.DataFrame:
        return self._yahoo_finance_client.fetch_candles(
            stock.ticker,
            start=first - self._candle_interval.length,
            end=last + self._candle_interval.length,
            interval=self._candle_interval,
        )

    def _containing_candle(self, candles: pd.DataFrame, timestamp: datetime) -> pd.Series | None:
        start = candles.index.asof(timestamp)

        if pd.isna(start) or timestamp >= start + self._candle_interval.length:
            return None

        return candles.loc[start]
