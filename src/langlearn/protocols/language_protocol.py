"""Language protocol for multi-language architecture."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol


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
        """Get record types this language supports (e.g., ['noun', 'verb', 'adjective'])."""
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