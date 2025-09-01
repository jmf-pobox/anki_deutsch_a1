"""German Noun Domain Model.

This module contains the domain model for German nouns with specialized logic for
German language learning applications. The module is responsible for:

CORE RESPONSIBILITIES:
    - Modeling German noun data (noun, article, English translation, plural, example)
    - Implementing MediaGenerationCapable protocol for media enrichment
    - Providing German-specific linguistic validation and gender classification
    - Contributing domain expertise for image search term generation
    - Supporting audio generation with proper article and plural pronunciation

DESIGN PRINCIPLES:
    - Domain model is SMART: Contains German noun expertise and linguistic knowledge
    - Services are DUMB: External services receive rich context, no domain logic
    - Single Responsibility: Noun logic stays in Noun model, not in services
    - Dependency Injection: Protocol-based design for loose coupling

GERMAN LINGUISTIC FEATURES:
    - Gender system with definite articles (der/die/das)
    - Plural formation patterns and irregular plurals
    - Concrete vs abstract noun classification for visualization strategies
    - Context-aware search term generation using linguistic domain knowledge
    - Audio generation combining singular and plural forms with articles

INTEGRATION POINTS:
    - MediaGenerationCapable protocol for image/audio media enrichment
    - AnthropicServiceProtocol for AI-powered search term generation
    - MediaEnricher service for coordinated media asset generation

Usage:
    Basic usage:
        >>> noun = Noun(
        ...     noun="Katze",
        ...     article="die",
        ...     english="cat",
        ...     plural="Katzen",
        ...     example="Die Katze schläft auf dem Sofa."
        ... )

    Media generation with dependency injection:
        >>> strategy = noun.get_image_search_strategy(anthropic_service)
        >>> search_terms = strategy()  # Returns context-aware search terms
        >>> audio_text = noun.get_combined_audio_text()  # Article + noun forms
"""

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.protocols.anthropic_protocol import AnthropicServiceProtocol


class Noun(BaseModel):
    """German noun domain model with linguistic expertise and media generation.

    Represents a German noun with its properties, German linguistic knowledge,
    and specialized logic for media enrichment. German nouns are characterized
    by their grammatical gender (reflected in articles), plural formation patterns,
    and case declension system.

    This model implements MediaGenerationCapable protocol to contribute domain
    expertise for image and audio generation, using concrete/abstract classification
    strategies for appropriate visual representation.

    Attributes:
        noun: The German noun (e.g., "Katze", "Haus")
        article: Definite article indicating gender ("der", "die", "das")
        english: English translation (e.g., "cat", "house")
        plural: Plural form (e.g., "Katzen", "Häuser")
        example: German example sentence demonstrating usage
        related: Related words or phrases (optional)

    Note:
        This model follows the design principle that domain models are SMART
        (contain expertise) while services are DUMB (execute instructions).
    """

    noun: str = Field(..., description="The German noun")
    article: str = Field(..., description="The definite article (der/die/das)")
    english: str = Field(..., description="English translation")
    plural: str = Field(..., description="Plural form of the noun")
    example: str = Field(..., description="Example sentence using the noun")
    related: str = Field(default="", description="Related words or phrases")

    def get_combined_audio_text(self) -> str:
        """Get combined text for German noun audio generation.

        Combines the noun with its article in both singular and plural forms
        to provide proper pronunciation context for German language learners.
        This helps learners associate nouns with their grammatical gender and
        plural formation patterns.

        Returns:
            Formatted string: "{article} {noun}, {plural_with_article}" for audio.

        Example:
            >>> noun = Noun(noun="Katze", article="die", english="cat",
            ...             plural="Katzen", example="Die Katze schläft.")
            >>> noun.get_combined_audio_text()
            'die Katze, die Katzen'
        """
        # Check if plural already includes article
        if self.plural.startswith(("der ", "die ", "das ")):
            return f"{self.article} {self.noun}, {self.plural}"
        else:
            return f"{self.article} {self.noun}, die {self.plural}"

    def is_concrete(self) -> bool:
        """Determine if this noun represents a concrete concept.

        Uses German-specific patterns and suffixes to classify nouns as
        concrete (physical objects) or abstract (concepts, ideas).

        Returns:
            True if the noun likely represents a concrete object
        """
        if not self.noun:
            return False

        noun_lower = self.noun.lower()

        # Abstract noun suffixes in German
        abstract_suffixes = [
            "heit",
            "keit",
            "ung",
            "ion",
            "tion",
            "sion",
            "schaft",
            "tum",
            "nis",
            "mus",
            "tät",
            "ität",
            "ei",
            "ie",
            "ur",
            "anz",
        ]

        # Check for abstract suffixes
        for suffix in abstract_suffixes:
            if noun_lower.endswith(suffix):
                return False

        # Common concrete noun patterns (more likely to be concrete)
        concrete_indicators = [
            "chen",
            "lein",  # Diminutives are usually concrete
            "zeug",
            "werk",
            "gerät",  # Tools and objects
        ]

        for indicator in concrete_indicators:
            if indicator in noun_lower:
                return True

        # Known abstract concept words
        abstract_words = {
            "freiheit",
            "liebe",
            "glück",
            "freude",
            "angst",
            "mut",
            "hoffnung",
            "zeit",
            "gedanke",
            "idee",
            "träume",
            "wissen",
            "bildung",
            "kultur",
            "musik",
            "kunst",
            "sprache",
            "geschichte",
            "zukunft",
            "vergangenheit",
            "wahrheit",
            "schönheit",
            "gesundheit",
            "krankheit",
            "erfolg",
        }

        if noun_lower in abstract_words:
            return False

        # Known concrete objects
        concrete_words = {
            "hund",
            "katze",
            "haus",
            "auto",
            "baum",
            "stuhl",
            "tisch",
            "buch",
            "telefon",
            "computer",
            "brot",
            "wasser",
            "apfel",
            "blume",
            "berg",
            "fluss",
            "stadt",
            "straße",
            "fenster",
            "tür",
            "bett",
            "küche",
        }

        if noun_lower in concrete_words:
            return True

        # Default heuristic: assume concrete unless proven abstract
        # This works better for vocabulary learning where most nouns
        # taught to beginners are concrete objects
        return True

    def get_image_search_strategy(
        self, anthropic_service: "AnthropicServiceProtocol"
    ) -> "Callable[[], str]":
        """Get strategy for generating image search terms with domain expertise.

        Creates a callable that uses this noun's domain knowledge to generate
        context-aware image search terms. The noun contributes German linguistic
        expertise (concrete vs abstract classification, gender context) while
        the anthropic service executes the actual AI processing.

        Design: Domain model is SMART (provides rich context), service is DUMB
        (processes whatever context it receives).

        Args:
            anthropic_service: Service implementing AnthropicServiceProtocol for
                AI-powered search term generation.

        Returns:
            Callable that when invoked returns image search terms as string.
            Falls back to concrete/abstract handling if service fails.

        Example:
            >>> noun = Noun(noun="Katze", article="die", english="cat",
            ...             plural="Katzen", example="Die Katze schläft.")
            >>> strategy = noun.get_image_search_strategy(anthropic_service)
            >>> search_terms = strategy()  # Returns context-aware search terms
        """

        def generate_search_terms() -> str:
            """Execute search term generation strategy with noun context."""
            try:
                # Use domain expertise to build rich context for the service
                context = self._build_search_context()
                result = anthropic_service.generate_pexels_query(context)
                if result and result.strip():
                    return result.strip()
            except Exception:
                # Service failed, use fallback
                pass

            # Fallback to domain-specific handling
            return self._get_fallback_search_terms()

        return generate_search_terms

    def _get_fallback_search_terms(self) -> str:
        """Get fallback search terms based on concrete/abstract noun handling."""

        if not self.is_concrete():
            return self._get_abstract_concept_terms()
        return self.english  # Concrete nouns use direct English translation

    def _get_abstract_concept_terms(self) -> str:
        """Generate search terms for abstract concepts.

        Returns:
            Enhanced search terms for abstract nouns
        """
        # Context-aware search term generation for abstract nouns
        concept_mappings = {
            "freedom": "person celebrating independence",
            "love": "heart symbol family together",
            "happiness": "smiling person joy celebration",
            "fear": "worried person anxiety",
            "hope": "sunrise bright future",
            "time": "clock calendar schedule",
            "knowledge": "books learning education",
            "culture": "art museum heritage",
            "music": "musical notes instruments",
            "art": "painting gallery creative",
            "future": "forward arrow progress",
            "success": "trophy achievement winner",
        }

        english_lower = self.english.lower()
        for key, enhanced_terms in concept_mappings.items():
            if key in english_lower:
                return enhanced_terms

        return f"{self.english} concept symbol"

    def _build_search_context(self) -> str:
        """Build rich context for image search using German noun expertise.

        Constructs visualization guidance based on German linguistic knowledge.
        Considers gender (article), concrete vs abstract classification, and
        provides type-specific strategies for representing noun concepts visually.

        This method embodies the domain model's expertise about German nouns and
        their visualization challenges, providing rich context that services can
        use without needing to understand German linguistic classifications.

        Returns:
            Formatted context string with:
            - Noun details (German noun, article/gender, English translation)
            - Concrete/abstract classification with visualization strategy
            - Example usage and related context
            - Instructions for generating appropriate search terms

        Example:
            For concrete noun "Katze":
                "Focus on the physical object, use direct visual representation"
            For abstract noun "Freiheit":
                "Use symbolic imagery, metaphorical representations"

        Note:
            This is a private method called by get_image_search_strategy() to
            contribute domain expertise to the search term generation process.
        """
        # Determine visualization strategy based on concrete/abstract classification
        if self.is_concrete():
            visual_strategy = (
                "Focus on the physical object, use direct visual representation. "
                "Show the actual item, its typical context, or environment where "
                "it's commonly found."
            )
        else:
            visual_strategy = (
                "Use symbolic imagery, metaphorical representations, or visual "
                "metaphors. Abstract concepts need creative visual interpretation "
                "through symbols, emotions, or representative scenarios."
            )

        # Add gender context (German linguistic feature)
        gender_info = {"der": "masculine", "die": "feminine", "das": "neuter"}.get(
            self.article, "unknown gender"
        )

        return f"""
        German noun: {self.noun} ({self.article} - {gender_info})
        English: {self.english}
        Plural: {self.plural}
        Example usage: {self.example}
        Classification: {"Concrete" if self.is_concrete() else "Abstract"} noun

        Challenge: Generate search terms for finding images that represent this noun.
        Visual strategy: {visual_strategy}

        Generate search terms that photographers would use to tag images of
        this concept.
        """


# Removed field processing methods - now pure domain model with only business logic
