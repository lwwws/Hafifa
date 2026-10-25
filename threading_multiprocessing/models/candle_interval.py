import pandas as pd
from pydantic import BaseModel, ConfigDict


class CandleInterval(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    yahoo_name: str
    length: pd.DateOffset


SUPPORTED_INTERVALS = {
    interval.yahoo_name: interval
    for interval in (
        CandleInterval(yahoo_name="1h", length=pd.DateOffset(hours=1)),
        CandleInterval(yahoo_name="1d", length=pd.DateOffset(days=1)),
        CandleInterval(yahoo_name="1mo", length=pd.DateOffset(months=1)),
    )
}


def interval_by_name(name: str) -> CandleInterval:
    try:
        return SUPPORTED_INTERVALS[name]
    except KeyError:
        raise ValueError(f"Unsupported candle interval {name!r}, expected one of: {', '.join(SUPPORTED_INTERVALS)}") from None
