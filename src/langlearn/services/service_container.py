"""Service container for dependency injection."""

from typing import Optional

from .anthropic_service import AnthropicService
from .translation_service import AnthropicTranslationService, TranslationServiceProtocol


class ServiceContainer:
    """Simple service container for managing shared service instances."""

    _instance: Optional["ServiceContainer"] = None
    _anthropic_service: AnthropicService | None = None
    _translation_service: TranslationServiceProtocol | None = None

    def __new__(cls) -> "ServiceContainer":
        """Singleton pattern to ensure one container instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_anthropic_service(self) -> AnthropicService | None:
        """Get the shared AnthropicService instance.

        Returns:
            AnthropicService instance or None if not available
        """
        if self._anthropic_service is None:
            try:
                self._anthropic_service = AnthropicService()
            except Exception:
                # Service not available (e.g., no API key)
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
                try:
                    self._translation_service = AnthropicTranslationService(anthropic_service)
                except Exception:
                    # Translation service not available
                    return None
        return self._translation_service

    def reset(self) -> None:
        """Reset the container (useful for testing)."""
        self._anthropic_service = None
        self._translation_service = None


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


def reset_services() -> None:
    """Reset all services (useful for testing)."""
    _container.reset()
