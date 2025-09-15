"""German language implementation for multi-language architecture."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langlearn.protocols.language_protocol import Language


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