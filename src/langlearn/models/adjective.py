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

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Callable

    from langlearn.protocols.anthropic_protocol import AnthropicServiceProtocol


class Adjective(BaseModel):
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

    word: str = Field(..., description="The German adjective")
    english: str = Field(..., description="English translation")
    example: str = Field(..., description="Example sentence using the adjective")
    comparative: str = Field(..., description="Comparative form of the adjective")
    superlative: str = Field("", description="Superlative form of the adjective")

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
        self, anthropic_service: "AnthropicServiceProtocol"
    ) -> "Callable[[], str]":
        """Get strategy for generating image search terms with domain expertise.

        Creates a callable that uses this adjective's domain knowledge to generate
        context-aware image search terms. The adjective contributes German linguistic
        expertise (comparison forms, concept mappings) while the anthropic service
        executes the actual AI processing.

        Design: Domain model is SMART (provides rich context), service is DUMB
        (processes whatever context it receives).

        Args:
            anthropic_service: Service implementing AnthropicServiceProtocol for
                AI-powered search term generation.

        Returns:
            Callable that when invoked returns image search terms as string.
            Falls back to concept mappings if service fails.

        Example:
            >>> adjective = Adjective(word="schön", english="beautiful",
            ...                      comparative="schöner", superlative="am schönsten",
            ...                      example="Das ist schön.")
            >>> strategy = adjective.get_image_search_strategy(anthropic_service)
            >>> search_terms = strategy()  # Returns context-aware search terms
        """

        def generate_search_terms() -> str:
            """Execute search term generation strategy with adjective context."""
            try:
                # Pass model object directly - adjective has compatible fields
                result = anthropic_service.generate_pexels_query(self)
                if result and result.strip():
                    return result.strip()
            except Exception:
                # Service failed, use fallback
                pass

            # Fallback to domain-specific handling
            return self._get_fallback_search_terms()

        return generate_search_terms

    def _get_fallback_search_terms(self) -> str:
        """Get fallback search terms using concept mappings."""

        # Enhanced concept mappings for difficult-to-visualize adjectives
        concept_mappings = {
            "impolite": "rude behavior angry person frown",
            "polite": "courteous person handshake smile greeting",
            "honest": "trustworthy person handshake truth",
            "dishonest": "lying person finger crossed deception",
            "patient": "calm waiting person meditation zen",
            "impatient": "frustrated waiting person clock time",
            "responsible": "reliable person checklist tasks organization",
            "irresponsible": "careless person mess chaos disorganized",
            "mature": "adult professional person business suit",
            "immature": "childish person tantrum emotional",
            "independent": "self-reliant person solo achievement success",
            "dependent": "needy person help support assistance",
            "confident": "assured person podium presentation speaking",
            "insecure": "uncertain person hiding shy timid",
            "generous": "giving person donation charity sharing",
            "selfish": "greedy person hoarding money grabbing",
            "humble": "modest person bowing respectful gesture",
            "arrogant": "proud person nose up superior attitude",
            "optimistic": "positive person sunrise thumbs up smile",
            "pessimistic": "negative person storm clouds frown down",
            "creative": "artistic person paintbrush palette art",
            "boring": "dull person yawn sleep monotone gray",
            "interesting": "engaging person books light bulb discovery",
            "lazy": "inactive person couch sleep procrastination",
            "hardworking": "diligent person desk work computer busy",
            "organized": "neat person files folders clean desk",
            "messy": "cluttered person chaos scattered papers disorder",
            "punctual": "timely person clock watch schedule calendar",
            "late": "delayed person running clock time pressure",
            "friendly": "welcoming person handshake smile greeting",
            "unfriendly": "cold person crossed arms rejection distance",
            "helpful": "supportive person assistance helping hand",
            "unhelpful": "uncooperative person refusal blocking gesture",
            "kind": "compassionate person heart care gentle touch",
            "cruel": "harsh person anger aggression violence",
            "fair": "just person scales balance equality justice",
            "unfair": "biased person unequal scales discrimination",
            "logical": "rational person brain thinking analysis charts",
            "illogical": "irrational person confusion question marks chaos",
            "practical": "useful person tools hammer work utility",
            "impractical": "useless person broken tools waste inefficient",
        }

        english_lower = self.english.lower().strip()

        # Check for exact matches first
        if english_lower in concept_mappings:
            return concept_mappings[english_lower]

        # Check for partial matches (for compound words)
        for key, mapping in concept_mappings.items():
            if key in english_lower or english_lower in key:
                return mapping

        # Default: use the English translation
        return self.english

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
