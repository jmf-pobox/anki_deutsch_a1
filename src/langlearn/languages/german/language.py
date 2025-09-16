"""German language implementation for multi-language architecture."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langlearn.core.records import BaseRecord
    from langlearn.protocols.domain_model_protocol import LanguageDomainModel


class GermanLanguage:
    """German language implementation."""

    @property
    def code(self) -> str:
        """ISO language code."""
        return "de"

    @property
    def name(self) -> str:
        """Human-readable language name."""
        return "German"

    def get_supported_record_types(self) -> list[str]:
        """Get record types this language supports."""
        return [
            "noun",
            "verb",
            "adjective",
            "adverb",
            "article",
            "negation",
            "preposition",
            "phrase",
        ]

    def get_card_builder(self) -> Any:
        """Get the card builder for this language."""
        from .services import CardBuilder

        return CardBuilder

    def get_grammar_service(self) -> Any:
        """Get language-specific grammar service."""
        # German doesn't have a single grammar service - functionality is distributed
        # across article_application_service, article_pattern_processor, etc.
        from .services import article_application_service

        return article_application_service

    def get_record_mapper(self) -> Any:
        """Get language-specific record mapper."""
        from .services import RecordMapper

        return RecordMapper

    def get_template_path(self, record_type: str, side: str) -> str:
        """Get template path for record type and side (front/back).

        German templates follow the pattern:
        {record_type}_DE_de_{side}.html
        """
        # Get the path to the German templates directory
        current_dir = Path(__file__).parent
        templates_dir = current_dir / "templates"

        # German template naming convention
        template_name = f"{record_type}_DE_de_{side}.html"
        template_path = templates_dir / template_name

        return str(template_path)

    def get_template_filename(self, card_type: str, side: str) -> str:
        """Get template filename for card type and side.

        Args:
            card_type: Type of card (noun, verb, etc.)
            side: Template side ("front", "back", "css")

        Returns:
            Template filename following German convention
        """
        if side == "css":
            return f"{card_type}_DE_de.css"
        else:
            return f"{card_type}_DE_de_{side}.html"

    def get_template_directory(self) -> Path:
        """Get the templates directory for German language."""
        current_dir = Path(__file__).parent
        return current_dir / "templates"

    def create_domain_model(
        self, record_type: str, record: BaseRecord
    ) -> LanguageDomainModel:
        """Create German domain model from record using proper type narrowing.

        Args:
            record_type: Type of record (noun, verb, adjective, etc.)
            record: Validated record data from CSV

        Returns:
            German domain model implementing LanguageDomainModel protocol

        Raises:
            ValueError: If record_type is not supported by German language
        """
        # Import records and domain models for type narrowing
        from .records.adjective_record import AdjectiveRecord
        from .records.adverb_record import AdverbRecord
        from .records.negation_record import NegationRecord
        from .records.noun_record import NounRecord
        from .records.phrase_record import PhraseRecord
        from .records.preposition_record import PrepositionRecord
        from .records.verb_record import VerbRecord

        # Use isinstance checks for proper type narrowing
        if record_type == "noun" and isinstance(record, NounRecord):
            from .models.noun import Noun

            return Noun(
                noun=record.noun,
                article=record.article,
                english=record.english,
                example=record.example,
                plural=record.plural,
            )

        elif record_type == "verb" and isinstance(record, VerbRecord):
            from .models.verb import Verb

            return Verb(
                verb=record.verb,
                english=record.english,
                present_ich=record.present_ich,
                present_du=record.present_du,
                present_er=record.present_er,
                perfect=record.perfect,
                example=record.example,
                classification=record.classification,
                präteritum=record.präteritum,
                auxiliary=record.auxiliary,
                separable=record.separable,
            )

        elif record_type == "adjective" and isinstance(record, AdjectiveRecord):
            from .models.adjective import Adjective

            return Adjective(
                word=record.word,  # AdjectiveRecord uses 'word' not 'adjective'
                english=record.english,
                example=record.example,
                comparative=record.comparative,
                superlative=record.superlative,
            )

        elif record_type == "adverb" and isinstance(record, AdverbRecord):
            from .models.adverb import Adverb, AdverbType

            # Convert string type to AdverbType enum
            adverb_type = AdverbType(record.type) if record.type else AdverbType.MANNER

            return Adverb(
                word=record.word,  # AdverbRecord uses 'word' not 'adverb'
                english=record.english,
                type=adverb_type,  # Required AdverbType parameter
                example=record.example,
            )

        elif record_type == "negation" and isinstance(record, NegationRecord):
            from .models.negation import Negation, NegationType

            # Convert string type to NegationType enum
            negation_type = (
                NegationType(record.type) if record.type else NegationType.GENERAL
            )

            return Negation(
                word=record.word,  # NegationRecord uses 'word' not 'negation'
                english=record.english,
                type=negation_type,  # Required NegationType parameter
                example=record.example,
            )

        elif record_type == "phrase" and isinstance(record, PhraseRecord):
            from .models.phrase import Phrase

            return Phrase(
                phrase=record.phrase,
                english=record.english,
                context=record.context,  # PhraseRecord uses 'context' not 'example'
                related=record.related,  # Required 'related' parameter
            )

        elif record_type == "preposition" and isinstance(record, PrepositionRecord):
            from .models.preposition import Preposition

            return Preposition(
                preposition=record.preposition,
                english=record.english,
                case=record.case,
                example1=record.example1,  # PrepositionRecord has example1/example2
                example2=record.example2,
            )

        else:
            supported_types = self.get_supported_record_types()
            raise ValueError(
                f"Unsupported record type '{record_type}' for German language "
                f"or incorrect record instance type. Supported types: {supported_types}"
            )
