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

    def get_anthropic_service(self) -> AnthropicService | None:
        """Get the shared AnthropicService instance.

        Returns:
            AnthropicService instance or None if configuration is missing
        """
        if self._anthropic_service is None:
            try:
                self._anthropic_service = AnthropicService()
            except ValueError as e:
                # Expected error: Missing API key configuration
                logger.info(f"AnthropicService not available: {e}")
                return None
            except ImportError as e:
                # Expected error: Missing anthropic package
                logger.warning(f"AnthropicService package not installed: {e}")
                return None
        return self._anthropic_service

    def get_translation_service(self) -> TranslationServiceProtocol | None:
        """Get the shared TranslationService instance.

        Returns:
            TranslationService instance or None if not available
        """
        if self._translation_service is None:
            # Try to create translation service using Anthropic
            anthropic_service = self.get_anthropic_service()
            if anthropic_service:
                # Check for explicit test mode environment variable to avoid
                # creating translation service during testing
                if os.getenv("DISABLE_TRANSLATION_SERVICE") == "1":
                    logger.debug(
                        "Translation service disabled via DISABLE_TRANSLATION_SERVICE"
                    )
                    return None

                # Require a real underlying client
                client = getattr(anthropic_service, "client", None)
                if client is None:
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

    def get_audio_service(self) -> "AudioService | None":
        """Get the shared AudioService instance.

        Returns:
            AudioService instance or None if AWS credentials are missing
        """
        if self._audio_service is None:
            try:
                from langlearn.services.audio import AudioService
                import tempfile
                import os

                # Use temporary directory for tests, proper directory structure otherwise
                if "pytest" in os.environ.get("_", "") or "PYTEST_CURRENT_TEST" in os.environ:
                    # In test environment - use temporary directory
                    temp_dir = tempfile.mkdtemp()
                    self._audio_service = AudioService(output_dir=temp_dir)
                else:
                    # In production environment - use default audio directory
                    self._audio_service = AudioService()
            except ValueError as e:
                # Expected error: Missing AWS credentials or configuration
                logger.info(f"AudioService not available: {e}")
                return None
            except ImportError as e:
                # Expected error: Missing boto3 or AWS SDK
                logger.warning(f"AudioService dependencies missing: {e}")
                return None
        return self._audio_service

    def get_pexels_service(self) -> "PexelsService | None":
        """Get the shared PexelsService instance.

        Returns:
            PexelsService instance or None if API key is missing
        """
        if self._pexels_service is None:
            try:
                from langlearn.services.pexels_service import PexelsService

                self._pexels_service = PexelsService()
            except ValueError as e:
                # Expected error: Missing API key configuration
                logger.info(f"PexelsService not available: {e}")
                return None
            except ImportError as e:
                # Expected error: Missing requests or dependencies
                logger.warning(f"PexelsService dependencies missing: {e}")
                return None
        return self._pexels_service

    def reset(self) -> None:
        """Reset the container (useful for testing)."""
        self._anthropic_service = None
        self._translation_service = None
        self._audio_service = None
        self._pexels_service = None


# Global instance
_container = ServiceContainer()


def get_anthropic_service() -> AnthropicService | None:
    """Factory function to get AnthropicService instance.

    Returns:
        AnthropicService instance or None if not available
    """
    return _container.get_anthropic_service()


def get_translation_service() -> TranslationServiceProtocol | None:
    """Factory function to get TranslationService instance.

    Returns:
        TranslationService instance or None if not available
    """
    return _container.get_translation_service()


def get_audio_service() -> "AudioService | None":
    """Factory function to get AudioService instance.

    Returns:
        AudioService instance or None if not available
    """
    return _container.get_audio_service()


def get_pexels_service() -> "PexelsService | None":
    """Factory function to get PexelsService instance.

    Returns:
        PexelsService instance or None if not available
    """
    return _container.get_pexels_service()


def reset_services() -> None:
    """Reset all services (useful for testing)."""
    _container.reset()
