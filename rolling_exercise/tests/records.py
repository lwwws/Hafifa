import datetime

from src.db.air_quality_record import AirQualityRecord
from src.db.alert import Alert
from src.models.aqi_result import AqiResult
from tests.providers.aqi import Co2, No2, Pm25


def make_record(date: datetime.date, city: str, aqi_result: AqiResult, with_alert: bool = False) -> AirQualityRecord:
    record = AirQualityRecord(
        date=date,
        city=city,
        pm25=Pm25.GOOD,
        no2=No2.GOOD,
        co2=Co2.GOOD,
        aqi=aqi_result.aqi,
        aqi_level=aqi_result.aqi_level,
    )

    if with_alert:
        record.alert = Alert(date=date, city=city, aqi=aqi_result.aqi)

    return record
