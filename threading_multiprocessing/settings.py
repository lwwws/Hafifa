from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from candle_interval import CandleInterval, interval_by_name


class MinerSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, enable_decoding=False)

    destination_file: Path
    # Used for timestamps in the dates files that have no timezone of their own
    default_dates_timezone: ZoneInfo
    candle_interval: CandleInterval

    @field_validator("candle_interval", mode="before")
    @classmethod
    def _interval_from_name(cls, name: str) -> CandleInterval:
        return interval_by_name(name)
