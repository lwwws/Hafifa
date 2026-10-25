import logging
from pathlib import Path

import pandas as pd

from price_fetcher import HourlyChange
from settings import MinerSettings
from stock_miner import mine_stocks

logger = logging.getLogger(__name__)


def write_changes(changes: list[HourlyChange], path: Path) -> None:
    rows = pd.DataFrame([change.model_dump() for change in changes], columns=list(HourlyChange.model_fields))

    path.parent.mkdir(parents=True, exist_ok=True)
    rows.sort_values(["stock", "hour"]).to_csv(path, index=False)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(threadName)s] %(message)s")

    settings = MinerSettings()
    logger.info("Mining %s", ", ".join(job.stock.name for job in settings.jobs))

    changes = mine_stocks(settings.jobs)

    write_changes(changes, settings.destination_file)
    logger.info("Wrote %d rows to %s", len(changes), settings.destination_file)


if __name__ == "__main__":
    main()
