import io

import pytest

from src.errors import InvalidCsvFileError
from src.models.parsed_upload import ParsedUpload
from src.models.valid_row import ValidRow
from src.parsing.air_quality_csv_parser import AirQualityCsvParser
from tests.csv_rows import to_csv, to_csv_file
from tests.providers.csv_content import CsvFileContent, CsvRow, Reading

ROW_COUNT_PAST_FIRST_READ_CHUNK = 1_000


def parse_rows(*rows: str) -> ParsedUpload:
    return AirQualityCsvParser().parse(to_csv_file(*rows))


def parse_content(file_content: bytes) -> ParsedUpload:
    return AirQualityCsvParser().parse(io.BytesIO(file_content))


def test_valid_row_becomes_reading():
    parsed = parse_rows(CsvRow.VALID)

    assert parsed.valid_rows == [ValidRow(line_number=2, reading=Reading.OF_VALID_ROW)]
    assert parsed.rejected_rows == []


def test_city_is_stored_in_one_form_whatever_its_case_and_spacing():
    parsed = parse_rows(CsvRow.CITY_WITH_MIXED_CASE_AND_SPACES)

    assert [valid_row.reading for valid_row in parsed.valid_rows] == [Reading.OF_CITY_WITH_MIXED_CASE_AND_SPACES]


def test_zero_pollutant_values_are_valid():
    parsed = parse_rows(CsvRow.ZERO_POLLUTANTS)

    assert len(parsed.valid_rows) == 1
    assert parsed.rejected_rows == []


@pytest.mark.parametrize(
    ("row", "rejected_column"),
    [
        (CsvRow.NAN_CO2, "CO2"),
        (CsvRow.EMPTY_NO2, "NO2"),
        (CsvRow.NEGATIVE_PM25, "PM2.5"),
        (CsvRow.NON_NUMERIC_PM25, "PM2.5"),
        (CsvRow.INVALID_DATE, "date"),
        (CsvRow.TIMESTAMP_DATE, "date"),
        (CsvRow.DATE_WITH_TIME, "date"),
        (CsvRow.EMPTY_CITY, "city"),
    ],
)
def test_invalid_value_rejects_row_and_names_the_column(row, rejected_column):
    parsed = parse_rows(row)

    assert parsed.valid_rows == []
    assert len(parsed.rejected_rows) == 1
    assert parsed.rejected_rows[0].reason.startswith(f"{rejected_column}:")


@pytest.mark.parametrize(
    ("row", "expected_reason"),
    [
        (CsvRow.EXTRA_VALUE, "Expected 5 values, got 6"),
        (CsvRow.MISSING_NO2_AND_CO2, "Expected 5 values, got 3"),
    ],
)
def test_row_with_wrong_number_of_values_is_rejected(row, expected_reason):
    parsed = parse_rows(row)

    assert parsed.valid_rows == []
    assert [rejected_row.reason for rejected_row in parsed.rejected_rows] == [expected_reason]


def test_unknown_extra_column_is_ignored():
    parsed = parse_content(CsvFileContent.UNKNOWN_EXTRA_COLUMN)

    assert len(parsed.valid_rows) == 1
    assert parsed.rejected_rows == []


def test_blank_lines_are_skipped():
    parsed = parse_content(CsvFileContent.BLANK_LINES_BETWEEN_ROWS)

    assert len(parsed.valid_rows) == 2
    assert parsed.rejected_rows == []


def test_invalid_row_does_not_stop_valid_rows():
    parsed = parse_rows(CsvRow.VALID, CsvRow.EMPTY_NO2)

    assert [valid_row.reading for valid_row in parsed.valid_rows] == [Reading.OF_VALID_ROW]
    assert [rejected_row.line_number for rejected_row in parsed.rejected_rows] == [3]


@pytest.mark.parametrize(
    ("file_content", "expected_message"),
    [
        (CsvFileContent.EMPTY, "File is empty"),
        (CsvFileContent.MISSING_NO2_AND_CO2_COLUMNS, "Missing columns: NO2, CO2"),
        (CsvFileContent.NOT_UTF8, "File is not a UTF-8 text file"),
        (CsvFileContent.DUPLICATE_CITY_COLUMN, "Duplicate columns: city"),
        (CsvFileContent.TEXT_AFTER_CLOSING_QUOTE, "File is not a valid CSV"),
        (CsvFileContent.VALUE_OVER_CSV_FIELD_LIMIT, "File is not a valid CSV"),
    ],
)
def test_unusable_file_raises(file_content, expected_message):
    with pytest.raises(InvalidCsvFileError, match=expected_message):
        parse_content(file_content)


def test_non_utf8_bytes_deep_in_the_file_raise():
    many_valid_rows = [CsvRow.VALID] * ROW_COUNT_PAST_FIRST_READ_CHUNK

    with pytest.raises(InvalidCsvFileError, match="File is not a UTF-8 text file"):
        parse_content(to_csv(*many_valid_rows) + b"\n" + CsvFileContent.NOT_UTF8)


def test_parsing_leaves_the_file_open_for_its_owner():
    file = to_csv_file(CsvRow.VALID)

    AirQualityCsvParser().parse(file)

    assert not file.closed
