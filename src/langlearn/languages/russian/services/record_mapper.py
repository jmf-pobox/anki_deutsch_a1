"""Russian RecordMapper service for record-based architecture."""

from __future__ import annotations

import logging
from pathlib import Path

from langlearn.core.records.base_record import BaseRecord

logger = logging.getLogger(__name__)


class RussianRecordMapper:
    """Maps CSV field arrays to Russian Record instances."""

    def __init__(self, project_root: Path | None = None):
        """Initialize Russian RecordMapper."""
        self._project_root = project_root or Path.cwd()
        logger.debug(
            "Russian RecordMapper initialized with project root: %s", self._project_root
        )

    def map_fields_to_record(self, record_type: str, fields: list[str]) -> BaseRecord:
        """Map CSV field array to Russian Record instance."""
        logger.debug(
            "Mapping %d fields to Russian %s record: %s",
            len(fields),
            record_type,
            fields[:3] if len(fields) > 3 else fields,
        )

        try:
            if record_type == "noun":
                from langlearn.languages.russian.records.noun_record import (
                    RussianNounRecord,
                )

                return RussianNounRecord.from_csv_fields(fields)
            else:
                raise ValueError(f"Unsupported Russian record type: {record_type}")

        except ValueError as e:
            logger.error(
                "Failed to create Russian %s record from fields %s: %s",
                record_type,
                fields,
                e,
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error mapping fields to Russian %s record: %s",
                record_type,
                e,
            )
            raise

    def map_csv_to_records(
        self, csv_file_path: Path, record_type: str
    ) -> list[BaseRecord]:
        """Read CSV file and convert rows to Record instances."""
        import csv

        records = []
        with open(csv_file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip header
            logger.info("Processing Russian CSV with headers: %s", headers)

            for i, row in enumerate(reader, 1):
                try:
                    record = self.map_fields_to_record(record_type, row)
                    records.append(record)
                except Exception as e:
                    logger.warning("Skipping row %d due to error: %s", i, e)
                    continue

        logger.info(
            "Successfully mapped %d Russian %s records", len(records), record_type
        )
        return records

    def load_records_from_csv(
        self, csv_path: str | Path, record_type: str | None = None
    ) -> list[BaseRecord]:
        """Load Russian records from CSV with optional type specification."""
        from pathlib import Path

        csv_path = Path(csv_path)
        logger.info("Loading Russian records from CSV: %s", csv_path)

        # Use provided record type or auto-detect
        if record_type is None:
            filename = csv_path.name
            if "noun" in filename.lower():
                record_type = "noun"
            else:
                raise ValueError(
                    f"Cannot detect Russian record type from filename: {filename}"
                )
        else:
            logger.info("Using specified record type: %s", record_type)

        # Load records using the existing method
        return self.map_csv_to_records(csv_path, record_type)
