"""Model for German adverbs."""

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.protocols.anthropic_protocol import AnthropicServiceProtocol


class AdverbType(str, Enum):
    """Types of German adverbs."""

    LOCATION = "Ortsadverb"  # 8 entries
    TIME = "Zeitadverb"  # 8 entries
    FREQUENCY = "Häufigkeitsadverb"  # 6 entries
    MANNER = "Modaladverb"  # 9 entries
    INTENSITY = "Gradadverb"  # 5 entries
    ADDITION = "Modaladverb"  # 1 entry - auch
    LIMITATION = "Modaladverb"  # 1 entry - nur
    ATTITUDE = "Kommentaradverb"  # 2 entries
    PROBABILITY = "Modaladverb"  # 2 entries - vielleicht, wahrscheinlich


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


class Adverb(BaseModel):
    """Model representing a German adverb with its properties and business logic.

    German adverbs are words that modify verbs, adjectives, or other adverbs.
    They provide information about time, place, manner, degree, etc.
    Unlike adjectives, they do not change their form.

    Implements MediaGenerationCapable protocol methods for media enrichment support.
    """

    word: str = Field(..., description="The German adverb")
    english: str = Field(..., description="English translation")
    type: AdverbType = Field(..., description="Type of adverb")
    example: str = Field(..., description="Example sentence using the adverb")

    def get_image_search_strategy(
        self, anthropic_service: "AnthropicServiceProtocol"
    ) -> "Callable[[], str]":
        """Get a strategy for generating search terms with dependency injection.

        The Adverb uses its domain knowledge to construct context-aware requests,
        emphasizing the challenge of visualizing abstract adverbial concepts.

        Args:
            anthropic_service: Service for context-aware search term generation.

        Returns:
            A callable that generates image search terms when invoked
        """

        def generate_search_terms() -> str:
            """Execute a search term generation strategy with adverb
            context."""
            try:
                result = anthropic_service.generate_pexels_query(self)
                if result and result.strip():
                    return result.strip()
            except Exception:
                # Service failed, use fallback
                pass

            # Simple fallback: use the example sentence
            return self.example

        return generate_search_terms

    def get_combined_audio_text(self) -> str:
        """Get the text to be used for audio generation.

        For German adverbs, this includes the adverb and its example sentence
        to provide pronunciation context.

        Returns:
            Text string for audio generation
        """
        return f"{self.word}. {self.example}"

    def get_image_search_terms(self) -> str:
        """Legacy method for backward compatibility - executes strategy immediately.

        Note: This method maintains compatibility but should be replaced with
        get_image_search_strategy() for better performance. Returns simple fallback.
        """
        # Simple fallback: use the raw German word directly
        return self.word

    def _build_search_context(self) -> str:
        """Build adverb-specific context for image search term generation.

        Uses domain knowledge about German adverbs and their visualization challenges
        to provide guidance to the Anthropic service.

        Returns:
            Context string with part-of-speech specific guidance
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
