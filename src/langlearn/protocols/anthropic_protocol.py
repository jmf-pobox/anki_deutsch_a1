"""Protocol for Anthropic service capabilities."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class AnthropicServiceProtocol(Protocol):
    """Protocol defining the interface for Anthropic AI services.

    This protocol defines the contract that Anthropic service implementations
    must follow to support media generation and other AI-powered features.
    """

    def generate_pexels_query(self, context: Any) -> str:
        """Generate a Pexels search query from rich domain context.

        Args:
            context: Rich context string from domain model's _build_search_context()
                    method containing German linguistic expertise and visualization guidance

        Returns:
            Search query string suitable for Pexels API
        """
        ...
