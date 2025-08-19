"""
Tests for AnkiBackend delegation to domain models via ModelFactory.

This module tests that AnkiBackend correctly delegates field processing
to appropriate domain models for all 6 German word types.
"""

from unittest.mock import Mock, patch

import pytest

from langlearn.backends.anki_backend import AnkiBackend


class TestAnkiBackendDomainDelegation:
    """Test AnkiBackend delegation to domain models via ModelFactory."""

    def test_delegation_to_adjective_model(self) -> None:
        """Test field processing delegation to Adjective model."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            # Mock ModelFactory to return an Adjective processor
            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "schön",
                    "beautiful",
                    "processed_example",
                ]
                mock_factory.return_value = mock_processor

                fields = ["schön", "beautiful", "original_example"]
                result = backend._process_fields_with_media("German Adjective", fields)

                # Verify delegation occurred
                mock_factory.assert_called_once_with("German Adjective")
                mock_processor.process_fields_for_media_generation.assert_called_once_with(
                    fields, backend._domain_media_generator
                )
                assert result == ["schön", "beautiful", "processed_example"]

    def test_delegation_to_noun_model(self) -> None:
        """Test field processing delegation to Noun model."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "der",
                    "Hund",
                    "dog",
                    "processed_field",
                ]
                mock_factory.return_value = mock_processor

                fields = ["der", "Hund", "dog", "original_field"]
                result = backend._process_fields_with_media("German Noun", fields)

                mock_factory.assert_called_once_with("German Noun")
                assert result == ["der", "Hund", "dog", "processed_field"]

    def test_delegation_to_verb_model(self) -> None:
        """Test field processing delegation to Verb model."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "gehen",
                    "to go",
                    "ich gehe",
                    "processed_conjugation",
                ]
                mock_factory.return_value = mock_processor

                fields = ["gehen", "to go", "ich gehe", "original_conjugation"]
                result = backend._process_fields_with_media("German Verb", fields)

                mock_factory.assert_called_once_with("German Verb")
                assert result == ["gehen", "to go", "ich gehe", "processed_conjugation"]

    def test_delegation_to_adverb_model(self) -> None:
        """Test field processing delegation to Adverb model."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "schnell",
                    "quickly",
                    "processed_example",
                ]
                mock_factory.return_value = mock_processor

                fields = ["schnell", "quickly", "original_example"]
                result = backend._process_fields_with_media("German Adverb", fields)

                mock_factory.assert_called_once_with("German Adverb")
                assert result == ["schnell", "quickly", "processed_example"]

    def test_delegation_to_negation_model(self) -> None:
        """Test field processing delegation to Negation model."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "nicht",
                    "not",
                    "processed_example",
                ]
                mock_factory.return_value = mock_processor

                fields = ["nicht", "not", "original_example"]
                result = backend._process_fields_with_media("German Negation", fields)

                mock_factory.assert_called_once_with("German Negation")
                assert result == ["nicht", "not", "processed_example"]

    def test_delegation_to_preposition_model(self) -> None:
        """Test field processing delegation to Preposition model."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "mit",
                    "with",
                    "Dativ",
                    "processed_example",
                ]
                mock_factory.return_value = mock_processor

                fields = ["mit", "with", "Dativ", "original_example"]
                result = backend._process_fields_with_media(
                    "German Preposition", fields
                )

                mock_factory.assert_called_once_with("German Preposition")
                assert result == ["mit", "with", "Dativ", "processed_example"]

    def test_delegation_to_phrase_model(self) -> None:
        """Test field processing delegation to Phrase model."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "Guten Tag",
                    "Good day",
                    "processed_context",
                ]
                mock_factory.return_value = mock_processor

                fields = ["Guten Tag", "Good day", "original_context"]
                result = backend._process_fields_with_media("German Phrase", fields)

                mock_factory.assert_called_once_with("German Phrase")
                assert result == ["Guten Tag", "Good day", "processed_context"]

    def test_all_six_word_types_with_case_insensitive_detection(self) -> None:
        """Test all 6 German word types with case-insensitive note type detection."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            # Test cases with different capitalizations
            test_cases = [
                ("GERMAN ADJECTIVE", "adjective"),
                ("german noun", "noun"),
                ("German Verb", "verb"),
                ("GERMAN ADVERB", "adverb"),
                ("german negation", "negation"),
                ("German Preposition", "preposition"),
                ("GERMAN PHRASE", "phrase"),
            ]

            for note_type_name, _expected_type in test_cases:
                with patch(
                    "langlearn.models.model_factory.ModelFactory.create_field_processor"
                ) as mock_factory:
                    mock_processor = Mock()
                    mock_processor.process_fields_for_media_generation.return_value = [
                        "processed"
                    ]
                    mock_factory.return_value = mock_processor

                    result = backend._process_fields_with_media(
                        note_type_name, ["original"]
                    )

                    # Verify factory was called with the original name
                    mock_factory.assert_called_once_with(note_type_name)
                    assert result == ["processed"]

    def test_unsupported_note_type_returns_original_fields(self) -> None:
        """Test that unsupported note types return original fields unchanged."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            # Mock factory to return None (unsupported type)
            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor",
                return_value=None,
            ):
                original_fields = ["field1", "field2", "field3"]
                result = backend._process_fields_with_media(
                    "Unsupported Type", original_fields
                )

                # Should return original fields unchanged
                assert result == original_fields

    def test_domain_media_generator_is_passed_correctly(self) -> None:
        """Test that DomainMediaGenerator is passed correctly to field processors."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "processed"
                ]
                mock_factory.return_value = mock_processor

                backend._process_fields_with_media("German Noun", ["test"])

                # Verify the domain media generator was passed
                mock_processor.process_fields_for_media_generation.assert_called_once_with(
                    ["test"], backend._domain_media_generator
                )
                # Verify the domain media generator exists and has expected services
                assert hasattr(backend._domain_media_generator, "_media_service")

    def test_error_handling_during_delegation(self) -> None:
        """Test error handling when field processor raises exception."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                # Mock processor that raises an exception
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.side_effect = (
                    Exception("Processing error")
                )
                mock_factory.return_value = mock_processor

                original_fields = ["field1", "field2"]
                result = backend._process_fields_with_media(
                    "German Adjective", original_fields
                )

                # Should return original fields on exception
                assert result == original_fields

    def test_mixed_note_type_names_with_multiple_keywords(self) -> None:
        """Test note type names that might contain multiple keywords."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            # Test case where note type name contains multiple keywords
            # Factory should match first keyword in create_field_processor order
            test_cases = [
                "German Adjective and Noun",  # Should match adjective (comes first)
                "Verb Phrase Example",  # Should match verb (comes first)
                "Noun with Preposition",  # Should match noun (comes first)
            ]

            for note_type_name in test_cases:
                with patch(
                    "langlearn.models.model_factory.ModelFactory.create_field_processor"
                ) as mock_factory:
                    mock_processor = Mock()
                    mock_processor.process_fields_for_media_generation.return_value = [
                        "processed"
                    ]
                    mock_factory.return_value = mock_processor

                    result = backend._process_fields_with_media(
                        note_type_name, ["original"]
                    )

                    # Verify delegation occurred
                    mock_factory.assert_called_once_with(note_type_name)
                    assert result == ["processed"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
