import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from dates_reader import read_dates
from price_fetcher import PriceChange, fetch_price_changes
from settings import MinerSettings
from stocks import StockJob

logger = logging.getLogger(__name__)


def _run_job(job: StockJob, settings: MinerSettings) -> list[PriceChange]:
    timestamps = read_dates(job.dates_file, settings.default_dates_timezone)
    return fetch_price_changes(job.stock, timestamps, settings.candle_interval)


def mine_stocks(jobs: list[StockJob], settings: MinerSettings) -> list[PriceChange]:
    with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        future_to_job = {executor.submit(_run_job, job, settings): job for job in jobs}

        changes = []
        for future in as_completed(future_to_job):
            try:
                changes.extend(future.result())
            except Exception:
                logger.exception("%s: failed, skipping", future_to_job[future].stock.name)

    return changes
