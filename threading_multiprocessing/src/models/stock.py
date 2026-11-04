from pydantic import BaseModel, ConfigDict


class Stock(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    ticker: str


SUPPORTED_STOCKS = {
    "BITCOIN_DATES": Stock(name="Bitcoin", ticker="BTC-USD"),
    "GOOGLE_DATES": Stock(name="Google", ticker="GOOGL"),
    "AMAZON_DATES": Stock(name="Amazon", ticker="AMZN"),
}
