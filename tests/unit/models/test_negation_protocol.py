"""Tests for Negation model MediaGenerationCapable protocol compliance."""

from unittest.mock import Mock

import pytest

from langlearn.exceptions import MediaGenerationError
from langlearn.models.negation import Negation, NegationType
from langlearn.protocols import MediaGenerationCapable
from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)


class TestNegationProtocolCompliance:
    """Test that Negation implements MediaGenerationCapable protocol."""

    def test_negation_satisfies_protocol(self) -> None:
        """Test that Negation instance satisfies MediaGenerationCapable protocol."""
        negation = Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="Ich bin nicht müde.",
        )

        # This should pass with @runtime_checkable protocol
        assert isinstance(negation, MediaGenerationCapable)

    def test_protocol_method_implementation(self) -> None:
        """Test that Negation implements required protocol methods."""
        negation = Negation(
            word="kein",
            english="no",
            type=NegationType.ARTICLE,
            example="Ich habe kein Auto.",
        )

        # Test get_image_search_strategy returns callable with mock service
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mock search terms"

        strategy = negation.get_image_search_strategy(mock_service)
        assert callable(strategy)

        # Test get_combined_audio_text returns string
        audio_text = negation.get_combined_audio_text()
        assert isinstance(audio_text, str)
        assert audio_text == "kein. Ich habe kein Auto."

    def test_protocol_with_dependency_injection(self) -> None:
        """Test protocol works with dependency injection pattern."""

        def use_media_capable(
            obj: MediaGenerationCapable, service: ImageQueryGenerationProtocol
        ) -> tuple[str, str]:
            """Function that uses MediaGenerationCapable protocol."""
            strategy = obj.get_image_search_strategy(service)
            audio_text = obj.get_combined_audio_text()
            return strategy(), audio_text

        negation = Negation(
            word="niemand",
            english="nobody",
            type=NegationType.PRONOUN,
            example="Niemand ist hier.",
        )

        # Create mock service that fails - should raise exception
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        # Should raise MediaGenerationError when service fails (images required)
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for negation 'niemand'",
        ):
            use_media_capable(negation, mock_service)

    def test_protocol_with_mock_anthropic_service(self) -> None:
        """Test protocol works with mock Anthropic service injection."""
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mocked search terms"

        negation = Negation(
            word="nie",
            english="never",
            type=NegationType.TEMPORAL,
            example="Ich gehe nie ins Kino.",
        )

        strategy = negation.get_image_search_strategy(mock_service)
        result = strategy()

        assert result == "mocked search terms"
        mock_service.generate_image_query.assert_called_once()

    def test_context_building_for_general_negation(self) -> None:
        """Test that general negations build appropriate context."""
        negation = Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="Das ist nicht richtig.",
        )

        context = negation._build_search_context()

        # Check that context contains negation information
        assert "nicht" in context
        assert "not" in context
        assert "general negation" in context
        assert "Das ist nicht richtig" in context

        # Check general negation strategy
        assert "prohibition symbols" in context
        assert "stop signs" in context
        assert "crossed-out imagery" in context

    def test_context_building_for_temporal_negation(self) -> None:
        """Test that temporal negations build appropriate context."""
        negation = Negation(
            word="nie",
            english="never",
            type=NegationType.TEMPORAL,
            example="Ich komme nie zu spät.",
        )

        context = negation._build_search_context()

        # Check that context contains negation information
        assert "nie" in context
        assert "never" in context
        assert "temporal negation" in context

        # Check temporal negation strategy
        assert "time-related imagery" in context
        assert "clocks with X marks" in context
        assert "calendars crossed out" in context

    def test_context_building_for_pronoun_negation(self) -> None:
        """Test that pronoun negations build appropriate context."""
        negation = Negation(
            word="niemand",
            english="nobody",
            type=NegationType.PRONOUN,
            example="Niemand war da.",
        )

        context = negation._build_search_context()

        # Check that context contains negation information
        assert "niemand" in context
        assert "nobody" in context
        assert "pronoun negation" in context

        # Check pronoun negation strategy
        assert "emptiness or void" in context
        assert "silhouettes" in context
        assert "empty chairs" in context

    def test_service_failure_raises_error_for_all_types(self) -> None:
        """Test service failure raises error for all negation types."""
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        test_cases = [
            ("nothing", "nichts"),
            ("nobody", "niemand"),
            ("never", "nie"),
            ("nowhere", "nirgends"),
        ]

        for english, german in test_cases:
            negation = Negation(
                word=german,
                english=english,
                type=NegationType.GENERAL,
                example=f"Test {german}.",
            )

            strategy = negation.get_image_search_strategy(mock_service)

            # Should raise MediaGenerationError when service fails
            with pytest.raises(
                MediaGenerationError,
                match=f"Failed to generate image search for negation '{german}'",
            ):
                strategy()

    def test_service_exception_raises_error(self) -> None:
        """Test exception when service fails."""
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        # Use an english translation that won't match any concept mappings
        negation = Negation(
            word="überhaupt",
            english="at all",  # No specific concept mapping
            type=NegationType.INTENSIFIER,
            example="Das gefällt mir überhaupt nicht.",
        )

        strategy = negation.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError when service fails
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for negation 'überhaupt'",
        ):
            strategy()

    def test_negation_type_strategies(self) -> None:
        """Test that different negation types get appropriate strategies."""
        type_test_cases = [
            (NegationType.GENERAL, "prohibition symbols"),
            (NegationType.ARTICLE, "absence or lack of objects"),
            (NegationType.PRONOUN, "emptiness or void"),
            (NegationType.TEMPORAL, "time-related imagery"),
            (NegationType.SPATIAL, "empty locations"),
            (NegationType.CORRELATIVE, "choice rejection"),
            (NegationType.INTENSIFIER, "Emphasize prohibition strongly"),
        ]

        for neg_type, expected_strategy in type_test_cases:
            negation = Negation(
                word="test",
                english="test",
                type=neg_type,
                example="Test sentence.",
            )

            context = negation._build_search_context()
            assert expected_strategy in context

    def test_audio_text_format(self) -> None:
        """Test that combined audio text follows the correct format."""
        test_cases = [
            ("nicht", "Ich bin nicht da.", "nicht. Ich bin nicht da."),
            ("kein", "Kein Problem.", "kein. Kein Problem."),
            ("niemand", "Niemand weiß das.", "niemand. Niemand weiß das."),
            ("nie", "Ich bin nie müde.", "nie. Ich bin nie müde."),
        ]

        for word, example, expected in test_cases:
            negation = Negation(
                word=word,
                english="test",
                type=NegationType.GENERAL,
                example=example,
            )

            assert negation.get_combined_audio_text() == expected

    def test_context_includes_abstract_concept_explanation(self) -> None:
        """Test that context explains negation as abstract concept needing symbols."""
        negation = Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="Das stimmt nicht.",
        )

        context = negation._build_search_context()

        # Should explain the visualization challenge
        assert "abstract concepts representing absence" in context
        assert "symbolic or metaphorical representation" in context
        assert "prohibition, absence, or negation concepts" in context

    def test_empty_service_result_raises_error(self) -> None:
        """Test exception when service returns empty result."""
        mock_service = Mock()
        mock_service.generate_image_query.return_value = ""  # Empty result

        negation = Negation(
            word="nicht",
            english="not",
            type=NegationType.GENERAL,
            example="Das ist nicht gut.",
        )

        strategy = negation.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError for empty result
        with pytest.raises(
            MediaGenerationError,
            match="AI service returned empty image search query for negation 'nicht'",
        ):
            strategy()
