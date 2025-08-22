"""Unit tests for CSVService."""

import csv
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from pydantic import BaseModel, ValidationError, field_validator

from langlearn.models.records import AdjectiveRecord, NounRecord
from langlearn.services.csv_service import CSVService


class SimpleModel(BaseModel):
    """Simple test model for CSV parsing."""

    name: str
    value: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if v == "":
            raise ValueError("name cannot be empty")
        return v

    @field_validator("value")
    @classmethod
    def value_must_not_be_empty(cls, v: str) -> str:
        if v == "":
            raise ValueError("value cannot be empty")
        return v


class TestCSVService:
    """Test CSVService functionality."""

    @pytest.fixture
    def csv_service(self) -> CSVService:
        """CSVService instance for testing."""
        return CSVService()

    @pytest.fixture
    def temp_csv_file(self) -> Generator[Path, None, None]:
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,value\n")
            f.write("test1,value1\n")
            f.write("test2,value2\n")
            temp_path = Path(f.name)

        yield temp_path

        # Cleanup
        if temp_path.exists():
            temp_path.unlink()

    def test_read_csv_success(
        self, csv_service: CSVService, temp_csv_file: Path
    ) -> None:
        """Test successful CSV reading."""
        results = csv_service.read_csv(temp_csv_file, SimpleModel)

        assert len(results) == 2
        assert isinstance(results[0], SimpleModel)
        assert results[0].name == "test1"
        assert results[0].value == "value1"
        assert results[1].name == "test2"
        assert results[1].value == "value2"

    def test_read_csv_file_not_found(self, csv_service: CSVService) -> None:
        """Test FileNotFoundError exception handling."""
        non_existent_file = Path("non_existent_file.csv")

        with pytest.raises(FileNotFoundError):
            csv_service.read_csv(non_existent_file, SimpleModel)

    def test_read_csv_csv_error(self, csv_service: CSVService) -> None:
        """Test csv.Error exception handling."""
        # Mock csv.DictReader to raise a CSV error
        with (
            patch("csv.DictReader", side_effect=csv.Error("CSV parsing error")),
            patch("builtins.open", mock_open()),
            pytest.raises(csv.Error),
        ):
            csv_service.read_csv(Path("test.csv"), SimpleModel)

    def test_read_csv_validation_error(self, csv_service: CSVService) -> None:
        """Test ValidationError exception handling for invalid model data."""
        # Create a CSV file with data that doesn't match the model
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("wrong_field,another_field\n")
            f.write("value1,value2\n")  # Missing required 'name' and 'value' fields
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValidationError):
                csv_service.read_csv(temp_path, SimpleModel)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_read_csv_generic_exception(self, csv_service: CSVService) -> None:
        """Test generic exception handling."""
        # Mock open to raise a generic exception
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            test_path = Path("test.csv")

            with pytest.raises(PermissionError):
                csv_service.read_csv(test_path, SimpleModel)

    def test_read_csv_empty_file(self, csv_service: CSVService) -> None:
        """Test reading an empty CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,value\n")  # Header only, no data rows
            temp_path = Path(f.name)

        try:
            results = csv_service.read_csv(temp_path, SimpleModel)
            assert len(results) == 0
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_read_csv_empty_values_handling(self, csv_service: CSVService) -> None:
        """Test that empty values are handled correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,value\n")
            f.write(",value2\n")  # Empty name field (should cause ValidationError)
            temp_path = Path(f.name)

        try:
            # This should raise ValidationError because 'name' is required but empty
            with pytest.raises(ValidationError):
                csv_service.read_csv(temp_path, SimpleModel)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_read_csv_none_values_converted_to_empty_string(
        self, csv_service: CSVService
    ) -> None:
        """Test that None values are converted to empty strings."""
        # Mock csv.DictReader to return None values
        mock_csv_data = [
            {
                "name": None,
                "value": "value1",
            }  # None name should become empty and fail validation
        ]

        with (
            patch("csv.DictReader") as mock_reader,
            patch("builtins.open", mock_open()),
            pytest.raises(ValidationError),
        ):
            mock_reader.return_value = mock_csv_data
            # This should fail validation because name is None -> empty string
            # -> validation error
            csv_service.read_csv(Path("test.csv"), SimpleModel)

    def test_read_csv_unicode_handling(self, csv_service: CSVService) -> None:
        """Test reading CSV files with Unicode characters."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("name,value\n")
            f.write("Müller,Größe\n")  # German umlauts
            f.write("Café,Naïve\n")  # French accents
            temp_path = Path(f.name)

        try:
            results = csv_service.read_csv(temp_path, SimpleModel)
            assert len(results) == 2
            assert results[0].name == "Müller"
            assert results[0].value == "Größe"
            assert results[1].name == "Café"
            assert results[1].value == "Naïve"
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_read_csv_large_dataset(self, csv_service: CSVService) -> None:
        """Test reading a larger CSV file to ensure scalability."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,value\n")
            # Write 100 test rows
            for i in range(100):
                f.write(f"test{i},value{i}\n")
            temp_path = Path(f.name)

        try:
            results = csv_service.read_csv(temp_path, SimpleModel)
            assert len(results) == 100
            assert results[0].name == "test0"
            assert results[99].name == "test99"
        finally:
            if temp_path.exists():
                temp_path.unlink()


class OptionalFieldModel(BaseModel):
    """Model with optional fields for testing empty value handling."""

    required_field: str
    optional_field: str = ""


class TestCSVServiceOptionalFields:
    """Test CSVService with models that have optional fields."""

    @pytest.fixture
    def csv_service(self) -> CSVService:
        """CSVService instance for testing."""
        return CSVService()

    def test_read_csv_with_optional_fields(self, csv_service: CSVService) -> None:
        """Test reading CSV with optional fields that may be empty."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("required_field,optional_field\n")
            f.write("test1,has_value\n")
            f.write("test2,\n")  # Empty optional field
            temp_path = Path(f.name)

        try:
            results = csv_service.read_csv(temp_path, OptionalFieldModel)
            assert len(results) == 2
            assert results[0].required_field == "test1"
            assert results[0].optional_field == "has_value"
            assert results[1].required_field == "test2"
            assert results[1].optional_field == ""  # Empty string from CSV processing
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestCSVServiceRecords:
    """Test CSVService Record-based functionality for Clean Pipeline Architecture."""

    @pytest.fixture
    def csv_service(self) -> CSVService:
        """Create CSVService instance for testing."""
        return CSVService()

    @pytest.fixture
    def temp_noun_csv(self) -> Generator[Path, None, None]:
        """Create temporary noun CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("noun,article,english,plural,example,related\n")
            f.write("Katze,die,cat,Katzen,Die Katze ist süß.,Tier\n")
            f.write("Hund,der,dog,Hunde,Der Hund bellt.,Tier\n")
            temp_path = Path(f.name)

        try:
            yield temp_path
        finally:
            if temp_path.exists():
                temp_path.unlink()

    @pytest.fixture
    def temp_adjective_csv(self) -> Generator[Path, None, None]:
        """Create temporary adjective CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("word,english,example,comparative,superlative\n")
            f.write("schön,beautiful,Das ist schön.,schöner,am schönsten\n")
            f.write("gut,good,Das ist gut.,besser,am besten\n")
            temp_path = Path(f.name)

        try:
            yield temp_path
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_read_csv_as_records_noun(
        self, csv_service: CSVService, temp_noun_csv: Path
    ) -> None:
        """Test reading noun CSV as records."""
        from langlearn.models.records import NounRecord

        records = csv_service.read_csv_as_records(temp_noun_csv, "noun")

        assert len(records) == 2
        assert all(isinstance(r, NounRecord) for r in records)

        assert isinstance(records[0], NounRecord)
        first_record = records[0]
        assert first_record.noun == "Katze"
        assert first_record.article == "die"
        assert first_record.english == "cat"
        assert first_record.plural == "Katzen"

    def test_read_csv_as_records_adjective(
        self, csv_service: CSVService, temp_adjective_csv: Path
    ) -> None:
        """Test reading adjective CSV as records."""

        records = csv_service.read_csv_as_records(temp_adjective_csv, "adjective")

        assert len(records) == 2
        assert all(isinstance(r, AdjectiveRecord) for r in records)

        assert isinstance(records[0], AdjectiveRecord)
        first_record = records[0]
        assert first_record.word == "schön"
        assert first_record.english == "beautiful"
        assert first_record.comparative == "schöner"

    def test_read_csv_as_records_unsupported_type(
        self, csv_service: CSVService, temp_noun_csv: Path
    ) -> None:
        """Test reading CSV with unsupported record type."""
        with pytest.raises(ValueError, match="Unsupported record type: unknown"):
            csv_service.read_csv_as_records(temp_noun_csv, "unknown")

    def test_read_csv_as_records_file_not_found(self, csv_service: CSVService) -> None:
        """Test reading CSV file that doesn't exist."""
        nonexistent_path = Path("nonexistent.csv")

        with pytest.raises(FileNotFoundError):
            csv_service.read_csv_as_records(nonexistent_path, "noun")

    def test_read_csv_as_records_malformed_row(self, csv_service: CSVService) -> None:
        """Test reading CSV with malformed rows."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("noun,article,english,plural,example,related\n")
            f.write("Katze,die,cat,Katzen,Die Katze ist süß.,Tier\n")
            f.write("BadRow,only_two_fields\n")  # Malformed row - will be skipped
            f.write("Hund,der,dog,Hunde,Der Hund bellt.,Tier\n")
            temp_path = Path(f.name)

        try:
            records = csv_service.read_csv_as_records(temp_path, "noun")

            # Should have 2 records (malformed row skipped)
            assert len(records) == 2
            # Cast to NounRecords after filtering
            noun_records = [r for r in records if isinstance(r, NounRecord)]
            assert len(noun_records) == 2
            assert noun_records[0].noun == "Katze"
            assert noun_records[1].noun == "Hund"

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_read_noun_records(
        self, csv_service: CSVService, temp_noun_csv: Path
    ) -> None:
        """Test convenience method for reading noun records."""
        from langlearn.models.records import NounRecord

        records = csv_service.read_noun_records(temp_noun_csv)

        assert len(records) == 2
        assert all(isinstance(r, NounRecord) for r in records)

    def test_read_adjective_records(
        self, csv_service: CSVService, temp_adjective_csv: Path
    ) -> None:
        """Test convenience method for reading adjective records."""

        records = csv_service.read_adjective_records(temp_adjective_csv)

        assert len(records) == 2
        assert all(isinstance(r, AdjectiveRecord) for r in records)

    def test_get_supported_record_types(self, csv_service: CSVService) -> None:
        """Test getting supported record types."""
        types = csv_service.get_supported_record_types()

        expected_types = {
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
        }
        assert set(types) == expected_types

    def test_validate_csv_structure_valid(
        self, csv_service: CSVService, temp_noun_csv: Path
    ) -> None:
        """Test CSV structure validation with valid file."""
        is_valid = csv_service.validate_csv_structure_for_record_type(
            temp_noun_csv, "noun"
        )

        assert is_valid is True

    def test_validate_csv_structure_missing_fields(
        self, csv_service: CSVService
    ) -> None:
        """Test CSV structure validation with missing fields."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("noun,article\n")  # Missing required fields for noun
            f.write("Katze,die\n")
            temp_path = Path(f.name)

        try:
            is_valid = csv_service.validate_csv_structure_for_record_type(
                temp_path, "noun"
            )

            assert is_valid is False

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_validate_csv_structure_unsupported_type(
        self, csv_service: CSVService, temp_noun_csv: Path
    ) -> None:
        """Test CSV structure validation with unsupported record type."""
        with pytest.raises(ValueError, match="Unsupported record type: unknown"):
            csv_service.validate_csv_structure_for_record_type(temp_noun_csv, "unknown")

    def test_validate_csv_structure_file_not_found(
        self, csv_service: CSVService
    ) -> None:
        """Test CSV structure validation with non-existent file."""
        nonexistent_path = Path("nonexistent.csv")

        with pytest.raises(FileNotFoundError):
            csv_service.validate_csv_structure_for_record_type(nonexistent_path, "noun")


class TestCSVServiceIntegration:
    """Test CSVService integration with real CSV files."""

    def test_load_real_csv_files_as_records(self) -> None:
        """Test loading actual project CSV files as records."""
        csv_service = CSVService()
        project_root = Path.cwd()

        # Test with actual CSV files if they exist
        test_files = [
            ("data/nouns.csv", "noun"),
            ("data/adjectives.csv", "adjective"),
            ("data/adverbs.csv", "adverb"),
            ("data/negations.csv", "negation"),
        ]

        for csv_file, record_type in test_files:
            csv_path = project_root / csv_file
            if csv_path.exists():
                # Test that we can read the file without errors
                records = csv_service.read_csv_as_records(csv_path, record_type)
                assert len(records) > 0

                # Test that structure validation passes
                is_valid = csv_service.validate_csv_structure_for_record_type(
                    csv_path, record_type
                )
                assert is_valid is True
