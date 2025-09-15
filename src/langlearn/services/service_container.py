"""Service container for dependency injection."""

import logging
import os
from typing import TYPE_CHECKING, Optional

from .anthropic_service import AnthropicService
from .translation_service import AnthropicTranslationService, TranslationServiceProtocol

if TYPE_CHECKING:
    from langlearn.services.audio import AudioService
    from langlearn.services.pexels_service import PexelsService

# Module-level logger for tests to patch/log
logger = logging.getLogger(__name__)


class ServiceContainer:
    """Simple service container for managing shared service instances."""

    _instance: Optional["ServiceContainer"] = None
    _anthropic_service: AnthropicService | None = None
    _translation_service: TranslationServiceProtocol | None = None
    _audio_service: "AudioService | None" = None
    _pexels_service: "PexelsService | None" = None

    def __new__(cls) -> "ServiceContainer":
        """Singleton pattern to ensure one container instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_anthropic_service(self) -> AnthropicService:
        """Get the shared AnthropicService instance.

        Returns:
            AnthropicService instance

        Raises:
            ValueError: If API key configuration is missing
            ImportError: If anthropic package is not installed
        """
        if self._anthropic_service is None:
            self._anthropic_service = AnthropicService()
        return self._anthropic_service

    def get_translation_service(self) -> TranslationServiceProtocol | None:
        """Get the shared TranslationService instance.

        Returns:
            TranslationService instance or None if not available
        """
        if self._translation_service is None:
            # Try to create translation service using Anthropic
            try:
                anthropic_service = self.get_anthropic_service()
            except (ValueError, ImportError):
                # AnthropicService not available, translation service unavailable
                return None

            # Check for explicit test mode environment variable to avoid
            # creating translation service during testing
            if os.getenv("DISABLE_TRANSLATION_SERVICE") == "1":
                logger.debug(
                    "Translation service disabled via DISABLE_TRANSLATION_SERVICE"
                )
                return None

            # Require a real underlying client
            if anthropic_service.client is None:
                logger.debug(
                    "Translation unavailable: Anthropic client not initialized"
                )
                return None
            try:
                self._translation_service = AnthropicTranslationService(
                    anthropic_service
                )
            except ValueError as e:
                # Expected error: Invalid configuration
                logger.info(f"TranslationService not available: {e}")
                return None
            except ImportError as e:
                # Expected error: Missing dependencies
                logger.warning(f"TranslationService dependencies missing: {e}")
                return None
        return self._translation_service

    def get_audio_service(self) -> "AudioService":
        """Get the shared AudioService instance.

        Returns:
            AudioService instance

        Raises:
            ValueError: If AWS credentials are missing or invalid
            ImportError: If boto3 or AWS SDK dependencies are missing
        """
        if self._audio_service is None:
            import os
            import tempfile

            from langlearn.services.audio import AudioService

            # Use temporary directory for tests, proper directory otherwise
            if (
                "pytest" in os.environ.get("_", "")
                or "PYTEST_CURRENT_TEST" in os.environ
            ):
                # In test environment - use temporary directory
                temp_dir = tempfile.mkdtemp()
                self._audio_service = AudioService(output_dir=temp_dir)
            else:
                # In production environment - use default audio directory
                self._audio_service = AudioService()
        return self._audio_service

    def get_pexels_service(self) -> "PexelsService":
        """Get the shared PexelsService instance.

        Returns:
            PexelsService instance

        Raises:
            ValueError: If API key configuration is missing
            ImportError: If requests or dependencies are missing
        """
        if self._pexels_service is None:
            from langlearn.services.pexels_service import PexelsService

            self._pexels_service = PexelsService()
        return self._pexels_service

    def reset(self) -> None:
        """Reset the container (useful for testing)."""
        self._anthropic_service = None
        self._translation_service = None
        self._audio_service = None
        self._pexels_service = None


# Global instance
_container = ServiceContainer()


def get_anthropic_service() -> AnthropicService:
    """Factory function to get AnthropicService instance.

    Returns:
        AnthropicService instance

    Raises:
        ValueError: If API key configuration is missing
        ImportError: If anthropic package is not installed
    """
    return _container.get_anthropic_service()


def get_translation_service() -> TranslationServiceProtocol | None:
    """Factory function to get TranslationService instance.

    Returns:
        TranslationService instance or None if not available
    """
    return _container.get_translation_service()


def get_audio_service() -> "AudioService":
    """Factory function to get AudioService instance.

    Returns:
        AudioService instance

    Raises:
        ValueError: If AWS credentials are missing or invalid
        ImportError: If boto3 or AWS SDK dependencies are missing
    """
    return _container.get_audio_service()


def get_pexels_service() -> "PexelsService":
    """Factory function to get PexelsService instance.

    Returns:
        PexelsService instance

    Raises:
        ValueError: If API key configuration is missing
        ImportError: If requests or dependencies are missing
    """
    return _container.get_pexels_service()


def reset_services() -> None:
    """Reset all services (useful for testing)."""
    _container.reset()
