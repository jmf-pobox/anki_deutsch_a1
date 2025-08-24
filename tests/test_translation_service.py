"""Tests for translation service functionality."""

from unittest.mock import Mock, patch

from langlearn.services.translation_service import (
    AnthropicTranslationService,
    MockTranslationService,
)


class TestAnthropicTranslationService:
    """Test cases for AnthropicTranslationService."""

    def test_translate_to_english_success(self) -> None:
        """Test successful translation from German to English."""
        # Arrange
        mock_anthropic = Mock()
        mock_anthropic._generate_response.return_value = "I go to school"
        service = AnthropicTranslationService(mock_anthropic)

        # Act
        result = service.translate_to_english("Ich gehe in die Schule")

        # Assert
        assert result == "I go to school"
        mock_anthropic._generate_response.assert_called_once()

        # Check that the prompt contains the German text
        call_args = mock_anthropic._generate_response.call_args
        prompt = call_args[0][0]
        assert "Ich gehe in die Schule" in prompt
        assert "Translate this German text to English" in prompt

    def test_translate_empty_text_returns_original(self) -> None:
        """Test that empty text returns original without API call."""
        # Arrange
        mock_anthropic = Mock()
        service = AnthropicTranslationService(mock_anthropic)

        # Act & Assert
        assert service.translate_to_english("") == ""
        assert service.translate_to_english("   ") == "   "
        assert service.translate_to_english(None) is None

        # No API calls should be made
        mock_anthropic._generate_response.assert_not_called()

    def test_translate_caches_results(self) -> None:
        """Test that translation results are cached."""
        # Arrange
        mock_anthropic = Mock()
        mock_anthropic._generate_response.return_value = "I go to school"
        service = AnthropicTranslationService(mock_anthropic)

        # Act - translate same text twice
        result1 = service.translate_to_english("Ich gehe in die Schule")
        result2 = service.translate_to_english("Ich gehe in die Schule")

        # Assert
        assert result1 == "I go to school"
        assert result2 == "I go to school"
        # API should only be called once due to caching
        mock_anthropic._generate_response.assert_called_once()

    def test_translate_case_insensitive_cache(self) -> None:
        """Test that cache is case-insensitive."""
        # Arrange
        mock_anthropic = Mock()
        mock_anthropic._generate_response.return_value = "I go to school"
        service = AnthropicTranslationService(mock_anthropic)

        # Act - translate with different cases
        result1 = service.translate_to_english("Ich gehe in die Schule")
        result2 = service.translate_to_english("ICH GEHE IN DIE SCHULE")

        # Assert
        assert result1 == "I go to school"
        assert result2 == "I go to school"
        # API should only be called once due to case-insensitive caching
        mock_anthropic._generate_response.assert_called_once()

    def test_translate_api_failure_returns_original(self) -> None:
        """Test that API failure returns original German text."""
        # Arrange
        mock_anthropic = Mock()
        mock_anthropic._generate_response.side_effect = Exception("API Error")
        service = AnthropicTranslationService(mock_anthropic)

        # Act
        result = service.translate_to_english("Ich gehe in die Schule")

        # Assert
        assert result == "Ich gehe in die Schule"  # Original text returned

    def test_translate_empty_response_returns_original(self) -> None:
        """Test that empty API response returns original text."""
        # Arrange
        mock_anthropic = Mock()
        mock_anthropic._generate_response.return_value = ""
        service = AnthropicTranslationService(mock_anthropic)

        # Act
        result = service.translate_to_english("Ich gehe in die Schule")

        # Assert
        assert result == "Ich gehe in die Schule"  # Original text returned

    def test_clear_cache(self) -> None:
        """Test cache clearing functionality."""
        # Arrange
        mock_anthropic = Mock()
        mock_anthropic._generate_response.return_value = "I go to school"
        service = AnthropicTranslationService(mock_anthropic)

        # Act - translate, clear cache, translate again
        service.translate_to_english("Ich gehe in die Schule")
        service.clear_cache()
        service.translate_to_english("Ich gehe in die Schule")

        # Assert - API should be called twice (cache was cleared)
        assert mock_anthropic._generate_response.call_count == 2

    def test_get_cache_size(self) -> None:
        """Test cache size tracking."""
        # Arrange
        mock_anthropic = Mock()
        mock_anthropic._generate_response.return_value = "Translation"
        service = AnthropicTranslationService(mock_anthropic)

        # Act & Assert
        assert service.get_cache_size() == 0

        service.translate_to_english("Text 1")
        assert service.get_cache_size() == 1

        service.translate_to_english("Text 2")
        assert service.get_cache_size() == 2

        service.clear_cache()
        assert service.get_cache_size() == 0

    def test_create_translation_prompt(self) -> None:
        """Test translation prompt creation."""
        # Arrange
        mock_anthropic = Mock()
        service = AnthropicTranslationService(mock_anthropic)

        # Act
        prompt = service._create_translation_prompt("Ich gehe in die Schule")

        # Assert
        assert "Ich gehe in die Schule" in prompt
        assert "Translate this German text to English" in prompt
        assert "optimized for image search" in prompt
        assert "visual concepts" in prompt
        assert "Output only the English translation" in prompt


class TestMockTranslationService:
    """Test cases for MockTranslationService."""

    def test_mock_translate_known_phrases(self) -> None:
        """Test mock translation of known phrases."""
        # Arrange
        service = MockTranslationService()

        # Act & Assert
        assert (
            service.translate_to_english("Ich gehe in die Schule") == "I go to school"
        )
        assert service.translate_to_english("Er spielt Fußball") == "he plays football"
        assert (
            service.translate_to_english("Sie kocht das Essen") == "she cooks the food"
        )

    def test_mock_translate_case_insensitive(self) -> None:
        """Test mock translation is case insensitive."""
        # Arrange
        service = MockTranslationService()

        # Act & Assert
        assert (
            service.translate_to_english("ICH GEHE IN DIE SCHULE") == "I go to school"
        )
        assert (
            service.translate_to_english("ich gehe in die schule") == "I go to school"
        )

    def test_mock_translate_unknown_returns_original(self) -> None:
        """Test mock translation returns original for unknown phrases."""
        # Arrange
        service = MockTranslationService()

        # Act & Assert
        assert service.translate_to_english("Unknown phrase") == "Unknown phrase"
        assert service.translate_to_english("") == ""

    def test_mock_translate_none_returns_none(self) -> None:
        """Test mock translation handles None input."""
        # Arrange
        service = MockTranslationService()

        # Act & Assert
        assert service.translate_to_english(None) is None


class TestTranslationServiceIntegration:
    """Integration tests for translation service with MediaEnricher."""

    @patch("langlearn.services.translation_service.logger")
    def test_translation_service_logging(self, mock_logger: Mock) -> None:
        """Test that translation service logs appropriately."""
        # Arrange
        mock_anthropic = Mock()
        mock_anthropic._generate_response.return_value = "I go to school"
        service = AnthropicTranslationService(mock_anthropic)

        # Act
        service.translate_to_english("Ich gehe in die Schule")

        # Assert - debug logging should occur
        mock_logger.debug.assert_called()

    def test_translation_service_with_real_examples(self) -> None:
        """Test translation service with real German examples from our data."""
        # Arrange
        mock_anthropic = Mock()
        service = AnthropicTranslationService(mock_anthropic)

        # Real examples from our CSV data
        test_cases = [
            ("Ich gehe in die Schule.", "I go to school."),
            ("Er spielt Fußball.", "He plays football."),
            ("Sie kocht das Essen.", "She cooks the food."),
            ("Das Auto ist rot.", "The car is red."),
            ("Der Hund läuft schnell.", "The dog runs fast."),
        ]

        for german_text, expected_english in test_cases:
            # Arrange
            mock_anthropic._generate_response.return_value = expected_english

            # Act
            result = service.translate_to_english(german_text)

            # Assert
            assert result == expected_english

            # Reset mock for next iteration
            mock_anthropic.reset_mock()
