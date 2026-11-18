import csv
import datetime
import io
import logging
from collections import Counter
from typing import BinaryIO, TextIO

from pydantic import ValidationError

from src.errors import InvalidCsvFileError, InvalidRowError
from src.models.air_quality_reading import AirQualityReading
from src.models.parsed_upload import ParsedUpload
from src.models.rejected_row import RejectedRow
from src.models.valid_row import ValidRow

logger = logging.getLogger(__name__)

FIELD_BY_COLUMN = {"date": "date", "city": "city", "PM2.5": "pm25", "NO2": "no2", "CO2": "co2"}
COLUMN_BY_FIELD = {field: column for column, field in FIELD_BY_COLUMN.items()}
CSV_DATE_FORMAT = "%Y-%m-%d"


class AirQualityCsvParser:
    def parse(self, file: BinaryIO) -> ParsedUpload:
        text_stream = io.TextIOWrapper(file, encoding="utf-8-sig", newline="")

        try:
            return self._parse_rows(text_stream)
        except UnicodeDecodeError:
            raise InvalidCsvFileError("File is not a UTF-8 text file")
        except csv.Error as error:
            raise InvalidCsvFileError(f"File is not a valid CSV: {error}")
        finally:
            # Closing the wrapper would close the caller's file too, so hand the file back instead
            text_stream.detach()

    def _parse_rows(self, text_stream: TextIO) -> ParsedUpload:
        reader = csv.reader(text_stream, strict=True)
        columns = next(reader, [])
        self._check_columns(columns)
        valid_rows = []
        rejected_rows = []

        for values in reader:
            if not values:
                continue

            try:
                valid_rows.append(ValidRow(line_number=reader.line_num, reading=self._to_reading(columns, values)))
            except InvalidRowError as error:
                rejected_row = RejectedRow(line_number=reader.line_num, reason=str(error))
                logger.warning(f"Rejected line {rejected_row.line_number}: {rejected_row.reason}")
                rejected_rows.append(rejected_row)

        logger.info(f"Parsed {len(valid_rows)} valid rows, rejected {len(rejected_rows)}")

        return ParsedUpload(valid_rows=valid_rows, rejected_rows=rejected_rows)

    def _check_columns(self, columns: list[str]):
        if not columns:
            raise InvalidCsvFileError("File is empty")

        duplicate_columns = [column for column, count in Counter(columns).items() if count > 1]

        if duplicate_columns:
            raise InvalidCsvFileError(f"Duplicate columns: {', '.join(duplicate_columns)}")

        missing_columns = [column for column in FIELD_BY_COLUMN if column not in columns]

        if missing_columns:
            raise InvalidCsvFileError(f"Missing columns: {', '.join(missing_columns)}")

    def _to_reading(self, columns: list[str], values: list[str]) -> AirQualityReading:
        if len(values) != len(columns):
            raise InvalidRowError(f"Expected {len(columns)} values, got {len(values)}")

        row = dict(zip(columns, values))
        fields = {field: row[column] for column, field in FIELD_BY_COLUMN.items()}
        fields["date"] = self._to_date(row["date"])

        try:
            return AirQualityReading.model_validate(fields)
        except ValidationError as error:
            raise InvalidRowError(self._to_rejection_reason(error))

    def _to_date(self, value: str) -> datetime.date:
        try:
            return datetime.datetime.strptime(value, CSV_DATE_FORMAT).date()
        except ValueError:
            raise InvalidRowError(f"date: Expected a date in YYYY-MM-DD format, got '{value}'")

    def _to_rejection_reason(self, error: ValidationError) -> str:
        return "; ".join(f"{COLUMN_BY_FIELD[issue['loc'][0]]}: {issue['msg']}" for issue in error.errors())
