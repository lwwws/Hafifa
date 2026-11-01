from pathlib import Path

import pandas as pd

from models.stock_snapshot import StockSnapshot


def write_stock_snapshots(snapshots: list[StockSnapshot], path: Path):
    rows = pd.DataFrame([snapshot.model_dump() for snapshot in snapshots], columns=list(StockSnapshot.model_fields))

    path.parent.mkdir(parents=True, exist_ok=True)
    rows.sort_values(["stock_name", "timestamp"]).to_csv(path, index=False)
