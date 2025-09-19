from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from langlearn.core.protocols.domain_model_protocol import LanguageDomainModel
from langlearn.core.protocols.media_generation_protocol import MediaGenerationCapable
from langlearn.exceptions import MediaGenerationError

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.core.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )

logger = logging.getLogger(__name__)

"""German Adjective Domain Model.

This module contains the domain model for German adjectives with specialized logic for
German language learning applications. The module is responsible for:

CORE RESPONSIBILITIES:
    - Modeling German adjective data (word, English translation, comparative,
      superlative, example)
    - Implementing MediaGenerationCapable protocol for media enrichment
    - Providing German-specific linguistic validation and comparison form patterns
    - Contributing domain expertise for image search term generation
    - Supporting audio generation with proper declension form pronunciation

DESIGN PRINCIPLES:
    - Domain model is SMART: Contains German adjective expertise and linguistic
      knowledge
    - Services are DUMB: External services receive rich context, no domain logic
    - Single Responsibility: Adjective logic stays in Adjective model, not in services
    - Dependency Injection: Protocol-based design for loose coupling

GERMAN LINGUISTIC FEATURES:
    - Comparison forms: positive, comparative, superlative (gut/besser/am besten)
    - Irregular comparison patterns and umlaut changes (alt/älter/am ältesten)
    - Concept-based visualization strategies for abstract adjective qualities
    - Context-aware search term generation using linguistic domain knowledge
    - Audio generation combining all comparison forms

INTEGRATION POINTS:
    - MediaGenerationCapable protocol for image/audio media enrichment
    - AnthropicServiceProtocol for AI-powered search term generation
    - MediaEnricher service for coordinated media asset generation

Usage:
    Basic usage:
        >>> adjective = Adjective(
        ...     word="schön",
        ...     english="beautiful",
        ...     comparative="schöner",
        ...     superlative="am schönsten",
        ...     example="Das Haus ist sehr schön."
        ... )

    Media generation with dependency injection:
        >>> strategy = adjective.get_image_search_strategy(anthropic_service)
        >>> search_terms = strategy()  # Returns context-aware search terms
        >>> audio_text = adjective.get_combined_audio_text()  # All forms
"""


@dataclass
class Adjective(LanguageDomainModel, MediaGenerationCapable):
    """German adjective domain model with linguistic expertise and media generation.

    Represents a German adjective with its properties, German linguistic knowledge,
    and specialized logic for media enrichment. German adjectives are characterized
    by their comparison system (positive, comparative, superlative), irregular
    patterns, and complex declension rules.

    This model implements MediaGenerationCapable protocol to contribute domain
    expertise for image and audio generation, using concept-based strategies
    for abstract adjective quality visualization.

    Attributes:
        word: The German adjective (e.g., "schön", "gut")
        english: English translation (e.g., "beautiful", "good")
        example: German example sentence demonstrating usage
        comparative: Comparative form (e.g., "schöner", "besser")
        superlative: Superlative form (e.g., "am schönsten", "am besten")

    Note:
        This model follows the design principle that domain models are SMART
        (contain expertise) while services are DUMB (execute instructions).
    """

    word: str
    english: str
    example: str
    comparative: str = field(default="")
    superlative: str = field(default="")

    def __post_init__(self) -> None:
        """Validate the adjective data after initialization."""
        # Validate core required fields - 'comparative' and 'superlative' can be empty
        required_fields = ["word", "english", "example"]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Required field '{field_name}' cannot be empty")

    def get_combined_audio_text(self) -> str:
        """Get combined text for German adjective audio generation.

        Combines the adjective with its comparative and superlative forms
        to provide proper pronunciation context for German language learners.
        This helps learners understand the comparison system and irregular patterns.

        Returns:
            Formatted string: "{word}, {comparative}, {superlative}" for audio.

        Example:
            >>> adjective = Adjective(word="schön", english="beautiful",
            ...                      comparative="schöner", superlative="am schönsten",
            ...                      example="Das ist schön.")
            >>> adjective.get_combined_audio_text()
            'schön, schöner, am schönsten'
        """
        parts = [self.word]
        if self.comparative:
            parts.append(self.comparative)
        if self.superlative:
            parts.append(self.superlative)
        return ", ".join(parts)

    def get_audio_segments(self) -> dict[str, str]:
        """Get all audio segments needed for adjective cards.

        Adjectives require two audio segments:
        - word_audio: The adjective with comparative and superlative forms
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

        Returns the German adjective that identifies this domain model.

        Returns:
            The German adjective (e.g., "schön", "gut")
        """
        return self.word

    def validate_comparative(self) -> bool:
        """Validate that the comparative form follows German grammar rules.

        Returns:
            bool: True if the comparative form is valid
        """
        # Most German comparatives add -er to the base form
        # Some have umlaut changes (e.g., alt -> älter)
        # A few are irregular (e.g., gut -> besser)

        irregular_comparatives = {
            "gut": "besser",
            "viel": "mehr",
            "gern": "lieber",
            "hoch": "höher",
            "nah": "näher",
        }

        # Check for irregular comparatives
        if self.word in irregular_comparatives:
            return self.comparative == irregular_comparatives[self.word]

        # Check for regular pattern (-er ending)
        if not self.comparative.endswith("er"):
            return False

        # Check that the comparative starts with the base adjective
        # (allowing for possible umlaut changes)
        base = self.word.rstrip("e")  # Remove trailing 'e' if present
        comp_base = self.comparative[:-2]  # Remove 'er' ending

        # Check if bases match, accounting for umlaut changes
        umlaut_pairs = [("a", "ä"), ("o", "ö"), ("u", "ü")]
        if base == comp_base:
            return True

        # Check for umlaut changes
        for normal, umlaut in umlaut_pairs:
            if base.replace(normal, umlaut) == comp_base:
                return True

        return False

    def validate_superlative(self) -> bool:
        """Validate that the superlative form follows German grammar rules.

        Returns:
            bool: True if the superlative form is valid
        """
        if not self.superlative:
            return True  # Optional field

        # Most German superlatives are formed with "am" + adjective + "sten"
        # Some add -esten instead of -sten
        # Some have umlaut changes
        # Some are irregular (e.g., gut -> am besten)

        irregular_superlatives = {
            "gut": "am besten",
            "viel": "am meisten",
            "gern": "am liebsten",
            "hoch": "am höchsten",
            "nah": "am nächsten",
        }

        # Check for irregular superlatives
        if self.word in irregular_superlatives:
            return self.superlative == irregular_superlatives[self.word]

        # Check for regular pattern
        if not self.superlative.startswith("am "):
            return False

        # Check for -sten or -esten ending
        if not (self.superlative.endswith("sten")):
            return False

        # Get the base form from the superlative, handling both -sten and -esten cases
        superlative_base = self.superlative[3:-4]  # Remove "am " and "sten"
        if superlative_base.endswith("e"):  # Handle -esten case
            superlative_base = superlative_base[:-1]

        base = self.word.rstrip("e")  # Remove trailing 'e' if present

        # Check if bases match, accounting for umlaut changes
        umlaut_pairs = [("a", "ä"), ("o", "ö"), ("u", "ü")]
        if base == superlative_base:
            return True

        # Check for umlaut changes
        for normal, umlaut in umlaut_pairs:
            if base.replace(normal, umlaut) == superlative_base:
                return True

        return False

    def get_image_search_strategy(
        self, anthropic_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get strategy for generating image search terms with domain expertise.

        Creates a callable that uses this adjective's domain knowledge to generate
        context-aware image search terms. The adjective contributes German linguistic
        expertise (comparison forms, concept mappings) while the anthropic service
        executes the actual AI processing.

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
            >>> adjective = Adjective(word="schön", english="beautiful",
            ...                      comparative="schöner", superlative="am schönsten",
            ...                      example="Das ist schön.")
            >>> strategy = adjective.get_image_search_strategy(anthropic_service)
            >>> search_terms = strategy()  # Returns context-aware search terms
        """

        def generate_search_terms() -> str:
            """Execute search term generation strategy with adjective context.

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
                    f"AI service returned empty image search query for adjective "
                    f"'{self.word}'"
                )
            except MediaGenerationError:
                # Re-raise our own exceptions
                raise
            except Exception as e:
                # Convert any other exception to MediaGenerationError
                raise MediaGenerationError(
                    f"Failed to generate image search for adjective '{self.word}': {e}"
                ) from e

        return generate_search_terms

    def _build_search_context(self) -> str:
        """Build rich context for image search using German adjective expertise.

        Constructs visualization guidance based on German linguistic knowledge.
        Considers comparison forms, concept abstraction levels, and provides
        type-specific strategies for representing adjective qualities visually.

        This method embodies the domain model's expertise about German adjectives
        and their visualization challenges, providing rich context that services can
        use without needing to understand German linguistic patterns.

        Returns:
            Formatted context string with:
            - Adjective details (German word, English translation, comparison forms)
            - Abstract quality visualization strategy
            - Example usage context
            - Instructions for generating appropriate search terms

        Example:
            For concrete adjective "rot" (red):
                "Focus on color representation, use direct visual examples"
            For abstract adjective "ehrlich" (honest):
                "Use symbolic imagery, behavioral representations"

        Note:
            This is a private method called by get_image_search_strategy() to
            contribute domain expertise to the search term generation process.
        """
        # Determine if adjective describes concrete or abstract qualities
        concrete_adjectives = {
            "red",
            "blue",
            "green",
            "yellow",
            "black",
            "white",
            "brown",
            "gray",
            "big",
            "small",
            "tall",
            "short",
            "long",
            "wide",
            "narrow",
            "hot",
            "cold",
            "warm",
            "cool",
            "wet",
            "dry",
            "round",
            "square",
            "flat",
            "curved",
            "straight",
            "soft",
            "hard",
            "smooth",
            "rough",
            "sharp",
            "blunt",
        }

        english_lower = self.english.lower().strip()
        is_concrete = any(concrete in english_lower for concrete in concrete_adjectives)

        if is_concrete:
            visual_strategy = (
                "Focus on direct visual representation of the quality. "
                "Show objects, people, or scenes that clearly demonstrate this "
                "adjective through obvious visual characteristics."
            )
        else:
            visual_strategy = (
                "Use symbolic imagery, behavioral representations, or metaphorical "
                "scenes. Abstract qualities need creative interpretation through "
                "actions, expressions, symbols, or representative scenarios."
            )

        # Build comparison context if available
        comparison_info = f"Forms: {self.word}"
        if self.comparative:
            comparison_info += f" → {self.comparative}"
        if self.superlative:
            comparison_info += f" → {self.superlative}"

        return f"""
        German adjective: {self.word} (English: {self.english})
        Comparison: {comparison_info}
        Example usage: {self.example}
        Quality type: {"Concrete/Physical" if is_concrete else "Abstract/Conceptual"}

        Challenge: Generate search terms for images representing this adjective quality.
        Visual strategy: {visual_strategy}

        Generate search terms that photographers would use to tag images showing
        this quality or characteristic.
        """
