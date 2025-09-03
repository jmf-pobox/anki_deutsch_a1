"""Tests for Preposition model MediaGenerationCapable protocol compliance."""

from unittest.mock import Mock

from langlearn.models.preposition import Preposition
from langlearn.protocols import MediaGenerationCapable
from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)


class TestPrepositionProtocolCompliance:
    """Test that Preposition implements MediaGenerationCapable protocol."""

    def test_preposition_satisfies_protocol(self) -> None:
        """Test that Preposition instance satisfies MediaGenerationCapable protocol."""
        preposition = Preposition(
            preposition="auf",
            english="on/onto",
            case="Akkusativ/Dativ",
            example1="Ich lege das Buch auf den Tisch.",
            example2="Das Buch liegt auf dem Tisch.",
        )

        # This should pass with @runtime_checkable protocol
        assert isinstance(preposition, MediaGenerationCapable)

    def test_protocol_method_implementation(self) -> None:
        """Test that Preposition implements required protocol methods."""
        preposition = Preposition(
            preposition="mit",
            english="with",
            case="Dativ",
            example1="Ich gehe mit dir.",
            example2="Er spricht mit seinem Freund.",
        )

        # Test get_image_search_strategy returns callable with mock service
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mock search terms"

        strategy = preposition.get_image_search_strategy(mock_service)
        assert callable(strategy)

        # Test get_combined_audio_text returns string
        audio_text = preposition.get_combined_audio_text()
        assert isinstance(audio_text, str)
        assert audio_text == "mit. Ich gehe mit dir.. Er spricht mit seinem Freund."

    def test_protocol_with_dependency_injection(self) -> None:
        """Test protocol works with dependency injection pattern."""

        def use_media_capable(
            obj: MediaGenerationCapable, service: ImageQueryGenerationProtocol
        ) -> tuple[str, str]:
            """Function that uses MediaGenerationCapable protocol."""
            strategy = obj.get_image_search_strategy(service)
            audio_text = obj.get_combined_audio_text()
            return strategy(), audio_text

        preposition = Preposition(
            preposition="in",
            english="in/into",
            case="Akkusativ/Dativ",
            example1="Ich gehe in die Schule.",
            example2="Ich bin in der Schule.",
        )

        # Create mock service that fails to simulate fallback
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        # Should work through protocol interface with fallback when service fails
        search_terms, audio = use_media_capable(preposition, mock_service)

        assert isinstance(search_terms, str)
        assert isinstance(audio, str)
        assert search_terms == "in/into"  # English fallback
        assert audio == "in. Ich gehe in die Schule.. Ich bin in der Schule."

    def test_protocol_with_mock_anthropic_service(self) -> None:
        """Test protocol works with mock Anthropic service injection."""
        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mocked search terms"

        preposition = Preposition(
            preposition="über",
            english="over/above",
            case="Akkusativ/Dativ",
            example1="Das Flugzeug fliegt über die Stadt.",
            example2="Das Bild hängt über dem Sofa.",
        )

        strategy = preposition.get_image_search_strategy(mock_service)
        result = strategy()

        assert result == "mocked search terms"
        mock_service.generate_image_query.assert_called_once()

    def test_context_building_for_preposition(self) -> None:
        """Test that prepositions build appropriate context."""
        preposition = Preposition(
            preposition="zwischen",
            english="between",
            case="Akkusativ/Dativ",
            example1="Ich stelle mich zwischen die Kinder.",
            example2="Ich stehe zwischen den Kindern.",
        )

        context = preposition._build_search_context()

        # Check that context contains preposition information
        assert "zwischen" in context
        assert "between" in context
        assert "accusative (motion) or dative (location)" in context
        assert "Ich stelle mich zwischen die Kinder" in context
        assert "Ich stehe zwischen den Kindern" in context

        # Check preposition-specific strategy
        assert "relationship or concept" in context
        assert "photographers would use" in context

    def test_two_way_preposition_detection(self) -> None:
        """Test two-way preposition detection logic."""
        two_way_prep = Preposition(
            preposition="auf",
            english="on/onto",
            case="Akkusativ/Dativ",
            example1="Ich lege das Buch auf den Tisch.",
            example2="Das Buch liegt auf dem Tisch.",
        )
        assert two_way_prep.is_two_way_preposition() is True

        one_way_prep = Preposition(
            preposition="mit",
            english="with",
            case="Dativ",
            example1="Ich gehe mit dir.",
        )
        assert one_way_prep.is_two_way_preposition() is False

    def test_case_description_generation(self) -> None:
        """Test case description generation for different case types."""
        accusative_prep = Preposition(
            preposition="durch",
            english="through",
            case="Akkusativ",
            example1="Ich gehe durch den Park.",
        )
        assert "accusative case" in accusative_prep.get_case_description()

        dative_prep = Preposition(
            preposition="mit",
            english="with",
            case="Dativ",
            example1="Ich gehe mit dir.",
        )
        assert "dative case" in dative_prep.get_case_description()

        two_way_prep = Preposition(
            preposition="in",
            english="in/into",
            case="Akkusativ/Dativ",
            example1="Ich gehe in die Schule.",
            example2="Ich bin in der Schule.",
        )
        description = two_way_prep.get_case_description()
        assert "accusative (motion) or dative (location)" in description

    def test_combined_audio_with_single_example(self) -> None:
        """Test combined audio generation with single example."""
        preposition = Preposition(
            preposition="mit",
            english="with",
            case="Dativ",
            example1="Ich gehe mit dir.",
            example2="",  # Empty second example
        )

        audio_text = preposition.get_combined_audio_text()
        assert audio_text == "mit. Ich gehe mit dir."

    def test_combined_audio_with_both_examples(self) -> None:
        """Test combined audio generation with both examples."""
        preposition = Preposition(
            preposition="auf",
            english="on/onto",
            case="Akkusativ/Dativ",
            example1="Ich lege das Buch auf den Tisch.",
            example2="Das Buch liegt auf dem Tisch.",
        )

        audio_text = preposition.get_combined_audio_text()
        expected_audio = (
            "auf. Ich lege das Buch auf den Tisch.. Das Buch liegt auf dem Tisch."
        )
        assert audio_text == expected_audio
