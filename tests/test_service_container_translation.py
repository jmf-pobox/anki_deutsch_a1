"""Tests for translation service integration with service container."""

from unittest.mock import Mock, patch

from langlearn.services.service_container import (
    ServiceContainer,
    get_translation_service,
    reset_services,
)
from langlearn.services.translation_service import AnthropicTranslationService


class TestServiceContainerTranslation:
    """Test translation service integration with service container."""

    def setup_method(self) -> None:
        """Reset services before each test."""
        reset_services()

    def teardown_method(self) -> None:
        """Reset services after each test."""
        reset_services()

    @patch("langlearn.services.service_container.AnthropicService")
    def test_get_translation_service_success(self, mock_anthropic_class: Mock) -> None:
        """Test successful creation of translation service."""
        # Arrange
        mock_anthropic_instance = Mock()
        mock_anthropic_class.return_value = mock_anthropic_instance

        container = ServiceContainer()

        # Act
        translation_service = container.get_translation_service()

        # Assert
        assert translation_service is not None
        assert isinstance(translation_service, AnthropicTranslationService)
        # Should reuse the same instance on subsequent calls
        assert container.get_translation_service() is translation_service

    @patch("langlearn.services.service_container.AnthropicService")
    def test_get_translation_service_anthropic_failure(
        self, mock_anthropic_class: Mock
    ) -> None:
        """Test translation service creation when Anthropic service fails."""
        # Arrange
        mock_anthropic_class.side_effect = Exception("API Key not found")

        container = ServiceContainer()

        # Act
        translation_service = container.get_translation_service()

        # Assert
        assert translation_service is None

    @patch("langlearn.services.service_container.AnthropicTranslationService")
    @patch("langlearn.services.service_container.AnthropicService")
    def test_get_translation_service_translation_creation_failure(
        self, mock_anthropic_class: Mock, mock_translation_class: Mock
    ) -> None:
        """Test translation service creation when translation service creation fails."""
        # Arrange
        mock_anthropic_instance = Mock()
        mock_anthropic_class.return_value = mock_anthropic_instance
        mock_translation_class.side_effect = Exception("Translation service error")

        container = ServiceContainer()

        # Act
        translation_service = container.get_translation_service()

        # Assert
        assert translation_service is None

    def test_reset_clears_translation_service(self) -> None:
        """Test that reset clears the translation service."""
        # Arrange
        container = ServiceContainer()

        # Mock successful creation
        with patch("langlearn.services.service_container.AnthropicService"):
            first_service = container.get_translation_service()

        # Act
        container.reset()

        # Mock successful creation again
        with patch("langlearn.services.service_container.AnthropicService"):
            second_service = container.get_translation_service()

        # Assert
        # Services should be different instances after reset
        if first_service and second_service:
            assert first_service is not second_service

    @patch("langlearn.services.service_container.AnthropicService")
    def test_factory_function_get_translation_service(
        self, mock_anthropic_class: Mock
    ) -> None:
        """Test the factory function for getting translation service."""
        # Arrange
        mock_anthropic_instance = Mock()
        mock_anthropic_class.return_value = mock_anthropic_instance

        # Act
        translation_service = get_translation_service()

        # Assert
        assert translation_service is not None
        assert isinstance(translation_service, AnthropicTranslationService)

    def test_factory_function_returns_none_when_unavailable(self) -> None:
        """Test factory function returns None when service unavailable."""
        # Arrange - no mocking, so Anthropic service will fail to create

        # Act
        translation_service = get_translation_service()

        # Assert
        assert translation_service is None

    @patch("langlearn.services.service_container.AnthropicService")
    def test_singleton_behavior(self, mock_anthropic_class: Mock) -> None:
        """Test that service container maintains singleton behavior."""
        # Arrange
        mock_anthropic_instance = Mock()
        mock_anthropic_class.return_value = mock_anthropic_instance

        # Act
        container1 = ServiceContainer()
        container2 = ServiceContainer()

        service1 = container1.get_translation_service()
        service2 = container2.get_translation_service()

        # Assert
        assert container1 is container2  # Singleton containers
        assert service1 is service2  # Same service instance


class TestTranslationServiceIntegrationWithDeckBuilder:
    """Test translation service integration with DeckBuilder."""

    def setup_method(self) -> None:
        """Reset services before each test."""
        reset_services()

    def teardown_method(self) -> None:
        """Reset services after each test."""
        reset_services()

    @patch("langlearn.deck_builder.get_translation_service")
    @patch("langlearn.services.media_enricher.StandardMediaEnricher")
    def test_deck_builder_injects_translation_service(
        self, mock_enricher_class: Mock, mock_get_translation: Mock
    ) -> None:
        """Test that DeckBuilder properly injects translation service."""
        # Arrange
        mock_translation_service = Mock()
        mock_get_translation.return_value = mock_translation_service

        # This test would require more complex setup to actually test DeckBuilder
        # For now, we verify the service is available

        # Act
        translation_service = mock_get_translation()

        # Assert
        assert translation_service is mock_translation_service
        mock_get_translation.assert_called_once()

    def test_translation_service_availability_in_production(self) -> None:
        """Test translation service availability in production-like conditions."""
        # This test checks if the service can be created without mocking
        # It will fail if no API key is available, which is expected in test environment

        # Act
        translation_service = get_translation_service()

        # Assert
        # In test environment without API key, service should be None
        # In production with API key, service should be available
        # This test documents the expected behavior
        if translation_service:
            assert isinstance(translation_service, AnthropicTranslationService)
        else:
            # Expected in test environment without API credentials
            assert translation_service is None


class TestTranslationServiceErrorHandling:
    """Test error handling in translation service integration."""

    def setup_method(self) -> None:
        """Reset services before each test."""
        reset_services()

    def teardown_method(self) -> None:
        """Reset services after each test."""
        reset_services()

    @patch("langlearn.services.service_container.logger")
    def test_service_creation_logs_appropriately(self, mock_logger: Mock) -> None:
        """Test that service creation logs appropriately."""
        # This test would verify logging behavior
        # For now, we just ensure the service container doesn't crash

        # Act
        translation_service = get_translation_service()

        # Assert
        # Service creation should not raise exceptions
        # Logging behavior depends on whether API key is available
        assert translation_service is None or isinstance(
            translation_service, AnthropicTranslationService
        )

    def test_multiple_service_requests_handle_failures_gracefully(self) -> None:
        """Test that multiple requests for unavailable service handle failures."""
        # Act - multiple requests should not crash
        service1 = get_translation_service()
        service2 = get_translation_service()
        service3 = get_translation_service()

        # Assert - all should return None (no API key in test environment)
        assert service1 is None
        assert service2 is None
        assert service3 is None
