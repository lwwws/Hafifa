from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PriceChange(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    stock: str
    change_percent: float
