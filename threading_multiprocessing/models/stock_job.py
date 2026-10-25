import os

from pydantic import BaseModel, ConfigDict, FilePath

from models.stock import SUPPORTED_STOCKS, Stock


class StockJob(BaseModel):
    model_config = ConfigDict(frozen=True)

    stock: Stock
    dates_file: FilePath


def build_jobs(stocks: tuple[Stock, ...] = SUPPORTED_STOCKS) -> list[StockJob]:
    jobs = [
        StockJob(stock=stock, dates_file=os.environ[stock.dates_env_var])
        for stock in stocks
        if stock.dates_env_var in os.environ
    ]

    if not jobs:
        env_vars = ", ".join(stock.dates_env_var for stock in stocks)
        raise ValueError(f"No stocks to mine, set at least one of: {env_vars}")

    return jobs
