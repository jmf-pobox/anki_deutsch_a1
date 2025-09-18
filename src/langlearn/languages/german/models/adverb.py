from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from langlearn.core.protocols.media_generation_protocol import MediaGenerationCapable
from langlearn.exceptions import MediaGenerationError

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.core.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )

logger = logging.getLogger(__name__)

"""German Adverb Domain Model.

This module contains the domain model for German adverbs with specialized logic for
German language learning applications. The module is responsible for:

CORE RESPONSIBILITIES:
    - Modeling German adverb data (word, English translation, type, example)
    - Implementing MediaGenerationCapable protocol for media enrichment
    - Providing German-specific linguistic validation and type classification
    - Contributing domain expertise for image search term generation
    - Supporting audio generation with proper pronunciation context

DESIGN PRINCIPLES:
    - Domain model is SMART: Contains German adverb expertise and linguistic knowledge
    - Services are DUMB: External services receive rich context, no domain logic
    - Single Responsibility: Adverb logic stays in Adverb model, not in services
    - Dependency Injection: Protocol-based design for loose coupling

GERMAN LINGUISTIC FEATURES:
    - 9 adverb types with German classifications (Ortsadverb, Zeitadverb, etc.)
    - Type-specific visualization strategies for abstract adverbial concepts
    - Context-aware search term generation using linguistic domain knowledge
    - Support for both German and English type naming for compatibility

INTEGRATION POINTS:
    - MediaGenerationCapable protocol for image/audio media enrichment
    - AnthropicServiceProtocol for AI-powered search term generation
    - MediaEnricher service for coordinated media asset generation

Usage:
    Basic usage:
        >>> adverb = Adverb(
        ...     word="heute",
        ...     english="today",
        ...     type=AdverbType.TIME,
        ...     example="Heute ist schönes Wetter."
        ... )

    Media generation with dependency injection:
        >>> strategy = adverb.get_image_search_strategy(anthropic_service)
        >>> search_terms = strategy()  # Returns context-aware search terms
        >>> audio_text = adverb.get_combined_audio_text()  # Combined text
"""


class AdverbType(str, Enum):
    """German adverb type classifications.

    Represents the nine types of German adverbs with their German linguistic
    classifications. Each type has specific visualization strategies for
    image search term generation.

    Attributes:
        LOCATION: Ortsadverb - spatial adverbs (hier, dort, etc.)
        TIME: Zeitadverb - temporal adverbs (heute, morgen, etc.)
        FREQUENCY: Häufigkeitsadverb - frequency adverbs (oft, manchmal, etc.)
        MANNER: Modaladverb - manner adverbs (schnell, langsam, etc.)
        INTENSITY: Gradadverb - degree adverbs (sehr, ziemlich, etc.)
        ADDITION: Modaladverb - additive adverbs (auch)
        LIMITATION: Modaladverb - limiting adverbs (nur)
        ATTITUDE: Kommentaradverb - attitudinal adverbs (leider, hoffentlich)
        PROBABILITY: Modaladverb - probability adverbs (vielleicht, wahrscheinlich)
    """

    LOCATION = "Ortsadverb"  # 8 entries
    TIME = "Zeitadverb"  # 8 entries
    FREQUENCY = "Häufigkeitsadverb"  # 6 entries
    MANNER = "Modaladverb"  # 9 entries
    INTENSITY = "Gradadverb"  # 5 entries
    ADDITION = "Modaladverb (Addition)"  # 1 entry - auch
    LIMITATION = "Modaladverb (Limitation)"  # 1 entry - nur
    ATTITUDE = "Kommentaradverb"  # 2 entries
    PROBABILITY = "Modaladverb (Probability)"  # 2 entries - vielleicht, wahrscheinlich


GERMAN_ADVERB_TYPES = [adverb_type.value for adverb_type in AdverbType]

GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP = {
    **{adverb_type.value: adverb_type for adverb_type in AdverbType},
    # Additional German variants for broader recognition
    "Lokaladverb": AdverbType.LOCATION,  # alternative for Ortsadverb
    "Temporaladverb": AdverbType.TIME,  # alternative for Zeitadverb
    "Artadverb": AdverbType.MANNER,  # alternative for Modaladverb
    "Kausaladverb": AdverbType.MANNER,  # causal adverbs map to manner
    # English types for backward compatibility
    "time": AdverbType.TIME,
    "place": AdverbType.LOCATION,
    "location": AdverbType.LOCATION,
    "manner": AdverbType.MANNER,
    "intensity": AdverbType.INTENSITY,
}


@dataclass
class Adverb(MediaGenerationCapable):
    """German adverb domain model with linguistic expertise and media generation.

    Represents a German adverb with its properties, German linguistic knowledge,
    and specialized logic for media enrichment. German adverbs are invariant words
    that modify verbs, adjectives, or other adverbs, providing information about
    time, place, manner, degree, etc.

    This model implements MediaGenerationCapable protocol to contribute domain
    expertise for image and audio generation, using type-specific strategies
    for abstract adverbial concept visualization.

    Attributes:
        word: The German adverb (e.g., "heute", "schnell")
        english: English translation (e.g., "today", "quickly")
        type: AdverbType classification (TIME, LOCATION, MANNER, etc.)
        example: German example sentence demonstrating usage

    Note:
        This model follows the design principle that domain models are SMART
        (contain expertise) while services are DUMB (execute instructions).
    """

    word: str
    english: str
    type: AdverbType
    example: str

    def __post_init__(self) -> None:
        """Validate the adverb data after initialization."""
        # Validate core required fields
        required_fields = ["word", "english", "example"]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Required field '{field_name}' cannot be empty")

        # Validate type is an AdverbType enum
        if not isinstance(self.type, AdverbType):
            raise ValueError(f"Type must be an AdverbType, got {type(self.type)}")

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get strategy for generating image search terms with domain expertise.

        Creates a callable that uses this adverb's domain knowledge to generate
        context-aware image search terms. The adverb contributes type-specific
        visualization strategies (e.g., TIME adverbs need temporal symbols) while
        the anthropic service executes the actual AI processing.

        Design: Domain model is SMART (provides rich context), service is DUMB
        (processes whatever context it receives).

        Args:
            anthropic_service: Service implementing ImageQueryGenerationProtocol for
                AI-powered search term generation.

        Returns:
            Callable that when invoked returns image search terms as string.

        Raises:
            MediaGenerationError: When AI service returns empty result or fails.

        Example:
            >>> adverb = Adverb(word="heute", english="today", type=AdverbType.TIME,
            ...                example="Heute regnet es.")
            >>> strategy = adverb.get_image_search_strategy(anthropic_service)
            >>> search_terms = strategy()  # Returns context-aware search terms
        """

        def generate_search_terms() -> str:
            """Execute search term generation strategy with adverb context.

            Raises:
                MediaGenerationError: When AI service fails or returns empty result.
            """
            try:
                # Use domain expertise to build rich context for the service
                context = self._build_search_context()
                result = anthropic_service.generate_image_query(context)
                if result and result.strip():
                    return result.strip()

                # AI service returned empty result - this is a service failure
                raise MediaGenerationError(
                    f"AI service returned empty image search query for adverb "
                    f"'{self.word}'"
                )
            except MediaGenerationError:
                # Re-raise our own exceptions
                raise
            except Exception as e:
                # Convert any other exception to MediaGenerationError
                raise MediaGenerationError(
                    f"Failed to generate image search for adverb '{self.word}': {e}"
                ) from e

        return generate_search_terms

    def get_combined_audio_text(self) -> str:
        """Get combined text for German adverb audio generation.

        Combines the adverb word with its example sentence to provide proper
        pronunciation context for German language learners. The format allows
        learners to hear both the isolated word and its usage in context.

        Returns:
            Formatted string: "{word}. {example}" for audio generation.

        Example:
            >>> adverb = Adverb(word="schnell", english="quickly",
            ...                type=AdverbType.MANNER,
            ...                example="Er läuft schnell.")
            >>> adverb.get_combined_audio_text()
            'schnell. Er läuft schnell.'
        """
        return f"{self.word}. {self.example}"

    def get_audio_segments(self) -> dict[str, str]:
        """Get all audio segments needed for adverb cards.

        Adverbs require two audio segments:
        - word_audio: The adverb word and example sentence
        - example_audio: The example sentence demonstrating usage

        Returns:
            Dictionary mapping audio field names to text content
        """
        return {
            "word_audio": self.get_combined_audio_text(),
            "example_audio": self.example,
        }

    def get_primary_word(self) -> str:
        """Get the primary word for filename generation and identification.

        Returns the German adverb that identifies this domain model.

        Returns:
            The German adverb (e.g., "heute", "schnell")
        """
        return self.word

    def _build_search_context(self) -> str:
        """Build rich context for image search using German adverb expertise.

        Constructs type-specific visualization guidance based on German linguistic
        knowledge. Each adverb type (TIME, LOCATION, MANNER, etc.) has specialized
        strategies for representing abstract adverbial concepts visually.

        This method embodies the domain model's expertise about German adverbs and
        their visualization challenges, providing rich context that services can
        use without needing to understand German linguistic classifications.

        Returns:
            Formatted context string with:
            - Adverb details (German word, English translation, type)
            - Type-specific visualization strategy
            - Instructions for generating appropriate search terms

        Example:
            For AdverbType.TIME:
                "Use temporal symbols like clocks, calendars, or sequential imagery"
            For AdverbType.LOCATION:
                "Consider spatial relationships, directional arrows, contexts"

        Note:
            This is a private method called by get_image_search_strategy() to
            contribute domain expertise to the search term generation process.
        """
        type_guidance = {
            AdverbType.LOCATION: (
                "Consider spatial relationships, directional arrows, "
                "or environmental contexts"
            ),
            AdverbType.TIME: (
                "Use temporal symbols like clocks, calendars, or sequential imagery"
            ),
            AdverbType.FREQUENCY: (
                "Show repetition patterns, cycles, or counting symbols"
            ),
            AdverbType.MANNER: (
                "Focus on how actions are performed, style, or method indicators"
            ),
            AdverbType.INTENSITY: (
                "Use visual emphasis, gradients, or scale representations"
            ),
            AdverbType.ADDITION: "Show addition, plus symbols, or accumulation",
            AdverbType.LIMITATION: (
                "Use restriction symbols, boundaries, or exclusion imagery"
            ),
            AdverbType.ATTITUDE: (
                "Express emotional tone or perspective through "
                "facial expressions or mood"
            ),
            AdverbType.PROBABILITY: (
                "Show uncertainty, question marks, or probability indicators"
            ),
        }

        guidance = type_guidance.get(self.type, "Use symbolic or conceptual imagery")

        return f"""
        German adverb: {self.word} (English: {self.english})
        Type: {self.type.value} ({self.type.name})
        Example usage: {self.example}

        Challenge: Adverbs are abstract concepts that modify actions or qualities.
        Visual strategy: {guidance}

        Generate search terms that can find images representing this concept visually.
        """
