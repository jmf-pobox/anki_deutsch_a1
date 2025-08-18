"""Model for German nouns."""

from typing import Any

from pydantic import BaseModel, Field

from .field_processor import (
    FieldProcessor,
    MediaGenerator,
    format_media_reference,
    validate_minimum_fields,
)


class Noun(BaseModel, FieldProcessor):
    """Model representing a German noun with its properties and field processing."""

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

    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: MediaGenerator
    ) -> list[str]:
        """Process noun fields with German-specific logic.

        Field Layout: [Noun, Article, English, Plural, Example, Related, Image,
                      WordAudio, ExampleAudio]

        Args:
            fields: Original field values
            media_generator: Interface for generating media

        Returns:
            Processed field values with media
        """
        validate_minimum_fields(fields, 9, "Noun")

        # Extract field values
        noun = fields[0]
        article = fields[1]
        english = fields[2]
        plural = fields[3]
        example = fields[4]
        related = fields[5]

        # Create a copy to modify
        processed = fields.copy()

        # Only generate audio if WordAudio field (index 7) is empty
        if not processed[7]:  # WordAudio field
            combined_text = self._get_combined_audio_text_from_fields(
                article, noun, plural
            )
            audio_path = media_generator.generate_audio(combined_text)
            if audio_path:
                processed[7] = format_media_reference(audio_path, "audio")

        # Only generate example audio if ExampleAudio field (index 8) is empty
        if not processed[8]:  # ExampleAudio field
            audio_path = media_generator.generate_audio(example)
            if audio_path:
                processed[8] = format_media_reference(audio_path, "audio")

        # Only generate image if Image field (index 6) is empty AND noun is concrete
        if not processed[6]:  # Image field
            # Create temporary noun instance to check if concrete
            temp_noun = Noun(
                noun=noun,
                article=article,
                english=english,
                plural=plural,
                example=example,
                related=related,
                word_audio="",
                example_audio="",
                image_path="",
            )
            if temp_noun.is_concrete():
                # Use context-enhanced search terms for better image results
                search_terms = temp_noun.get_image_search_terms()
                image_path = media_generator.generate_image(search_terms, english)
                if image_path:
                    processed[6] = format_media_reference(image_path, "image")

        return processed

    def _get_combined_audio_text_from_fields(
        self, article: str, noun: str, plural: str
    ) -> str:
        """Generate combined German noun audio text from field values.

        Returns audio text for: article + singular, article + plural
        Example: "die Katze, die Katzen"

        Args:
            article: The definite article (der/die/das)
            noun: The German noun
            plural: Plural form of the noun

        Returns:
            Combined text for audio generation
        """
        # Check if plural already includes article
        if plural.startswith(("der ", "die ", "das ")):
            return f"{article} {noun}, {plural}"
        else:
            return f"{article} {noun}, die {plural}"

    def get_expected_field_count(self) -> int:
        """Return expected number of fields for noun cards."""
        return 9

    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected noun structure."""
        return len(fields) >= 9

    def get_field_layout_info(self) -> dict[str, Any]:
        """Return information about the noun field layout."""
        return {
            "model_type": "Noun",
            "expected_field_count": 9,
            "field_names": self._get_field_names(),
            "description": "German noun with article, plural, and examples",
        }

    def _get_field_names(self) -> list[str]:
        """Return the field names for noun cards."""
        return [
            "Noun",  # 0
            "Article",  # 1
            "English",  # 2
            "Plural",  # 3
            "Example",  # 4
            "Related",  # 5
            "Image",  # 6
            "WordAudio",  # 7
            "ExampleAudio",  # 8
        ]
