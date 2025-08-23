"""Article pattern processor for multi-case card generation.

This service processes ArticleRecord instances to generate multiple
case-specific cards, transforming from 1 record per article type to 4-5 cards
per article type (gender recognition + 4 case contexts).
"""

import logging
from typing import TYPE_CHECKING, Any

from langlearn.backends.base import NoteType
from langlearn.models.records import (
    ArticleRecord,
    IndefiniteArticleRecord,
    NegativeArticleRecord,
    UnifiedArticleRecord,
)
from langlearn.services.german_explanation_factory import GermanExplanationFactory

if TYPE_CHECKING:
    from langlearn.services.card_builder import CardBuilder

logger = logging.getLogger(__name__)


class ArticlePatternProcessor:
    """Processes Article records into multiple case-specific cards.

    This service implements the core logic for the article card generation
    system, creating separate cards for each case and gender recognition
    rather than a single overwhelming declension table.

    From our PM-ARTICLES.md specification:
    - 1 Gender Recognition Card per record
    - 4 Case Context Cards per record (Nom, Acc, Dat, Gen)
    - Total: 5 cards per article record
    """

    def __init__(self, card_builder: "CardBuilder") -> None:
        """Initialize the processor with a CardBuilder instance.

        Args:
            card_builder: CardBuilder service for creating formatted cards
        """
        self._card_builder = card_builder
        self._explanation_factory = GermanExplanationFactory()
        logger.debug("ArticlePatternProcessor initialized")

    def process_article_records(
        self,
        records: list[
            ArticleRecord
            | IndefiniteArticleRecord
            | NegativeArticleRecord
            | UnifiedArticleRecord
        ],
        enriched_data_list: list[dict[str, Any]] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Generate multiple case-specific cards from article records.

        Transforms from 1 record per article type to 5 cards per record:
        - Gender Recognition card (learn der/die/das for this gender)
        - Nominative Context card (subject usage)
        - Accusative Context card (direct object usage)
        - Dative Context card (indirect object usage)
        - Genitive Context card (possession usage)

        Args:
            records: List of article record instances
            enriched_data_list: Optional enriched data for each record

        Returns:
            List of (field_values, note_type) tuples for multiple cards per record
        """
        logger.info("Building article pattern cards from %d records", len(records))
        cards = []

        for i, record in enumerate(records):
            enriched_data = enriched_data_list[i] if enriched_data_list else None

            # Generate 5 cards per record
            record_cards = self._generate_cards_for_record(record, enriched_data)
            cards.extend(record_cards)

        logger.info(
            "Generated %d total cards from %d records", len(cards), len(records)
        )
        return cards

    def _generate_cards_for_record(
        self,
        record: (
            ArticleRecord
            | IndefiniteArticleRecord
            | NegativeArticleRecord
            | UnifiedArticleRecord
        ),
        enriched_data: dict[str, Any] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Generate 5 cloze deletion cards for a single article record.

        Args:
            record: Single article record
            enriched_data: Optional enriched data

        Returns:
            List of 5 cloze cards (gender + 4 cases) with German explanations
        """
        cards = []

        # Card 1: Gender Recognition Cloze
        cards.append(self._create_gender_cloze_card(record, enriched_data))

        # Cards 2-5: Case Context Cloze cards
        cases = ["nominative", "accusative", "dative", "genitive"]
        for case in cases:
            cards.append(self._create_case_cloze_card(record, case, enriched_data))

        return cards

    def _create_gender_recognition_card(
        self,
        record: (
            ArticleRecord
            | IndefiniteArticleRecord
            | NegativeArticleRecord
            | UnifiedArticleRecord
        ),
        enriched_data: dict[str, Any] | None = None,
    ) -> tuple[list[str], NoteType]:
        """Create gender recognition card.

        Front: Gender type (e.g., "Masculine")
        Back: Article form (e.g., "der")
        """
        # Prepare card data
        card_data = record.to_dict()
        if enriched_data:
            card_data.update(enriched_data)

        # Add card-specific data
        card_data["card_type"] = "gender_recognition"
        card_data["front_text"] = record.gender.title()  # Masculine, Feminine, Neuter
        card_data["back_text"] = record.nominative  # der, die, das, etc.

        # Add compatibility fields for template (using properties)
        card_data["gender"] = record.gender
        card_data["nominative"] = record.nominative
        card_data["accusative"] = record.accusative
        card_data["dative"] = record.dative
        card_data["genitive"] = record.genitive

        # Add example fields if available
        if hasattr(record, "example_nom"):
            card_data["example_nom"] = record.example_nom

        # Add artikel_typ conditional fields for template (safe access)
        artikel_typ = getattr(record, "artikel_typ", "bestimmt")  # Default for legacy
        card_data["ArtikelTypBestimmt"] = "true" if artikel_typ == "bestimmt" else ""
        card_data["ArtikelTypUnbestimmt"] = (
            "true" if artikel_typ == "unbestimmt" else ""
        )
        card_data["ArtikelTypVerneinend"] = (
            "true" if artikel_typ == "verneinend" else ""
        )

        # Extract noun from example sentence and provide English translation
        if hasattr(record, "example_nom") and record.example_nom:
            noun_only = self._extract_noun_from_sentence(record.example_nom)
            card_data["NounOnly"] = noun_only  # Anki template field names are CamelCase
            # Simple English translations for common nouns
            noun_translations = {
                "Mann": "man",
                "Frau": "woman",
                "Kind": "child",
                "Kinder": "children",
                "Auto": "car",
                "Haus": "house",
                "Buch": "book",
                "Tisch": "table",
                "Stuhl": "chair",
            }
            card_data["NounEnglish"] = noun_translations.get(
                noun_only, noun_only.lower()
            )

        # Use specialized template
        template = self._card_builder._template_service.get_template("artikel_gender")
        note_type = self._card_builder._create_note_type_for_record(
            "artikel_gender", template
        )
        field_values = self._card_builder._extract_field_values(
            "artikel_gender", card_data, note_type
        )

        return field_values, note_type

    def _create_case_context_card(
        self,
        record: (
            ArticleRecord
            | IndefiniteArticleRecord
            | NegativeArticleRecord
            | UnifiedArticleRecord
        ),
        case: str,
        enriched_data: dict[str, Any] | None = None,
    ) -> tuple[list[str], NoteType]:
        """Create case context card.

        Front: Context sentence with blank (e.g., "___ Mann arbeitet")
        Back: Complete sentence (e.g., "Der Mann arbeitet")
        """
        # Prepare card data
        card_data = record.to_dict()
        if enriched_data:
            card_data.update(enriched_data)

        # Add card-specific data
        card_data["card_type"] = "case_context"
        card_data["case"] = case
        card_data["article_form"] = getattr(record, case)
        card_data["example_sentence"] = getattr(record, f"example_{case[:3]}")

        # Create front (sentence with blank) and back (complete sentence)
        complete_sentence = card_data["example_sentence"]
        article_form = card_data["article_form"]

        # Create front with blank: "mit _____ Mann"
        if complete_sentence and article_form:
            front_sentence = complete_sentence.replace(article_form, "_____")
            card_data["front_text"] = front_sentence
        else:
            card_data["front_text"] = "_____ [example missing]"

        card_data["back_text"] = complete_sentence
        card_data["case_rule"] = f"{record.gender.title()} {case} = {article_form}"

        # Add case usage descriptions
        case_usages = {
            "nominative": "the subject of the sentence",
            "accusative": "the direct object",
            "dative": "the indirect object",
            "genitive": "possession and certain prepositions",
        }
        card_data["case_usage"] = case_usages.get(case, "")

        # Set conditional fields for highlighting current case
        card_data["case_nominative"] = "true" if case == "nominative" else ""
        card_data["case_accusative"] = "true" if case == "accusative" else ""
        card_data["case_dative"] = "true" if case == "dative" else ""
        card_data["case_genitive"] = "true" if case == "genitive" else ""

        # Add artikel_typ conditional fields for template (safe access)
        artikel_typ = getattr(record, "artikel_typ", "bestimmt")  # Default for legacy
        card_data["ArtikelTypBestimmt"] = "true" if artikel_typ == "bestimmt" else ""
        card_data["ArtikelTypUnbestimmt"] = (
            "true" if artikel_typ == "unbestimmt" else ""
        )
        card_data["ArtikelTypVerneinend"] = (
            "true" if artikel_typ == "verneinend" else ""
        )

        # Extract noun from example sentence and provide English translation
        complete_sentence = card_data["example_sentence"]
        if complete_sentence:
            noun_only = self._extract_noun_from_sentence(complete_sentence)
            card_data["NounOnly"] = noun_only  # Anki template field names are CamelCase
            # Simple English translations for common nouns
            noun_translations = {
                "Mann": "man",
                "Frau": "woman",
                "Kind": "child",
                "Kinder": "children",
                "Auto": "car",
                "Haus": "house",
                "Buch": "book",
                "Tisch": "table",
                "Stuhl": "chair",
            }
            card_data["NounEnglish"] = noun_translations.get(
                noun_only, noun_only.lower()
            )

        # Use specialized template
        template = self._card_builder._template_service.get_template("artikel_context")
        note_type = self._card_builder._create_note_type_for_record(
            "artikel_context", template
        )
        field_values = self._card_builder._extract_field_values(
            "artikel_context", card_data, note_type
        )

        return field_values, note_type

    def get_expected_card_count(
        self,
        records: list[ArticleRecord | IndefiniteArticleRecord | NegativeArticleRecord],
    ) -> int:
        """Calculate expected number of cards from article records.

        Args:
            records: List of article records

        Returns:
            Expected card count (5 cards per record)
        """
        return len(records) * 5

    def _extract_noun_from_sentence(self, sentence: str) -> str:
        """Extract the main noun from an example sentence.

        Args:
            sentence: German sentence like "Der Mann ist hier" or "mit dem Mann"

        Returns:
            The extracted noun like "Mann"
        """
        import re

        # Remove common prepositions and articles
        words = sentence.split()

        # Skip articles, prepositions, and common words
        skip_words = {
            "der",
            "die",
            "das",
            "den",
            "dem",
            "des",
            "ein",
            "eine",
            "einen",
            "einem",
            "einer",
            "eines",
            "kein",
            "keine",
            "keinen",
            "keinem",
            "keiner",
            "keines",
            "mit",
            "ist",
            "sind",
            "hier",
            "ich",
            "sehe",
            "auto",
        }

        for word in words:
            # Clean word of punctuation
            clean_word = re.sub(r"[^\w]", "", word)
            if clean_word and clean_word.lower() not in skip_words:
                # Return the first significant word (likely the noun)
                return clean_word.capitalize()

        # Fallback - return first word that's not an article
        for word in words:
            clean_word = re.sub(r"[^\w]", "", word)
            if clean_word and not clean_word.lower().startswith(("der", "die", "das")):
                return clean_word.capitalize()

        return "Wort"  # Fallback

    # New cloze deletion methods

    def _create_gender_cloze_card(
        self,
        record: (
            ArticleRecord
            | IndefiniteArticleRecord
            | NegativeArticleRecord
            | UnifiedArticleRecord
        ),
        enriched_data: dict[str, Any] | None = None,
    ) -> tuple[list[str], NoteType]:
        """Create gender recognition cloze deletion card.

        Generates: "{{c1::Der}} Mann ist hier" for gender recognition learning.
        Uses German explanations like "Maskulin - Geschlecht erkennen".

        Args:
            record: Article record
            enriched_data: Optional enriched data

        Returns:
            Cloze card with German explanation
        """
        # Create cloze text: "{{c1::Der}} Mann ist hier"
        example_sentence = getattr(record, "example_nom", "") or "ist hier"
        article = record.nominative

        # Case-insensitive replacement to handle capitalized articles in sentences
        import re

        pattern = re.compile(re.escape(article), re.IGNORECASE)
        match = pattern.search(example_sentence)
        if match:
            # Preserve the original capitalization from the sentence
            original_article = match.group()
            cloze_text = example_sentence.replace(
                original_article, f"{{{{c1::{original_article}}}}}", 1
            )
        else:
            # Fallback if article not found - create a simple cloze
            cloze_text = f"{{{{c1::{article.title()}}}}} ist hier"

        # Generate German explanation
        explanation = self._explanation_factory.create_gender_recognition_explanation(
            record.gender
        )

        # Prepare card data for cloze template
        card_data = {
            "Text": cloze_text,
            "Explanation": explanation,
            "Image": enriched_data.get("image_url") if enriched_data else "",
            "Audio": enriched_data.get("audio_file") if enriched_data else "",
        }

        # Use cloze template
        template = self._card_builder._template_service.get_template(
            "artikel_gender_cloze"
        )
        note_type = self._card_builder._create_note_type_for_record(
            "artikel_gender_cloze", template
        )
        field_values = self._card_builder._extract_field_values(
            "artikel_gender_cloze", card_data, note_type
        )

        return field_values, note_type

    def _create_case_cloze_card(
        self,
        record: (
            ArticleRecord
            | IndefiniteArticleRecord
            | NegativeArticleRecord
            | UnifiedArticleRecord
        ),
        case: str,
        enriched_data: dict[str, Any] | None = None,
    ) -> tuple[list[str], NoteType]:
        """Create case context cloze deletion card.

        Generates: "Ich sehe {{c1::den}} Mann" for case context learning.
        Uses German explanations like "den - Maskulin Akkusativ (wen/was?)".

        Args:
            record: Article record
            case: Case name (nominative, accusative, dative, genitive)
            enriched_data: Optional enriched data

        Returns:
            Cloze card with German case explanation
        """
        # Get case-specific data
        article = getattr(record, case)
        example_sentence = (
            getattr(record, f"example_{case[:3]}", "") or f"{article} Wort"
        )

        # Create cloze text: "Ich sehe {{c1::den}} Mann"
        import re

        pattern = re.compile(re.escape(article), re.IGNORECASE)
        match = pattern.search(example_sentence)
        if match:
            # Preserve the original capitalization from the sentence
            original_article = match.group()
            cloze_text = example_sentence.replace(
                original_article, f"{{{{c1::{original_article}}}}}", 1
            )
        else:
            # Fallback if article not found - create a simple cloze
            cloze_text = f"{{{{c1::{article.title()}}}}} Wort"

        # Generate German case explanation
        explanation = self._explanation_factory.create_case_explanation(
            record.gender, case, article
        )

        # Prepare card data for cloze template
        card_data = {
            "Text": cloze_text,
            "Explanation": explanation,
            "Image": enriched_data.get("image_url") if enriched_data else "",
            "Audio": enriched_data.get("audio_file") if enriched_data else "",
        }

        # Use cloze template
        template = self._card_builder._template_service.get_template(
            "artikel_context_cloze"
        )
        note_type = self._card_builder._create_note_type_for_record(
            "artikel_context_cloze", template
        )
        field_values = self._card_builder._extract_field_values(
            "artikel_context_cloze", card_data, note_type
        )

        return field_values, note_type
