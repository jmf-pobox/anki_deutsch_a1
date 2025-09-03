from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from langlearn.protocols.media_generation_protocol import MediaGenerationCapable

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )

logger = logging.getLogger(__name__)

"""German Negation Domain Model.

This module contains the domain model for German negation words with specialized logic
for German language learning applications. The module is responsible for:

CORE RESPONSIBILITIES:
    - Modeling German negation data (word, English translation, type, example)
    - Implementing MediaGenerationCapable protocol for media enrichment
    - Providing German-specific linguistic validation and position rules
    - Contributing domain expertise for image search term generation
    - Supporting audio generation with proper negation context

DESIGN PRINCIPLES:
    - Domain model is SMART: Contains German negation expertise and linguistic
      knowledge
    - Services are DUMB: External services receive rich context, no domain logic
    - Single Responsibility: Negation logic stays in Negation model, not in services
    - Dependency Injection: Protocol-based design for loose coupling

GERMAN LINGUISTIC FEATURES:
    - 7 negation types with specific position and usage rules
    - Position validation based on German syntax (nicht, kein, niemand, etc.)
    - Context-aware visualization strategies for abstract negation concepts
    - Type-specific search term generation using linguistic domain knowledge

INTEGRATION POINTS:
    - MediaGenerationCapable protocol for image/audio media enrichment
    - AnthropicServiceProtocol for AI-powered search term generation
    - MediaEnricher service for coordinated media asset generation

Usage:
    Basic usage:
        >>> negation = Negation(
        ...     word="nicht",
        ...     english="not",
        ...     type=NegationType.GENERAL,
        ...     example="Ich bin nicht müde."
        ... )

    Media generation with dependency injection:
        >>> strategy = negation.get_image_search_strategy(anthropic_service)
        >>> search_terms = strategy()  # Returns context-aware search terms
        >>> audio_text = negation.get_combined_audio_text()  # Word + example
"""


class NegationType(str, Enum):
    """Types of German negation words."""

    GENERAL = "general"  # nicht
    ARTICLE = "article"  # kein, keine
    PRONOUN = "pronoun"  # nichts, niemand
    TEMPORAL = "temporal"  # nie, niemals
    SPATIAL = "spatial"  # nirgends, nirgendwo
    CORRELATIVE = "correlative"  # weder...noch
    INTENSIFIER = "intensifier"  # gar nicht, überhaupt nicht


@dataclass
class Negation(MediaGenerationCapable):
    """German negation domain model with linguistic expertise and media generation.

    Represents a German negation word with its properties, German linguistic knowledge,
    and specialized logic for media enrichment. German negation follows specific
    syntactic rules and position requirements depending on the negation type.

    This model implements MediaGenerationCapable protocol to contribute domain
    expertise for image and audio generation, using type-specific strategies
    for abstract negation concept visualization.

    Attributes:
        word: The German negation word (e.g., "nicht", "kein", "niemand")
        english: English translation (e.g., "not", "no", "nobody")
        type: NegationType classification (GENERAL, ARTICLE, PRONOUN, etc.)
        example: German example sentence demonstrating proper usage

    Note:
        This model follows the design principle that domain models are SMART
        (contain expertise) while services are DUMB (execute instructions).
    """

    word: str
    english: str
    type: NegationType
    example: str

    def __post_init__(self) -> None:
        """Validate the negation data after initialization."""
        # Validate core required fields
        required_fields = ["word", "english", "example"]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Required field '{field_name}' cannot be empty")

        # Validate type is a NegationType enum
        if not isinstance(self.type, NegationType):
            raise ValueError(f"Type must be a NegationType, got {type(self.type)}")

    def validate_example(self) -> bool:
        """Validate that the example contains the negation and follows basic rules.

        Returns:
            bool: True if the example is valid
        """
        # Example must contain the negation (case-insensitive)
        if not any(part.lower() in self.example.lower() for part in self.word.split()):
            return False

        # Example must be a complete sentence
        if not any(self.example.endswith(p) for p in ".!?"):
            return False

        # Example must start with a capital letter
        if not self.example[0].isupper():
            return False

        # Check negation position and usage
        return self.validate_position()

    def validate_position(self) -> bool:
        """Validate that the negation is in a valid position in the example sentence.

        Returns:
            bool: True if the negation position is valid
        """
        # Split the example into words
        words = self.example.rstrip(".!?").split()

        # Convert words to lowercase for case-insensitive comparison
        words_lower = [w.lower() for w in words]

        # For multi-word negations, find the position of the first word
        word_parts = self.word.lower().split()
        try:
            # Find position of first part
            neg_pos = words_lower.index(word_parts[0])

            # For multi-word negations, verify all parts are present in sequence
            if len(word_parts) > 1:
                for i, part in enumerate(word_parts[1:], 1):
                    if (
                        neg_pos + i >= len(words_lower)
                        or words_lower[neg_pos + i] != part
                    ):
                        return False
        except ValueError:
            return False

        # General negation (nicht) typically comes at the end or before adjectives
        if self.type == NegationType.GENERAL:
            # Should not be at the start
            if neg_pos == 0:
                return False
            # Should be at the end or before an adjective/adverb
            if neg_pos == len(words) - 1:  # At end
                return True
            if neg_pos < len(words) - 1:  # Before adjective/adverb
                return True

        # Article negations (kein/keine) come where articles would
        if self.type == NegationType.ARTICLE and neg_pos < len(words) - 1:
            # Should be followed by a noun (simplified check)
            return True

        # Pronouns can be subjects (start) or objects (middle/end)
        if self.type == NegationType.PRONOUN and (neg_pos == 0 or neg_pos > 0):
            # Can be at start or in sentence
            return True

        # Temporal negations follow time expression rules
        if self.type == NegationType.TEMPORAL and neg_pos < len(words) - 1:
            # Should not be at the very end
            return True

        # Spatial negations follow place expression rules
        if self.type == NegationType.SPATIAL and neg_pos > 0:
            # Should be in the middle or end of clause
            return True

        # Correlative negations need their pair (simplified check)
        if self.type == NegationType.CORRELATIVE and neg_pos < len(words) - 2:
            # Should be followed by more words (for the 'noch' part)
            return True

        # Intensifiers modify other negations or come at clause end
        if self.type == NegationType.INTENSIFIER:
            # Account for multi-word intensifiers
            total_words = len(word_parts)
            # Should be at end or before what they modify
            if neg_pos + total_words == len(words):  # At end
                return True
            if neg_pos + total_words < len(words):  # Before what they modify
                return True

        return False

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get strategy for generating image search terms with domain expertise.

        Creates a callable that uses this negation's domain knowledge to generate
        context-aware image search terms. The negation contributes German linguistic
        expertise (type-specific positioning, abstract concept visualization) while
        the anthropic service executes the actual AI processing.

        Design: Domain model is SMART (provides rich context), service is DUMB
        (processes whatever context it receives).

        Args:
            anthropic_service: Service implementing ImageQueryGenerationProtocol for
                AI-powered search term generation.

        Returns:
            Callable that when invoked returns image search terms as string.
            Falls back to type-specific concept mappings if service fails.

        Example:
            >>> negation = Negation(word="nicht", english="not",
            ...                    type=NegationType.GENERAL,
            ...                    example="Ich bin nicht müde.")
            >>> strategy = negation.get_image_search_strategy(anthropic_service)
            >>> search_terms = strategy()  # Returns context-aware search terms
        """

        def generate_search_terms() -> str:
            """Execute search term generation strategy with negation context."""
            try:
                # Use domain expertise to build rich context for the service
                context = self._build_search_context()
                result = anthropic_service.generate_image_query(context)
                if result and result.strip():
                    return result.strip()
            except Exception:
                # Service failed, use fallback
                pass

            # Fallback to domain-specific handling
            return self._get_fallback_search_terms()

        return generate_search_terms

    def get_combined_audio_text(self) -> str:
        """Get combined text for German negation audio generation.

        Combines the negation word with its example sentence to provide proper
        pronunciation context for German language learners. This helps learners
        understand negation usage patterns and positioning rules.

        Returns:
            Formatted string: "{word}. {example}" for audio generation.

        Example:
            >>> negation = Negation(word="nicht", english="not",
            ...                    type=NegationType.GENERAL,
            ...                    example="Ich bin nicht müde.")
            >>> negation.get_combined_audio_text()
            'nicht. Ich bin nicht müde.'
        """
        return f"{self.word}. {self.example}"

    def _get_fallback_search_terms(self) -> str:
        """Get fallback search terms using negation concept mappings."""

        # Negation words are abstract concepts, so use enhanced search terms
        # Check for exact matches first, then partial matches (longer first)
        concept_mappings = [
            ("nobody", "empty person silhouette nobody"),
            ("nothing", "empty void blank nothing"),
            ("nowhere", "empty space void location"),
            ("neither", "choice rejection either"),
            ("never", "infinity crossed out never"),
            (
                "no/not a",
                "crossed out circle prohibition stop sign",
            ),  # Better search terms
            ("not", "prohibition stop sign red x"),
            ("no", "negative denial no symbol"),
        ]

        english_lower = self.english.lower()
        for key, enhanced_terms in concept_mappings:
            if key in english_lower:
                return enhanced_terms

        # For different negation types, add context
        type_mappings = {
            NegationType.GENERAL: f"{self.english} prohibition stop sign",
            NegationType.ARTICLE: f"{self.english} denial rejection symbol",
            NegationType.PRONOUN: f"{self.english} empty void absence",
            NegationType.TEMPORAL: f"{self.english} time crossed out never",
            NegationType.SPATIAL: f"{self.english} location empty void",
            NegationType.CORRELATIVE: f"{self.english} choice rejection neither",
            NegationType.INTENSIFIER: f"{self.english} emphasis prohibition strong",
        }
        return type_mappings.get(
            self.type, f"{self.english} negation prohibition symbol"
        )

    def _build_search_context(self) -> str:
        """Build rich context for image search using German negation expertise.

        Constructs visualization guidance based on German linguistic knowledge.
        Considers negation type, positioning rules, and provides type-specific
        strategies for representing abstract negation concepts visually.

        This method embodies the domain model's expertise about German negation
        and visualization challenges, providing rich context that services can
        use without needing to understand German syntactic rules.

        Returns:
            Formatted context string with:
            - Negation details (German word, English translation, type)
            - Type-specific visualization strategy and positioning context
            - Example usage demonstrating proper German syntax
            - Instructions for generating appropriate search terms

        Example:
            For NegationType.GENERAL ("nicht"):
                "Use prohibition symbols, crossed-out imagery, stop signs"
            For NegationType.PRONOUN ("niemand"):
                "Show emptiness, absence of people, void spaces"

        Note:
            This is a private method called by get_image_search_strategy() to
            contribute domain expertise to the search term generation process.
        """
        # Map negation types to visualization strategies
        type_strategies = {
            NegationType.GENERAL: (
                "Use prohibition symbols like stop signs, red X marks, or "
                "crossed-out imagery. Show actions or states being negated."
            ),
            NegationType.ARTICLE: (
                "Show absence or lack of objects. Use empty spaces, zero "
                "symbols, or 'no entry' signs with objects."
            ),
            NegationType.PRONOUN: (
                "Represent emptiness or void. Show silhouettes, empty chairs, "
                "or spaces where people/things should be but aren't."
            ),
            NegationType.TEMPORAL: (
                "Use time-related imagery with prohibition. Show clocks with "
                "X marks, calendars crossed out, or 'never' symbols."
            ),
            NegationType.SPATIAL: (
                "Show empty locations or 'nowhere' concepts. Use void spaces, "
                "maps with no destinations, or empty landscapes."
            ),
            NegationType.CORRELATIVE: (
                "Represent choice rejection. Show two options both being "
                "refused, either/or scenarios with both crossed out."
            ),
            NegationType.INTENSIFIER: (
                "Emphasize prohibition strongly. Use bold red symbols, "
                "multiple X marks, or intensified 'forbidden' imagery."
            ),
        }

        strategy = type_strategies.get(
            self.type,
            "Use general prohibition or negation symbols to represent this concept.",
        )

        return f"""
        German negation: {self.word} (English: {self.english})
        Type: {self.type.value} negation
        Example usage: {self.example}

        Challenge: Negation words are abstract concepts representing absence,
        prohibition, or denial. They need symbolic or metaphorical representation.

        Visual strategy: {strategy}

        Generate search terms that photographers would use to tag images showing
        prohibition, absence, or negation concepts.
        """
