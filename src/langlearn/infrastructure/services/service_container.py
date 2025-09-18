"""Service container for dependency injection."""

import logging
from typing import TYPE_CHECKING, Optional

from langlearn.infrastructure.services.ai_service import AnthropicService

if TYPE_CHECKING:
    from langlearn.infrastructure.services.audio_service import AudioService
    from langlearn.infrastructure.services.image_service import PexelsService

# Module-level logger for tests to patch/log
logger = logging.getLogger(__name__)


class ServiceContainer:
    """Simple service container for managing shared service instances."""

    _instance: Optional["ServiceContainer"] = None
    _anthropic_service: AnthropicService | None = None
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

            from langlearn.infrastructure.services.audio_service import AudioService

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
            from langlearn.infrastructure.services.image_service import PexelsService

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
