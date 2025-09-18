"""Unit tests for MediaEnricher services."""

import tempfile
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from langlearn.infrastructure.services.ai_service import AnthropicService
from langlearn.infrastructure.services.audio_service import AudioService
from langlearn.infrastructure.services.image_service import PexelsService
from langlearn.infrastructure.services.media_enricher import (
    MediaEnricherBase,
    StandardMediaEnricher,
)
from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)
from langlearn.protocols.media_generation_protocol import MediaGenerationCapable


class MockDomainModel:
    """Mock domain model implementing MediaGenerationCapable protocol."""

    def __init__(
        self,
        primary_word: str = "Haus",
        audio_segments: dict[str, str] | None = None,
        image_strategy_result: str = "house building",
    ):
        self.primary_word = primary_word
        self.audio_segments = audio_segments or {"word_audio": "das Haus"}
        self.image_strategy_result = image_strategy_result

    def get_primary_word(self) -> str:
        """Get the primary word for filename generation."""
        return self.primary_word

    def get_audio_segments(self) -> dict[str, str]:
        """Get audio segments for this model."""
        return self.audio_segments

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get image search strategy."""
        return lambda: self.image_strategy_result

    def get_combined_audio_text(self) -> str:
        """Get combined audio text."""
        return "das Haus"


class MockDomainModelWithNoImage:
    """Mock domain model with no image strategy - for testing edge cases."""

    def __init__(
        self,
        primary_word: str = "Haus",
        audio_segments: dict[str, str] | None = None,
    ):
        self.primary_word = primary_word
        self.audio_segments = audio_segments or {"word_audio": "das Haus"}

    def get_primary_word(self) -> str:
        """Get the primary word for filename generation."""
        return self.primary_word

    def get_audio_segments(self) -> dict[str, str]:
        """Get audio segments for this model."""
        return self.audio_segments

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get image search strategy that returns empty string."""
        return lambda: ""  # Empty string for no image

    def get_combined_audio_text(self) -> str:
        """Get combined audio text."""
        return "das Haus"


class ConcreteMediaEnricher(MediaEnricherBase):
    """Concrete implementation for testing abstract base class."""

    def enrich_with_media(self, domain_model: MediaGenerationCapable) -> dict[str, Any]:
        """Test implementation of enrich_with_media."""
        return {"test_field": "test_value"}

    def enrich_records(
        self, records: list[dict[str, Any]], domain_models: list[MediaGenerationCapable]
    ) -> list[dict[str, Any]]:
        """Test implementation of enrich_records."""
        return [{"enriched": True} for _ in records]


class TestMediaEnricherBase:
    """Test the abstract MediaEnricherBase class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that MediaEnricherBase cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            MediaEnricherBase()  # type: ignore[abstract]

    def test_concrete_implementation_works(self) -> None:
        """Test that concrete implementation can be instantiated and used."""
        enricher = ConcreteMediaEnricher()

        # Test enrich_with_media
        mock_model = MockDomainModel()
        result = enricher.enrich_with_media(mock_model)
        assert result == {"test_field": "test_value"}

        # Test enrich_records
        records = [{"word": "test"}]
        models: list[MediaGenerationCapable] = [mock_model]
        result_list = enricher.enrich_records(records, models)
        assert result_list == [{"enriched": True}]


class TestStandardMediaEnricher:
    """Test the StandardMediaEnricher implementation."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_services(self) -> dict[str, Mock]:
        """Create mock services for testing."""
        audio_service = Mock(spec=AudioService)
        pexels_service = Mock(spec=PexelsService)
        anthropic_service = Mock(spec=AnthropicService)

        return {
            "audio_service": audio_service,
            "pexels_service": pexels_service,
            "anthropic_service": anthropic_service,
        }

    @pytest.fixture
    def media_enricher(
        self, temp_dir: Path, mock_services: dict[str, Mock]
    ) -> StandardMediaEnricher:
        """Create StandardMediaEnricher instance for testing."""
        audio_path = temp_dir / "audio"
        image_path = temp_dir / "images"

        return StandardMediaEnricher(
            audio_service=mock_services["audio_service"],
            pexels_service=mock_services["pexels_service"],
            anthropic_service=mock_services["anthropic_service"],
            audio_base_path=audio_path,
            image_base_path=image_path,
        )

    def test_init_creates_directories(
        self, temp_dir: Path, mock_services: dict[str, Mock]
    ) -> None:
        """Test that initialization creates audio and image directories."""
        audio_path = temp_dir / "audio"
        image_path = temp_dir / "images"

        # Directories don't exist initially
        assert not audio_path.exists()
        assert not image_path.exists()

        StandardMediaEnricher(
            audio_service=mock_services["audio_service"],
            pexels_service=mock_services["pexels_service"],
            anthropic_service=mock_services["anthropic_service"],
            audio_base_path=audio_path,
            image_base_path=image_path,
        )

        # Directories should now exist
        assert audio_path.exists()
        assert image_path.exists()

    def test_enrich_with_media_success_path(
        self,
        media_enricher: StandardMediaEnricher,
        temp_dir: Path,
        mock_services: dict[str, Mock],
    ) -> None:
        """Test successful media enrichment with all components."""
        mock_model = MockDomainModel(
            primary_word="Haus",
            audio_segments={
                "word_audio": "das Haus",
                "example_audio": "Das ist ein Haus",
            },
            image_strategy_result="house building architecture",
        )

        # Mock audio service
        mock_services["audio_service"].generate_audio.return_value = Path(
            "/tmp/audio.mp3"
        )

        # Mock pexels service
        mock_services["pexels_service"].download_image.return_value = True

        result = media_enricher.enrich_with_media(mock_model)

        # Should have audio files
        assert "word_audio" in result
        assert "example_audio" in result
        assert result["word_audio"].endswith(".mp3")
        assert result["example_audio"].endswith(".mp3")

        # Should have image
        assert "image" in result
        assert result["image"] == "haus.jpg"

        # Verify service calls
        assert mock_services["audio_service"].generate_audio.call_count == 2
        mock_services["pexels_service"].download_image.assert_called_once()

    def test_enrich_with_media_existing_files(
        self,
        media_enricher: StandardMediaEnricher,
        temp_dir: Path,
        mock_services: dict[str, Mock],
    ) -> None:
        """Test enrichment when audio and image files already exist."""
        mock_model = MockDomainModel(
            primary_word="Haus", audio_segments={"word_audio": "das Haus"}
        )

        # Create existing audio file
        audio_dir = temp_dir / "audio"
        audio_hash = media_enricher._generate_content_hash("das Haus")
        existing_audio = audio_dir / f"{audio_hash}.mp3"
        existing_audio.touch()

        # Create existing image file
        image_dir = temp_dir / "images"
        existing_image = image_dir / "haus.jpg"
        existing_image.touch()

        result = media_enricher.enrich_with_media(mock_model)

        # Should use existing files without calling services
        assert "word_audio" in result
        assert "image" in result

        # Services should not be called
        mock_services["audio_service"].generate_audio.assert_not_called()
        mock_services["pexels_service"].download_image.assert_not_called()

    def test_enrich_with_media_audio_generation_failure(
        self, media_enricher: StandardMediaEnricher, mock_services: dict[str, Mock]
    ) -> None:
        """Test handling of audio generation failures."""
        mock_model = MockDomainModel(audio_segments={"word_audio": "das Haus"})

        # Mock audio service to raise exception
        mock_services["audio_service"].generate_audio.side_effect = Exception(
            "Audio generation failed"
        )
        mock_services["pexels_service"].download_image.return_value = True

        result = media_enricher.enrich_with_media(mock_model)

        # Should handle audio failure gracefully
        assert "word_audio" not in result
        assert "image" in result  # Image should still work

    def test_enrich_with_media_image_generation_failure(
        self, media_enricher: StandardMediaEnricher, mock_services: dict[str, Mock]
    ) -> None:
        """Test handling of image generation failures."""
        mock_model = MockDomainModel(audio_segments={"word_audio": "das Haus"})

        # Mock services
        mock_services["audio_service"].generate_audio.return_value = Path(
            "/tmp/audio.mp3"
        )
        mock_services["pexels_service"].download_image.return_value = False  # Failure

        result = media_enricher.enrich_with_media(mock_model)

        # Should handle image failure gracefully
        assert "word_audio" in result
        assert "image" not in result

    def test_enrich_with_media_no_image_query(
        self, media_enricher: StandardMediaEnricher, mock_services: dict[str, Mock]
    ) -> None:
        """Test behavior when domain model returns empty image query."""
        mock_model = MockDomainModelWithNoImage(
            audio_segments={"word_audio": "das Haus"}
        )

        mock_services["audio_service"].generate_audio.return_value = Path(
            "/tmp/audio.mp3"
        )

        result = media_enricher.enrich_with_media(mock_model)

        # Should have audio but no image
        assert "word_audio" in result
        assert "image" not in result

        # Pexels service should not be called
        mock_services["pexels_service"].download_image.assert_not_called()

    def test_enrich_records_success(
        self, media_enricher: StandardMediaEnricher, mock_services: dict[str, Mock]
    ) -> None:
        """Test successful batch record enrichment."""
        records = [
            {"word": "Haus", "translation": "house"},
            {"word": "Auto", "translation": "car"},
        ]

        models: list[MediaGenerationCapable] = [
            MockDomainModel(
                primary_word="Haus", audio_segments={"word_audio": "das Haus"}
            ),
            MockDomainModel(
                primary_word="Auto", audio_segments={"word_audio": "das Auto"}
            ),
        ]

        # Mock services
        mock_services["audio_service"].generate_audio.return_value = Path(
            "/tmp/audio.mp3"
        )
        mock_services["pexels_service"].download_image.return_value = True

        result = media_enricher.enrich_records(records, models)

        assert len(result) == 2

        # Check first record
        assert result[0]["word"] == "Haus"
        assert result[0]["translation"] == "house"
        assert "word_audio" in result[0]
        assert "image" in result[0]

        # Check second record
        assert result[1]["word"] == "Auto"
        assert result[1]["translation"] == "car"
        assert "word_audio" in result[1]
        assert "image" in result[1]

    def test_enrich_records_length_mismatch(
        self, media_enricher: StandardMediaEnricher
    ) -> None:
        """Test error handling when record and model counts don't match."""
        records = [{"word": "Haus"}]
        models: list[MediaGenerationCapable] = [
            MockDomainModel(),
            MockDomainModel(),
        ]  # More models than records

        with pytest.raises(
            ValueError, match="Records and domain models count mismatch"
        ):
            media_enricher.enrich_records(records, models)

    def test_enrich_records_individual_failure(
        self, media_enricher: StandardMediaEnricher, mock_services: dict[str, Mock]
    ) -> None:
        """Test handling of individual record enrichment failures."""
        records = [
            {"word": "Haus"},
            {"word": "Auto"},
        ]

        # Create models where second one will fail
        models: list[MediaGenerationCapable] = [
            MockDomainModel(primary_word="Haus"),
            MockDomainModel(primary_word="Auto"),
        ]

        # Mock to fail on second enrichment
        def mock_enrich_side_effect(model: MediaGenerationCapable) -> dict[str, Any]:
            if hasattr(model, "primary_word") and model.primary_word == "Auto":
                raise Exception("Enrichment failed for Auto")
            return {"word_audio": "test.mp3", "image": "test.jpg"}

        with patch.object(
            media_enricher, "enrich_with_media", side_effect=mock_enrich_side_effect
        ):
            result = media_enricher.enrich_records(records, models)

        assert len(result) == 2

        # First record should be enriched
        assert "word_audio" in result[0]
        assert "image" in result[0]

        # Second record should be original (not enriched due to failure)
        assert result[1] == {"word": "Auto"}

    def test_generate_content_hash(self, media_enricher: StandardMediaEnricher) -> None:
        """Test content hash generation."""
        content1 = "das Haus"
        content2 = "das Auto"
        content3 = "das Haus"  # Same as content1

        hash1 = media_enricher._generate_content_hash(content1)
        hash2 = media_enricher._generate_content_hash(content2)
        hash3 = media_enricher._generate_content_hash(content3)

        # Hashes should be deterministic and different for different content
        assert hash1 != hash2
        assert hash1 == hash3
        assert len(hash1) == 32  # MD5 hash length

    def test_extract_primary_word(self, media_enricher: StandardMediaEnricher) -> None:
        """Test primary word extraction from domain model."""
        mock_model = MockDomainModel(primary_word="TestWord")

        result = media_enricher._extract_primary_word(mock_model)

        assert result == "TestWord"

    def test_empty_audio_segments(
        self, media_enricher: StandardMediaEnricher, mock_services: dict[str, Mock]
    ) -> None:
        """Test handling of empty audio segments."""
        mock_model = MockDomainModel(
            audio_segments={"word_audio": "", "example_audio": ""}  # Empty values
        )

        mock_services["pexels_service"].download_image.return_value = True

        result = media_enricher.enrich_with_media(mock_model)

        # Should not generate audio for empty segments
        assert "word_audio" not in result
        assert "example_audio" not in result

        # Should still generate image
        assert "image" in result

        # Audio service should not be called
        mock_services["audio_service"].generate_audio.assert_not_called()

    def test_debug_logging(
        self,
        media_enricher: StandardMediaEnricher,
        mock_services: dict[str, Mock],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test debug logging functionality."""
        mock_model = MockDomainModel(primary_word="TestHaus")

        mock_services["audio_service"].generate_audio.return_value = Path(
            "/tmp/audio.mp3"
        )
        mock_services["pexels_service"].download_image.return_value = True

        with caplog.at_level("DEBUG"):
            media_enricher.enrich_with_media(mock_model)

        # Check that debug messages contain expected content
        info_messages = [
            record.message for record in caplog.records if record.levelname == "INFO"
        ]
        assert any("model_word: TestHaus" in msg for msg in info_messages)
        assert any("image_filename: testhaus.jpg" in msg for msg in info_messages)

    def test_exception_handling_in_image_generation(
        self, media_enricher: StandardMediaEnricher, mock_services: dict[str, Mock]
    ) -> None:
        """Test exception handling during image generation process."""
        mock_model = MockDomainModel(audio_segments={"word_audio": "das Haus"})

        # Mock audio service to succeed
        mock_services["audio_service"].generate_audio.return_value = Path(
            "/tmp/audio.mp3"
        )

        # Mock pexels service to raise exception
        mock_services["pexels_service"].download_image.side_effect = Exception(
            "Network error"
        )

        result = media_enricher.enrich_with_media(mock_model)

        # Should handle exception gracefully
        assert "word_audio" in result  # Audio should still work
        assert "image" not in result  # Image should fail gracefully

    def test_exception_handling_in_audio_segments_processing(
        self, media_enricher: StandardMediaEnricher, mock_services: dict[str, Mock]
    ) -> None:
        """Test exception handling during audio segments processing."""
        mock_model = MockDomainModel()

        # Mock get_audio_segments to raise exception
        with patch.object(
            mock_model,
            "get_audio_segments",
            side_effect=Exception("Audio segments error"),
        ):
            mock_services["pexels_service"].download_image.return_value = True

            result = media_enricher.enrich_with_media(mock_model)

            # Should handle exception gracefully
            assert "word_audio" not in result  # Audio should fail gracefully
            assert "image" in result  # Image should still work
