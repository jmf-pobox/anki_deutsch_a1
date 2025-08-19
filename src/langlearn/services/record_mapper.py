"""RecordMapper service for Clean Pipeline Architecture.

This service handles the conversion from CSV field arrays to Record instances,
providing clean separation between CSV parsing and domain logic.
"""

import logging
from pathlib import Path
from typing import Any

from langlearn.models.records import BaseRecord, create_record

logger = logging.getLogger(__name__)


class RecordMapper:
    """Maps CSV field arrays to Record instances for Clean Pipeline Architecture."""

    def __init__(self, project_root: Path | None = None):
        """Initialize RecordMapper.

        Args:
            project_root: Root path of the project for relative path resolution
        """
        self._project_root = project_root or Path.cwd()
        logger.debug(
            "RecordMapper initialized with project root: %s", self._project_root
        )

    def map_fields_to_record(self, record_type: str, fields: list[str]) -> BaseRecord:
        """Map CSV field array to Record instance.

        Args:
            record_type: Type of record (noun, adjective, adverb, negation)
            fields: Array of CSV field values

        Returns:
            Record instance of the appropriate type

        Raises:
            ValueError: If record_type is unsupported or fields are invalid
        """
        logger.debug(
            "Mapping %d fields to %s record: %s",
            len(fields),
            record_type,
            fields[:3]
            if len(fields) > 3
            else fields,  # Log first few fields for debugging
        )

        try:
            record = create_record(record_type, fields)
            logger.debug("Successfully created %s record", record_type)
            return record
        except ValueError as e:
            logger.error(
                "Failed to create %s record from fields %s: %s", record_type, fields, e
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error mapping fields to %s record: %s", record_type, e
            )
            raise

    def map_csv_row_to_record(
        self, record_type: str, csv_row: dict[str, Any]
    ) -> BaseRecord:
        """Map CSV row dictionary to Record instance.

        Args:
            record_type: Type of record (noun, adjective, adverb, negation)
            csv_row: Dictionary from csv.DictReader

        Returns:
            Record instance of the appropriate type

        Raises:
            ValueError: If record_type is unsupported or row data is invalid
        """
        logger.debug(
            "Mapping CSV row to %s record: %s", record_type, list(csv_row.keys())
        )

        # Extract field values from the CSV row based on record type
        try:
            if record_type == "noun":
                fields = [
                    csv_row.get("noun", ""),
                    csv_row.get("article", ""),
                    csv_row.get("english", ""),
                    csv_row.get("plural", ""),
                    csv_row.get("example", ""),
                    csv_row.get("related", ""),
                ]
            elif record_type == "adjective":
                fields = [
                    csv_row.get("word", ""),
                    csv_row.get("english", ""),
                    csv_row.get("example", ""),
                    csv_row.get("comparative", ""),
                    csv_row.get("superlative", ""),
                ]
            elif record_type in ["adverb", "negation"]:
                fields = [
                    csv_row.get("word", ""),
                    csv_row.get("english", ""),
                    csv_row.get("type", ""),
                    csv_row.get("example", ""),
                ]
            else:
                raise ValueError(f"Unsupported record type: {record_type}")

            return self.map_fields_to_record(record_type, fields)

        except Exception as e:
            logger.error("Failed to map CSV row to %s record: %s", record_type, e)
            raise

    def get_supported_record_types(self) -> list[str]:
        """Get list of supported record types.

        Returns:
            List of supported record type names
        """
        return ["noun", "adjective", "adverb", "negation"]

    def is_supported_record_type(self, record_type: str) -> bool:
        """Check if record type is supported.

        Args:
            record_type: Record type to check

        Returns:
            True if record type is supported
        """
        return record_type in self.get_supported_record_types()

    def validate_fields_for_record_type(
        self, record_type: str, fields: list[str]
    ) -> bool:
        """Validate that fields are appropriate for the record type.

        Args:
            record_type: Type of record to validate against
            fields: Field array to validate

        Returns:
            True if fields are valid for the record type

        Raises:
            ValueError: If record_type is unsupported
        """
        if not self.is_supported_record_type(record_type):
            raise ValueError(f"Unsupported record type: {record_type}")

        # Get expected field count from the record type
        try:
            # Create a temporary record to check field requirements
            create_record(record_type, fields)
            return True
        except ValueError:
            return False

    def get_field_names_for_record_type(self, record_type: str) -> list[str]:
        """Get expected field names for a record type.

        Args:
            record_type: Record type to get field names for

        Returns:
            List of field names in expected order

        Raises:
            ValueError: If record_type is unsupported
        """
        if not self.is_supported_record_type(record_type):
            raise ValueError(f"Unsupported record type: {record_type}")

        # Use the record classes' field name methods
        from langlearn.models.records import RECORD_TYPE_REGISTRY

        record_class = RECORD_TYPE_REGISTRY[record_type]
        return record_class.get_field_names()

    def get_expected_field_count_for_record_type(self, record_type: str) -> int:
        """Get expected field count for a record type.

        Args:
            record_type: Record type to get field count for

        Returns:
            Expected number of fields

        Raises:
            ValueError: If record_type is unsupported
        """
        if not self.is_supported_record_type(record_type):
            raise ValueError(f"Unsupported record type: {record_type}")

        # Use the record classes' field count methods
        from langlearn.models.records import RECORD_TYPE_REGISTRY

        record_class = RECORD_TYPE_REGISTRY[record_type]
        return record_class.get_expected_field_count()
