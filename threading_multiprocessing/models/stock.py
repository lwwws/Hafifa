from pydantic import BaseModel, ConfigDict


class Stock(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    ticker: str
    dates_env_var: str


SUPPORTED_STOCKS = (
    Stock(name="Bitcoin", ticker="BTC-USD", dates_env_var="BITCOIN_DATES"),
    Stock(name="Google", ticker="GOOGL", dates_env_var="GOOGLE_DATES"),
    Stock(name="Amazon", ticker="AMZN", dates_env_var="AMAZON_DATES"),
)
