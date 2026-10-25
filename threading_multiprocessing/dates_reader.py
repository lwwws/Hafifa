from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def _parse_date(text: str, timezone: ZoneInfo) -> datetime:
    date = datetime.fromisoformat(text)

    if date.tzinfo is None:
        return date.replace(tzinfo=timezone)

    return date


def read_dates(path: Path, timezone: ZoneInfo) -> list[datetime]:
    """Read one timestamp per line, skipping blank lines.

    Timestamps without a timezone of their own are read as being in `timezone`.
    """
    with path.open() as file:
        return [_parse_date(line.strip(), timezone) for line in file if line.strip()]
