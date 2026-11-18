import csv

HEADER = b"date,city,PM2.5,NO2,CO2"


class CsvValue:
    ZERO = "0"
    EMPTY = ""
    NAN = "NaN"
    NOT_A_NUMBER = "abc"
    NEGATIVE = "-1"
    INVALID_DATE = "2024-13-45"


class CsvFileContent:
    EMPTY = b""
    NOT_UTF8 = b"\xff\xfe\x00not text"
    MISSING_NO2_AND_CO2 = b"date,city,PM2.5\n2024-11-19,haifa,5"
    DUPLICATE_CITY_COLUMN = b"date,city,PM2.5,NO2,CO2,city\n2024-11-19,haifa,5,10,1,akko"
    TEXT_AFTER_CLOSING_QUOTE = HEADER + b'\n2024-11-19,"hai"fa,5,10,1'
    VALUE_OVER_CSV_FIELD_LIMIT = HEADER + b"\n2024-11-19," + b"x" * (csv.field_size_limit() + 1) + b",5,10,1"
    ROW_WITH_EXTRA_VALUE = HEADER + b"\n2024-11-19,haifa,5,10,1,extra"
    ROW_WITH_MISSING_VALUES = HEADER + b"\n2024-11-19,haifa,5"
    UNKNOWN_EXTRA_COLUMN = b"date,city,PM2.5,NO2,CO2,notes\n2024-11-19,haifa,5,10,1,sunny"
    BLANK_LINES_BETWEEN_ROWS = HEADER + b"\n2024-11-19,haifa,5,10,1\n\n\n2024-11-20,haifa,5,10,1"
