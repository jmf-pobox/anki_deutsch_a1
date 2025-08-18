"""Model for German nouns."""

from pydantic import BaseModel, Field


class Noun(BaseModel):
    """Model representing a German noun with its properties."""

    noun: str = Field(..., description="The German noun")
    article: str = Field(..., description="The definite article (der/die/das)")
    english: str = Field(..., description="English translation")
    plural: str = Field(..., description="Plural form of the noun")
    example: str = Field(..., description="Example sentence using the noun")
    related: str = Field(default="", description="Related words or phrases")
    word_audio: str = Field("", description="Path to audio file for the noun")
    example_audio: str = Field("", description="Path to audio file for the example")
    image_path: str = Field("", description="Path to image file for the noun")

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

    def get_image_search_terms(self) -> str:
        """Generate contextual image search terms for this noun.

        Returns:
            Search terms optimized for finding relevant images
        """
        # Handle empty English translation
        if not self.english.strip():
            return ""

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
