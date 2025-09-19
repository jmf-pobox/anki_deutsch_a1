"""Media enricher protocol for language-agnostic media enrichment."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from langlearn.core.protocols.media_generation_protocol import (
        MediaGenerationCapable,
    )


@runtime_checkable
class MediaEnricherProtocol(Protocol):
    """Protocol defining the interface for language-agnostic media enrichment.

    This protocol allows AnkiBackend and other core components to work with
    media enrichers from any language without knowing their specific implementation
    details. Each language implements media enrichers that provide language-specific
    media generation logic while conforming to this common interface.

    Examples:
        - German enricher: Handles German pronunciation, gender-specific images
        - Russian enricher: Handles Cyrillic audio, case-specific examples
        - Korean enricher: Handles honorifics, agglutination patterns
    """

    def enrich_with_media(self, domain_model: MediaGenerationCapable) -> dict[str, Any]:
        """Enrich domain model with media using its domain expertise.

        Args:
            domain_model: Domain model implementing MediaGenerationCapable protocol

        Returns:
            Dictionary containing generated media data with keys like:
            - 'image': Image filename or reference
            - 'word_audio': Audio filename for word pronunciation
            - 'example_audio': Audio filename for example sentence
            - Other language-specific media fields

        Raises:
            MediaGenerationError: If media generation fails
        """
        ...
