"""Tests for Adjective model MediaGenerationCapable protocol compliance."""

from unittest.mock import Mock

import pytest

from langlearn.exceptions import MediaGenerationError
from langlearn.languages.german.models.adjective import Adjective
from langlearn.protocols import MediaGenerationCapable
from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)


class TestAdjectiveProtocolCompliance:
    """Test that Adjective implements MediaGenerationCapable protocol."""

    def test_adjective_satisfies_protocol(self) -> None:
        """Test that Adjective instance satisfies MediaGenerationCapable protocol."""
        adjective = Adjective(
            word="schön",
            english="beautiful",
            example="Das Haus ist sehr schön.",
            comparative="schöner",
            superlative="am schönsten",
        )

        # This should pass with @runtime_checkable protocol
        assert isinstance(adjective, MediaGenerationCapable)

    def test_protocol_method_implementation(self) -> None:
        """Test that Adjective implements required protocol methods."""
        adjective = Adjective(
            word="gut",
            english="good",
            example="Das Essen ist gut.",
            comparative="besser",
            superlative="am besten",
        )

        # Test get_image_search_strategy returns callable with mock service
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mock search terms"

        strategy = adjective.get_image_search_strategy(mock_service)
        assert callable(strategy)

        # Test get_combined_audio_text returns string
        audio_text = adjective.get_combined_audio_text()
        assert isinstance(audio_text, str)
        assert audio_text == "gut, besser, am besten"

    def test_protocol_with_dependency_injection(self) -> None:
        """Test protocol works with dependency injection pattern."""

        def use_media_capable(
            obj: MediaGenerationCapable, service: ImageQueryGenerationProtocol
        ) -> tuple[str, str]:
            """Function that uses MediaGenerationCapable protocol."""
            strategy = obj.get_image_search_strategy(service)
            audio_text = obj.get_combined_audio_text()
            return strategy(), audio_text

        adjective = Adjective(
            word="schnell",
            english="fast",
            example="Er läuft sehr schnell.",
            comparative="schneller",
            superlative="am schnellsten",
        )

        # Create mock service that fails - should raise exception
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        # Should raise MediaGenerationError when service fails (images required)
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for adjective 'schnell'",
        ):
            use_media_capable(adjective, mock_service)

    def test_protocol_with_mock_anthropic_service(self) -> None:
        """Test protocol works with mock Anthropic service injection."""
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mocked search terms"

        adjective = Adjective(
            word="klein",
            english="small",
            example="Das Auto ist klein.",
            comparative="kleiner",
            superlative="am kleinsten",
        )

        strategy = adjective.get_image_search_strategy(mock_service)
        result = strategy()

        assert result == "mocked search terms"
        mock_service.generate_image_query.assert_called_once()

    def test_context_building_for_concrete_adjective(self) -> None:
        """Test that concrete adjectives build appropriate context."""
        adjective = Adjective(
            word="rot",
            english="red",
            example="Das Auto ist rot.",
            comparative="röter",
            superlative="am rötesten",
        )

        context = adjective._build_search_context()

        # Check that context contains adjective information
        assert "rot" in context
        assert "red" in context
        assert "röter" in context
        assert "am rötesten" in context
        assert "Das Auto ist rot" in context

        # Check concrete adjective strategy
        assert "Focus on direct visual representation" in context
        assert "Concrete/Physical" in context

    def test_context_building_for_abstract_adjective(self) -> None:
        """Test that abstract adjectives build appropriate context."""
        adjective = Adjective(
            word="ehrlich",
            english="honest",
            example="Er ist sehr ehrlich.",
            comparative="ehrlicher",
            superlative="am ehrlichsten",
        )

        context = adjective._build_search_context()

        # Check that context contains adjective information
        assert "ehrlich" in context
        assert "honest" in context
        assert "ehrlicher" in context

        # Check abstract adjective strategy
        assert "symbolic imagery" in context
        assert "behavioral representations" in context
        assert "Abstract/Conceptual" in context

    def test_service_failure_raises_error(self) -> None:
        """Test exception when service fails for adjectives."""
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        adjective = Adjective(
            word="blau",
            english="blue",
            example="Der Himmel ist blau.",
            comparative="blauer",
            superlative="am blauesten",
        )

        strategy = adjective.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError when service fails
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for adjective 'blau'",
        ):
            strategy()

    def test_service_failure_for_abstract_adjective_raises_error(self) -> None:
        """Test exception when service fails for abstract adjectives."""
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        adjective = Adjective(
            word="ehrlich",
            english="honest",
            example="Er ist ehrlich.",
            comparative="ehrlicher",
            superlative="am ehrlichsten",
        )

        strategy = adjective.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError when service fails
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for adjective 'ehrlich'",
        ):
            strategy()

    def test_service_failure_for_unmapped_adjective_raises_error(self) -> None:
        """Test exception when service fails for adjectives without concept mapping."""
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        adjective = Adjective(
            word="ungewöhnlich",
            english="unusual",  # Not in concept mappings
            example="Das ist ungewöhnlich.",
            comparative="ungewöhnlicher",
            superlative="am ungewöhnlichsten",
        )

        strategy = adjective.get_image_search_strategy(mock_service)

        # Should raise MediaGenerationError when service fails
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for adjective 'ungewöhnlich'",
        ):
            strategy()

    def test_comparison_forms_in_context(self) -> None:
        """Test that comparison forms are properly included in search context."""
        # Test with all forms present
        full_adjective = Adjective(
            word="schön",
            english="beautiful",
            example="Das ist schön.",
            comparative="schöner",
            superlative="am schönsten",
        )

        context = full_adjective._build_search_context()
        assert "Forms: schön → schöner → am schönsten" in context

        # Test with partial forms
        partial_adjective = Adjective(
            word="schnell",
            english="fast",
            example="Er läuft schnell.",
            comparative="schneller",
            superlative="",  # No superlative
        )

        context = partial_adjective._build_search_context()
        assert "Forms: schnell → schneller" in context
        assert "am schnellsten" not in context

    def test_concrete_vs_abstract_classification(self) -> None:
        """Test that adjectives are correctly classified as concrete or abstract."""
        concrete_cases = [
            ("rot", "red"),
            ("groß", "big"),
            ("heiß", "hot"),
            ("rund", "round"),
        ]

        abstract_cases = [
            ("ehrlich", "honest"),
            ("freundlich", "friendly"),
            ("intelligent", "intelligent"),
            ("glücklich", "happy"),
        ]

        for word, english in concrete_cases:
            adjective = Adjective(
                word=word,
                english=english,
                example="Test.",
                comparative="test",
                superlative="test",
            )
            context = adjective._build_search_context()
            assert "Concrete/Physical" in context

        for word, english in abstract_cases:
            adjective = Adjective(
                word=word,
                english=english,
                example="Test.",
                comparative="test",
                superlative="test",
            )
            context = adjective._build_search_context()
            assert "Abstract/Conceptual" in context
