"""Tests for domain media generator service."""

from unittest.mock import Mock, patch
import pytest

from langlearn.services.domain_media_generator import DomainMediaGenerator


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

    def test_generate_audio_success(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test successful audio generation."""
        result = generator.generate_audio("Hallo Welt")
        
        assert result == "/fake/audio.mp3"
        mock_media_service.generate_audio.assert_called_once_with("Hallo Welt")

    def test_generate_audio_empty_text(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test audio generation with empty text."""
        result = generator.generate_audio("")
        
        assert result is None
        mock_media_service.generate_audio.assert_not_called()

    def test_generate_audio_whitespace_only(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test audio generation with whitespace-only text."""
        result = generator.generate_audio("   \t\n  ")
        
        assert result is None
        mock_media_service.generate_audio.assert_not_called()

    def test_generate_audio_service_exception(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test audio generation when service raises exception."""
        mock_media_service.generate_audio.side_effect = Exception("Service error")
        
        with patch("langlearn.services.domain_media_generator.logger.warning") as mock_logger:
            result = generator.generate_audio("test text")
            
            assert result is None
            mock_logger.assert_called_once()
            assert "Audio generation failed" in mock_logger.call_args[0][0]

    def test_generate_image_success(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test successful image generation with primary query."""
        result = generator.generate_image("cat")
        
        assert result == "/fake/image.jpg"
        mock_media_service.generate_image.assert_called_once_with("cat")

    def test_generate_image_primary_fails_backup_succeeds(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test image generation when primary query fails but backup succeeds."""
        mock_media_service.generate_image.side_effect = [None, "/fake/backup.jpg"]
        
        result = generator.generate_image("obscure query", "animal")
        
        assert result == "/fake/backup.jpg"
        assert mock_media_service.generate_image.call_count == 2
        mock_media_service.generate_image.assert_any_call("obscure query")
        mock_media_service.generate_image.assert_any_call("animal")

    def test_generate_image_both_queries_fail(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test image generation when both primary and backup queries fail."""
        mock_media_service.generate_image.return_value = None
        
        result = generator.generate_image("invalid query", "also invalid")
        
        assert result is None
        assert mock_media_service.generate_image.call_count == 2

    def test_generate_image_empty_query(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test image generation with empty query."""
        result = generator.generate_image("")
        
        assert result is None
        mock_media_service.generate_image.assert_not_called()

    def test_generate_image_whitespace_only_query(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test image generation with whitespace-only query."""
        result = generator.generate_image("   \t\n  ")
        
        assert result is None
        mock_media_service.generate_image.assert_not_called()

    def test_generate_image_no_backup_query(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test image generation with only primary query (no backup)."""
        result = generator.generate_image("cat", None)
        
        assert result == "/fake/image.jpg"
        mock_media_service.generate_image.assert_called_once_with("cat")

    def test_generate_image_service_exception(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test image generation when service raises exception."""
        mock_media_service.generate_image.side_effect = Exception("Service error")
        
        with patch("langlearn.services.domain_media_generator.logger.warning") as mock_logger:
            result = generator.generate_image("test query")
            
            assert result is None
            mock_logger.assert_called_once()
            assert "Image generation failed" in mock_logger.call_args[0][0]

    def test_generate_image_exception_returns_none(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test image generation when service throws exception returns None."""
        mock_media_service.generate_image.side_effect = Exception("Service error")
        
        with patch("langlearn.services.domain_media_generator.logger.warning") as mock_logger:
            result = generator.generate_image("query")
            
            assert result is None
            mock_media_service.generate_image.assert_called_once_with("query")
            mock_logger.assert_called_once()
            assert "Image generation failed" in mock_logger.call_args[0][0]

    def test_get_context_enhanced_query_all_params(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test context enhanced query with all parameters provided."""
        with patch("langlearn.services.domain_media_generator.logger.debug") as mock_logger:
            result = generator.get_context_enhanced_query("Hund", "dog", "Der Hund bellt")
            
            assert result == "dog"
            mock_logger.assert_called_once()
            assert "Context enhancement not available" in mock_logger.call_args[0][0]

    def test_get_context_enhanced_query_missing_data(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test context enhanced query with missing data."""
        with patch("langlearn.services.domain_media_generator.logger.debug") as mock_logger:
            result = generator.get_context_enhanced_query("", "dog", "")
            
            assert result == "dog"
            mock_logger.assert_called_once()
            assert "Missing data for context enhancement" in mock_logger.call_args[0][0]

    def test_get_context_enhanced_query_all_empty(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test context enhanced query with all empty parameters."""
        result = generator.get_context_enhanced_query("", "", "")
        assert result == "concept"

    def test_get_conceptual_search_terms_all_params(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test conceptual search terms with all parameters."""
        with patch("langlearn.services.domain_media_generator.logger.debug") as mock_logger:
            result = generator.get_conceptual_search_terms("adverb", "schnell", "quickly")
            
            assert result == "quickly concept abstract"
            mock_logger.assert_called_once()
            assert "Conceptual search not available" in mock_logger.call_args[0][0]

    def test_get_conceptual_search_terms_missing_data(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test conceptual search terms with missing data."""
        with patch("langlearn.services.domain_media_generator.logger.debug") as mock_logger:
            result = generator.get_conceptual_search_terms("", "word", "")
            
            assert result == "word"
            mock_logger.assert_called_once()
            assert "Missing data for conceptual search" in mock_logger.call_args[0][0]

    def test_get_conceptual_search_terms_no_english(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test conceptual search terms without English translation."""
        with patch("langlearn.services.domain_media_generator.logger.debug") as mock_logger:
            result = generator.get_conceptual_search_terms("adverb", "schnell", "")
            
            assert result == "schnell"  # Returns fallback to word when english empty
            mock_logger.assert_called_once()
            assert "Missing data for conceptual search" in mock_logger.call_args[0][0]

    def test_get_stats_service_has_stats_with_dict(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test get_stats when media service has stats method returning object with __dict__."""
        mock_stats = type('MockStats', (), {"__dict__": {"audio_generated": 5, "images_downloaded": 3}})()
        mock_media_service.get_stats.return_value = mock_stats
        
        result = generator.get_stats()
        
        assert result == {"audio_generated": 5, "images_downloaded": 3}
        mock_media_service.get_stats.assert_called_once()

    def test_get_stats_service_returns_dict(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test get_stats when media service returns non-dict object."""
        mock_media_service.get_stats.return_value = "some_stats_string"
        
        result = generator.get_stats()
        
        assert result == {"stats": "some_stats_string"}

    def test_get_stats_service_no_stats_method(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test get_stats when media service has no stats method."""
        # Remove get_stats method
        if hasattr(mock_media_service, 'get_stats'):
            delattr(mock_media_service, 'get_stats')
        
        result = generator.get_stats()
        
        assert result == {"media_service_stats": "unavailable"}

    def test_get_stats_service_exception(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test get_stats when service raises exception."""
        mock_media_service.get_stats.side_effect = Exception("Stats error")
        
        with patch("langlearn.services.domain_media_generator.logger.warning") as mock_logger:
            result = generator.get_stats()
            
            assert result == {"error": "Stats error"}
            mock_logger.assert_called_once()
            assert "Could not get media service stats" in mock_logger.call_args[0][0]

    def test_clear_cache_service_has_method(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test clear_cache when service has clear_cache method."""
        with patch("langlearn.services.domain_media_generator.logger.info") as mock_logger:
            generator.clear_cache()
            
            mock_media_service.clear_cache.assert_called_once()
            mock_logger.assert_called_once()
            assert "Media service cache cleared" in mock_logger.call_args[0][0]

    def test_clear_cache_service_no_method(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test clear_cache when service has no clear_cache method."""
        # Remove clear_cache method
        if hasattr(mock_media_service, 'clear_cache'):
            delattr(mock_media_service, 'clear_cache')
        
        # Should execute without error when no method exists
        generator.clear_cache()  # No exception should be raised

    def test_clear_cache_service_exception(self, generator: DomainMediaGenerator, mock_media_service: Mock) -> None:
        """Test clear_cache when service raises exception."""
        mock_media_service.clear_cache.side_effect = Exception("Cache error")
        
        with patch("langlearn.services.domain_media_generator.logger.warning") as mock_logger:
            generator.clear_cache()
            
            mock_logger.assert_called_once()
            assert "Could not clear media service cache" in mock_logger.call_args[0][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])