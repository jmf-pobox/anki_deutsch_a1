"""Tests for custom exceptions."""

from langlearn.exceptions import ProcessingError, RecordValidationError
from langlearn.languages.german.records.noun_record import NounRecord


class TestProcessingError:
    """Test ProcessingError container class."""

    def test_processing_error_initialization(self) -> None:
        """Test ProcessingError with all parameters."""
        record = NounRecord(
            noun="Test",
            english="test",
            article="das",
            plural="Tests",
            example="Das ist ein Test.",
        )
        original_error = ValueError("Invalid value")
        context = "test context"

        error = ProcessingError(record=record, error=original_error, context=context)

        assert error.record == record
        assert error.error == original_error
        assert error.context == context

    def test_processing_error_str_representation(self) -> None:
        """Test string representation of ProcessingError."""
        record = NounRecord(
            noun="Haus",
            english="house",
            article="das",
            plural="Häuser",
            example="Das Haus ist groß.",
        )

        error = ProcessingError(record=record, error=Exception("Original error"))
        str_repr = str(error)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0


class TestRecordValidationError:
    """Test RecordValidationError exception class."""

    def test_record_validation_error_basic(self) -> None:
        """Test basic RecordValidationError functionality."""
        error = RecordValidationError("Test validation error")
        assert "Test validation error" in str(error)
        assert isinstance(error, Exception)

    def test_processing_error_without_context(self) -> None:
        """Test ProcessingError without context parameter."""
        record = NounRecord(
            noun="Test",
            english="test",
            article="das",
            plural="Tests",
            example="Das ist ein Test.",
        )

        # Test ProcessingError creation without context
        error = ProcessingError(record=record, error=ValueError("test error"))
        assert error.context is None
        assert error.record == record
        assert isinstance(error.error, ValueError)
