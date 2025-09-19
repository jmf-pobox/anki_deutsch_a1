"""Central registry for available languages."""

from __future__ import annotations

from typing import ClassVar

from langlearn.core.protocols.language_protocol import Language


class LanguageRegistry:
    """Central registry for available languages."""

    _languages: ClassVar[dict[str, type[Language]]] = {}

    @classmethod
    def register(cls, language_code: str, language_class: type[Language]) -> None:
        """Register a language implementation."""
        cls._languages[language_code] = language_class

    @classmethod
    def get(cls, language_code: str) -> Language:
        """Get a language implementation by code."""
        if language_code not in cls._languages:
            raise ValueError(f"Language {language_code} not registered")
        return cls._languages[language_code]()

    @classmethod
    def list_available(cls) -> list[str]:
        """List all registered language codes."""
        return list(cls._languages.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered languages (useful for testing)."""
        cls._languages.clear()
