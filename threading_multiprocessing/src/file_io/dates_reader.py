from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def _parse_date(text: str, default_timezone: ZoneInfo) -> datetime:
    date = datetime.fromisoformat(text)

    if date.tzinfo is None:
        return date.replace(tzinfo=default_timezone)

    return date


def read_dates(path: Path, default_timezone: ZoneInfo) -> list[datetime]:
    with path.open() as file:
        return [_parse_date(line.strip(), default_timezone) for line in file if line.strip()]
