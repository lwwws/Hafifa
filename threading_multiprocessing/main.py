import logging

from logging_config import configure_logging
from models.stock_mining_job import build_stock_mining_jobs
from settings import MinerSettings
from stock_miner import StockMiner
from stock_snapshots_writer import write_stock_snapshots
from yahoo_finance_client import YahooFinanceClient

logger = logging.getLogger(__name__)


def main():
    configure_logging()

    settings = MinerSettings()
    jobs = build_stock_mining_jobs(settings)
    logger.info(f"Mining {', '.join(job.stock.name for job in jobs)}")

    yahoo_finance_client = YahooFinanceClient()
    stock_miner = StockMiner(settings, yahoo_finance_client)
    snapshots = stock_miner.mine_stocks(jobs)

    write_stock_snapshots(snapshots, settings.destination_file)
    logger.info(f"Wrote {len(snapshots)} rows to {settings.destination_file}")


if __name__ == "__main__":
    main()
