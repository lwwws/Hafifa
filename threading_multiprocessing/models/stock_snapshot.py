from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    stock_name: str
    price_change_percent: float
