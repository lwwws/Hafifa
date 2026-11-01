import logging

from models.stock_mining_job import build_stock_mining_jobs
from settings import MinerSettings
from stock_miner import mine_stocks
from stock_snapshots_writer import write_stock_snapshots

logger = logging.getLogger(__name__)


def configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(threadName)s] %(message)s")


def main():
    configure_logging()

    settings = MinerSettings()
    jobs = build_stock_mining_jobs(settings)
    logger.info(f"Mining {', '.join(job.stock.name for job in jobs)}")

    snapshots = mine_stocks(jobs, settings)

    write_stock_snapshots(snapshots, settings.destination_file)
    logger.info(f"Wrote {len(snapshots)} rows to {settings.destination_file}")


if __name__ == "__main__":
    main()
