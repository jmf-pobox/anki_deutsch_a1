"""Translation service for converting German text to English for image search.

This service provides high-quality German-to-English translation specifically optimized
for image search queries, improving Pexels API search results by using English terms
instead of German text.
"""

import logging
from typing import Protocol

from .anthropic_service import AnthropicService

logger = logging.getLogger(__name__)


class TranslationServiceProtocol(Protocol):
    """Protocol for translation services."""

    def translate_to_english(self, german_text: str | None) -> str | None:
        """Translate German text to English for image search.

        Args:
            german_text: German text to translate

        Returns:
            English translation optimized for image search
        """
        ...


class AnthropicTranslationService:
    """Translation service using Anthropic Claude for German-to-English translation.

    Optimized for converting German vocabulary examples and phrases into English
    search terms that work well with the Pexels image search API.
    """

    def __init__(self, anthropic_service: AnthropicService) -> None:
        """Initialize the translation service.

        Args:
            anthropic_service: Injected Anthropic service for API calls
        """
        self._anthropic_service = anthropic_service
        self._translation_cache: dict[str, str] = {}

    def translate_to_english(self, german_text: str | None) -> str | None:
        """Translate German text to English for optimal image search results.

        Uses Claude to provide high-quality translation that preserves the visual
        concepts needed for effective image searches.

        Args:
            german_text: German text to translate (sentence, phrase, or word)

        Returns:
            English translation optimized for image search

        Raises:
            Exception: If translation fails after retries
        """
        if not german_text or not german_text.strip():
            return german_text

        # Check cache first
        cache_key = german_text.strip().lower()
        if cache_key in self._translation_cache:
            logger.debug(f"Using cached translation for: {german_text}")
            return self._translation_cache[cache_key]

        try:
            # Create optimized prompt for image search translation
            prompt = self._create_translation_prompt(german_text)

            # Get translation from Anthropic
            translation = self._anthropic_service.generate_translation(
                prompt,
                max_tokens=100,
                temperature=0.1,  # Low temperature for consistent translations
            )

            # Clean and validate translation
            cleaned_translation = translation.strip()
            if not cleaned_translation:
                logger.warning(f"Empty translation received for: {german_text}")
                return german_text

            # Cache the result
            self._translation_cache[cache_key] = cleaned_translation

            logger.debug(f"Translated '{german_text}' → '{cleaned_translation}'")
            return cleaned_translation

        except Exception as e:
            logger.error(f"Translation failed for '{german_text}': {e}")
            # Return original text as fallback
            return german_text

    def _create_translation_prompt(self, german_text: str) -> str:
        """Create optimized prompt for image search translation.

        Args:
            german_text: German text to translate

        Returns:
            Prompt optimized for image search translation
        """
        return f"""Translate this German text to English, optimized for image search:

German: {german_text}

Requirements:
- Provide a natural English translation
- Focus on visual concepts that would work well for image searches
- Keep the core meaning and visual elements
- Use simple, clear English terms
- If it's a sentence, translate the whole sentence naturally

Output only the English translation, nothing else."""

    def clear_cache(self) -> None:
        """Clear the translation cache."""
        self._translation_cache.clear()
        logger.debug("Translation cache cleared")

    def get_cache_size(self) -> int:
        """Get the current cache size.

        Returns:
            Number of cached translations
        """
        return len(self._translation_cache)


class MockTranslationService:
    """Mock translation service for testing."""

    def __init__(self) -> None:
        """Initialize mock service."""
        self._mock_translations = {
            "ich gehe in die schule": "I go to school",
            "er spielt fußball": "he plays football",
            "sie kocht das essen": "she cooks the food",
            "das auto ist rot": "the car is red",
            "der hund läuft schnell": "the dog runs fast",
        }

    def translate_to_english(self, german_text: str | None) -> str | None:
        """Mock translation that returns predefined translations or original text.

        Args:
            german_text: German text to translate

        Returns:
            Mock English translation or original text
        """
        if not german_text:
            return german_text

        # Return mock translation if available, otherwise return original
        cache_key = german_text.strip().lower()
        return self._mock_translations.get(cache_key, german_text)
