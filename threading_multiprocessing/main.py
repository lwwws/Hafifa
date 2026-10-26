import logging

from changes_writer import write_changes
from models.stock_job import build_jobs
from settings import MinerSettings
from stock_miner import mine_stocks

logger = logging.getLogger(__name__)


def configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(threadName)s] %(message)s")


def main():
    configure_logging()

    settings = MinerSettings()
    jobs = build_jobs()
    logger.info(f"Mining {', '.join(job.stock.name for job in jobs)}")

    changes = mine_stocks(jobs, settings)

    write_changes(changes, settings.destination_file)
    logger.info(f"Wrote {len(changes)} rows to {settings.destination_file}")


if __name__ == "__main__":
    main()
