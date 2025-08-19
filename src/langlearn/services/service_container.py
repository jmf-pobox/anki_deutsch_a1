"""Service container for dependency injection."""

from typing import Optional

from .anthropic_service import AnthropicService


class ServiceContainer:
    """Simple service container for managing shared service instances."""

    _instance: Optional["ServiceContainer"] = None
    _anthropic_service: AnthropicService | None = None

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

    def reset(self) -> None:
        """Reset the container (useful for testing)."""
        self._anthropic_service = None


# Global instance
_container = ServiceContainer()


def get_anthropic_service() -> AnthropicService | None:
    """Factory function to get AnthropicService instance.

    Returns:
        AnthropicService instance or None if not available
    """
    return _container.get_anthropic_service()


def reset_services() -> None:
    """Reset all services (useful for testing)."""
    _container.reset()
