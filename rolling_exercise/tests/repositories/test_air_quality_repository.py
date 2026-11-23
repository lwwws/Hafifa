import pytest
from sqlalchemy.exc import IntegrityError

from src.repositories.air_quality_repository import AirQualityRepository
from tests.providers.aqi import AqiResults
from tests.providers.city_days import City, Day
from tests.records import make_record


@pytest.fixture
def repository(session) -> AirQualityRepository:
    return AirQualityRepository(session)


def test_get_city_days_returns_only_those_dates(repository):
    repository.save_all(
        [
            make_record(Day.FIRST, City.HAIFA, AqiResults.GOOD),
            make_record(Day.SECOND, City.AKKO, AqiResults.GOOD),
            make_record(Day.THIRD, City.EILAT, AqiResults.GOOD),
        ]
    )

    city_days = repository.get_city_days({Day.FIRST, Day.THIRD})

    assert city_days == {(Day.FIRST, City.HAIFA), (Day.THIRD, City.EILAT)}


def test_same_city_and_date_twice_is_refused(repository):
    repository.save_all([make_record(Day.FIRST, City.HAIFA, AqiResults.GOOD)])

    with pytest.raises(IntegrityError):
        repository.save_all([make_record(Day.FIRST, City.HAIFA, AqiResults.GOOD)])
