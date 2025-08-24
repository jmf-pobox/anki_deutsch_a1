"""RecordMapper service for Clean Pipeline Architecture.

This service handles the conversion from CSV field arrays to Record instances,
providing clean separation between CSV parsing and domain logic.
"""

import csv
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
            (
                fields[:3] if len(fields) > 3 else fields
            ),  # Log first few fields for debugging
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
            record_type: Type of record (noun, adjective, adverb, negation,
                        article, indefinite_article, negative_article)
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
            elif record_type == "verb_conjugation":
                fields = [
                    csv_row.get("infinitive", ""),
                    csv_row.get("english", ""),
                    csv_row.get("classification", ""),
                    csv_row.get("separable", ""),
                    csv_row.get("auxiliary", ""),
                    csv_row.get("tense", ""),
                    csv_row.get("ich", ""),
                    csv_row.get("du", ""),
                    csv_row.get("er", ""),
                    csv_row.get("wir", ""),
                    csv_row.get("ihr", ""),
                    csv_row.get("sie", ""),
                    csv_row.get("example", ""),
                ]
            elif record_type == "verb_imperative":
                fields = [
                    csv_row.get("infinitive", ""),
                    csv_row.get("english", ""),
                    csv_row.get("classification", ""),
                    csv_row.get("separable", ""),
                    csv_row.get("du_form", ""),
                    csv_row.get("ihr_form", ""),
                    csv_row.get("sie_form", ""),
                    csv_row.get("example_du", ""),
                    csv_row.get("example_ihr", ""),
                    csv_row.get("example_sie", ""),
                ]
            elif record_type == "verb":
                fields = [
                    csv_row.get("verb", ""),
                    csv_row.get("english", ""),
                    csv_row.get("classification", ""),
                    csv_row.get("present_ich", ""),
                    csv_row.get("present_du", ""),
                    csv_row.get("present_er", ""),
                    csv_row.get("präteritum", ""),
                    csv_row.get("auxiliary", ""),
                    csv_row.get("perfect", ""),
                    csv_row.get("example", ""),
                    csv_row.get("separable", ""),
                ]
            elif record_type == "preposition":
                fields = [
                    csv_row.get("preposition", ""),
                    csv_row.get("english", ""),
                    csv_row.get("case", ""),
                    csv_row.get("example1", ""),
                    csv_row.get("example2", ""),
                ]
            elif record_type == "phrase":
                fields = [
                    csv_row.get("phrase", ""),
                    csv_row.get("english", ""),
                    csv_row.get("context", ""),
                    csv_row.get("related", ""),
                ]
            elif record_type in ["article", "indefinite_article", "negative_article"]:
                fields = [
                    csv_row.get("gender", ""),
                    csv_row.get("nominative", ""),
                    csv_row.get("accusative", ""),
                    csv_row.get("dative", ""),
                    csv_row.get("genitive", ""),
                    csv_row.get("example_nom", ""),
                    csv_row.get("example_acc", ""),
                    csv_row.get("example_dat", ""),
                    csv_row.get("example_gen", ""),
                ]
            elif record_type == "unified_article":
                fields = [
                    csv_row.get("artikel_typ", ""),
                    csv_row.get("geschlecht", ""),
                    csv_row.get("nominativ", ""),
                    csv_row.get("akkusativ", ""),
                    csv_row.get("dativ", ""),
                    csv_row.get("genitiv", ""),
                    csv_row.get("beispiel_nom", ""),
                    csv_row.get("beispiel_akk", ""),
                    csv_row.get("beispiel_dat", ""),
                    csv_row.get("beispiel_gen", ""),
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
        return [
            "noun",
            "adjective",
            "adverb",
            "negation",
            "verb",
            "preposition",
            "phrase",
            "verb_conjugation",
            "verb_imperative",
            "article",
            "indefinite_article",
            "negative_article",
            "unified_article",
        ]

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
        return record_class.get_field_names()  # type: ignore

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
        return record_class.get_expected_field_count()  # type: ignore

    def detect_csv_record_type(self, csv_path: str | Path) -> str:
        """Detect the record type from CSV file headers.

        Args:
            csv_path: Path to the CSV file

        Returns:
            Detected record type (verb_conjugation, verb_imperative, etc.)

        Raises:
            ValueError: If record type cannot be detected
            FileNotFoundError: If CSV file doesn't exist
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.debug("Detecting record type for CSV: %s", csv_path)

        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = set(reader.fieldnames or [])

            logger.debug("Found CSV headers: %s", headers)

            # Detect verb conjugation format
            conjugation_indicators = {"tense", "ich", "du", "er", "wir", "ihr", "sie"}
            if conjugation_indicators.issubset(headers):
                logger.debug("Detected verb conjugation CSV format")
                return "verb_conjugation"

            # Detect verb imperative format
            imperative_indicators = {"du_form", "ihr_form", "sie_form"}
            if imperative_indicators.issubset(headers):
                logger.debug("Detected verb imperative CSV format")
                return "verb_imperative"

            # Detect other record types by key indicators
            if {"noun", "article"}.issubset(headers):
                logger.debug("Detected noun CSV format")
                return "noun"

            if {"word", "comparative"}.issubset(headers):
                logger.debug("Detected adjective CSV format")
                return "adjective"

            if {"word", "type"}.issubset(headers) and "comparative" not in headers:
                # Distinguish between adverb and negation by typical patterns
                if any(word in str(csv_path).lower() for word in ["adverb"]):
                    logger.debug("Detected adverb CSV format")
                    return "adverb"
                elif any(word in str(csv_path).lower() for word in ["negation"]):
                    logger.debug("Detected negation CSV format")
                    return "negation"
                else:
                    # Default to adverb if ambiguous
                    logger.debug("Detected adverb CSV format (default)")
                    return "adverb"

            # Detect regular verb format
            verb_indicators = {
                "verb",
                "english",
                "present_ich",
                "present_du",
                "present_er",
            }
            if verb_indicators.issubset(headers):
                logger.debug("Detected regular verb CSV format")
                return "verb"

            # Detect preposition format
            preposition_indicators = {
                "preposition",
                "english",
                "case",
                "example1",
                "example2",
            }
            if preposition_indicators.issubset(headers):
                logger.debug("Detected preposition CSV format")
                return "preposition"

            # Detect phrase format
            phrase_indicators = {"phrase", "english", "context", "related"}
            if phrase_indicators.issubset(headers):
                logger.debug("Detected phrase CSV format")
                return "phrase"

            # Detect unified article format (with German terminology)
            unified_article_indicators = {
                "artikel_typ",
                "geschlecht",
                "nominativ",
                "akkusativ",
                "dativ",
                "genitiv",
                "beispiel_nom",
                "beispiel_akk",
                "beispiel_dat",
                "beispiel_gen",
            }
            if unified_article_indicators.issubset(headers):
                logger.debug("Detected unified article CSV format (German terminology)")
                return "unified_article"

            # Detect article pattern formats - legacy declension grid structure
            article_pattern_indicators = {
                "gender",
                "nominative",
                "accusative",
                "dative",
                "genitive",
                "example_nom",
                "example_acc",
                "example_dat",
                "example_gen",
            }
            if article_pattern_indicators.issubset(headers):
                # Check filename to distinguish article types
                filename_lower = str(csv_path).lower()
                if "indefinite" in filename_lower:
                    logger.debug("Detected indefinite article pattern CSV format")
                    return "indefinite_article"
                elif "negative" in filename_lower:
                    logger.debug("Detected negative article pattern CSV format")
                    return "negative_article"
                else:
                    logger.debug("Detected definite article pattern CSV format")
                    return "article"

            # If no patterns match, raise error
            raise ValueError(
                f"Cannot detect record type for CSV with headers: {headers}. "
                f"Supported formats: verb conjugation (with tense/ich/du/er/wir/ihr/sie), "  # noqa: E501
                f"verb imperative (with du_form/ihr_form/sie_form), "
                f"noun (with noun/article), adjective (with word/comparative), "
                f"adverb/negation (with word/type), "
                f"article patterns (with gender/nominative/accusative/dative/"
                f"genitive/examples)"
            )

        except Exception as e:
            logger.error("Failed to detect record type for %s: %s", csv_path, e)
            raise

    def load_records_from_csv(self, csv_path: str | Path) -> list[BaseRecord]:
        """Load records from CSV with automatic type detection.

        Args:
            csv_path: Path to the CSV file

        Returns:
            List of Record instances

        Raises:
            ValueError: If record type cannot be detected or records are invalid
            FileNotFoundError: If CSV file doesn't exist
        """
        csv_path = Path(csv_path)
        logger.info("Loading records from CSV: %s", csv_path)

        # Auto-detect record type
        record_type = self.detect_csv_record_type(csv_path)
        logger.info("Detected record type: %s", record_type)

        # Handle verb records that may have multiple rows per verb
        if record_type in ["verb_conjugation", "verb_imperative"]:
            return self._load_verb_records_from_csv(csv_path, record_type)
        else:
            return self._load_simple_records_from_csv(csv_path, record_type)

    def _load_simple_records_from_csv(
        self, csv_path: Path, record_type: str
    ) -> list[BaseRecord]:
        """Load records with 1:1 row-to-record mapping.

        Args:
            csv_path: Path to the CSV file
            record_type: Type of records to create

        Returns:
            List of Record instances
        """
        records = []

        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 (header is 1)
                    try:
                        record = self.map_csv_row_to_record(record_type, row)
                        records.append(record)
                        logger.debug(
                            "Created %s record from row %d", record_type, row_num
                        )
                    except Exception as e:
                        logger.error(
                            "Failed to create %s record from row %d: %s",
                            record_type,
                            row_num,
                            e,
                        )
                        raise ValueError(
                            f"Invalid {record_type} data at row {row_num}: {e}"
                        ) from e

            logger.info("Successfully loaded %d %s records", len(records), record_type)
            return records

        except Exception as e:
            logger.error(
                "Failed to load %s records from %s: %s", record_type, csv_path, e
            )
            raise

    def _load_verb_records_from_csv(
        self, csv_path: Path, record_type: str
    ) -> list[BaseRecord]:
        """Load verb records from CSV (multiple rows per verb supported).

        For the hybrid approach, each row represents one tense/imperative set
        for a verb, so we create one record per row.

        Args:
            csv_path: Path to the CSV file
            record_type: Type of verb records to create

        Returns:
            List of verb Record instances
        """
        records = []

        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 (header is 1)
                    try:
                        # Each row becomes one record (1 tense per row approach)
                        record = self.map_csv_row_to_record(record_type, row)
                        records.append(record)
                        logger.debug(
                            "Created %s record from row %d", record_type, row_num
                        )
                    except Exception as e:
                        logger.error(
                            "Failed to create %s record from row %d: %s",
                            record_type,
                            row_num,
                            e,
                        )
                        raise ValueError(
                            f"Invalid {record_type} data at row {row_num}: {e}"
                        ) from e

            logger.info("Successfully loaded %d %s records", len(records), record_type)
            return records

        except Exception as e:
            logger.error(
                "Failed to load %s records from %s: %s", record_type, csv_path, e
            )
            raise
