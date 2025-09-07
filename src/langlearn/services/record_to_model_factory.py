"""Factory for converting Records to Domain Models.

This factory handles the conversion from lightweight Pydantic Records
(data containers) to rich Domain Models (business logic objects) for
media enrichment purposes.
"""

from __future__ import annotations

from langlearn.languages.german.records.records import BaseRecord
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
        from langlearn.languages.german.records.records import RecordType

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
        elif record_type == RecordType.VERB_CONJUGATION:
            return RecordToModelFactory._create_verb_conjugation_model(record)
        elif record_type == RecordType.VERB_IMPERATIVE:
            return RecordToModelFactory._create_verb_imperative_model(record)
        elif record_type == RecordType.UNIFIED_ARTICLE:
            return RecordToModelFactory._create_unified_article_model(record)
        else:
            raise ValueError(
                f"Cannot create domain model for record type: {record_type}. "
                f"Domain model conversion not implemented for this type."
            )

    @staticmethod
    def _create_noun_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Noun domain model from NounRecord."""
        from langlearn.languages.german.models.noun import Noun

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
        from langlearn.languages.german.models.adjective import Adjective

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
        from langlearn.languages.german.models.adverb import (
            GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP,
            Adverb,
            AdverbType,
        )

        record_dict = record.to_dict()
        type_str = record_dict.get("type", "")

        # Convert type string to AdverbType enum
        adverb_type = GERMAN_TO_ENGLISH_ADVERB_TYPE_MAP.get(type_str, AdverbType.MANNER)

        return Adverb(
            word=record_dict.get("word", ""),
            english=record_dict.get("english", ""),
            type=adverb_type,
            example=record_dict.get("example", ""),
        )

    @staticmethod
    def _create_negation_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Negation domain model from NegationRecord."""
        from langlearn.languages.german.models.negation import Negation, NegationType

        record_dict = record.to_dict()
        type_str = record_dict.get("type", "")

        # Convert type string to NegationType enum
        try:
            negation_type = NegationType(type_str)
        except ValueError:
            # Default to GENERAL if type string doesn't match any enum value
            negation_type = NegationType.GENERAL

        return Negation(
            word=record_dict.get("word", ""),
            english=record_dict.get("english", ""),
            type=negation_type,
            example=record_dict.get("example", ""),
        )

    @staticmethod
    def _create_phrase_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Phrase domain model from PhraseRecord."""
        from langlearn.languages.german.models.phrase import Phrase

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
        from langlearn.languages.german.models.preposition import Preposition

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
        from langlearn.languages.german.models.verb import Verb

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

    @staticmethod
    def _create_verb_conjugation_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Verb domain model from VerbConjugationRecord."""
        from langlearn.languages.german.models.verb import Verb

        record_dict = record.to_dict()
        # VerbConjugationRecord has infinitive, not verb field
        infinitive = record_dict.get("infinitive", record_dict.get("verb", ""))
        tense = record_dict.get("tense", "")

        # Handle imperative tense records specially
        if tense == "imperative":
            # For imperative, use the actual imperative forms instead of present tense
            # Imperative CSV structure: ,,fahr ab,,fahren wir ab,fahrt ab,fahren Sie ab,
            return Verb(
                verb=infinitive,
                english=record_dict.get("english", ""),
                # For imperative, use imperative forms in present fields for audio
                present_ich="[imperative]",  # No ich form for imperative
                present_du=record_dict.get("du", ""),  # du imperative form
                present_er="[imperative]",  # No er form for imperative
                perfect="[imperative]",  # No perfect for imperative
                example=record_dict.get("example", ""),
            )
        else:
            # Handle regular conjugation (present, perfect, preterite)
            # Construct perfect form from auxiliary + past participle (placeholder)
            auxiliary = record_dict.get("auxiliary", "haben")
            # Create a simple past participle form (this is a simplification)
            past_participle = (
                f"ge{infinitive[:-2]}t"
                if infinitive.endswith("en")
                else f"ge{infinitive}t"
            )
            perfect_form = f"{auxiliary} {past_participle}"

            return Verb(
                verb=infinitive,
                english=record_dict.get("english", ""),
                present_ich=record_dict.get("ich", ""),
                present_du=record_dict.get("du", ""),
                present_er=record_dict.get("er", ""),  # Use "er", not "er_sie_es"
                perfect=perfect_form,
                example=record_dict.get("example", ""),  # Use "example", not "beispiel"
            )

    @staticmethod
    def _create_verb_imperative_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Verb domain model from VerbImperativeRecord."""
        from langlearn.languages.german.models.verb import Verb

        record_dict = record.to_dict()
        # VerbImperativeRecord has infinitive field
        infinitive = record_dict.get("infinitive", record_dict.get("verb", ""))
        # VerbImperativeRecord has example_du, example_ihr, example_sie (no beispiel)
        example_text = record_dict.get("example_du", record_dict.get("example", ""))

        return Verb(
            verb=infinitive,
            english=record_dict.get("english", ""),
            present_ich="[imperative]",  # Placeholder: no ich form
            present_du=record_dict.get("du", ""),  # Use 'du' not 'du_imperative'
            present_er="[imperative]",  # Placeholder: no er form
            perfect="[imperative]",  # Placeholder: no perfect
            example=example_text,
        )

    @staticmethod
    def _create_unified_article_model(record: BaseRecord) -> MediaGenerationCapable:
        """Create Article domain model from UnifiedArticleRecord."""
        from langlearn.languages.german.models.article import Article

        record_dict = record.to_dict()

        return Article(
            artikel_typ=record_dict.get("artikel_typ", "bestimmt"),
            geschlecht=record_dict.get("geschlecht", "maskulin"),
            nominativ=record_dict.get("nominativ", ""),
            akkusativ=record_dict.get("akkusativ", ""),
            dativ=record_dict.get("dativ", ""),
            genitiv=record_dict.get("genitiv", ""),
            beispiel_nom=record_dict.get("beispiel_nom", ""),
            beispiel_akk=record_dict.get("beispiel_akk", ""),
            beispiel_dat=record_dict.get("beispiel_dat", ""),
            beispiel_gen=record_dict.get("beispiel_gen", ""),
        )
