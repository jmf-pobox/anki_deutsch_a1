"""Language protocol for multi-language architecture."""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from langlearn.core.records import BaseRecord
    from langlearn.protocols.domain_model_protocol import LanguageDomainModel


class Language(Protocol):
    """Protocol defining what each language must implement."""

    @property
    @abstractmethod
    def code(self) -> str:
        """ISO language code (e.g., 'de', 'ru', 'ko')."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable language name (e.g., 'German', 'Russian', 'Korean')."""
        ...

    @abstractmethod
    def get_supported_record_types(self) -> list[str]:
        """Get record types this language supports (e.g., ['noun', 'verb'])."""
        ...

    @abstractmethod
    def get_card_builder(self) -> Any:
        """Get the card builder for this language."""
        ...

    @abstractmethod
    def get_grammar_service(self) -> Any:
        """Get language-specific grammar service."""
        ...

    @abstractmethod
    def get_record_mapper(self) -> Any:
        """Get language-specific record mapper."""
        ...

    @abstractmethod
    def get_template_path(self, record_type: str, side: str) -> str:
        """Get template path for record type and side (front/back)."""
        ...

    @abstractmethod
    def get_template_filename(self, card_type: str, side: str) -> str:
        """Get template filename for card type and side."""
        ...

    @abstractmethod
    def get_template_directory(self) -> Path:
        """Get the templates directory for this language."""
        ...

    @abstractmethod
    def create_domain_model(
        self, record_type: str, record: BaseRecord
    ) -> LanguageDomainModel:
        """Create language-specific domain model from record.

        Args:
            record_type: Type of record (noun, verb, adjective, etc.)
            record: Validated record data from CSV

        Returns:
            Language-specific domain model implementing LanguageDomainModel protocol

        Raises:
            ValueError: If record_type is not supported by this language
        """
        ...
