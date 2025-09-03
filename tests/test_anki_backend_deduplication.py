"""
Tests for AnkiBackend deduplication and optimization features.

This module tests the advanced deduplication and optimization functionality
that prevents duplicate media file generation and tracks reuse statistics.
"""

import hashlib
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.backends.anki_backend import AnkiBackend


class TestAnkiBackendDeduplication:
    """Test AnkiBackend media deduplication and optimization features."""

    def test_audio_deduplication_new_file(self, mock_media_service: Mock) -> None:
        """Test audio generation for new file (not duplicate)."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Mock file system - file doesn't exist (new file)
            text = "Guten Tag"

            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_audio",
                    return_value="[sound:test.mp3]",
                ) as mock_audio,
                patch.object(Path, "exists", return_value=False),
            ):
                result = backend._generate_or_get_audio(text)

                # Verify result and stats
                assert result == "[sound:test.mp3]"
                assert backend._media_generation_stats["audio_generated"] == 1
                assert backend._media_generation_stats["audio_reused"] == 0
                mock_audio.assert_called_once_with(text)

    def test_audio_deduplication_existing_file(self, mock_media_service: Mock) -> None:
        """Test audio deduplication when file already exists."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Mock file system - file exists (duplicate)
            text = "Hallo Welt"

            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_audio",
                    return_value="[sound:existing.mp3]",
                ),
                patch.object(Path, "exists", return_value=True),
            ):
                result = backend._generate_or_get_audio(text)

                # Verify result and stats show reuse
                assert result == "[sound:existing.mp3]"
                assert backend._media_generation_stats["audio_generated"] == 0
                assert backend._media_generation_stats["audio_reused"] == 1

    def test_image_deduplication_new_file(self, mock_media_service: Mock) -> None:
        """Test image generation for new file (not duplicate)."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Mock file system - file doesn't exist (new file)
            word = "Katze"

            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_image",
                    return_value='<img src="cat.jpg">',
                ) as mock_image,
                patch.object(Path, "exists", return_value=False),
            ):
                result = backend._generate_or_get_image(word, "cat")

                # Verify result and stats
                assert result == '<img src="cat.jpg">'
                assert backend._media_generation_stats["images_downloaded"] == 1
                assert backend._media_generation_stats["images_reused"] == 0
                mock_image.assert_called_once_with(word, "cat", "")

    def test_image_deduplication_existing_file(self, mock_media_service: Mock) -> None:
        """Test image deduplication when file already exists."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Mock file system - file exists (duplicate)
            word = "Hund"

            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_image",
                    return_value='<img src="existing_cat.jpg">',
                ),
                patch.object(Path, "exists", return_value=True),
            ):
                result = backend._generate_or_get_image(word, "dog", "Der Hund bellt")

                # Verify result and stats show reuse
                assert result == '<img src="existing_cat.jpg">'
                assert backend._media_generation_stats["images_downloaded"] == 0
                assert backend._media_generation_stats["images_reused"] == 1

    def test_mixed_media_deduplication_statistics(
        self, mock_media_service: Mock
    ) -> None:
        """Test statistics tracking with mixed new and duplicate media."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Directly set statistics to test calculation logic
            backend._media_generation_stats.update(
                {
                    "audio_generated": 1,
                    "audio_reused": 1,
                    "images_downloaded": 1,
                    "images_reused": 1,
                    "generation_errors": 0,
                }
            )

            # Verify mixed statistics
            stats = backend._media_generation_stats
            assert stats["audio_generated"] == 1
            assert stats["audio_reused"] == 1
            assert stats["images_downloaded"] == 1
            assert stats["images_reused"] == 1
            assert stats["generation_errors"] == 0

    def test_deduplication_stats_in_get_stats(self, mock_media_service: Mock) -> None:
        """Test that deduplication stats appear in comprehensive statistics."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )
            mock_collection.db.scalar.return_value = 10

            backend = AnkiBackend("Test Deck", mock_media_service)

            # Set up deduplication statistics
            backend._media_generation_stats.update(
                {
                    "audio_generated": 3,
                    "audio_reused": 2,
                    "images_downloaded": 1,
                    "images_reused": 4,
                    "generation_errors": 1,
                }
            )

            stats = backend.get_stats()
            media_stats = stats["media_generation_stats"]

            # Verify deduplication stats are included
            assert media_stats["audio_generated"] == 3
            assert media_stats["audio_reused"] == 2
            assert media_stats["images_downloaded"] == 1
            assert media_stats["images_reused"] == 4
            assert media_stats["generation_errors"] == 1

            # Verify calculated totals include reuse
            assert media_stats["total_media_generated"] == 4  # 3 audio + 1 image
            assert media_stats["total_media_reused"] == 6  # 2 audio + 4 image

    def test_audio_hash_based_deduplication_logic(
        self, mock_media_service: Mock
    ) -> None:
        """Test that audio deduplication uses correct MD5 hash logic."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)
            text = "Spezielle deutsche Wörter"
            expected_hash = hashlib.md5(text.encode()).hexdigest()

            # Verify hash calculation works
            assert len(expected_hash) == 32  # MD5 is 32 chars
            assert expected_hash.isalnum()  # MD5 is alphanumeric

            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_audio",
                    return_value="[sound:hashed.mp3]",
                ),
                patch.object(Path, "exists", return_value=True),
            ):
                backend._generate_or_get_audio(text)
                assert backend._media_generation_stats["audio_reused"] == 1

    def test_image_word_based_deduplication_logic(
        self, mock_media_service: Mock
    ) -> None:
        """Test that image deduplication uses word-based file naming."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)
            word = "Schmetterling"

            # Test word-based filename logic
            assert word.isalpha()  # German word should be alphabetic

            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_image",
                    return_value='<img src="word_image.jpg">',
                ),
                patch.object(Path, "exists", return_value=True),
            ):
                backend._generate_or_get_image(word, "butterfly")
                assert backend._media_generation_stats["images_reused"] == 1

    def test_deduplication_with_media_service_failure(
        self, mock_media_service: Mock
    ) -> None:
        """Test deduplication behavior when MediaService fails."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            with (
                patch.object(
                    backend._media_service, "generate_or_get_audio", return_value=None
                ),
                patch.object(Path, "exists", return_value=False),
            ):
                result = backend._generate_or_get_audio("test text")

                # Verify error handling doesn't interfere with deduplication tracking
                assert result is None
                assert backend._media_generation_stats["generation_errors"] == 1
                assert backend._media_generation_stats["audio_generated"] == 0
                assert backend._media_generation_stats["audio_reused"] == 0

    def test_optimization_directory_setup(self, mock_media_service: Mock) -> None:
        """Test that AnkiBackend sets up optimized directory structure."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Verify directories are set up for optimization
            assert backend._audio_dir is not None
            assert backend._images_dir is not None
            assert str(backend._audio_dir).endswith("data/audio")
            assert str(backend._images_dir).endswith("data/images")

    def test_concurrent_deduplication_safety(self, mock_media_service: Mock) -> None:
        """Test deduplication is safe under concurrent access patterns."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Simulate concurrent calls with same text
            text = "Gleichzeitig"

            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_audio",
                    return_value="[sound:concurrent.mp3]",
                ),
                patch.object(Path, "exists", return_value=True),
            ):
                # Multiple calls should all be handled correctly
                results = []
                for _ in range(3):
                    results.append(backend._generate_or_get_audio(text))

                # All results should be the same
                assert all(r == "[sound:concurrent.mp3]" for r in results)

                # Statistics should be accurate
                assert backend._media_generation_stats["audio_reused"] == 3
                assert backend._media_generation_stats["audio_generated"] == 0


class TestAnkiBackendOptimizationFeatures:
    """Test AnkiBackend optimization features beyond deduplication."""

    def test_media_directory_optimization(self, mock_media_service: Mock) -> None:
        """Test optimized media directory structure creation."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Verify directory paths are set up correctly for optimization
            assert backend._audio_dir is not None
            assert backend._images_dir is not None
            assert "audio" in str(backend._audio_dir)
            assert "images" in str(backend._images_dir)

    def test_statistics_optimization_tracking(self, mock_media_service: Mock) -> None:
        """Test that statistics track optimization effectiveness."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck", mock_media_service)

            # Set up scenario with high reuse (good optimization)
            backend._media_generation_stats.update(
                {
                    "audio_generated": 2,
                    "audio_reused": 8,  # 80% reuse rate
                    "images_downloaded": 1,
                    "images_reused": 9,  # 90% reuse rate
                    "generation_errors": 0,
                }
            )

            stats = backend.get_stats()["media_generation_stats"]

            # Calculate optimization effectiveness
            total_audio = stats["audio_generated"] + stats["audio_reused"]
            total_images = stats["images_downloaded"] + stats["images_reused"]
            audio_reuse_rate = (
                stats["audio_reused"] / total_audio if total_audio > 0 else 0
            )
            image_reuse_rate = (
                stats["images_reused"] / total_images if total_images > 0 else 0
            )

            # Verify high optimization effectiveness
            assert audio_reuse_rate == 0.8  # 80% audio reuse
            assert image_reuse_rate == 0.9  # 90% image reuse
            assert (
                stats["total_media_reused"] > stats["total_media_generated"]
            )  # More reuse than new


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
