import io
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.air_quality_record import AirQualityRecord
from src.db.alert import Alert
from src.errors import InvalidCsvFileError
from src.models.aqi_result import AqiResult
from src.models.rejected_row import RejectedRow
from src.models.upload_report import UploadReport
from src.parsing.air_quality_csv_parser import AirQualityCsvParser
from src.repositories.air_quality_repository import AirQualityRepository
from src.services.air_quality_upload_service import AirQualityUploadService
from src.services.aqi_calculator import AqiCalculator
from tests.csv_rows import to_csv_file
from tests.providers.aqi import AqiLevel, AqiResults, Pm25
from tests.providers.city_days import City, Day
from tests.providers.csv_content import CsvFileContent, CsvRow

ALERT_AQI_THRESHOLD = 300


@pytest.fixture
def calculator() -> Mock:
    calculator = Mock(spec=AqiCalculator)
    calculator.calculate.return_value = AqiResults.GOOD

    return calculator


@pytest.fixture
def service(calculator, session) -> AirQualityUploadService:
    return AirQualityUploadService(
        AirQualityCsvParser(), calculator, AirQualityRepository(session), ALERT_AQI_THRESHOLD
    )


def upload_rows(service: AirQualityUploadService, *rows: str) -> UploadReport:
    return service.upload("air_quality.csv", to_csv_file(*rows))


def saved_records(session: Session) -> list[AirQualityRecord]:
    return list(session.scalars(select(AirQualityRecord).order_by(AirQualityRecord.id)))


def saved_alerts(session: Session) -> list[Alert]:
    return list(session.scalars(select(Alert).order_by(Alert.id)))


def rejected_lines(report: UploadReport) -> list[int]:
    return [rejected_row.line_number for rejected_row in report.rejected_rows]


def test_valid_row_is_saved_with_its_aqi(service, session):
    report = upload_rows(service, CsvRow.VALID)

    (record,) = saved_records(session)
    assert (record.date, record.city) == (Day.FIRST, City.HAIFA)
    assert (record.aqi, record.aqi_level) == (AqiResults.GOOD.aqi, AqiResults.GOOD.aqi_level)
    assert report.saved_rows == 1


def test_aqi_over_threshold_creates_alert(service, calculator, session):
    calculator.calculate.return_value = AqiResult(aqi=ALERT_AQI_THRESHOLD + 1, aqi_level=AqiLevel.HAZARDOUS)

    report = upload_rows(service, CsvRow.VALID)

    (alert,) = saved_alerts(session)
    assert alert.city == City.HAIFA
    assert alert.aqi == ALERT_AQI_THRESHOLD + 1
    assert report.created_alerts == 1


def test_aqi_at_threshold_creates_no_alert(service, calculator, session):
    calculator.calculate.return_value = AqiResult(aqi=ALERT_AQI_THRESHOLD, aqi_level=AqiLevel.VERY_UNHEALTHY)

    report = upload_rows(service, CsvRow.VALID)

    assert saved_alerts(session) == []
    assert report.created_alerts == 0


def test_city_that_already_has_data_for_the_date_is_rejected(service, session):
    upload_rows(service, CsvRow.VALID)

    report = upload_rows(service, CsvRow.VALID)

    assert len(saved_records(session)) == 1
    assert report.rejected_rows == [RejectedRow(line_number=2, reason=f"{City.HAIFA} already has data for {Day.FIRST}")]


def test_duplicate_check_ignores_city_case(service, session):
    upload_rows(service, CsvRow.VALID)

    report = upload_rows(service, CsvRow.VALID_WITH_UPPERCASE_CITY)

    assert len(saved_records(session)) == 1
    assert rejected_lines(report) == [2]


def test_same_city_on_another_date_is_saved(service, session):
    upload_rows(service, CsvRow.VALID)

    report = upload_rows(service, CsvRow.VALID_ON_NEXT_DAY)

    assert len(saved_records(session)) == 2
    assert rejected_lines(report) == []


def test_same_city_and_date_twice_in_file_keeps_the_first(service, session):
    report = upload_rows(service, CsvRow.VALID, CsvRow.SAME_CITY_AND_DAY_AS_VALID)

    assert [record.pm25 for record in saved_records(session)] == [Pm25.GOOD]
    assert rejected_lines(report) == [3]


def test_invalid_row_is_reported_and_not_saved(service, session):
    report = upload_rows(service, CsvRow.VALID, CsvRow.EMPTY_NO2)

    assert len(saved_records(session)) == 1
    assert rejected_lines(report) == [3]


def test_duplicate_and_invalid_rows_are_reported_in_line_order(service):
    report = upload_rows(service, CsvRow.VALID, CsvRow.VALID, CsvRow.EMPTY_NO2)

    assert rejected_lines(report) == [3, 4]


def test_unusable_file_saves_nothing(service, session):
    with pytest.raises(InvalidCsvFileError):
        service.upload("empty.csv", io.BytesIO(CsvFileContent.EMPTY))

    assert saved_records(session) == []
