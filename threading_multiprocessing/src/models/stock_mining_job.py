from pydantic import BaseModel, ConfigDict, FilePath

from src.configs.settings import MinerSettings
from src.models.stock import SUPPORTED_STOCKS, Stock


class StockMiningJob(BaseModel):
    model_config = ConfigDict(frozen=True)

    stock: Stock
    dates_file: FilePath


def build_stock_mining_jobs(settings: MinerSettings) -> list[StockMiningJob]:
    return [
        StockMiningJob(stock=SUPPORTED_STOCKS[env_var], dates_file=dates_file)
        for env_var, dates_file in settings.dates_files.items()
    ]
