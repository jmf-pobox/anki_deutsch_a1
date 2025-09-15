"""Multi-language support package.

This package provides language-specific implementations and the language registry
system for the multi-language Anki deck generator.
"""

from .german.language import GermanLanguage
from .registry import LanguageRegistry

# Register German language
LanguageRegistry.register("de", GermanLanguage)
LanguageRegistry.register("german", GermanLanguage)  # Allow both codes

__all__ = [
    "GermanLanguage",
    "LanguageRegistry",
]
