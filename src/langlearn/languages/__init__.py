"""Multi-language support package.

This package provides language-specific implementations and the language registry
system for the multi-language Anki deck generator.
"""

from .german.language import GermanLanguage
from .korean.language import KoreanLanguage
from .registry import LanguageRegistry
from .russian.language import RussianLanguage

# Register German language
LanguageRegistry.register("de", GermanLanguage)
LanguageRegistry.register("german", GermanLanguage)  # Allow both codes

# Register Russian language
LanguageRegistry.register("ru", RussianLanguage)
LanguageRegistry.register("russian", RussianLanguage)  # Allow both codes

# Register Korean language
LanguageRegistry.register("ko", KoreanLanguage)
LanguageRegistry.register("korean", KoreanLanguage)  # Allow both codes

__all__ = [
    "GermanLanguage",
    "KoreanLanguage",
    "LanguageRegistry",
    "RussianLanguage",
]
