import csv

from src.models.air_quality_reading import AirQualityReading
from tests.csv_rows import HEADER, csv_row, to_csv, to_csv_lines
from tests.providers.aqi import Co2, No2, Pm25
from tests.providers.city_days import City, Day


class CsvRow:
    VALID = csv_row(Day.FIRST, City.HAIFA, Pm25.GOOD, No2.GOOD, Co2.GOOD)
    CITY_WITH_MIXED_CASE_AND_SPACES = csv_row(Day.FIRST, "  Tel AVIV ", Pm25.GOOD, No2.GOOD, Co2.GOOD)
    ZERO_POLLUTANTS = csv_row(Day.FIRST, City.HAIFA, 0, 0, 0)
    VALID_WITH_UPPERCASE_CITY = csv_row(Day.FIRST, City.HAIFA.upper(), Pm25.GOOD, No2.GOOD, Co2.GOOD)
    VALID_ON_NEXT_DAY = csv_row(Day.SECOND, City.HAIFA, Pm25.GOOD, No2.GOOD, Co2.GOOD)
    SAME_CITY_AND_DAY_AS_VALID = csv_row(Day.FIRST, City.HAIFA, Pm25.MODERATE, No2.GOOD, Co2.GOOD)

    NAN_CO2 = csv_row(Day.FIRST, City.HAIFA, Pm25.GOOD, No2.GOOD, "NaN")
    EMPTY_NO2 = csv_row(Day.FIRST, City.HAIFA, Pm25.GOOD, "", Co2.GOOD)
    NEGATIVE_PM25 = csv_row(Day.FIRST, City.HAIFA, -1, No2.GOOD, Co2.GOOD)
    NON_NUMERIC_PM25 = csv_row(Day.FIRST, City.HAIFA, "abc", No2.GOOD, Co2.GOOD)
    INVALID_DATE = csv_row("2024-13-45", City.HAIFA, Pm25.GOOD, No2.GOOD, Co2.GOOD)
    TIMESTAMP_DATE = csv_row(0, City.HAIFA, Pm25.GOOD, No2.GOOD, Co2.GOOD)
    DATE_WITH_TIME = csv_row("2024-11-19T00:00:00", City.HAIFA, Pm25.GOOD, No2.GOOD, Co2.GOOD)
    EMPTY_CITY = csv_row(Day.FIRST, "", Pm25.GOOD, No2.GOOD, Co2.GOOD)

    EXTRA_VALUE = csv_row(Day.FIRST, City.HAIFA, Pm25.GOOD, No2.GOOD, Co2.GOOD, "extra")
    MISSING_NO2_AND_CO2 = csv_row(Day.FIRST, City.HAIFA, Pm25.GOOD)
    TEXT_AFTER_CLOSING_QUOTE = csv_row(Day.FIRST, '"hai"fa', Pm25.GOOD, No2.GOOD, Co2.GOOD)
    VALUE_OVER_CSV_FIELD_LIMIT = csv_row(Day.FIRST, "x" * (csv.field_size_limit() + 1), Pm25.GOOD, No2.GOOD, Co2.GOOD)


class Reading:
    OF_VALID_ROW = AirQualityReading(date=Day.FIRST, city=City.HAIFA, pm25=Pm25.GOOD, no2=No2.GOOD, co2=Co2.GOOD)
    OF_CITY_WITH_MIXED_CASE_AND_SPACES = AirQualityReading(
        date=Day.FIRST, city="tel aviv", pm25=Pm25.GOOD, no2=No2.GOOD, co2=Co2.GOOD
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
