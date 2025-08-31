"""Tests for service container dependency injection."""

from unittest.mock import Mock, patch

from langlearn.services.service_container import (
    ServiceContainer,
    get_anthropic_service,
    get_audio_service,
    get_pexels_service,
    reset_services,
)


class TestServiceContainer:
    """Test ServiceContainer functionality."""

    def setup_method(self) -> None:
        """Reset services before each test."""
        reset_services()

    def teardown_method(self) -> None:
        """Reset services after each test."""
        reset_services()

    def test_singleton_pattern(self) -> None:
        """Test that ServiceContainer follows singleton pattern."""
        container1 = ServiceContainer()
        container2 = ServiceContainer()

        assert container1 is container2

    def test_get_anthropic_service_returns_none_on_exception(self) -> None:
        """Test that get_anthropic_service returns None when service unavailable."""
        with patch(
            "langlearn.services.service_container.AnthropicService"
        ) as mock_service:
            mock_service.side_effect = Exception("Service unavailable")

            result = get_anthropic_service()
            assert result is None

    @patch("langlearn.services.audio.AudioService")
    def test_get_audio_service_creates_instance(self, mock_audio_service: Mock) -> None:
        """Test that get_audio_service creates AudioService instance."""
        mock_instance = Mock()
        mock_audio_service.return_value = mock_instance

        result = get_audio_service()

        assert result is mock_instance
        mock_audio_service.assert_called_once()

    def test_get_audio_service_returns_none_on_exception(self) -> None:
        """Test that get_audio_service returns None when service unavailable."""
        with patch("langlearn.services.audio.AudioService") as mock_service:
            mock_service.side_effect = Exception("AWS credentials not available")

            result = get_audio_service()
            assert result is None

    @patch("langlearn.services.pexels_service.PexelsService")
    def test_get_pexels_service_creates_instance(
        self, mock_pexels_service: Mock
    ) -> None:
        """Test that get_pexels_service creates PexelsService instance."""
        mock_instance = Mock()
        mock_pexels_service.return_value = mock_instance

        result = get_pexels_service()

        assert result is mock_instance
        mock_pexels_service.assert_called_once()

    def test_get_pexels_service_returns_none_on_exception(self) -> None:
        """Test that get_pexels_service returns None when service unavailable."""
        with patch("langlearn.services.pexels_service.PexelsService") as mock_service:
            mock_service.side_effect = Exception("API key not available")

            result = get_pexels_service()
            assert result is None

    @patch("langlearn.services.audio.AudioService")
    def test_service_caching(self, mock_audio_service: Mock) -> None:
        """Test that services are cached and not recreated."""
        mock_instance = Mock()
        mock_audio_service.return_value = mock_instance

        # Call twice
        result1 = get_audio_service()
        result2 = get_audio_service()

        # Should be same instance and service constructor called only once
        assert result1 is result2
        assert result1 is mock_instance
        mock_audio_service.assert_called_once()

    def test_reset_services_clears_cache(self) -> None:
        """Test that reset_services clears all cached services."""
        with patch("langlearn.services.audio.AudioService") as mock_audio:
            mock_audio.return_value = Mock()

            # Get service to cache it
            get_audio_service()

            # Reset services
            reset_services()

            # Get service again - should create new instance
            get_audio_service()

            # Should have been called twice (before and after reset)
            assert mock_audio.call_count == 2
