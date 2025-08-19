"""Model for German adjectives."""

from pydantic import BaseModel, Field

from .field_processor import (
    FieldProcessor,
    MediaGenerator,
    format_media_reference,
    validate_minimum_fields,
)


class Adjective(BaseModel, FieldProcessor):
    """Model representing a German adjective with its properties.

    German adjectives have comparative and superlative forms, and follow
    specific patterns for their formation.
    """

    word: str = Field(..., description="The German adjective")
    english: str = Field(..., description="English translation")
    example: str = Field(..., description="Example sentence using the adjective")
    comparative: str = Field(..., description="Comparative form of the adjective")
    superlative: str = Field("", description="Superlative form of the adjective")

    def get_combined_audio_text(self) -> str:
        """Generate combined German adjective audio text.

        Returns audio text for: base, comparative, superlative
        Example: "schön, schöner, am schönsten"

        Returns:
            Combined text for audio generation
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

    # FieldProcessor interface implementation
    def process_fields_for_media_generation(
        self, fields: list[str], media_generator: MediaGenerator
    ) -> list[str]:
        """Process adjective fields with combined audio and image generation.

        Field Layout: [Word, English, Example, Comparative, Superlative, Image,
                       WordAudio, ExampleAudio]

        Args:
            fields: List of field values for this adjective
            media_generator: Interface for generating audio/image media

        Returns:
            Processed field list with media references added where appropriate
        """
        # Extend fields to expected 8-field layout if needed
        while len(fields) < 8:
            fields.append("")

        validate_minimum_fields(fields, 8, "Adjective")

        # Extract field values
        word = fields[0]
        english = fields[1]
        example = fields[2]
        comparative = fields[3]
        superlative = fields[4]

        # Create working copy
        processed_fields = fields.copy()

        # Generate word audio (combined adjective forms) if empty
        if not processed_fields[6]:  # WordAudio field
            # Create adjective instance to use domain logic
            adjective = Adjective(
                word=word,
                english=english,
                example=example,
                comparative=comparative,
                superlative=superlative,
            )
            combined_text = adjective.get_combined_audio_text()
            audio_path = media_generator.generate_audio(combined_text)
            if audio_path:
                processed_fields[6] = format_media_reference(audio_path, "audio")

        # Generate example audio if empty
        if not processed_fields[7]:  # ExampleAudio field
            audio_path = media_generator.generate_audio(example)
            if audio_path:
                processed_fields[7] = format_media_reference(audio_path, "audio")

        # Generate image if empty
        if not processed_fields[5]:  # Image field
            # Check if image already exists before expensive AI call
            from pathlib import Path
            expected_image_path = Path(f"data/images/{word.lower()}.jpg")
            
            if expected_image_path.exists():
                # Image exists, just reference it
                processed_fields[5] = format_media_reference(str(expected_image_path), "image")
            else:
                # Image doesn't exist, use AI-enhanced search terms for generation
                temp_adjective = Adjective(
                    word=word,
                    english=english,
                    example=example,
                    comparative=comparative,
                    superlative=superlative,
                )

                search_terms = temp_adjective.get_image_search_terms()
                image_path = media_generator.generate_image(search_terms, english)
                if image_path:
                    processed_fields[5] = format_media_reference(image_path, "image")

        return processed_fields

    def get_expected_field_count(self) -> int:
        """Return expected number of fields for adjective processing."""
        return 8

    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected structure for adjectives."""
        return len(fields) >= self.get_expected_field_count()

    def _get_field_names(self) -> list[str]:
        """Get human-readable names for each field position."""
        return [
            "Word",
            "English",
            "Example",
            "Comparative",
            "Superlative",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

    def get_image_search_terms(self) -> str:
        """Get enhanced search terms prioritizing sentence context for better results.

        Returns:
            Context-aware search terms generated from the example sentence,
            with fallback to concept mappings for abstract adjectives
        """
        # Try to use Anthropic service for context-aware query generation
        try:
            from langlearn.services.service_container import get_anthropic_service

            service = get_anthropic_service()
            if service:
                context_query = service.generate_pexels_query(self)
                if context_query and context_query.strip():
                    return context_query.strip()
        except Exception:
            # Fall back to concept mappings if Anthropic service fails
            pass

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
