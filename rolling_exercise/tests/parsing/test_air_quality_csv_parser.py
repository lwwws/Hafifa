import io

import pytest

from src.errors import InvalidCsvFileError
from src.models.air_quality_reading import AirQualityReading
from src.parsing.air_quality_csv_parser import AirQualityCsvParser
from tests.csv_rows import csv_row, to_csv, to_csv_file
from tests.providers.aqi import Co2, No2, Pm25
from tests.providers.cities import City
from tests.providers.csv_values import CsvFileContent, CsvValue
from tests.providers.dates import Day

# Enough rows to push the end of the file past the first chunk the parser decodes
ROW_COUNT_PAST_FIRST_READ_CHUNK = 1_000


def test_valid_row_becomes_reading():
    parsed = AirQualityCsvParser().parse(to_csv_file(csv_row()))

    assert parsed.readings == [
        AirQualityReading(
            line_number=2, date=Day.DEFAULT, city=City.DEFAULT, pm25=Pm25.GOOD, no2=No2.GOOD, co2=Co2.GOOD
        )
    ]
    assert parsed.rejected_rows == []


def test_city_is_stored_in_one_form_whatever_its_case_and_spacing():
    parsed = AirQualityCsvParser().parse(to_csv_file(csv_row(city=City.WITH_MIXED_CASE_AND_SPACES)))

    assert [reading.city for reading in parsed.readings] == [City.WITH_MIXED_CASE_AND_SPACES_NORMALIZED]


def test_zero_pollutant_values_are_valid():
    parsed = AirQualityCsvParser().parse(to_csv_file(csv_row(pm25=CsvValue.ZERO, no2=CsvValue.ZERO, co2=CsvValue.ZERO)))

    assert len(parsed.readings) == 1
    assert parsed.rejected_rows == []


@pytest.mark.parametrize(
    ("row", "rejected_column"),
    [
        (csv_row(co2=CsvValue.NAN), "CO2"),
        (csv_row(no2=CsvValue.EMPTY), "NO2"),
        (csv_row(pm25=CsvValue.NEGATIVE), "PM2.5"),
        (csv_row(pm25=CsvValue.NOT_A_NUMBER), "PM2.5"),
        (csv_row(date=CsvValue.INVALID_DATE), "date"),
        (csv_row(city=CsvValue.EMPTY), "city"),
    ],
)
def test_invalid_value_rejects_row_and_names_the_column(row, rejected_column):
    parsed = AirQualityCsvParser().parse(to_csv_file(row))

    assert parsed.readings == []
    assert len(parsed.rejected_rows) == 1
    assert parsed.rejected_rows[0].reason.startswith(f"{rejected_column}:")


def test_invalid_row_does_not_stop_valid_rows():
    parsed = AirQualityCsvParser().parse(
        to_csv_file(csv_row(city=City.DEFAULT), csv_row(city=City.OTHER, no2=CsvValue.EMPTY))
    )

    assert [reading.city for reading in parsed.readings] == [City.DEFAULT]
    assert [rejected_row.line_number for rejected_row in parsed.rejected_rows] == [3]


@pytest.mark.parametrize(
    ("file_content", "expected_message"),
    [
        (CsvFileContent.EMPTY, "File is empty"),
        (CsvFileContent.MISSING_NO2_AND_CO2, "Missing columns: NO2, CO2"),
        (CsvFileContent.NOT_UTF8, "File is not a UTF-8 text file"),
    ],
)
def test_unusable_file_raises(file_content, expected_message):
    with pytest.raises(InvalidCsvFileError, match=expected_message):
        AirQualityCsvParser().parse(io.BytesIO(file_content))


def test_non_utf8_bytes_deep_in_the_file_raise():
    many_valid_rows = [csv_row(city=f"City{index}") for index in range(ROW_COUNT_PAST_FIRST_READ_CHUNK)]
    file = io.BytesIO(to_csv(*many_valid_rows) + b"\n" + CsvFileContent.NOT_UTF8)

    with pytest.raises(InvalidCsvFileError, match="File is not a UTF-8 text file"):
        AirQualityCsvParser().parse(file)


def test_parsing_leaves_the_file_open_for_its_owner():
    file = to_csv_file(csv_row())

    AirQualityCsvParser().parse(file)

    assert not file.closed
