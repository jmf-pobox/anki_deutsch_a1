"""Tests for Adverb model MediaGenerationCapable protocol compliance."""

from langlearn.models.adverb import Adverb, AdverbType
from langlearn.protocols import MediaGenerationCapable
from langlearn.protocols.anthropic_protocol import AnthropicServiceProtocol


class TestAdverbProtocolCompliance:
    """Test that Adverb implements MediaGenerationCapable protocol."""

    def test_adverb_satisfies_protocol(self) -> None:
        """Test that Adverb instance satisfies MediaGenerationCapable protocol."""
        adverb = Adverb(
            word="heute",
            english="today",
            type=AdverbType.TIME,
            example="Ich gehe heute ins Kino.",
        )

        # This should pass with @runtime_checkable protocol
        assert isinstance(adverb, MediaGenerationCapable)

    def test_protocol_method_implementation(self) -> None:
        """Test that Adverb implements required protocol methods."""
        adverb = Adverb(
            word="schnell",
            english="quickly",
            type=AdverbType.MANNER,
            example="Er läuft schnell zur Schule.",
        )

        # Test get_image_search_strategy returns callable with mock service
        from unittest.mock import Mock

        mock_service = Mock()
        mock_service.generate_pexels_query.return_value = "mock search terms"

        strategy = adverb.get_image_search_strategy(mock_service)
        assert callable(strategy)

        # Test get_combined_audio_text returns string
        audio_text = adverb.get_combined_audio_text()
        assert isinstance(audio_text, str)
        assert audio_text == "schnell. Er läuft schnell zur Schule."

    def test_protocol_with_dependency_injection(self) -> None:
        """Test protocol works with dependency injection pattern."""
        from unittest.mock import Mock

        def use_media_capable(
            obj: MediaGenerationCapable, service: AnthropicServiceProtocol
        ) -> tuple[str, str]:
            """Function that uses MediaGenerationCapable protocol."""
            strategy = obj.get_image_search_strategy(service)
            audio_text = obj.get_combined_audio_text()
            return strategy(), audio_text

        adverb = Adverb(
            word="hier",
            english="here",
            type=AdverbType.LOCATION,
            example="Das Buch liegt hier auf dem Tisch.",
        )

        # Create mock service that fails to simulate fallback
        mock_service = Mock()
        mock_service.generate_pexels_query.side_effect = Exception("Service failed")

        # Should work through protocol interface with fallback when service fails
        search_terms, audio = use_media_capable(adverb, mock_service)

        assert isinstance(search_terms, str)
        assert isinstance(audio, str)
        assert search_terms == "hier"  # Raw German word fallback
        assert audio == "hier. Das Buch liegt hier auf dem Tisch."

    def test_protocol_with_mock_anthropic_service(self) -> None:
        """Test protocol works with mock Anthropic service injection."""
        from unittest.mock import Mock

        mock_service = Mock()
        mock_service.generate_pexels_query.return_value = "mocked search terms"

        adverb = Adverb(
            word="schnell",
            english="quickly",
            type=AdverbType.MANNER,
            example="Er läuft schnell.",
        )

        strategy = adverb.get_image_search_strategy(mock_service)
        result = strategy()

        assert result == "mocked search terms"
        mock_service.generate_pexels_query.assert_called_once()

    def test_context_building_for_different_types(self) -> None:
        """Test that different adverb types build appropriate context."""
        time_adverb = Adverb(
            word="heute",
            english="today",
            type=AdverbType.TIME,
            example="Heute ist schönes Wetter.",
        )

        location_adverb = Adverb(
            word="hier",
            english="here",
            type=AdverbType.LOCATION,
            example="Das Buch liegt hier.",
        )

        time_context = time_adverb._build_search_context()
        location_context = location_adverb._build_search_context()

        # Check that contexts contain type-specific guidance
        assert "temporal symbols" in time_context
        assert "clocks, calendars" in time_context
        assert "spatial relationships" in location_context
        assert "directional arrows" in location_context
