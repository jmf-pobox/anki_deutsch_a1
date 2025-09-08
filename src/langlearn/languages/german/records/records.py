"""
Record types for the Clean Pipeline Architecture.

These are pure data containers that represent structured CSV data without
business logic. They serve as the intermediate representation between raw CSV
fields and domain models.
"""

from typing import Literal, overload

from .adjective_record import AdjectiveRecord
from .adverb_record import AdverbRecord
from .article_record import ArticleRecord
from .base import BaseRecord, RecordClassProtocol, RecordType
from .indefinite_article_record import IndefiniteArticleRecord
from .negation_record import NegationRecord
from .negative_article_record import NegativeArticleRecord
from .noun_record import NounRecord
from .phrase_record import PhraseRecord
from .preposition_record import PrepositionRecord
from .unified_article_record import UnifiedArticleRecord
from .verb_conjugation_record import VerbConjugationRecord
from .verb_imperative_record import VerbImperativeRecord
from .verb_record import VerbRecord

# Export all record types and base classes for external imports
__all__ = [
    "AdjectiveRecord",
    "AdverbRecord",
    "ArticleRecord",
    "BaseRecord",
    "IndefiniteArticleRecord",
    "NegationRecord",
    "NegativeArticleRecord",
    "NounRecord",
    "PhraseRecord",
    "PrepositionRecord",
    "RecordClassProtocol",
    "RecordType",
    "UnifiedArticleRecord",
    "VerbConjugationRecord",
    "VerbImperativeRecord",
    "VerbRecord",
]


# Registry for mapping model types to record types
RECORD_TYPE_REGISTRY: dict[str, type[RecordClassProtocol]] = {
    "noun": NounRecord,
    "adjective": AdjectiveRecord,
    "adverb": AdverbRecord,
    "negation": NegationRecord,
    "verb": VerbRecord,
    "phrase": PhraseRecord,
    "preposition": PrepositionRecord,
    "verb_conjugation": VerbConjugationRecord,
    "verb_imperative": VerbImperativeRecord,
    "article": ArticleRecord,
    "indefinite_article": IndefiniteArticleRecord,
    "negative_article": NegativeArticleRecord,
    "unified_article": UnifiedArticleRecord,
}


@overload
def create_record(model_type: Literal["noun"], fields: list[str]) -> NounRecord: ...


@overload
def create_record(
    model_type: Literal["adjective"], fields: list[str]
) -> AdjectiveRecord: ...


@overload
def create_record(model_type: Literal["adverb"], fields: list[str]) -> AdverbRecord: ...


@overload
def create_record(
    model_type: Literal["negation"], fields: list[str]
) -> NegationRecord: ...


@overload
def create_record(model_type: Literal["verb"], fields: list[str]) -> VerbRecord: ...


@overload
def create_record(model_type: Literal["phrase"], fields: list[str]) -> PhraseRecord: ...


@overload
def create_record(
    model_type: Literal["preposition"], fields: list[str]
) -> PrepositionRecord: ...


@overload
def create_record(
    model_type: Literal["verb_conjugation"], fields: list[str]
) -> VerbConjugationRecord: ...


@overload
def create_record(
    model_type: Literal["verb_imperative"], fields: list[str]
) -> VerbImperativeRecord: ...


@overload
def create_record(
    model_type: Literal["article"], fields: list[str]
) -> ArticleRecord: ...


@overload
def create_record(
    model_type: Literal["indefinite_article"], fields: list[str]
) -> IndefiniteArticleRecord: ...


@overload
def create_record(
    model_type: Literal["negative_article"], fields: list[str]
) -> NegativeArticleRecord: ...


@overload
def create_record(model_type: str, fields: list[str]) -> BaseRecord: ...


def create_record(model_type: str, fields: list[str]) -> BaseRecord:
    """Factory function to create records from model type and CSV fields.

    Args:
        model_type: Type of model (noun, adjective, adverb, negation,
                   verb, phrase, preposition, verb_conjugation, verb_imperative,
                   article, indefinite_article, negative_article)
        fields: CSV field values

    Returns:
        Record instance of the appropriate type

    Raises:
        ValueError: If model_type is unknown or fields are invalid
    """
    if model_type not in RECORD_TYPE_REGISTRY:
        raise ValueError(
            f"Unknown model type: {model_type}. "
            f"Available: {list(RECORD_TYPE_REGISTRY.keys())}"
        )

    record_class = RECORD_TYPE_REGISTRY[model_type]
    # Type ignore needed because mypy can't infer the exact return type from registry
    return record_class.from_csv_fields(fields)  # type: ignore
