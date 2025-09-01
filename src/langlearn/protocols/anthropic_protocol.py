"""Protocol for Anthropic service capabilities."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class AnthropicServiceProtocol(Protocol):
    """Protocol defining the interface for Anthropic AI services.

    This protocol defines the contract that Anthropic service implementations
    must follow to support media generation and other AI-powered features.
    """

    def generate_pexels_query(self, model: Any) -> str:
        """Generate a Pexels search query from a domain model.

        Args:
            model: Domain model containing the data to generate search terms for

        Returns:
            Search query string suitable for Pexels API
        """
        ...
