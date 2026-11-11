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
    MISSING_NO2_AND_CO2 = b"date,city,PM2.5\n2024-11-19,Haifa,12"
