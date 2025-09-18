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


@dataclass
class Article(MediaGenerationCapable):
    """German article domain model with linguistic expertise and media generation.

    Represents German articles (der, die, das, ein, eine, kein, keine) with their
    grammatical properties and usage patterns. This model contains German-specific
    logic for article processing including case declensions and gender patterns.

    This model implements MediaGenerationCapable protocol to contribute domain
    expertise for image and audio generation using article pattern visualization
    and natural German pronunciation.

    Attributes:
        artikel_typ: Type of article (bestimmt, unbestimmt, verneinend)
        geschlecht: Gender (maskulin, feminin, neutral, plural)
        nominativ: Nominative case form (der, die, das, ein, eine, kein, keine)
        akkusativ: Accusative case form
        dativ: Dative case form
        genitiv: Genitive case form
        beispiel_nom: Example sentence in nominative case
        beispiel_akk: Example sentence in accusative case
        beispiel_dat: Example sentence in dative case
        beispiel_gen: Example sentence in genitive case
    """

    artikel_typ: str
    geschlecht: str
    nominativ: str
    akkusativ: str
    dativ: str
    genitiv: str
    beispiel_nom: str
    beispiel_akk: str
    beispiel_dat: str
    beispiel_gen: str

    def __post_init__(self) -> None:
        """Validate the article data after initialization."""
        # Validate core required fields
        required_fields = [
            "artikel_typ",
            "geschlecht",
            "nominativ",
            "beispiel_nom",  # At minimum we need the nominative example
        ]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if not value or not isinstance(value, str) or not value.strip():
                raise ValueError(f"Required field '{field_name}' cannot be empty")

        # Validate artikel_typ
        valid_types = ["bestimmt", "unbestimmt", "verneinend"]
        if self.artikel_typ not in valid_types:
            raise ValueError(f"artikel_typ must be one of {valid_types}")

        # Validate geschlecht
        valid_genders = ["maskulin", "feminin", "neutral", "plural"]
        if self.geschlecht not in valid_genders:
            raise ValueError(f"geschlecht must be one of {valid_genders}")

    def get_combined_audio_text(self) -> str:
        """Generate combined text for audio pronunciation.

        Creates comprehensive audio content covering all cases and examples
        for complete article pattern learning.

        Returns:
            Combined German text suitable for audio generation
        """
        # Start with the article declension pattern
        audio_parts = [
            f"{self.artikel_typ} Artikel, {self.geschlecht}:",
            f"Nominativ: {self.nominativ}",
            f"Akkusativ: {self.akkusativ}",
            f"Dativ: {self.dativ}",
            f"Genitiv: {self.genitiv}",
        ]

        # Add the primary example
        if self.beispiel_nom:
            audio_parts.append(f"Beispiel: {self.beispiel_nom}")

        return ". ".join(audio_parts)

    def get_audio_segments(self) -> dict[str, str]:
        """Get all audio segments needed for article cards.

        Articles require comprehensive audio segments covering:
        - Main pattern audio with declension
        - Individual case examples
        - Pattern explanation

        Returns:
            Dictionary mapping audio field names to text content
        """
        audio_segments = {
            "word_audio": self.get_combined_audio_text(),
            "pattern_audio": (
                f"{self.nominativ}, {self.akkusativ}, {self.dativ}, {self.genitiv}"
            ),
        }

        # Add example audio segments for each case that has content
        if self.beispiel_nom:
            audio_segments["example_nom_audio"] = self.beispiel_nom
        if self.beispiel_akk:
            audio_segments["example_akk_audio"] = self.beispiel_akk
        if self.beispiel_dat:
            audio_segments["example_dat_audio"] = self.beispiel_dat
        if self.beispiel_gen:
            audio_segments["example_gen_audio"] = self.beispiel_gen

        return audio_segments

    def get_primary_word(self) -> str:
        """Get the primary word for filename generation and identification.

        Returns a unique identifier combining gender and article type for articles.

        Returns:
            Combination of gender and article type (e.g., "maskulin_definit")
        """
        # Use gender and type for unique filename, consistent with original logic
        return f"{self.geschlecht}_{self.artikel_typ}"

    def get_image_search_strategy(
        self, ai_service: ImageQueryGenerationProtocol
    ) -> Callable[[], str]:
        """Get strategy for generating image search terms for German article learning.

        Articles require visual context that demonstrates grammatical concepts rather
        than specific objects. This creates search terms for images that support
        German case learning and gender recognition.

        Args:
            ai_service: Service for generating context-aware search terms

        Returns:
            Callable that generates appropriate image search terms for article concepts

        Raises:
            MediaGenerationError: When AI service returns empty result or fails.
        """

        def generate_search_terms() -> str:
            """Generate image search terms for German article concepts.

            Raises:
                MediaGenerationError: When AI service fails or returns empty result.
            """
            logger.debug(
                f"Generating search terms for article: "
                f"'{self.nominativ}' ({self.geschlecht})"
            )

            try:
                # Build context emphasizing grammatical learning
                context_parts = [
                    "German article learning visualization",
                    f"Gender: {self.geschlecht} ({self.nominativ})",
                    f"Article type: {self.artikel_typ}",
                    "Focus on educational context for German language learning",
                ]

                # Add example context if available
                if self.beispiel_nom:
                    context_parts.append(f"Example context: {self.beispiel_nom}")

                context = ". ".join(context_parts)

                # Request educational/conceptual imagery suitable for language learning
                search_terms = ai_service.generate_image_query(context)

                if search_terms and search_terms.strip():
                    logger.debug(f"Generated search terms: {search_terms}")
                    return search_terms.strip()

                # AI service returned empty result - this is a service failure
                raise MediaGenerationError(
                    f"AI service returned empty image search query for article "
                    f"'{self.nominativ}'"
                )
            except MediaGenerationError:
                # Re-raise our own exceptions
                raise
            except Exception as e:
                # Convert any other exception to MediaGenerationError
                raise MediaGenerationError(
                    f"Failed to generate image search for article "
                    f"'{self.nominativ}': {e}"
                ) from e

        return generate_search_terms

    @staticmethod
    def extract_clean_text_from_cloze(cloze_text: str) -> str:
        """Extract clean German text from cloze markup.

        This method contains German-specific logic for processing cloze deletions
        in article learning contexts.

        Args:
            cloze_text: Text with cloze markup like "{{c1::Der}} Mann ist hier"

        Returns:
            Clean German text: "Der Mann ist hier"
        """
        # Remove cloze markup using regex for robust parsing - German linguistic logic
        import re

        # Pattern matches {{c1::text}}, {{c2::text}}, etc. and captures just the text
        cloze_pattern = r"\{\{c\d+::(.*?)\}\}"
        clean_text = re.sub(cloze_pattern, r"\1", cloze_text)
        return clean_text.strip()
