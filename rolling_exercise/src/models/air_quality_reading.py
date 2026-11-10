import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.city_name import CityName


class AirQualityReading(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    line_number: int
    date: datetime.date
    city: CityName
    pm25: float = Field(ge=0, allow_inf_nan=False)
    no2: float = Field(ge=0, allow_inf_nan=False)
    co2: float = Field(ge=0, allow_inf_nan=False)
