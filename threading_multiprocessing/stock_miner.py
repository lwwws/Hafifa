import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from dates_reader import read_dates
from price_fetcher import HourlyChange, fetch_hourly_changes
from settings import StockJob

logger = logging.getLogger(__name__)


def _run_job(job: StockJob) -> list[HourlyChange]:
    hours = read_dates(job.dates_file, job.dates_timezone)
    return fetch_hourly_changes(job.stock, hours)


def mine_stocks(jobs: list[StockJob]) -> list[HourlyChange]:
    """Run each job in its own thread and collect the changes of all of them.

    A failed job is logged and skipped.
    """
    with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        future_to_job = {executor.submit(_run_job, job): job for job in jobs}

        changes = []
        for future in as_completed(future_to_job):
            try:
                changes.extend(future.result())
            except Exception:
                logger.exception("%s: failed, skipping", future_to_job[future].stock.name)

    return changes
