import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.db.air_quality_record import AirQualityRecord
from src.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    air_quality_record_id: Mapped[int] = mapped_column(ForeignKey(AirQualityRecord.id), unique=True)
    date: Mapped[datetime.date]
    city: Mapped[str]
    aqi: Mapped[float]
