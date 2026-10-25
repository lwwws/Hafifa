import logging
from pathlib import Path

import pandas as pd

from price_fetcher import PriceChange
from settings import MinerSettings
from stock_miner import mine_stocks
from stocks import build_jobs

logger = logging.getLogger(__name__)


def write_changes(changes: list[PriceChange], path: Path) -> None:
    rows = pd.DataFrame([change.model_dump() for change in changes], columns=list(PriceChange.model_fields))

    path.parent.mkdir(parents=True, exist_ok=True)
    rows.sort_values(["stock", "timestamp"]).to_csv(path, index=False)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(threadName)s] %(message)s")

    settings = MinerSettings()
    jobs = build_jobs()
    logger.info("Mining %s", ", ".join(job.stock.name for job in jobs))

    changes = mine_stocks(jobs, settings)

    write_changes(changes, settings.destination_file)
    logger.info("Wrote %d rows to %s", len(changes), settings.destination_file)


if __name__ == "__main__":
    main()
