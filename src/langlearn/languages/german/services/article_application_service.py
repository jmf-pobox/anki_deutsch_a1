"""ArticleApplicationService for noun-article integration cards.

This service creates cards that help students learn which article goes with each noun,
addressing the core use case of German article learning: noun-article association.
"""

import logging
from typing import TYPE_CHECKING, Any

from langlearn.backends.base import NoteType
from langlearn.languages.german.records.factory import NounRecord

if TYPE_CHECKING:
    from .card_builder import CardBuilder

logger = logging.getLogger(__name__)


class ArticleApplicationService:
    """Generates article practice cards by composing noun + article data.

    This service creates noun-specific article cards that test students on
    which article (der/die/das) goes with each noun, providing the practical
    application of German article knowledge.

    Card Types Generated:
    1. Article Recognition: "Haus" → "das Haus"
    2. Case Context Cards: "___ Haus ist klein" → "Das Haus ist klein"
    """

    def __init__(self, card_builder: "CardBuilder") -> None:
        """Initialize the service with a CardBuilder instance.

        Args:
            card_builder: CardBuilder service for creating formatted cards
        """
        self._card_builder = card_builder
        logger.debug("ArticleApplicationService initialized")

    def generate_noun_article_cards(
        self,
        noun_records: list[NounRecord],
        enriched_data_list: list[dict[str, Any]] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Generate article practice cards for nouns.

        Creates multiple card types per noun to reinforce article-noun associations:
        - Article Recognition: Test recall of correct article
        - Case Context Cards: Test article usage in different cases

        Args:
            noun_records: List of noun records with article information
            enriched_data_list: Optional enriched data for each record

        Returns:
            List of (field_values, note_type) tuples for article practice cards
        """
        logger.info(
            "Building noun-article cards from %d noun records", len(noun_records)
        )
        cards = []

        for i, noun_record in enumerate(noun_records):
            enriched_data = enriched_data_list[i] if enriched_data_list else None

            # Generate article practice cards for this noun
            noun_cards = self._generate_cards_for_noun(noun_record, enriched_data)
            cards.extend(noun_cards)

        logger.info(
            "Generated %d total noun-article cards from %d nouns",
            len(cards),
            len(noun_records),
        )
        return cards

    def _generate_cards_for_noun(
        self,
        noun_record: NounRecord,
        enriched_data: dict[str, Any] | None = None,
    ) -> list[tuple[list[str], NoteType]]:
        """Generate article practice cards for a single noun.

        Args:
            noun_record: Single noun record with article information
            enriched_data: Optional enriched data

        Returns:
            List of article practice cards for this noun
        """
        cards = []

        # Card 1: Article Recognition
        cards.append(self._create_article_recognition_card(noun_record, enriched_data))

        # Cards 2-5: Case Context cards
        cases = ["nominativ", "akkusativ", "dativ", "genitiv"]
        for case in cases:
            cards.append(self._create_noun_case_card(noun_record, case, enriched_data))

        return cards

    def _create_article_recognition_card(
        self,
        noun_record: NounRecord,
        enriched_data: dict[str, Any] | None = None,
    ) -> tuple[list[str], NoteType]:
        """Create article recognition card for a noun.

        Front: "Haus" (just the noun)
        Back: "das Haus" (article + noun)
        """
        # Prepare card data
        card_data = noun_record.to_dict()
        if enriched_data:
            card_data.update(enriched_data)

        # Add card-specific data
        card_data["card_type"] = "noun_article_recognition"
        card_data["front_text"] = noun_record.noun  # Just the noun
        card_data["back_text"] = (
            f"{noun_record.article} {noun_record.noun}"  # article + noun
        )
        card_data["english_meaning"] = noun_record.english

        # Add fields for updated template format
        card_data["NounOnly"] = noun_record.noun  # For "_____ Haus" format
        card_data["NounEnglishWithArticle"] = f"the {noun_record.english.lower()}"

        # Use specialized template
        template = self._card_builder._template_service.get_template(
            "noun_article_recognition"
        )
        note_type = self._card_builder._create_note_type_for_record(
            "noun_article_recognition", template
        )
        field_values = self._card_builder._extract_field_values(
            "noun_article_recognition", card_data, note_type
        )

        return field_values, note_type

    def _create_noun_case_card(
        self,
        noun_record: NounRecord,
        case: str,
        enriched_data: dict[str, Any] | None = None,
    ) -> tuple[list[str], NoteType]:
        """Create case context card for a noun.

        Front: Context sentence with blank (e.g., "___ Haus ist klein")
        Back: Complete sentence (e.g., "Das Haus ist klein")
        """
        # Prepare card data
        card_data = noun_record.to_dict()
        if enriched_data:
            card_data.update(enriched_data)

        # Generate case-specific article form
        article_forms = self._get_article_forms_for_noun(noun_record.article)
        case_article = article_forms.get(case, noun_record.article)

        # Create example sentences for each case
        case_examples = self._generate_case_examples(
            noun_record.noun, case_article, case
        )
        complete_sentence = case_examples[case]

        # Create front (sentence with blank) using case-insensitive replacement
        import re

        pattern = r"\b" + re.escape(case_article) + r"\b"
        front_sentence = re.sub(
            pattern, "___", complete_sentence, count=1, flags=re.IGNORECASE
        )

        # Add card-specific data
        card_data["card_type"] = "noun_case_context"
        card_data["case"] = case
        card_data["article_form"] = case_article
        card_data["front_text"] = front_sentence
        card_data["back_text"] = complete_sentence
        gender = self._get_gender_from_article(noun_record.article)
        card_data["case_rule"] = f"{gender} {case} = {case_article}"

        # Add case usage descriptions
        case_usages = {
            "nominativ": "das Subjekt des Satzes",
            "akkusativ": "das direkte Objekt",
            "dativ": "das indirekte Objekt",
            "genitiv": "Besitz und bestimmte Präpositionen",
        }
        card_data["case_usage"] = case_usages.get(case, "")

        # Set conditional fields for highlighting current case
        card_data["case_nominativ"] = "true" if case == "nominativ" else ""
        card_data["case_akkusativ"] = "true" if case == "akkusativ" else ""
        card_data["case_dativ"] = "true" if case == "dativ" else ""
        card_data["case_genitiv"] = "true" if case == "genitiv" else ""

        # Use specialized template
        template = self._card_builder._template_service.get_template(
            "noun_case_context"
        )
        note_type = self._card_builder._create_note_type_for_record(
            "noun_case_context", template
        )
        field_values = self._card_builder._extract_field_values(
            "noun_case_context", card_data, note_type
        )

        return field_values, note_type

    def _get_article_forms_for_noun(self, base_article: str) -> dict[str, str]:
        """Get all case forms for a noun's article.

        Args:
            base_article: The nominative article (der/die/das)

        Returns:
            Dictionary mapping case names to article forms
        """
        # Article declension patterns
        article_patterns = {
            "der": {  # masculine
                "nominativ": "der",
                "akkusativ": "den",
                "dativ": "dem",
                "genitiv": "des",
            },
            "die": {  # feminine
                "nominativ": "die",
                "akkusativ": "die",
                "dativ": "der",
                "genitiv": "der",
            },
            "das": {  # neuter
                "nominativ": "das",
                "akkusativ": "das",
                "dativ": "dem",
                "genitiv": "des",
            },
        }

        return article_patterns.get(
            base_article,
            {
                "nominativ": base_article,
                "akkusativ": base_article,
                "dativ": base_article,
                "genitiv": base_article,
            },
        )

    def _get_gender_from_article(self, article: str) -> str:
        """Get gender name from article.

        Args:
            article: The article (der/die/das)

        Returns:
            German gender name (Maskulin/Feminin/Neutral)
        """
        gender_map = {
            "der": "Maskulin",
            "die": "Feminin",
            "das": "Neutral",
        }
        return gender_map.get(article, "Unbekannt")

    def _generate_case_examples(
        self, noun: str, article: str, case: str
    ) -> dict[str, str]:
        """Generate example sentences for different cases.

        Args:
            noun: The German noun
            article: The case-appropriate article
            case: The grammatical case

        Returns:
            Dictionary mapping case names to example sentences
        """
        # Create contextually appropriate examples for each case
        examples = {
            "nominativ": f"{article} {noun} ist hier.",  # Subject
            "akkusativ": f"Ich sehe {article} {noun}.",  # Direct object
            "dativ": f"Mit {article} {noun} arbeite ich.",  # With dative preposition
            "genitiv": f"Das ist die Farbe {article} {noun}es.",  # Possession/genitive
        }

        return examples

    def get_expected_card_count(self, noun_records: list[NounRecord]) -> int:
        """Calculate expected number of cards from noun records.

        Args:
            noun_records: List of noun records

        Returns:
            Expected card count (5 cards per noun: 1 recognition + 4 cases)
        """
        return len(noun_records) * 5
