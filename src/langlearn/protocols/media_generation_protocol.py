"""Protocol defining the interface for media generation capabilities.

This protocol defines the contract that domain models must implement to support
media enrichment through dependency injection. It enables the MediaEnricher to
work with any domain model that provides media generation capabilities without
tight coupling to specific implementations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Callable


@runtime_checkable
class MediaGenerationCapable(Protocol):
    """Protocol for domain models that can generate media search terms.

    This protocol defines the interface that domain models must implement
    to support media enrichment. It enables dependency injection and loose
    coupling between MediaEnricher and domain models.
    """

    def get_image_search_strategy(self) -> "Callable[[], str]":
        """Get a strategy for generating image search terms.

        Returns a callable that when invoked will generate context-aware
        search terms for image retrieval. The strategy pattern allows for
        lazy evaluation to avoid unnecessary API calls.

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
