"""Generic CSV data provider service for German language learning."""

import csv
import logging.handlers
from pathlib import Path
from typing import TypeVar

from langlearn.languages.german.records.records import BaseRecord
from langlearn.services.record_mapper import RecordMapper

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Add file handler for csv.log
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "csv.log",
    maxBytes=1024 * 1024,
    backupCount=5,  # 1MB
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

T = TypeVar("T")


class CSVService:
    """Generic CSV service for reading data files.

    Supports both legacy domain model loading and new Clean Pipeline Architecture
    with Record-based processing.
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize CSVService.

        Args:
            project_root: Root path of the project for RecordMapper initialization
        """
        self._record_mapper = RecordMapper(project_root)

    def read_csv(self, file_path: Path, model_class: type[T]) -> list[T]:
        """Read data from a CSV file and convert to specified model type.

        Args:
            file_path: Path to the CSV file
            model_class: Pydantic model class to convert rows to

        Returns:
            List of model instances parsed from the CSV file

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            csv.Error: If there's an error parsing the CSV file
            ValidationError: If the CSV data doesn't match the model schema
        """
        logger.info("Reading data from %s", file_path)
        items: list[T] = []
        try:
            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Keep empty strings as empty strings for media fields,
                    # only convert None for truly optional fields
                    cleaned_row = {k: v or "" for k, v in row.items()}
                    item = model_class(**cleaned_row)
                    items.append(item)
            logger.info("Successfully read %d items from %s", len(items), file_path)
            return items
        except FileNotFoundError:
            logger.error("CSV file not found: %s", file_path)
            raise
        except csv.Error as e:
            logger.error("Error reading CSV file %s: %s", file_path, e)
            raise
        except Exception as e:
            logger.error("Unexpected error reading data from %s: %s", file_path, e)
            raise

    # Clean Pipeline Architecture methods

    def read_csv_as_records(
        self, file_path: Path, record_type: str
    ) -> list[BaseRecord]:
        """Read CSV data as Record instances for Clean Pipeline Architecture.

        Args:
            file_path: Path to the CSV file
            record_type: Type of record (noun, adjective, adverb, negation)

        Returns:
            List of Record instances

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            csv.Error: If there's an error parsing the CSV file
            ValueError: If record_type is unsupported or data is invalid
        """
        logger.info("Reading %s records from %s", record_type, file_path)

        if not self._record_mapper.is_supported_record_type(record_type):
            raise ValueError(f"Unsupported record type: {record_type}")

        records: list[BaseRecord] = []

        try:
            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                # Start at 2 (header is row 1)
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Clean row data (handle None values)
                        cleaned_row = {k: v or "" for k, v in row.items()}

                        # Check if row has sufficient non-empty data to be valid
                        # For records to be meaningful, require minimum fields based
                        # on record type
                        required_field_count = self._get_minimum_required_fields(
                            record_type
                        )
                        non_empty_fields = sum(
                            1 for value in cleaned_row.values() if value.strip()
                        )

                        if non_empty_fields < required_field_count:
                            logger.warning(
                                "Skipping row %d: insufficient data (%d/%d fields)",
                                row_num,
                                non_empty_fields,
                                required_field_count,
                            )
                            continue

                        # Map CSV row to Record
                        record = self._record_mapper.map_csv_row_to_record(
                            record_type, cleaned_row
                        )
                        records.append(record)

                    except Exception as e:
                        logger.warning(
                            "Failed to create %s record from row %d in %s: %s",
                            record_type,
                            row_num,
                            file_path,
                            e,
                        )
                        # Continue processing other rows rather than failing completely
                        continue

            logger.info(
                "Successfully read %d %s records from %s",
                len(records),
                record_type,
                file_path,
            )
            return records

        except FileNotFoundError:
            logger.error("CSV file not found: %s", file_path)
            raise
        except csv.Error as e:
            logger.error("Error reading CSV file %s: %s", file_path, e)
            raise
        except Exception as e:
            logger.error("Unexpected error reading records from %s: %s", file_path, e)
            raise

    def read_noun_records(self, file_path: Path) -> list[BaseRecord]:
        """Read noun data as NounRecord instances.

        Args:
            file_path: Path to the nouns CSV file

        Returns:
            List of NounRecord instances
        """
        return self.read_csv_as_records(file_path, "noun")

    def read_adjective_records(self, file_path: Path) -> list[BaseRecord]:
        """Read adjective data as AdjectiveRecord instances.

        Args:
            file_path: Path to the adjectives CSV file

        Returns:
            List of AdjectiveRecord instances
        """
        return self.read_csv_as_records(file_path, "adjective")

    def read_adverb_records(self, file_path: Path) -> list[BaseRecord]:
        """Read adverb data as AdverbRecord instances.

        Args:
            file_path: Path to the adverbs CSV file

        Returns:
            List of AdverbRecord instances
        """
        return self.read_csv_as_records(file_path, "adverb")

    def read_negation_records(self, file_path: Path) -> list[BaseRecord]:
        """Read negation data as NegationRecord instances.

        Args:
            file_path: Path to the negations CSV file

        Returns:
            List of NegationRecord instances
        """
        return self.read_csv_as_records(file_path, "negation")

    def get_supported_record_types(self) -> list[str]:
        """Get list of supported record types.

        Returns:
            List of supported record type names
        """
        return self._record_mapper.get_supported_record_types()

    def validate_csv_structure_for_record_type(
        self, file_path: Path, record_type: str
    ) -> bool:
        """Validate that CSV file structure matches expected record type format.

        Args:
            file_path: Path to the CSV file
            record_type: Expected record type

        Returns:
            True if CSV structure is valid for the record type

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If record_type is unsupported
        """
        if not self._record_mapper.is_supported_record_type(record_type):
            raise ValueError(f"Unsupported record type: {record_type}")

        try:
            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []

                # Get expected field names for this record type
                expected_fields = self._record_mapper.get_field_names_for_record_type(
                    record_type
                )

                # Check if all expected fields are present in headers
                missing_fields = set(expected_fields) - set(headers)

                if missing_fields:
                    logger.warning(
                        "CSV file %s missing expected fields for %s: %s",
                        file_path,
                        record_type,
                        missing_fields,
                    )
                    return False

                logger.debug(
                    "CSV file %s has valid structure for %s records",
                    file_path,
                    record_type,
                )
                return True

        except FileNotFoundError:
            logger.error("CSV file not found: %s", file_path)
            raise
        except Exception as e:
            logger.error("Error validating CSV structure for %s: %s", file_path, e)
            return False

    def _get_minimum_required_fields(self, record_type: str) -> int:
        """Get minimum number of non-empty fields required for a record type.

        Args:
            record_type: Type of record

        Returns:
            Minimum number of non-empty fields needed for meaningful record
        """
        # Define minimum requirements for each record type
        # These are the core fields needed for a meaningful language learning card
        minimums = {
            "noun": 3,  # noun, article, english (at minimum)
            "adjective": 3,  # word, english, example (at minimum)
            "adverb": 3,  # word, english, type (at minimum)
            "negation": 3,  # word, english, type (at minimum)
        }

        return minimums.get(record_type, 2)  # Default to 2 if unknown type
