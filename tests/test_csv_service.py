"""Unit tests for CSVService."""

import csv
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from pydantic import BaseModel, ValidationError, field_validator

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
