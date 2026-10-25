import os

from pydantic import BaseModel, ConfigDict, FilePath


class Stock(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    ticker: str
    dates_env_var: str


class StockJob(BaseModel):
    """A stock to mine in this run, with the file listing its timestamps."""

    model_config = ConfigDict(frozen=True)

    stock: Stock
    dates_file: FilePath


SUPPORTED_STOCKS = (
    Stock(name="Bitcoin", ticker="BTC-USD", dates_env_var="BITCOIN_DATES"),
    Stock(name="Google", ticker="GOOGL", dates_env_var="GOOGLE_DATES"),
    Stock(name="Amazon", ticker="AMZN", dates_env_var="AMAZON_DATES"),
)


def build_jobs(stocks: tuple[Stock, ...] = SUPPORTED_STOCKS) -> list[StockJob]:
    """Create a job for every stock whose dates env var is set."""
    jobs = [
        StockJob(stock=stock, dates_file=os.environ[stock.dates_env_var])
        for stock in stocks
        if stock.dates_env_var in os.environ
    ]

    if not jobs:
        env_vars = ", ".join(stock.dates_env_var for stock in stocks)
        raise ValueError(f"No stocks to mine, set at least one of: {env_vars}")

    return jobs
