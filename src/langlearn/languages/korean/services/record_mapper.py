"""Korean record mapper service for converting CSV data to records."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from langlearn.core.records.base_record import BaseRecord

logger = logging.getLogger(__name__)


class KoreanRecordMapper:
    """Maps CSV data to Korean language records."""

    def __init__(self) -> None:
        """Initialize Korean record mapper."""
        self._supported_record_types = {
            "korean_noun": self._create_korean_noun_record,
            "korean_nouns": self._create_korean_noun_record,  # Alternative naming
            "nouns": self._create_korean_noun_record,  # Simplified naming
        }

    def create_records_from_csv_files(
        self, data_directory: Path
    ) -> dict[str, list[BaseRecord]]:
        """Create Korean records from CSV files in the data directory."""
        records_by_type: dict[str, list[BaseRecord]] = {}

        csv_files = list(data_directory.glob("*.csv"))
        if not csv_files:
            logger.warning(
                f"No CSV files found in Korean data directory: {data_directory}"
            )
            return records_by_type

        for csv_file in csv_files:
            file_stem = csv_file.stem.lower()
            logger.info(f"Processing Korean CSV file: {csv_file}")

            # Determine record type from filename
            record_type = self._determine_record_type(file_stem)
            if not record_type:
                logger.warning(
                    f"Unknown Korean record type for file: {csv_file}. "
                    f"Supported types: {list(self._supported_record_types.keys())}"
                )
                continue

            try:
                records = self._load_csv_records(csv_file, record_type)
                if records:
                    records_by_type[record_type] = records
                    logger.info(f"Loaded {len(records)} Korean {record_type} records")
                else:
                    logger.warning(f"No valid records found in Korean file: {csv_file}")
            except Exception as e:
                logger.error(f"Error processing Korean CSV file {csv_file}: {e}")
                raise

        return records_by_type

    def _determine_record_type(self, filename: str) -> str | None:
        """Determine record type from filename."""
        # Direct matches
        if filename in self._supported_record_types:
            return filename

        # Pattern matching
        if "noun" in filename:
            return "korean_noun"

        return None

    def _load_csv_records(self, csv_file: Path, record_type: str) -> list[BaseRecord]:
        """Load records from a Korean CSV file."""

        records = []
        record_factory = self._supported_record_types[record_type]

        try:
            with csv_file.open("r", encoding="utf-8") as file:
                reader = csv.reader(file)

                # Skip header row
                next(reader, None)

                for row_index, row in enumerate(
                    reader, start=2
                ):  # Start at 2 for header
                    # Skip empty rows
                    if not any(field.strip() for field in row):
                        continue

                    try:
                        record = record_factory(row)
                        records.append(record)
                    except Exception as e:
                        logger.error(
                            f"Error creating Korean record from row {row_index} "
                            f"in {csv_file}: {e}"
                        )
                        logger.error(f"Row data: {row}")
                        # Continue processing other rows

        except Exception as e:
            logger.error(f"Error reading Korean CSV file {csv_file}: {e}")
            raise

        return records

    def _create_korean_noun_record(self, csv_fields: list[str]) -> BaseRecord:
        """Create a Korean noun record from CSV fields."""
        from langlearn.languages.korean.records.noun_record import KoreanNounRecord

        return KoreanNounRecord.from_csv_fields(csv_fields)

    def load_records_from_csv(
        self, csv_path: str | Path, record_type: str | None = None
    ) -> list[BaseRecord]:
        """Load Korean records from a single CSV file with optional type specification.

        Args:
            csv_path: Path to the CSV file to load
            record_type: Optional record type. If None, type is auto-detected

        Returns:
            List of Korean records from the CSV file
        """
        csv_file = Path(csv_path) if isinstance(csv_path, str) else csv_path

        # Use provided record type or auto-detect
        if record_type is None:
            file_stem = csv_file.stem.lower()
            record_type = self._determine_record_type(file_stem)
            if not record_type:
                logger.warning(
                    f"Unknown Korean record type for file: {csv_file}. "
                    f"Supported types: {list(self._supported_record_types.keys())}"
                )
                return []
        else:
            logger.info("Using specified record type: %s", record_type)

        return self._load_csv_records(csv_file, record_type)

    def get_supported_record_types(self) -> list[str]:
        """Get list of supported Korean record types."""
        return list(self._supported_record_types.keys())
