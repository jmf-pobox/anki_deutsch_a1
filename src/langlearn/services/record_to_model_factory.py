"""Factory for converting Records to Domain Models.

This factory handles the conversion from lightweight Pydantic Records
(data containers) to rich Domain Models (business logic objects) for
media enrichment purposes.
"""

from __future__ import annotations

from langlearn.models.records import BaseRecord
from langlearn.protocols.media_generation_protocol import MediaGenerationCapable


class RecordToModelFactory:
    """Factory that converts Records to Domain Models for media enrichment."""

    @staticmethod
    def create_domain_model(record: BaseRecord) -> MediaGenerationCapable:
        """Convert a Record to its corresponding Domain Model.
        
        Args:
            record: Record object to convert
            
        Returns:
            Domain model implementing MediaGenerationCapable protocol
            
        Raises:
            ValueError: If record type cannot be converted to domain model
        """
        from langlearn.models.records import RecordType

        record_type = record.get_record_type()

        if record_type == RecordType.NOUN:
            return RecordToModelFactory._create_noun_model(record)
        elif record_type == RecordType.ADJECTIVE:
            return RecordToModelFactory._create_adjective_model(record)
        elif record_type == RecordType.ADVERB:
            return RecordToModelFactory._create_adverb_model(record)
        elif record_type == RecordType.NEGATION:
            return RecordToModelFactory._create_negation_model(record)
        elif record_type == RecordType.PHRASE:
            return RecordToModelFactory._create_phrase_model(record)
        elif record_type == RecordType.PREPOSITION:
            return RecordToModelFactory._create_preposition_model(record)
        elif record_type == RecordType.VERB:
            return RecordToModelFactory._create_verb_model(record)
        else:
            raise ValueError(
                f"Cannot create domain model for record type: {record_type}. "
                f"Domain model conversion not implemented for this type."
            )

    @staticmethod
    def _create_noun_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Noun domain model from NounRecord."""
        from langlearn.models.noun import Noun

        record_dict = record.to_dict()
        return Noun(
            noun=record_dict.get("noun", ""),
            article=record_dict.get("article", ""),
            english=record_dict.get("english", ""),
            plural=record_dict.get("plural", ""),
            example=record_dict.get("example", ""),
            related=record_dict.get("related", ""),
        )

    @staticmethod
    def _create_adjective_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Adjective domain model from AdjectiveRecord."""
        from langlearn.models.adjective import Adjective

        record_dict = record.to_dict()
        return Adjective(
            word=record_dict.get("word", ""),
            english=record_dict.get("english", ""),
            example=record_dict.get("example", ""),
            comparative=record_dict.get("comparative", ""),
            superlative=record_dict.get("superlative", ""),
        )

    @staticmethod
    def _create_adverb_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Adverb domain model from AdverbRecord."""
        from langlearn.models.adverb import Adverb

        record_dict = record.to_dict()
        return Adverb(
            word=record_dict.get("word", ""),
            english=record_dict.get("english", ""),
            type=record_dict.get("type", ""),
            example=record_dict.get("example", ""),
        )

    @staticmethod
    def _create_negation_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Negation domain model from NegationRecord."""
        from langlearn.models.negation import Negation

        record_dict = record.to_dict()
        return Negation(
            word=record_dict.get("word", ""),
            english=record_dict.get("english", ""),
            type=record_dict.get("type", ""),
            example=record_dict.get("example", ""),
        )

    @staticmethod
    def _create_phrase_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Phrase domain model from PhraseRecord."""
        from langlearn.models.phrase import Phrase

        record_dict = record.to_dict()
        return Phrase(
            phrase=record_dict.get("phrase", ""),
            english=record_dict.get("english", ""),
            context=record_dict.get("context", ""),
            related=record_dict.get("related", ""),
        )

    @staticmethod
    def _create_preposition_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Preposition domain model from PrepositionRecord."""
        from langlearn.models.preposition import Preposition

        record_dict = record.to_dict()
        return Preposition(
            preposition=record_dict.get("preposition", ""),
            english=record_dict.get("english", ""),
            case=record_dict.get("case", ""),
            example1=record_dict.get("example1", ""),
            example2=record_dict.get("example2", ""),
        )

    @staticmethod
    def _create_verb_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Verb domain model from VerbRecord."""
        from langlearn.models.verb import Verb

        record_dict = record.to_dict()
        return Verb(
            verb=record_dict.get("verb", ""),
            english=record_dict.get("english", ""),
            present_ich=record_dict.get("present_ich", ""),
            present_du=record_dict.get("present_du", ""),
            present_er=record_dict.get("present_er", ""),
            perfect=record_dict.get("perfect", ""),
            example=record_dict.get("example", ""),
        )
