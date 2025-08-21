"""Model for German nouns."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Callable

# Removed field_processor import - now pure domain model


class Noun(BaseModel):
    """Model representing a German noun with its properties and business logic."""

    noun: str = Field(..., description="The German noun")
    article: str = Field(..., description="The definite article (der/die/das)")
    english: str = Field(..., description="English translation")
    plural: str = Field(..., description="Plural form of the noun")
    example: str = Field(..., description="Example sentence using the noun")
    related: str = Field(default="", description="Related words or phrases")

    def get_combined_audio_text(self) -> str:
        """Generate combined German noun audio text.

        Returns audio text for: article + singular, article + plural
        Example: "die Katze, die Katzen"

        Returns:
            Combined text for audio generation
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

    def get_image_search_strategy(self) -> "Callable[[], str]":
        """Get a strategy for generating search terms without executing it immediately.
        
        This lazy evaluation approach prevents unnecessary Anthropic API calls
        when images already exist or aren't needed.

        Returns:
            A callable that when invoked will generate context-aware search terms,
            with fallback to concrete/abstract noun handling
        """
        def generate_search_terms() -> str:
            """Execute the search term generation strategy."""
            # Handle empty English translation
            if not self.english.strip():
                return ""

            # Try to use Anthropic service for context-aware query generation
            try:
                from langlearn.services.service_container import get_anthropic_service

                service = get_anthropic_service()
                if service:
                    context_query = service.generate_pexels_query(self)
                    if context_query and context_query.strip():
                        return context_query.strip()
            except Exception:
                # Fall back to concrete/abstract handling if Anthropic service fails
                pass
            
            # Return fallback search terms
            return self._get_fallback_search_terms()
        
        return generate_search_terms
    
    def get_image_search_terms(self) -> str:
        """Legacy method for backward compatibility - executes strategy immediately.
        
        Note: This method maintains compatibility but should be replaced with
        get_image_search_strategy() for better performance.
        """
        strategy = self.get_image_search_strategy()
        return strategy()
    
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


# Removed field processing methods - now pure domain model with only business logic
