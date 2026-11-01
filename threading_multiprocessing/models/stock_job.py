from pydantic import BaseModel, ConfigDict, FilePath

from models.stock import SUPPORTED_STOCKS, Stock
from settings import MinerSettings


class StockJob(BaseModel):
    model_config = ConfigDict(frozen=True)

    stock: Stock
    dates_file: FilePath


def build_jobs(settings: MinerSettings) -> list[StockJob]:
    return [
        StockJob(stock=SUPPORTED_STOCKS[env_var], dates_file=dates_file)
        for env_var, dates_file in settings.dates_files.items()
    ]
