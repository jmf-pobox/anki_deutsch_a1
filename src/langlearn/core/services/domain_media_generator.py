"""
Domain media generator implementation.

This module provides the DomainMediaGenerator class that adapts the existing
MediaService to provide the MediaGenerator interface that domain models require
for field processing.
"""

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langlearn.core.services.media_service import MediaService

logger = logging.getLogger(__name__)


class DomainMediaGenerator:
    """Adapter that provides MediaGenerator interface to domain models.

    This class bridges the gap between domain models (which need clean interfaces)
    and the existing service layer (MediaService). It implements the MediaGenerator
    protocol while maintaining separation of concerns.
    """

    def __init__(self, media_service: "MediaService"):
        """Initialize domain media generator.

        Args:
            media_service: Service for generating audio and images
        """
        self._media_service = media_service

    def generate_audio(self, text: str) -> str | None:
        """Generate audio file for the given text.

        Args:
            text: Text to convert to speech

        Returns:
            Path to generated audio file, or None if generation failed

        Raises:
            MediaGenerationError: If audio generation fails
        """
        if not text or not text.strip():
            logger.debug("Skipping audio generation for empty text")
            return None

        try:
            return self._media_service.generate_audio(text)
        except Exception as e:
            logger.error(f"Audio generation failed for '{text[:50]}...': {e}")
            from langlearn.exceptions import MediaGenerationError

            raise MediaGenerationError(
                f"Failed to generate audio for '{text[:50]}...': {e}"
            ) from e

    def generate_image(self, query: str, backup_query: str | None = None) -> str | None:
        """Generate/download image for the given search query.

        Args:
            query: Primary image search query
            backup_query: Fallback query if primary fails

        Returns:
            Path to generated/downloaded image, or None if generation failed

        Raises:
            MediaGenerationError: If image generation fails
        """
        if not query or not query.strip():
            logger.debug("Skipping image generation for empty query")
            return None

        try:
            # Try primary query first
            result = self._media_service.generate_image(query)
            if result:
                return result

            # Try backup query if primary failed and backup is provided
            if backup_query and backup_query.strip():
                logger.debug(
                    f"Primary image query failed, trying backup: {backup_query}"
                )
                return self._media_service.generate_image(backup_query)

            # Both primary and backup failed - raise exception
            from langlearn.exceptions import MediaGenerationError

            raise MediaGenerationError(
                f"No photos found for query '{query}' and backup query '{backup_query}'"
            )
        except Exception as e:
            logger.error(f"Image generation failed for '{query}': {e}")
            from langlearn.exceptions import MediaGenerationError

            raise MediaGenerationError(
                f"Failed to generate image for '{query}': {e}"
            ) from e

    def get_context_enhanced_query(self, word: str, english: str, example: str) -> str:
        """Get context-enhanced search query from German sentence analysis.

        Args:
            word: German word
            english: English translation
            example: German example sentence

        Returns:
            Enhanced search query with contextual information
        """
        if not all([word, english, example]):
            logger.debug("Missing data for context enhancement, using English fallback")
            return english or word or "concept"

        # Legacy method - now just returns English fallback
        # since legacy service is removed
        logger.debug(
            "Context enhancement not available (legacy service removed), "
            "using English fallback"
        )
        return english or word or "concept"

    def get_conceptual_search_terms(
        self, word_type: str, word: str, english: str
    ) -> str:
        """Get conceptual search terms for abstract words.

        Args:
            word_type: Type of word (adverb, negation, etc.)
            word: German word
            english: English translation

        Returns:
            Search terms for conceptual imagery
        """
        if not all([word_type, word, english]):
            logger.debug("Missing data for conceptual search, using English fallback")
            return english or word or "abstract concept"

        # Legacy method - now provides basic conceptual terms
        # since legacy service is removed
        logger.debug(
            "Conceptual search not available (legacy service removed), "
            "using basic terms"
        )
        return f"{english} concept abstract" if english else "abstract concept"

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about media generation for debugging/monitoring.

        Returns:
            Dictionary containing media generation statistics

        Raises:
            MediaGenerationError: If stats collection fails
        """
        try:
            stats = self._media_service.get_stats()
            # Convert MediaGenerationStats to dict for consistent interface
            return stats.__dict__
        except Exception as e:
            logger.error(f"Could not get media service stats: {e}")
            from langlearn.exceptions import MediaGenerationError

            raise MediaGenerationError(f"Failed to get media service stats: {e}") from e

    def clear_cache(self) -> None:
        """Clear any caches in the underlying media service.

        Note: MediaService doesn't currently support cache clearing.
        This method exists for interface compatibility but is a no-op.
        """
        # MediaService doesn't have cache clearing - this is a no-op
        # If cache clearing is needed, implement it directly in MediaService
        logger.debug("DomainMediaGenerator.clear_cache() called - no action taken")


class MockDomainMediaGenerator:
    """Mock implementation of MediaGenerator for testing.

    This class provides predictable responses for testing domain model
    field processing without requiring external API calls.
    """

    def __init__(self) -> None:
        """Initialize mock media generator."""
        self.audio_calls: list[str] = []
        self.image_calls: list[tuple[str, str | None]] = []
        self.context_calls: list[tuple[str, str, str]] = []
        self.conceptual_calls: list[tuple[str, str, str]] = []

        # Default responses (can be customized per test)
        self.audio_response = "/fake/audio.mp3"
        self.image_response = "/fake/image.jpg"
        self.context_response = "enhanced query"
        self.conceptual_response = "conceptual terms"

    def generate_audio(self, text: str) -> str | None:
        """Mock audio generation."""
        self.audio_calls.append(text)
        return self.audio_response

    def generate_image(self, query: str, backup_query: str | None = None) -> str | None:
        """Mock image generation."""
        self.image_calls.append((query, backup_query))
        return self.image_response

    def get_context_enhanced_query(self, word: str, english: str, example: str) -> str:
        """Mock context enhancement."""
        self.context_calls.append((word, english, example))
        return self.context_response

    def get_conceptual_search_terms(
        self, word_type: str, word: str, english: str
    ) -> str:
        """Mock conceptual search."""
        self.conceptual_calls.append((word_type, word, english))
        return self.conceptual_response

    def reset(self) -> None:
        """Reset all call tracking."""
        self.audio_calls.clear()
        self.image_calls.clear()
        self.context_calls.clear()
        self.conceptual_calls.clear()

    def set_responses(self, **responses: Any) -> None:
        """Set custom responses for testing.

        Args:
            **responses: Keyword arguments for response values:
                - audio: str | None - Response for generate_audio
                - image: str | None - Response for generate_image
                - context: str - Response for get_context_enhanced_query
                - conceptual: str - Response for get_conceptual_search_terms
        """
        if "audio" in responses:
            self.audio_response = responses["audio"]
        if "image" in responses:
            self.image_response = responses["image"]
        if "context" in responses:
            self.context_response = responses["context"]
        if "conceptual" in responses:
            self.conceptual_response = responses["conceptual"]
