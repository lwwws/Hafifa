import logging
from typing import BinaryIO

from src.db.air_quality_record import AirQualityRecord
from src.db.alert import Alert
from src.models.air_quality_reading import AirQualityReading
from src.models.rejected_row import RejectedRow
from src.models.upload_report import UploadReport
from src.models.valid_row import ValidRow
from src.parsing.air_quality_csv_parser import AirQualityCsvParser
from src.repositories.air_quality_repository import AirQualityRepository
from src.services.aqi_calculator import AqiCalculator

logger = logging.getLogger(__name__)


class AirQualityUploadService:
    def __init__(
        self,
        parser: AirQualityCsvParser,
        calculator: AqiCalculator,
        air_quality_repository: AirQualityRepository,
        alert_aqi_threshold: float,
    ):
        self._parser = parser
        self._calculator = calculator
        self._air_quality_repository = air_quality_repository
        self._alert_aqi_threshold = alert_aqi_threshold

    def upload(self, file_name: str, file: BinaryIO) -> UploadReport:
        logger.info(f"Processing upload {file_name}")

        parsed_upload = self._parser.parse(file)
        new_rows, duplicate_rows = self._reject_duplicates(parsed_upload.valid_rows)
        records = [self._to_record(valid_row.reading) for valid_row in new_rows]
        self._air_quality_repository.save_all(records)

        upload_report = UploadReport(
            saved_rows=len(records),
            created_alerts=sum(record.alert is not None for record in records),
            rejected_rows=sorted(
                parsed_upload.rejected_rows + duplicate_rows, key=lambda rejected_row: rejected_row.line_number
            ),
        )
        logger.info(
            f"Finished upload {file_name}: saved {upload_report.saved_rows} rows, "
            f"created {upload_report.created_alerts} alerts, rejected {len(upload_report.rejected_rows)}"
        )

        return upload_report

    def _reject_duplicates(self, valid_rows: list[ValidRow]) -> tuple[list[ValidRow], list[RejectedRow]]:
        upload_dates = {valid_row.reading.date for valid_row in valid_rows}
        taken_city_days = self._air_quality_repository.get_city_days(upload_dates)
        new_rows = []
        duplicate_rows = []

        for valid_row in valid_rows:
            reading = valid_row.reading
            city_day = (reading.date, reading.city)

            if city_day in taken_city_days:
                duplicate_row = RejectedRow(
                    line_number=valid_row.line_number, reason=f"{reading.city} already has data for {reading.date}"
                )
                logger.warning(f"Rejected line {duplicate_row.line_number}: {duplicate_row.reason}")
                duplicate_rows.append(duplicate_row)
            else:
                taken_city_days.add(city_day)
                new_rows.append(valid_row)

        return new_rows, duplicate_rows

    def _to_record(self, reading: AirQualityReading) -> AirQualityRecord:
        aqi_result = self._calculator.calculate(reading.pm25, reading.no2, reading.co2)
        record = AirQualityRecord(
            date=reading.date,
            city=reading.city,
            pm25=reading.pm25,
            no2=reading.no2,
            co2=reading.co2,
            aqi=aqi_result.aqi,
            aqi_level=aqi_result.aqi_level,
        )

        if record.aqi > self._alert_aqi_threshold:
            logger.info(f"Alert for {record.city} on {record.date}: AQI {record.aqi}")
            record.alert = Alert(date=record.date, city=record.city, aqi=record.aqi)

        return record
