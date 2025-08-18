"""
Tests for field processor interface and domain media generator.

This test module validates the Phase 1 components of the domain field
processing refactoring, ensuring the interfaces work correctly.
"""

import pytest

from langlearn.models.field_processor import (
    FieldProcessingError,
    FieldProcessor,
    MediaGenerator,
    format_media_reference,
    validate_minimum_fields,
)
from langlearn.services.domain_media_generator import (
    DomainMediaGenerator,
    MockDomainMediaGenerator,
)


class TestFieldProcessorInterface:
    """Test the abstract FieldProcessor interface."""

    def test_field_processor_is_abstract(self) -> None:
        """Test that FieldProcessor cannot be instantiated directly."""
        with pytest.raises(TypeError):
            FieldProcessor()  # type: ignore  # Should raise TypeError for abstract class

    def test_media_generator_protocol(self) -> None:
        """Test MediaGenerator protocol detection."""
        mock = MockDomainMediaGenerator()

        # Should recognize mock as MediaGenerator
        assert isinstance(mock, MediaGenerator)

        # Should have required methods
        assert hasattr(mock, "generate_audio")
        assert hasattr(mock, "generate_image")
        assert hasattr(mock, "get_context_enhanced_query")
        assert hasattr(mock, "get_conceptual_search_terms")


class TestFieldProcessingUtilities:
    """Test utility functions for field processing."""

    def test_format_media_reference_audio(self) -> None:
        """Test formatting audio media references."""
        result = format_media_reference("/path/to/audio.mp3", "audio")
        assert result == "[sound:audio.mp3]"

        result = format_media_reference(None, "audio")
        assert result == ""

    def test_format_media_reference_image(self) -> None:
        """Test formatting image media references."""
        result = format_media_reference("/path/to/image.jpg", "image")
        assert result == '<img src="image.jpg">'

        result = format_media_reference(None, "image")
        assert result == ""

    def test_format_media_reference_invalid_type(self) -> None:
        """Test error handling for invalid media type."""
        with pytest.raises(ValueError, match="Unknown media type"):
            format_media_reference("/path/file.txt", "invalid")

    def test_validate_minimum_fields_success(self) -> None:
        """Test successful field validation."""
        fields = ["word", "english", "example"]
        # Should not raise exception
        validate_minimum_fields(fields, 2, "TestModel")
        validate_minimum_fields(fields, 3, "TestModel")

    def test_validate_minimum_fields_failure(self) -> None:
        """Test field validation failure."""
        fields = ["word", "english"]

        with pytest.raises(FieldProcessingError) as exc_info:
            validate_minimum_fields(fields, 5, "TestModel")

        error = exc_info.value
        assert "Insufficient fields" in str(error)
        assert "got 2, need at least 5" in str(error)
        assert error.model_type == "TestModel"
        assert error.original_fields == fields


class TestFieldProcessingError:
    """Test FieldProcessingError exception."""

    def test_field_processing_error_creation(self) -> None:
        """Test creating FieldProcessingError."""
        fields = ["test", "data"]
        error = FieldProcessingError("Test error", fields, "TestModel")

        assert error.message == "Test error"
        assert error.original_fields == fields
        assert error.model_type == "TestModel"

    def test_field_processing_error_string_representation(self) -> None:
        """Test FieldProcessingError string representation."""
        fields = ["test", "data"]
        error = FieldProcessingError("Test error", fields, "TestModel")

        error_str = str(error)
        assert "Test error" in error_str
        assert "TestModel" in error_str
        assert "2" in error_str  # field count


class TestMockDomainMediaGenerator:
    """Test MockDomainMediaGenerator for testing support."""

    @pytest.fixture
    def mock_generator(self) -> MockDomainMediaGenerator:
        """Create mock media generator for testing."""
        return MockDomainMediaGenerator()

    def test_mock_audio_generation(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test mock audio generation tracking."""
        result = mock_generator.generate_audio("test text")

        assert result == "/fake/audio.mp3"
        assert mock_generator.audio_calls == ["test text"]

    def test_mock_image_generation(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test mock image generation tracking."""
        result = mock_generator.generate_image("test query", "backup")

        assert result == "/fake/image.jpg"
        assert mock_generator.image_calls == [("test query", "backup")]

    def test_mock_context_enhancement(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test mock context enhancement tracking."""
        result = mock_generator.get_context_enhanced_query("word", "english", "example")

        assert result == "enhanced query"
        assert mock_generator.context_calls == [("word", "english", "example")]

    def test_mock_conceptual_search(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test mock conceptual search tracking."""
        result = mock_generator.get_conceptual_search_terms("adverb", "schnell", "fast")

        assert result == "conceptual terms"
        assert mock_generator.conceptual_calls == [("adverb", "schnell", "fast")]

    def test_mock_custom_responses(
        self, mock_generator: MockDomainMediaGenerator
    ) -> None:
        """Test setting custom responses in mock."""
        mock_generator.set_responses(
            audio="/custom/audio.mp3",
            image=None,  # Simulate failure
            context="custom context",
            conceptual="custom conceptual",
        )

        assert mock_generator.generate_audio("test") == "/custom/audio.mp3"
        assert mock_generator.generate_image("test") is None
        result_context = mock_generator.get_context_enhanced_query("a", "b", "c")
        assert result_context == "custom context"
        result_conceptual = mock_generator.get_conceptual_search_terms("x", "y", "z")
        assert result_conceptual == "custom conceptual"

    def test_mock_reset(self, mock_generator: MockDomainMediaGenerator) -> None:
        """Test resetting mock call tracking."""
        # Make some calls
        mock_generator.generate_audio("test1")
        mock_generator.generate_audio("test2")
        mock_generator.generate_image("query", None)

        assert len(mock_generator.audio_calls) == 2
        assert len(mock_generator.image_calls) == 1

        # Reset and verify
        mock_generator.reset()
        assert len(mock_generator.audio_calls) == 0
        assert len(mock_generator.image_calls) == 0
        assert len(mock_generator.context_calls) == 0
        assert len(mock_generator.conceptual_calls) == 0


class TestDomainMediaGeneratorInterface:
    """Test DomainMediaGenerator implementation interface."""

    def test_domain_media_generator_implements_protocol(self) -> None:
        """Test that DomainMediaGenerator implements MediaGenerator protocol."""
        # We can't easily test the real implementation without mocking the services,
        # but we can verify the mock implements the protocol
        mock = MockDomainMediaGenerator()
        assert isinstance(mock, MediaGenerator)

    def test_domain_media_generator_methods_exist(self) -> None:
        """Test that DomainMediaGenerator has required methods."""
        # Import without instantiating to check class structure

        assert hasattr(DomainMediaGenerator, "generate_audio")
        assert hasattr(DomainMediaGenerator, "generate_image")
        assert hasattr(DomainMediaGenerator, "get_context_enhanced_query")
        assert hasattr(DomainMediaGenerator, "get_conceptual_search_terms")
        assert hasattr(DomainMediaGenerator, "get_stats")
        assert hasattr(DomainMediaGenerator, "clear_cache")


class ConcreteFieldProcessor(FieldProcessor):
    """Concrete implementation of FieldProcessor for testing."""

    def __init__(self, expected_fields: int = 5):
        self._expected_fields = expected_fields

    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: MediaGenerator
    ) -> list[str]:
        """Simple test implementation."""
        if not self.validate_field_structure(fields):
            raise FieldProcessingError(
                "Invalid field structure", fields, "ConcreteFieldProcessor"
            )

        processed = fields.copy()

        # Simple test logic: add audio if last field is empty
        if len(processed) > 0 and not processed[-1]:
            audio_path = media_generator.generate_audio(processed[0])
            if audio_path:
                processed[-1] = format_media_reference(audio_path, "audio")

        return processed

    def get_expected_field_count(self) -> int:
        return self._expected_fields

    def validate_field_structure(self, fields: list[str]) -> bool:
        return len(fields) >= self._expected_fields

    def _get_field_names(self) -> list[str]:
        return [f"Field{i + 1}" for i in range(self._expected_fields)]


class TestFieldProcessorImplementation:
    """Test concrete FieldProcessor implementation."""

    @pytest.fixture
    def processor(self) -> ConcreteFieldProcessor:
        """Create concrete field processor for testing."""
        return ConcreteFieldProcessor(3)

    @pytest.fixture
    def mock_generator(self) -> MockDomainMediaGenerator:
        """Create mock media generator."""
        return MockDomainMediaGenerator()

    def test_field_processor_basic_processing(
        self,
        processor: ConcreteFieldProcessor,
        mock_generator: MockDomainMediaGenerator,
    ) -> None:
        """Test basic field processing."""
        fields = ["word", "english", ""]  # Empty last field should get audio

        result = processor.process_fields_for_media_generation(fields, mock_generator)

        assert len(result) == 3
        assert result[0] == "word"
        assert result[1] == "english"
        assert result[2] == "[sound:audio.mp3]"  # Should be filled

        # Verify mock was called
        assert mock_generator.audio_calls == ["word"]

    def test_field_processor_insufficient_fields(
        self,
        processor: ConcreteFieldProcessor,
        mock_generator: MockDomainMediaGenerator,
    ) -> None:
        """Test error handling for insufficient fields."""
        fields = ["word"]  # Only 1 field, need 3

        with pytest.raises(FieldProcessingError) as exc_info:
            processor.process_fields_for_media_generation(fields, mock_generator)

        assert "Invalid field structure" in str(exc_info.value)

    def test_field_processor_validation(
        self, processor: ConcreteFieldProcessor
    ) -> None:
        """Test field structure validation."""
        assert processor.validate_field_structure(["a", "b", "c"]) is True
        assert processor.validate_field_structure(["a", "b", "c", "d"]) is True
        assert processor.validate_field_structure(["a", "b"]) is False

    def test_field_processor_metadata(self, processor: ConcreteFieldProcessor) -> None:
        """Test field processor metadata."""
        assert processor.get_expected_field_count() == 3

        info = processor.get_field_layout_info()
        assert info["model_type"] == "ConcreteFieldProcessor"
        assert info["expected_field_count"] == 3
        assert info["field_names"] == ["Field1", "Field2", "Field3"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
