import io
from typing import BinaryIO

HEADER = "date,city,PM2.5,NO2,CO2"


def csv_row(*values: object) -> str:
    return ",".join(str(value) for value in values)


def to_csv_lines(*lines: str) -> bytes:
    return "\n".join(lines).encode()


def to_csv(*rows: str) -> bytes:
    return to_csv_lines(HEADER, *rows)


def to_csv_file(*rows: str) -> BinaryIO:
    return io.BytesIO(to_csv(*rows))
