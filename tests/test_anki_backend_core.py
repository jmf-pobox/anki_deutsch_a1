"""
Core AnkiBackend functionality tests targeting coverage gaps.

This module provides focused tests for the most critical untested AnkiBackend methods
to increase coverage while ensuring proper functionality.
"""

from unittest.mock import Mock, patch

import pytest

from langlearn.infrastructure.backends.anki_backend import AnkiBackend
from langlearn.languages.german.language import GermanLanguage


class TestAnkiBackendCore:
    """Test core AnkiBackend functionality with focused coverage."""

    def test_initialization_and_media_generation_stats(
        self, mock_media_service: Mock
    ) -> None:
        """Test initialization and media generation statistics."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_collection_class,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            # Mock collection creation
            mock_collection = Mock()
            mock_collection_class.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            # Verify initialization worked
            assert backend.deck_name == "Test Deck"
            assert backend._media_generation_stats["audio_generated"] == 0
            assert backend._media_generation_stats["generation_errors"] == 0

    def test_generate_or_get_audio_success(self, mock_media_service: Mock) -> None:
        """Test audio generation method success path."""
        with (
            patch("langlearn.infrastructure.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            # Mock successful audio generation
            with patch.object(
                backend._media_service,
                "generate_or_get_audio",
                return_value="[sound:test.mp3]",
            ) as mock_audio:
                result = backend._generate_or_get_audio("Hallo Welt")

                assert result == "[sound:test.mp3]"
                mock_audio.assert_called_once_with("Hallo Welt")

    def test_generate_or_get_audio_error_handling(
        self, mock_media_service: Mock
    ) -> None:
        """Test audio generation error handling and statistics."""
        with (
            patch("langlearn.infrastructure.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            # Mock service failure
            with patch.object(
                backend._media_service,
                "generate_or_get_audio",
                side_effect=Exception("API Error"),
            ):
                # Should raise MediaGenerationError on error and increment error count
                from langlearn.exceptions import MediaGenerationError

                with pytest.raises(
                    MediaGenerationError, match="Failed to generate audio"
                ):
                    backend._generate_or_get_audio("test text")

                assert backend._media_generation_stats["generation_errors"] == 1

    def test_generate_or_get_image_success(self, mock_media_service: Mock) -> None:
        """Test image generation method success path."""
        with (
            patch("langlearn.infrastructure.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            # Mock successful image generation
            with patch.object(
                backend._media_service,
                "generate_or_get_image",
                return_value='<img src="cat.jpg">',
            ) as mock_image:
                result = backend._generate_or_get_image(
                    "cat", "cute cat", "The cat is sleeping"
                )

                assert result == '<img src="cat.jpg">'
                mock_image.assert_called_once_with(
                    "cat", "cute cat", "The cat is sleeping"
                )

    def test_generate_or_get_image_error_handling(
        self, mock_media_service: Mock
    ) -> None:
        """Test image generation error handling."""
        with (
            patch("langlearn.infrastructure.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            # Mock service failure
            with patch.object(
                backend._media_service,
                "generate_or_get_image",
                side_effect=Exception("Network Error"),
            ):
                # Should raise MediaGenerationError on error and increment error count
                from langlearn.exceptions import MediaGenerationError

                with pytest.raises(
                    MediaGenerationError, match="Failed to generate image"
                ):
                    backend._generate_or_get_image("word", "search")

                assert backend._media_generation_stats["generation_errors"] == 1

    def test_backward_compatibility_properties(self, mock_media_service: Mock) -> None:
        """Test backward compatibility properties for service access."""
        with (
            patch("langlearn.infrastructure.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            # Mock the nested service properties using patch.object
            mock_audio_service = Mock()
            mock_pexels_service = Mock()

            with (
                patch.object(
                    backend._media_service, "_audio_service", mock_audio_service
                ),
                patch.object(
                    backend._media_service, "_pexels_service", mock_pexels_service
                ),
            ):
                # Test properties return the correct services
                assert backend._audio_service is mock_audio_service
                assert backend._pexels_service is mock_pexels_service

    def test_cleanup_on_deletion(self, mock_media_service: Mock) -> None:
        """Test temporary directory cleanup functionality exists."""
        with (
            patch("langlearn.infrastructure.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test_cleanup"),
            patch("os.path.exists", return_value=True),
            patch("shutil.rmtree") as mock_rmtree,
            patch("langlearn.infrastructure.backends.anki_backend.AudioService"),
            patch("langlearn.infrastructure.backends.anki_backend.PexelsService"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())
            temp_dir = backend._temp_dir

            # Verify temp dir is set correctly
            assert temp_dir == "/tmp/test_cleanup"

            # Manually call __del__ to test cleanup logic
            backend.__del__()

            # Verify rmtree was called with ignore_errors=True
            mock_rmtree.assert_called_with(temp_dir, ignore_errors=True)

    def test_get_stats_with_mock_data(self, mock_media_service: Mock) -> None:
        """Test statistics retrieval with mocked data."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_collection_class,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            # Mock collection and database
            mock_collection = Mock()
            mock_collection_class.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )
            mock_collection.db.scalar.return_value = 25  # 25 notes

            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            # Set up some test data
            backend._note_type_map = {"1": Mock(), "2": Mock()}  # 2 note types
            backend._media_files = [Mock(), Mock(), Mock()]  # 3 media files
            backend._media_generation_stats.update(
                {
                    "audio_generated": 4,
                    "audio_reused": 2,
                    "images_downloaded": 1,
                    "images_reused": 1,
                    "generation_errors": 0,
                }
            )

            stats = backend.get_stats()

            # Verify all expected stats are present
            assert stats["deck_name"] == "Test Deck"
            assert stats["note_types_count"] == 2
            assert stats["notes_count"] == 25
            assert stats["media_files_count"] == 3

            # Verify media generation stats
            media_stats = stats["media_generation_stats"]
            assert media_stats["audio_generated"] == 4
            assert media_stats["total_media_generated"] == 5  # 4 audio + 1 image
            assert media_stats["total_media_reused"] == 3  # 2 audio + 1 image

    def test_add_media_file_audio_format(self, mock_media_service: Mock) -> None:
        """Test adding audio media file with proper formatting."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_collection_class,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
            patch("os.path.exists", return_value=True),
        ):
            mock_collection = Mock()
            mock_collection_class.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            # Mock media.add_file method
            mock_collection.media.add_file.return_value = None

            media_file = backend.add_media_file("/path/to/test.mp3")

            # Verify audio file gets [sound:] formatting
            assert media_file.reference == "[sound:test.mp3]"
            assert media_file.path == "/path/to/test.mp3"
            mock_collection.media.add_file.assert_called_once_with("/path/to/test.mp3")

    def test_add_media_file_image_format(self, mock_media_service: Mock) -> None:
        """Test adding image media file without sound formatting."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_collection_class,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
            patch("os.path.exists", return_value=True),
        ):
            mock_collection = Mock()
            mock_collection_class.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())
            mock_collection.media.add_file.return_value = None

            media_file = backend.add_media_file("/path/to/image.jpg")

            # Image files should not get [sound:] formatting
            assert media_file.reference == "image.jpg"
            assert media_file.path == "/path/to/image.jpg"

    def test_add_media_file_not_found_error(self, mock_media_service: Mock) -> None:
        """Test error handling when media file doesn't exist."""
        with (
            patch("langlearn.infrastructure.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
            patch("os.path.exists", return_value=False),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service, GermanLanguage())

            with pytest.raises(FileNotFoundError, match="Media file not found"):
                backend.add_media_file("/nonexistent/file.mp3")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
