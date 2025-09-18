"""German Record Factory for record-based architecture.

Provides factory methods for creating German record instances with type-safe
overloaded methods and centralized registry management."""

from typing import ClassVar, Literal, overload

from langlearn.core.records import BaseRecord, RecordClassProtocol, RecordType

from .adjective_record import AdjectiveRecord
from .adverb_record import AdverbRecord
from .article_record import ArticleRecord
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

# Export all record types, base classes, and factory for external imports
__all__ = [
    "AdjectiveRecord",
    "AdverbRecord",
    "ArticleRecord",
    "BaseRecord",
    "GermanRecordFactory",
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
    "create_record",  # Backward compatibility function
]


class GermanRecordFactory:
    """Factory class for creating German record instances with type safety."""

    # Registry for mapping model types to record classes
    _registry: ClassVar[dict[str, type[RecordClassProtocol]]] = {
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

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported record types."""
        return list(cls._registry.keys())

    @classmethod
    def is_supported_type(cls, model_type: str) -> bool:
        """Check if a model type is supported."""
        return model_type in cls._registry

    @classmethod
    @overload
    def create(cls, model_type: Literal["noun"], fields: list[str]) -> NounRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["adjective"], fields: list[str]
    ) -> AdjectiveRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["adverb"], fields: list[str]
    ) -> AdverbRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["negation"], fields: list[str]
    ) -> NegationRecord: ...

    @classmethod
    @overload
    def create(cls, model_type: Literal["verb"], fields: list[str]) -> VerbRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["phrase"], fields: list[str]
    ) -> PhraseRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["preposition"], fields: list[str]
    ) -> PrepositionRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["verb_conjugation"], fields: list[str]
    ) -> VerbConjugationRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["verb_imperative"], fields: list[str]
    ) -> VerbImperativeRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["article"], fields: list[str]
    ) -> ArticleRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["indefinite_article"], fields: list[str]
    ) -> IndefiniteArticleRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["negative_article"], fields: list[str]
    ) -> NegativeArticleRecord: ...

    @classmethod
    @overload
    def create(
        cls, model_type: Literal["unified_article"], fields: list[str]
    ) -> UnifiedArticleRecord: ...

    @classmethod
    @overload
    def create(cls, model_type: str, fields: list[str]) -> BaseRecord: ...

    @classmethod
    def create(cls, model_type: str, fields: list[str]) -> BaseRecord:
        """Create a German record instance from model type and CSV fields.

        Args:
            model_type: Type of model (noun, adjective, adverb, negation, verb,
                       phrase, preposition, verb_conjugation, verb_imperative,
                       article, indefinite_article, negative_article, unified_article)
            fields: CSV field values

        Returns:
            Record instance of the appropriate type

        Raises:
            ValueError: If model_type is unknown or fields are invalid
        """
        if not cls.is_supported_type(model_type):
            raise ValueError(
                f"Unknown model type: {model_type}. "
                f"Available: {cls.get_supported_types()}"
            )

        record_class = cls._registry[model_type]
        # Type ignore needed because mypy can't infer exact return type
        return record_class.from_csv_fields(fields)  # type: ignore[no-any-return, attr-defined]


# Backward compatibility function - delegates to factory
def create_record(model_type: str, fields: list[str]) -> BaseRecord:
    """Legacy factory function for backward compatibility.

    Use GermanRecordFactory.create() for new code.
    """
    return GermanRecordFactory.create(model_type, fields)


# Legacy registry access for backward compatibility
RECORD_TYPE_REGISTRY = GermanRecordFactory._registry
