import os
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict


class Stock(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    ticker: str
    dates_env_var: str


class StockJob(BaseModel):
    """A stock to mine in this run, with the file listing its hours."""

    model_config = ConfigDict(frozen=True)

    stock: Stock
    dates_file: FilePath
    # Used for timestamps in the dates file that have no timezone of their own
    dates_timezone: ZoneInfo


# A stock is mined only if its dates env var is set
SUPPORTED_STOCKS = (
    Stock(name="Bitcoin", ticker="BTC-USD", dates_env_var="BITCOIN_DATES"),
    Stock(name="Google", ticker="GOOGL", dates_env_var="GOOGLE_DATES"),
    Stock(name="Amazon", ticker="AMZN", dates_env_var="AMAZON_DATES"),
)


def _jobs_from_env(dates_timezone: ZoneInfo) -> list[StockJob]:
    return [
        # NOTE: Im not sure how to decouple supported stocks from its env var in a clean way
        # Also prviding timezones is a bit messy
        StockJob(stock=stock, dates_file=os.environ[stock.dates_env_var], dates_timezone=dates_timezone)
        for stock in SUPPORTED_STOCKS
        if stock.dates_env_var in os.environ
    ]


class MinerSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True)

    destination_file: Path
    default_dates_timezone: ZoneInfo = ZoneInfo("UTC")
    jobs: list[StockJob] = Field(
        default_factory=lambda data: _jobs_from_env(data["default_dates_timezone"]),
        min_length=1,
        validate_default=True,
    )
