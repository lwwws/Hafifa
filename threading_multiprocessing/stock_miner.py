import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from dates_reader import read_dates
from models.stock_mining_job import StockMiningJob
from models.stock_snapshot import StockSnapshot
from price_fetcher import fetch_stock_snapshots
from settings import MinerSettings

logger = logging.getLogger(__name__)


def _mine_stock(job: StockMiningJob, settings: MinerSettings) -> list[StockSnapshot]:
    timestamps = read_dates(job.dates_file, settings.default_dates_timezone)

    return fetch_stock_snapshots(job.stock, timestamps, settings.candle_interval)


def mine_stocks(jobs: list[StockMiningJob], settings: MinerSettings) -> list[StockSnapshot]:
    with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
        future_to_job = {executor.submit(_mine_stock, job, settings): job for job in jobs}

        snapshots = []
        for future in as_completed(future_to_job):
            try:
                snapshots.extend(future.result())
            except Exception:
                logger.exception(f"{future_to_job[future].stock.name}: failed, skipping")

    return snapshots
