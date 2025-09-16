"""Domain model protocol for language-agnostic interfaces."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from langlearn.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )


@runtime_checkable
class LanguageDomainModel(Protocol):
    """Protocol defining the common interface all language domain models must implement.

    This protocol allows the AnkiBackend and other core components to work with
    domain models from any language without knowing their specific implementation
    details. Each language implements domain models that provide language-specific
    business logic while conforming to this common interface.

    Examples:
        - German models: Handle gender, cases, separable verbs
        - Russian models: Handle 6-case system, verb aspects
        - Korean models: Handle honorifics, agglutination
    """

    @abstractmethod
    def get_combined_audio_text(self) -> str:
        """Get the complete text for audio generation.

        Returns the text that should be passed to TTS services for generating
        pronunciation audio. May include multiple components (word, example, etc.).

        Returns:
            Complete text string for audio generation
        """

    @abstractmethod
    def get_audio_segments(self) -> dict[str, str]:
        """Get individual audio segments for targeted pronunciation practice.

        Returns a mapping of segment names to text content for generating
        separate audio files. Allows learners to practice specific components.

        Returns:
            Dictionary mapping segment names to audio text content
        """

    @abstractmethod
    def get_primary_word(self) -> str:
        """Get the primary word/term for this domain model.

        Returns the main vocabulary item being learned, without additional
        context or formatting. Used for file naming and basic display.

        Returns:
            The primary vocabulary word/term
        """

    @abstractmethod
    def get_image_search_strategy(
        self, ai_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get strategy for generating contextual image search terms.

        Returns a callable that uses this model's domain knowledge and the
        AI service to generate appropriate search terms for image generation.
        Different languages may have different strategies based on their
        linguistic features.

        Args:
            ai_service: Service for AI-powered search term generation

        Returns:
            Callable that generates image search query when invoked
        """
