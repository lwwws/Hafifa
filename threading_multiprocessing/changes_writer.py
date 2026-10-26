from pathlib import Path

import pandas as pd

from models.price_change import PriceChange


def write_changes(changes: list[PriceChange], path: Path):
    rows = pd.DataFrame([change.model_dump() for change in changes], columns=list(PriceChange.model_fields))

    path.parent.mkdir(parents=True, exist_ok=True)
    rows.sort_values(["stock", "timestamp"]).to_csv(path, index=False)
