from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from langlearn.core.protocols.media_generation_protocol import MediaGenerationCapable
from langlearn.exceptions import MediaGenerationError

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.core.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )

logger = logging.getLogger(__name__)


"""German Phrase Domain Model.

This module contains the domain model for German phrases with specialized logic for
German language learning applications. The module is responsible for:

CORE RESPONSIBILITIES:
    - Modeling German phrase data (phrase, English, context, related phrases)
    - Implementing MediaGenerationCapable protocol for media enrichment
    - Providing German-specific linguistic validation and phrase categorization
    - Contributing domain expertise for image search term generation
    - Supporting audio generation with proper German phrase pronunciation

DESIGN PRINCIPLES:
    - Domain model is SMART: Contains German phrase expertise and linguistic knowledge
    - Services are DUMB: External services receive rich context, no domain logic
    - Single Responsibility: Phrase logic stays in Phrase model, not in services
    - Dependency Injection: Protocol-based design for loose coupling

GERMAN LINGUISTIC FEATURES:
    - Phrase categorization system (greetings, farewells, formal, informal, general)
    - Context-aware usage patterns and social register
    - Situational appropriateness guidance for German conversation
    - Context-driven search term generation using communicative scenarios
    - Audio generation with natural German phrase intonation

INTEGRATION POINTS:
    - MediaGenerationCapable protocol for image/audio media enrichment
    - AnthropicServiceProtocol for AI-powered search term generation
    - MediaEnricher service for coordinated media asset generation

Usage:
    Basic usage:
        >>> phrase = Phrase(
        ...     phrase="Guten Morgen!",
        ...     english="Good morning!",
        ...     context="formal greeting used until about 10 AM",
        ...     related="Guten Tag, Guten Abend"
        ... )

    Media generation with dependency injection:
        >>> strategy = phrase.get_image_search_strategy(anthropic_service)
        >>> search_terms = strategy()  # Returns context-aware search terms
        >>> audio_text = phrase.get_combined_audio_text()  # German phrase audio
"""


@dataclass
class Phrase(MediaGenerationCapable):
    """German phrase domain model with linguistic expertise and media generation.

    Represents a German phrase with its properties, German linguistic knowledge,
    and specialized logic for media enrichment. German phrases are characterized
    by their communicative function, social register (formal/informal), and
    situational appropriateness in German conversation.

    This model implements MediaGenerationCapable protocol to contribute domain
    expertise for image and audio generation, using situational strategies
    for phrase concept visualization and natural German pronunciation.

    Attributes:
        phrase: The German phrase (e.g., "Guten Morgen!", "Wie geht's?")
        english: English translation (e.g., "Good morning!", "How are you?")
        context: Context or usage description explaining when/how to use
        related: Related phrases or expressions with similar usage

    Note:
        This model follows the design principle that domain models are SMART
        (contain expertise) while services are DUMB (execute instructions).
    """

    phrase: str
    english: str
    context: str
    related: str

    def __post_init__(self) -> None:
        """Validate the phrase data after initialization."""
        # Validate core required fields
        required_fields = ["phrase", "english", "context", "related"]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Required field '{field_name}' cannot be empty")

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get strategy for generating image search terms with domain expertise.

        Creates a callable that uses this phrase's domain knowledge to generate
        context-aware image search terms. The phrase contributes German linguistic
        expertise (communicative function, social register, situational context) while
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
            >>> phrase = Phrase(phrase="Guten Morgen!", english="Good morning!",
            ...                context="formal greeting", related="Guten Tag")
            >>> strategy = phrase.get_image_search_strategy(anthropic_service)
            >>> search_terms = strategy()  # Returns context-aware search terms
        """

        def generate_search_terms() -> str:
            """Execute search term generation strategy with phrase context.

            Raises:
                MediaGenerationError: When AI service fails or returns empty result.
            """
            logger.debug(f"Generating search terms for phrase: '{self.phrase}'")

            try:
                # Use domain expertise to build rich context for the service
                context = self._build_search_context()
                result = anthropic_service.generate_image_query(context)
                if result and result.strip():
                    ai_generated_terms = result.strip()
                    logger.info(f"AI terms for '{self.phrase}': '{ai_generated_terms}'")
                    return ai_generated_terms

                # AI service returned empty result - this is a service failure
                raise MediaGenerationError(
                    f"AI service returned empty image search query for phrase "
                    f"'{self.phrase}'"
                )
            except MediaGenerationError:
                # Re-raise our own exceptions
                raise
            except Exception as e:
                # Convert any other exception to MediaGenerationError
                raise MediaGenerationError(
                    f"Failed to generate image search for phrase '{self.phrase}': {e}"
                ) from e

        return generate_search_terms

    def get_combined_audio_text(self) -> str:
        """Get combined text for German phrase audio generation.

        Returns:
            The German phrase for audio generation with natural pronunciation.
            For phrases, we use the phrase directly as it represents a complete
            communicative unit.

        Example:
            >>> phrase = Phrase(phrase="Guten Morgen!", english="Good morning!",
            ...                context="formal greeting", related="Guten Tag")
            >>> phrase.get_combined_audio_text()
            'Guten Morgen!'
        """
        return self.phrase

    def get_audio_segments(self) -> dict[str, str]:
        """Get all audio segments needed for phrase cards.

        Phrases require phrase_audio instead of word_audio since they represent
        complete communicative units rather than individual words.

        Returns:
            Dictionary mapping audio field names to text content
        """
        return {
            "phrase_audio": self.phrase,
        }

    def get_primary_word(self) -> str:
        """Get the primary word for filename generation and identification.

        Returns the first word of the German phrase for identification.

        Returns:
            The first word of the German phrase (e.g., "Guten" from "Guten Morgen")
        """
        # Use first word of phrase for filename, consistent with original logic
        return self.phrase.split()[0] if self.phrase else "phrase"

    def _build_search_context(self) -> str:
        """Build rich context for image search using German phrase expertise.

        Constructs visualization guidance based on German linguistic knowledge.
        Considers phrase category (greeting, farewell, formal, etc.), social register,
        and communicative function to provide situational strategies for representing
        phrase concepts visually.

        This method embodies the domain model's expertise about German phrases and
        their visualization challenges, providing rich context that services can
        use without needing to understand German communicative patterns.

        Returns:
            Formatted context string with:
            - Phrase details (German phrase, English translation, category)
            - Situational visualization strategy
            - Context and usage information
            - Instructions for generating appropriate search terms

        Example:
            For greeting "Guten Morgen!":
                "Focus on morning greeting scenario, show people meeting in morning"
            For farewell "Auf Wiedersehen!":
                "Focus on parting scenario, show people saying goodbye"

        Note:
            This is a private method called by get_image_search_strategy() to
            contribute domain expertise to the search term generation process.
        """
        # Determine visualization strategy based on phrase category
        category = self.get_phrase_category()
        situational_strategy = self._get_situational_visualization_strategy(category)

        return f"""
        German phrase: {self.phrase}
        English: {self.english}
        Category: {category}
        Context: {self.context}
        Related phrases: {self.related}

        Challenge: Generate search terms for images representing this phrase situation.
        Visual strategy: {situational_strategy}

        Generate search terms that photographers would use to tag images of
        people in situations where this phrase would be used.
        """

    def _get_situational_visualization_strategy(self, category: str) -> str:
        """Get situational visualization strategy for phrase categories.

        Args:
            category: The phrase category (greeting, farewell, formal, etc.)

        Returns:
            Strategic guidance for visualizing phrase situations based on German
            communicative context and social appropriateness.
        """
        category_strategies = {
            "greeting": (
                "Focus on meeting and greeting scenarios. Show people encountering "
                "each other for the first time in the day, waving, shaking hands, "
                "or acknowledging each other in appropriate social contexts."
            ),
            "farewell": (
                "Focus on parting and departure scenarios. Show people saying goodbye, "
                "waving farewell, leaving situations, or concluding interactions "
                "with appropriate emotional tone."
            ),
            "formal": (
                "Focus on formal or professional contexts. Show business settings, "
                "official interactions, respectful exchanges, or situations requiring "
                "polite and proper German communication."
            ),
            "informal": (
                "Focus on casual, friendly interactions. Show relaxed social settings, "
                "friends talking, informal gatherings, or everyday conversation "
                "scenarios with comfortable, approachable atmosphere."
            ),
            "general": (
                "Focus on the communicative situation implied by the phrase. Show "
                "people engaged in conversation or interaction that would naturally "
                "lead to using this expression in German."
            ),
        }

        return category_strategies.get(category, category_strategies["general"])

    def is_greeting(self) -> bool:
        """Check if this phrase is a greeting.

        Returns:
            True if phrase appears to be a greeting
        """
        greeting_indicators = ["guten", "hallo", "hi", "greeting"]
        phrase_lower = self.phrase.lower()
        context_lower = self.context.lower()

        return any(
            indicator in phrase_lower or indicator in context_lower
            for indicator in greeting_indicators
        )

    def is_farewell(self) -> bool:
        """Check if this phrase is a farewell expression.

        Returns:
            True if phrase appears to be a farewell
        """
        farewell_indicators = ["auf wiedersehen", "tschüss", "bis", "goodbye", "bye"]
        phrase_lower = self.phrase.lower()
        context_lower = self.context.lower()

        return any(
            indicator in phrase_lower or indicator in context_lower
            for indicator in farewell_indicators
        )

    def get_phrase_category(self) -> str:
        """Categorize the phrase based on its content and context.

        Returns:
            Category name for the phrase
        """
        if self.is_greeting():
            return "greeting"
        elif self.is_farewell():
            return "farewell"
        elif any(word in self.context.lower() for word in ["polite", "formal"]):
            return "formal"
        elif any(word in self.context.lower() for word in ["informal", "casual"]):
            return "informal"
        else:
            return "general"
