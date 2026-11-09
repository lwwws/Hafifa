import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.air_quality_record import AirQualityRecord


class AirQualityRepository:
    def __init__(self, session: Session):
        self._session = session

    def save_all(self, records: list[AirQualityRecord]):
        self._session.add_all(records)
        self._session.commit()

    def get_city_days(self, dates: set[datetime.date]) -> set[tuple[datetime.date, str]]:
        query = select(AirQualityRecord.date, AirQualityRecord.city).where(AirQualityRecord.date.in_(dates))

        return {(date, city) for date, city in self._session.execute(query)}
