"""Tests for Adverb model MediaGenerationCapable protocol compliance."""

import pytest

from langlearn.core.protocols import MediaGenerationCapable
from langlearn.core.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)
from langlearn.exceptions import MediaGenerationError
from langlearn.languages.german.models.adverb import Adverb, AdverbType


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
        mock_service.generate_image_query.return_value = "mock search terms"

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
            obj: MediaGenerationCapable, service: ImageQueryGenerationProtocol
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

        # Create mock service that fails - should raise exception
        mock_service = Mock()
        mock_service.generate_image_query.side_effect = Exception("Service failed")

        # Should raise MediaGenerationError when service fails (images required)
        with pytest.raises(
            MediaGenerationError,
            match="Failed to generate image search for adverb 'hier'",
        ):
            use_media_capable(adverb, mock_service)

    def test_protocol_with_mock_anthropic_service(self) -> None:
        """Test protocol works with mock Anthropic service injection."""
        from unittest.mock import Mock

        mock_service = Mock()
        mock_service.generate_image_query.return_value = "mocked search terms"

        adverb = Adverb(
            word="schnell",
            english="quickly",
            type=AdverbType.MANNER,
            example="Er läuft schnell.",
        )

        strategy = adverb.get_image_search_strategy(mock_service)
        result = strategy()

        assert result == "mocked search terms"
        mock_service.generate_image_query.assert_called_once()

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
