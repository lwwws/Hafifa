import datetime
import io

import pytest

from src.errors import InvalidCsvFileError
from src.models.air_quality_reading import AirQualityReading
from src.parsing.air_quality_csv_parser import AirQualityCsvParser
from tests.csv_rows import csv_row, to_csv, to_csv_file


def test_valid_row_becomes_reading():
    parsed = AirQualityCsvParser().parse(to_csv_file("2024-11-19,Haifa,12,40,3"))

    assert parsed.readings == [
        AirQualityReading(line_number=2, date=datetime.date(2024, 11, 19), city="Haifa", pm25=12, no2=40, co2=3)
    ]
    assert parsed.rejected_rows == []


def test_city_is_stored_in_one_form_whatever_its_case_and_spacing():
    parsed = AirQualityCsvParser().parse(to_csv_file(csv_row(city="  Tel AVIV ")))

    assert [reading.city for reading in parsed.readings] == ["tel aviv"]


def test_zero_pollutant_values_are_valid():
    parsed = AirQualityCsvParser().parse(to_csv_file(csv_row(pm25="0", no2="0", co2="0")))

    assert len(parsed.readings) == 1
    assert parsed.rejected_rows == []


@pytest.mark.parametrize(
    ("row", "rejected_column"),
    [
        (csv_row(co2="NaN"), "CO2"),
        (csv_row(no2=""), "NO2"),
        (csv_row(pm25="-1"), "PM2.5"),
        (csv_row(pm25="abc"), "PM2.5"),
        (csv_row(date="2024-13-45"), "date"),
        (csv_row(city=""), "city"),
    ],
)
def test_invalid_value_rejects_row_and_names_the_column(row, rejected_column):
    parsed = AirQualityCsvParser().parse(to_csv_file(row))

    assert parsed.readings == []
    assert len(parsed.rejected_rows) == 1
    assert parsed.rejected_rows[0].reason.startswith(f"{rejected_column}:")


def test_invalid_row_does_not_stop_valid_rows():
    parsed = AirQualityCsvParser().parse(to_csv_file(csv_row(city="Haifa"), csv_row(city="Akko", no2="")))

    assert [reading.city for reading in parsed.readings] == ["haifa"]
    assert [rejected_row.line_number for rejected_row in parsed.rejected_rows] == [3]


@pytest.mark.parametrize(
    ("file_content", "expected_message"),
    [
        (b"", "File is empty"),
        (b"date,city,PM2.5\n2024-11-19,Haifa,12", "Missing columns: NO2, CO2"),
        (b"\xff\xfe\x00not text", "File is not a UTF-8 text file"),
    ],
)
def test_unusable_file_raises(file_content, expected_message):
    with pytest.raises(InvalidCsvFileError, match=expected_message):
        AirQualityCsvParser().parse(io.BytesIO(file_content))


def test_non_utf8_bytes_deep_in_the_file_raise():
    many_valid_rows = [csv_row(city=f"City{index}") for index in range(1_000)]
    file = io.BytesIO(to_csv(*many_valid_rows) + b"\n\xff\xfe")

    with pytest.raises(InvalidCsvFileError, match="File is not a UTF-8 text file"):
        AirQualityCsvParser().parse(file)


def test_parsing_leaves_the_file_open_for_its_owner():
    file = to_csv_file(csv_row())

    AirQualityCsvParser().parse(file)

    assert not file.closed
