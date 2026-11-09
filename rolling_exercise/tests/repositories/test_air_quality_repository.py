from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from src.repositories.air_quality_repository import AirQualityRepository
from tests.records import make_record


@pytest.fixture
def repository(session) -> AirQualityRepository:
    return AirQualityRepository(session)


def test_get_city_days_returns_only_those_dates(repository):
    repository.save_all(
        [
            make_record(date=date(2024, 11, 19), city="Haifa"),
            make_record(date=date(2024, 11, 20), city="Akko"),
            make_record(date=date(2024, 11, 21), city="Eilat"),
        ]
    )

    city_days = repository.get_city_days({date(2024, 11, 19), date(2024, 11, 21)})

    assert city_days == {(date(2024, 11, 19), "Haifa"), (date(2024, 11, 21), "Eilat")}


def test_same_city_and_date_twice_is_refused(repository):
    repository.save_all([make_record(date=date(2024, 11, 19), city="Haifa")])

    with pytest.raises(IntegrityError):
        repository.save_all([make_record(date=date(2024, 11, 19), city="Haifa")])
