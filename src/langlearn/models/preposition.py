"""German Preposition Domain Model."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from langlearn.protocols.media_generation_protocol import MediaGenerationCapable

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.protocols.image_query_generation_protocol import (
        ImageQueryGenerationProtocol,
    )


@dataclass
class Preposition(MediaGenerationCapable):
    """German preposition domain model with linguistic expertise and media generation.

    Represents a German preposition with its properties, German linguistic knowledge,
    and specialized logic for media enrichment. German prepositions govern the case
    of their objects and establish relationships (spatial, temporal, abstract) between
    sentence elements.

    This model implements MediaGenerationCapable protocol to contribute domain
    expertise for image and audio generation, using relationship-based strategies
    for preposition concept visualization.

    Attributes:
        preposition: The German preposition (e.g., "auf", "in", "mit")
        english: English translation (e.g., "on", "in", "with")
        case: German case(s) governed (e.g., "Akkusativ", "Dativ", "Akkusativ/Dativ")
        example1: First German example sentence demonstrating usage
        example2: Second example sentence (optional)
        audio1/audio2/image_path: Media fields (populated during processing)

    Note:
        This model follows the design principle that domain models are SMART
        (contain expertise) while services are DUMB (execute instructions).
    """

    preposition: str
    english: str
    case: str
    example1: str = field(default="")
    example2: str = field(default="")
    # Media fields (not from CSV but added during processing)
    audio1: str = field(default="")
    audio2: str = field(default="")
    image_path: str = field(default="")

    def __post_init__(self) -> None:
        """Validate the preposition data after initialization."""
        # Validate case contains valid German cases (if case is provided)
        if self.case and self.case.strip():
            valid_cases = [
                "Accusative",
                "Dative",
                "Genitive",
                "Akkusativ",
                "Dativ",
                "Genitiv",
            ]
            case_parts = self.case.replace("/", " ").split()
            if not any(case_part in valid_cases for case_part in case_parts):
                raise ValueError(f"Invalid case specification: {self.case}")

    def get_image_search_strategy(
        self, anthropic_service: "ImageQueryGenerationProtocol"
    ) -> "Callable[[], str]":
        """Get strategy for generating image search terms with domain expertise.

        Creates a callable that uses this preposition's domain knowledge to generate
        context-aware image search terms based on the preposition's spatial/temporal
        meaning and example usage.

        Args:
            anthropic_service: Service implementing ImageQueryGenerationProtocol for
                AI-powered search term generation.

        Returns:
            Callable that when invoked returns image search terms as string.
            Falls back to direct English translation if service fails.
        """

        def generate_search_terms() -> str:
            """Execute search term generation strategy with preposition context."""
            try:
                # Use domain expertise to build rich context for the service
                context = self._build_search_context()
                result = anthropic_service.generate_image_query(context)
                if result and result.strip():
                    return result.strip()
            except Exception:
                # Service failed, use fallback
                pass

            # Fallback to direct English translation
            return self.english

        return generate_search_terms

    def get_combined_audio_text(self) -> str:
        """Get combined text for German preposition audio generation.

        Returns:
            Combined text with preposition and both examples for pronunciation context.
        """
        parts = [self.preposition]
        if self.example1:
            parts.append(self.example1)
        if self.example2:
            parts.append(self.example2)
        return ". ".join(parts)

    def _build_search_context(self) -> str:
        """Build rich context for image search using German preposition expertise."""
        case_info = self.get_case_description()
        two_way_info = " (two-way preposition)" if self.is_two_way_preposition() else ""

        return f"""
        German preposition: {self.preposition}
        English: {self.english}
        Grammar: {case_info}{two_way_info}
        Example 1: {self.example1}
        Example 2: {self.example2}

        Challenge: Generate search terms for images representing this preposition's
        spatial, temporal, or abstract relationship concept.

        Generate search terms that photographers would use to tag images showing
        the relationship or concept this preposition represents.
        """

    def get_case_description(self) -> str:
        """Get human-readable description of the grammatical case(s).

        Returns:
            Formatted description of case usage
        """
        # Normalize common German labels to English keywords for consistency with tests
        normalized = (
            self.case.replace("Akkusativ", "accusative")
            .replace("Dativ", "dative")
            .replace("Genitiv", "genitive")
        )
        case_key = normalized.lower()

        case_descriptions = {
            "accusative": "takes accusative case (direct object)",
            "dative": "takes dative case (indirect object)",
            "genitive": "takes genitive case (possession)",
            "accusative/dative": "takes accusative (motion) or dative (location)",
        }

        # Fall back to original case string if not in our mapping
        return case_descriptions.get(case_key, f"takes {self.case} case")

    def is_two_way_preposition(self) -> bool:
        """Check if this preposition can take both accusative and dative cases.

        Returns:
            True if preposition takes both accusative and dative
        """
        case_lower = (
            self.case.replace("Akkusativ", "accusative")
            .replace("Dativ", "dative")
            .lower()
        )
        return (
            "/" in case_lower and "accusative" in case_lower and "dative" in case_lower
        )
