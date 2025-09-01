"""Protocol defining the interface for media generation capabilities.

This protocol defines the contract that domain models must implement to support
media enrichment through dependency injection. It enables the MediaEnricher to
work with any domain model that provides media generation capabilities without
tight coupling to specific implementations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.protocols.anthropic_protocol import AnthropicServiceProtocol


@runtime_checkable
class MediaGenerationCapable(Protocol):
    """Protocol for domain models that can generate media search terms.

    This protocol defines the interface that domain models must implement
    to support media enrichment. It enables dependency injection and loose
    coupling between MediaEnricher and domain models.
    """

    def get_image_search_strategy(
        self, anthropic_service: "AnthropicServiceProtocol"
    ) -> "Callable[[], str]":
        """Get a strategy for generating image search terms with dependency injection.

        The domain model constructs context-aware requests using its knowledge of
        which fields are most relevant and part-of-speech specific guidance.

        Args:
            anthropic_service: Service for context-aware search term generation.

        Returns:
            A callable that generates image search terms when invoked
        """
        ...

    def get_combined_audio_text(self) -> str:
        """Get the text to be used for audio generation.

        Returns the complete text that should be converted to speech,
        including any German-specific pronunciation guidance or formatting.

        Returns:
            Text string for audio generation
        """
        ...
