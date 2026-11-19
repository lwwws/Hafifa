from pydantic import BaseModel

from src.models.air_quality_reading import AirQualityReading


class ValidRow(BaseModel):
    line_number: int
    reading: AirQualityReading
