import csv
import datetime

from src.models.air_quality_reading import AirQualityReading
from tests.csv_rows import HEADER, csv_row, to_csv, to_csv_lines
from tests.providers.aqi import Co2, No2, Pm25

_VALID_DATE = datetime.date(2024, 11, 19)
_VALID_CITY = "haifa"


class CsvRow:
    VALID = csv_row(_VALID_DATE, _VALID_CITY, Pm25.GOOD, No2.GOOD, Co2.GOOD)
    CITY_WITH_MIXED_CASE_AND_SPACES = csv_row(_VALID_DATE, "  Tel AVIV ", Pm25.GOOD, No2.GOOD, Co2.GOOD)
    ZERO_POLLUTANTS = csv_row(_VALID_DATE, _VALID_CITY, 0, 0, 0)

    NAN_CO2 = csv_row(_VALID_DATE, _VALID_CITY, Pm25.GOOD, No2.GOOD, "NaN")
    EMPTY_NO2 = csv_row(_VALID_DATE, _VALID_CITY, Pm25.GOOD, "", Co2.GOOD)
    NEGATIVE_PM25 = csv_row(_VALID_DATE, _VALID_CITY, -1, No2.GOOD, Co2.GOOD)
    NON_NUMERIC_PM25 = csv_row(_VALID_DATE, _VALID_CITY, "abc", No2.GOOD, Co2.GOOD)
    INVALID_DATE = csv_row("2024-13-45", _VALID_CITY, Pm25.GOOD, No2.GOOD, Co2.GOOD)
    EMPTY_CITY = csv_row(_VALID_DATE, "", Pm25.GOOD, No2.GOOD, Co2.GOOD)

    EXTRA_VALUE = csv_row(_VALID_DATE, _VALID_CITY, Pm25.GOOD, No2.GOOD, Co2.GOOD, "extra")
    MISSING_NO2_AND_CO2 = csv_row(_VALID_DATE, _VALID_CITY, Pm25.GOOD)
    TEXT_AFTER_CLOSING_QUOTE = csv_row(_VALID_DATE, '"hai"fa', Pm25.GOOD, No2.GOOD, Co2.GOOD)
    VALUE_OVER_CSV_FIELD_LIMIT = csv_row(_VALID_DATE, "x" * (csv.field_size_limit() + 1), Pm25.GOOD, No2.GOOD, Co2.GOOD)


class Reading:
    OF_VALID_ROW = AirQualityReading(date=_VALID_DATE, city=_VALID_CITY, pm25=Pm25.GOOD, no2=No2.GOOD, co2=Co2.GOOD)
    OF_CITY_WITH_MIXED_CASE_AND_SPACES = AirQualityReading(
        date=_VALID_DATE, city="tel aviv", pm25=Pm25.GOOD, no2=No2.GOOD, co2=Co2.GOOD
    )


class CsvFileContent:
    EMPTY = b""
    NOT_UTF8 = b"\xff\xfe\x00not text"
    MISSING_NO2_AND_CO2_COLUMNS = to_csv_lines(csv_row("date", "city", "PM2.5"), CsvRow.MISSING_NO2_AND_CO2)
    DUPLICATE_CITY_COLUMN = to_csv_lines(csv_row(HEADER, "city"), CsvRow.EXTRA_VALUE)
    UNKNOWN_EXTRA_COLUMN = to_csv_lines(csv_row(HEADER, "notes"), CsvRow.EXTRA_VALUE)
    TEXT_AFTER_CLOSING_QUOTE = to_csv(CsvRow.TEXT_AFTER_CLOSING_QUOTE)
    VALUE_OVER_CSV_FIELD_LIMIT = to_csv(CsvRow.VALUE_OVER_CSV_FIELD_LIMIT)
    BLANK_LINES_BETWEEN_ROWS = to_csv(CsvRow.VALID, "", "", CsvRow.VALID)
