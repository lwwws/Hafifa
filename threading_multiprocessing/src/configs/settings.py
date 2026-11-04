import os
from pathlib import Path
from typing import Self
from zoneinfo import ZoneInfo

from pydantic import Field, FilePath, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.models.candle_interval import CandleInterval, interval_by_name
from src.models.stock import SUPPORTED_STOCKS


def _read_dates_files() -> dict[str, str]:
    return {env_var: os.environ[env_var] for env_var in SUPPORTED_STOCKS if env_var in os.environ}


class MinerSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, enable_decoding=False)

    destination_file: Path
    default_dates_timezone: ZoneInfo
    candle_interval: CandleInterval
    max_workers: int = Field(gt=0)
    dates_files: dict[str, FilePath] = Field(default_factory=_read_dates_files, validate_default=True)

    @field_validator("candle_interval", mode="before")
    @classmethod
    def _interval_from_name(cls, name: str) -> CandleInterval:
        return interval_by_name(name)

    @model_validator(mode="after")
    def _require_dates_file(self) -> Self:
        if not self.dates_files:
            raise ValueError(f"No stocks to mine, set at least one of: {', '.join(SUPPORTED_STOCKS)}")

        return self
