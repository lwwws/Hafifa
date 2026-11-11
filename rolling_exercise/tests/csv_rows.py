import io
from typing import BinaryIO

from tests.providers.aqi import Co2, No2, Pm25
from tests.providers.cities import City
from tests.providers.dates import Day

HEADER = "date,city,PM2.5,NO2,CO2"


def csv_row(
    date: str = Day.DEFAULT.isoformat(),
    city: str = City.DEFAULT,
    pm25: str = str(Pm25.GOOD),
    no2: str = str(No2.GOOD),
    co2: str = str(Co2.GOOD),
) -> str:
    return f"{date},{city},{pm25},{no2},{co2}"


def to_csv(*rows: str) -> bytes:
    return "\n".join([HEADER, *rows]).encode()


def to_csv_file(*rows: str) -> BinaryIO:
    return io.BytesIO(to_csv(*rows))
