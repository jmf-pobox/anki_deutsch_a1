"""Tests for domain media generator service."""

from unittest.mock import Mock, patch

import pytest

from langlearn.exceptions import MediaGenerationError
from langlearn.infrastructure.services.domain_media_generator import (
    DomainMediaGenerator,
)


class TestDomainMediaGenerator:
    """Test DomainMediaGenerator adapter functionality."""

    @pytest.fixture
    def mock_media_service(self) -> Mock:
        """Create a mock MediaService for testing."""
        mock_service = Mock()
        mock_service.generate_audio.return_value = "/fake/audio.mp3"
        mock_service.generate_image.return_value = "/fake/image.jpg"
        return mock_service

    @pytest.fixture
    def generator(self, mock_media_service: Mock) -> DomainMediaGenerator:
        """Create a DomainMediaGenerator instance for testing."""
        return DomainMediaGenerator(mock_media_service)

    def test_initialization(self, mock_media_service: Mock) -> None:
        """Test generator initializes with media service."""
        generator = DomainMediaGenerator(mock_media_service)
        assert generator._media_service is mock_media_service

    def test_generate_audio_success(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test successful audio generation."""
        result = generator.generate_audio("Hallo Welt")

        assert result == "/fake/audio.mp3"
        mock_media_service.generate_audio.assert_called_once_with("Hallo Welt")

    def test_generate_audio_empty_text(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test audio generation with empty text."""
        result = generator.generate_audio("")

        assert result is None
        mock_media_service.generate_audio.assert_not_called()

    def test_generate_audio_whitespace_only(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test audio generation with whitespace-only text."""
        result = generator.generate_audio("   \t\n  ")

        assert result is None
        mock_media_service.generate_audio.assert_not_called()

    def test_generate_audio_service_exception(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test audio generation when service raises exception."""
        mock_media_service.generate_audio.side_effect = Exception("Service error")

        with pytest.raises(
            MediaGenerationError, match=r"Failed to generate audio for 'test text...'"
        ):
            generator.generate_audio("test text")

    def test_generate_image_success(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test successful image generation with primary query."""
        result = generator.generate_image("cat")

        assert result == "/fake/image.jpg"
        mock_media_service.generate_image.assert_called_once_with("cat")

    def test_generate_image_primary_fails_backup_succeeds(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test image generation when primary query fails but backup succeeds."""
        mock_media_service.generate_image.side_effect = [None, "/fake/backup.jpg"]

        result = generator.generate_image("obscure query", "animal")

        assert result == "/fake/backup.jpg"
        assert mock_media_service.generate_image.call_count == 2
        mock_media_service.generate_image.assert_any_call("obscure query")
        mock_media_service.generate_image.assert_any_call("animal")

    def test_generate_image_both_queries_fail(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test image generation when both primary and backup queries fail."""
        mock_media_service.generate_image.return_value = None

        result = generator.generate_image("invalid query", "also invalid")

        assert result is None
        assert mock_media_service.generate_image.call_count == 2

    def test_generate_image_empty_query(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test image generation with empty query."""
        result = generator.generate_image("")

        assert result is None
        mock_media_service.generate_image.assert_not_called()

    def test_generate_image_whitespace_only_query(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test image generation with whitespace-only query."""
        result = generator.generate_image("   \t\n  ")

        assert result is None
        mock_media_service.generate_image.assert_not_called()

    def test_generate_image_no_backup_query(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test image generation with only primary query (no backup)."""
        result = generator.generate_image("cat", None)

        assert result == "/fake/image.jpg"
        mock_media_service.generate_image.assert_called_once_with("cat")

    def test_generate_image_service_exception(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test image generation when service raises exception."""
        mock_media_service.generate_image.side_effect = Exception("Service error")

        with pytest.raises(
            MediaGenerationError, match="Failed to generate image for 'test query'"
        ):
            generator.generate_image("test query")

    def test_generate_image_exception_raises_error(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test image generation when service throws exception raises
        MediaGenerationError."""
        mock_media_service.generate_image.side_effect = Exception("Service error")

        with pytest.raises(
            MediaGenerationError, match="Failed to generate image for 'query'"
        ):
            generator.generate_image("query")

        mock_media_service.generate_image.assert_called_once_with("query")

    def test_get_context_enhanced_query_all_params(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test context enhanced query with all parameters provided."""
        with patch(
            "langlearn.infrastructure.services.domain_media_generator.logger.debug"
        ) as mock_logger:
            result = generator.get_context_enhanced_query(
                "Hund", "dog", "Der Hund bellt"
            )

            assert result == "dog"
            mock_logger.assert_called_once()
            assert "Context enhancement not available" in mock_logger.call_args[0][0]

    def test_get_context_enhanced_query_missing_data(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test context enhanced query with missing data."""
        with patch(
            "langlearn.infrastructure.services.domain_media_generator.logger.debug"
        ) as mock_logger:
            result = generator.get_context_enhanced_query("", "dog", "")

            assert result == "dog"
            mock_logger.assert_called_once()
            assert "Missing data for context enhancement" in mock_logger.call_args[0][0]

    def test_get_context_enhanced_query_all_empty(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test context enhanced query with all empty parameters."""
        result = generator.get_context_enhanced_query("", "", "")
        assert result == "concept"

    def test_get_conceptual_search_terms_all_params(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test conceptual search terms with all parameters."""
        with patch(
            "langlearn.infrastructure.services.domain_media_generator.logger.debug"
        ) as mock_logger:
            result = generator.get_conceptual_search_terms(
                "adverb", "schnell", "quickly"
            )

            assert result == "quickly concept abstract"
            mock_logger.assert_called_once()
            assert "Conceptual search not available" in mock_logger.call_args[0][0]

    def test_get_conceptual_search_terms_missing_data(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test conceptual search terms with missing data."""
        with patch(
            "langlearn.infrastructure.services.domain_media_generator.logger.debug"
        ) as mock_logger:
            result = generator.get_conceptual_search_terms("", "word", "")

            assert result == "word"
            mock_logger.assert_called_once()
            assert "Missing data for conceptual search" in mock_logger.call_args[0][0]

    def test_get_conceptual_search_terms_no_english(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test conceptual search terms without English translation."""
        with patch(
            "langlearn.infrastructure.services.domain_media_generator.logger.debug"
        ) as mock_logger:
            result = generator.get_conceptual_search_terms("adverb", "schnell", "")

            assert result == "schnell"  # Returns fallback to word when english empty
            mock_logger.assert_called_once()
            assert "Missing data for conceptual search" in mock_logger.call_args[0][0]

    def test_get_stats_service_has_stats_with_dict(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test get_stats when media service has stats method returning object
        with __dict__.
        """
        mock_stats = type(
            "MockStats",
            (),
            {"__dict__": {"audio_generated": 5, "images_downloaded": 3}},
        )()
        mock_media_service.get_stats.return_value = mock_stats

        result = generator.get_stats()

        assert result == {"audio_generated": 5, "images_downloaded": 3}
        mock_media_service.get_stats.assert_called_once()

    def test_get_stats_service_returns_invalid_stats(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test get_stats with invalid stats object - should fail fast."""
        mock_media_service.get_stats.return_value = "some_stats_string"

        with pytest.raises(
            MediaGenerationError, match="Failed to get media service stats"
        ):
            generator.get_stats()

    def test_get_stats_service_no_stats_method(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test get_stats when media service has no stats method - should fail fast."""
        # Remove get_stats method
        if hasattr(mock_media_service, "get_stats"):
            delattr(mock_media_service, "get_stats")

        with pytest.raises(
            MediaGenerationError, match="Failed to get media service stats"
        ):
            generator.get_stats()

    def test_get_stats_service_exception(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test get_stats when service raises exception."""
        mock_media_service.get_stats.side_effect = Exception("Stats error")

        with pytest.raises(
            MediaGenerationError, match="Failed to get media service stats"
        ):
            generator.get_stats()

    def test_clear_cache_is_noop(
        self, generator: DomainMediaGenerator, mock_media_service: Mock
    ) -> None:
        """Test clear_cache is a no-op since MediaService doesn't support caching."""
        with patch(
            "langlearn.infrastructure.services.domain_media_generator.logger.debug"
        ) as mock_logger:
            generator.clear_cache()

            # Should not call media service (it doesn't have clear_cache)
            assert (
                not hasattr(mock_media_service, "clear_cache")
                or not mock_media_service.clear_cache.called
            )
            mock_logger.assert_called_once()
            assert "no action taken" in mock_logger.call_args[0][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
