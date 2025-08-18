"""Tests for MediaManager functionality."""

import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.backends.base import DeckBackend, MediaFile
from langlearn.managers.media_manager import MediaManager, MediaStats
from langlearn.services.media_service import MediaGenerationStats, MediaService


class TestMediaManager:
    """Test MediaManager media coordination functionality."""

    @pytest.fixture
    def mock_backend(self) -> Mock:
        """Create a mock backend for testing."""
        backend = Mock(spec=DeckBackend)
        backend.add_media_file.return_value = MediaFile(
            path="/fake/file.mp3", reference="[sound:file.mp3]"
        )
        return backend

    @pytest.fixture
    def mock_media_service(self) -> Mock:
        """Create a mock media service for testing."""
        service = Mock(spec=MediaService)
        service.generate_audio.return_value = "/fake/audio.mp3"
        service.generate_image.return_value = "/fake/image.jpg"
        service.get_stats.return_value = MediaGenerationStats(
            audio_generated=2,
            audio_reused=1,
            images_downloaded=1,
            images_reused=0,
            generation_errors=0,
        )
        return service

    @pytest.fixture
    def media_manager(
        self, mock_backend: Mock, mock_media_service: Mock
    ) -> MediaManager:
        """Create a MediaManager instance for testing."""
        return MediaManager(mock_backend, mock_media_service)

    @pytest.fixture
    def temp_file(self) -> Generator[str, None, None]:
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(b"fake audio content")
            temp_path = f.name
        yield temp_path
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    def test_initialization(self, mock_backend: Mock) -> None:
        """Test MediaManager initialization."""
        manager = MediaManager(mock_backend)

        assert manager._backend is mock_backend
        assert manager._media_service is None
        assert len(manager._added_files) == 0

    def test_initialization_with_media_service(
        self, mock_backend: Mock, mock_media_service: Mock
    ) -> None:
        """Test MediaManager initialization with MediaService."""
        manager = MediaManager(mock_backend, mock_media_service)

        assert manager._backend is mock_backend
        assert manager._media_service is mock_media_service

    def test_add_media_file_success(
        self, media_manager: MediaManager, mock_backend: Mock, temp_file: str
    ) -> None:
        """Test successful media file addition."""
        media_file = media_manager.add_media_file(temp_file)

        assert media_file is not None
        assert media_file.path == "/fake/file.mp3"
        assert media_file.reference == "[sound:file.mp3]"

        mock_backend.add_media_file.assert_called_once_with(temp_file)

        # Check statistics
        stats = media_manager.get_media_stats()
        assert stats.files_added == 1
        assert stats.duplicates_skipped == 0
        assert stats.unique_files == 1

    def test_add_media_file_nonexistent(self, media_manager: MediaManager) -> None:
        """Test adding nonexistent media file."""
        media_file = media_manager.add_media_file("/nonexistent/file.mp3")

        assert media_file is None

        # Check statistics
        stats = media_manager.get_media_stats()
        assert stats.files_added == 0

    def test_add_media_file_duplicate_prevention(
        self, media_manager: MediaManager, temp_file: str
    ) -> None:
        """Test that duplicate files are prevented."""
        # Add file first time
        media_file1 = media_manager.add_media_file(temp_file)
        assert media_file1 is not None

        # Try to add same file again
        media_file2 = media_manager.add_media_file(temp_file)
        assert media_file2 is None

        # Check statistics
        stats = media_manager.get_media_stats()
        assert stats.files_added == 1
        assert stats.duplicates_skipped == 1
        assert stats.unique_files == 1

    def test_add_media_file_allow_duplicates(
        self, media_manager: MediaManager, mock_backend: Mock, temp_file: str
    ) -> None:
        """Test allowing duplicates when explicitly requested."""
        # Add file first time
        media_file1 = media_manager.add_media_file(temp_file)
        assert media_file1 is not None

        # Add same file again with allow_duplicates=True
        media_file2 = media_manager.add_media_file(temp_file, allow_duplicates=True)
        assert media_file2 is not None

        # Backend should be called twice
        assert mock_backend.add_media_file.call_count == 2

        # Check statistics
        stats = media_manager.get_media_stats()
        assert stats.files_added == 2
        assert stats.duplicates_skipped == 0

    def test_generate_and_add_audio_success(
        self, media_manager: MediaManager, mock_media_service: Mock, mock_backend: Mock
    ) -> None:
        """Test successful audio generation and addition."""
        with patch.object(Path, "exists", return_value=True):
            media_file = media_manager.generate_and_add_audio("test text")

        assert media_file is not None
        mock_media_service.generate_audio.assert_called_once_with("test text")
        mock_backend.add_media_file.assert_called_once_with("/fake/audio.mp3")

    def test_generate_and_add_audio_no_service(self, mock_backend: Mock) -> None:
        """Test audio generation when no MediaService is available."""
        manager = MediaManager(mock_backend)  # No MediaService

        media_file = manager.generate_and_add_audio("test text")

        assert media_file is None
        mock_backend.add_media_file.assert_not_called()

    def test_generate_and_add_audio_generation_failure(
        self, media_manager: MediaManager, mock_media_service: Mock
    ) -> None:
        """Test audio generation failure."""
        mock_media_service.generate_audio.return_value = None

        media_file = media_manager.generate_and_add_audio("test text")

        assert media_file is None

    def test_generate_and_add_image_success(
        self, media_manager: MediaManager, mock_media_service: Mock, mock_backend: Mock
    ) -> None:
        """Test successful image generation and addition."""
        with patch.object(Path, "exists", return_value=True):
            media_file = media_manager.generate_and_add_image(
                "test", "search query", "example sentence"
            )

        assert media_file is not None
        mock_media_service.generate_image.assert_called_once_with(
            "test", "search query", "example sentence"
        )
        mock_backend.add_media_file.assert_called_once_with("/fake/image.jpg")

    def test_get_media_stats(self, media_manager: MediaManager, temp_file: str) -> None:
        """Test media statistics reporting."""
        # Add a file
        media_manager.add_media_file(temp_file)

        stats = media_manager.get_media_stats()

        assert isinstance(stats, MediaStats)
        assert stats.files_added == 1
        assert stats.duplicates_skipped == 0
        assert stats.unique_files == 1
        assert stats.total_size_bytes > 0  # File has content

    def test_get_added_files(self, media_manager: MediaManager, temp_file: str) -> None:
        """Test getting list of added files."""
        # Initially empty
        assert media_manager.get_added_files() == []

        # Add a file
        media_manager.add_media_file(temp_file)
        added_files = media_manager.get_added_files()

        assert len(added_files) == 1
        assert temp_file in added_files

    def test_is_file_added(self, media_manager: MediaManager, temp_file: str) -> None:
        """Test checking if file has been added."""
        # Initially not added
        assert media_manager.is_file_added(temp_file) is False

        # Add file
        media_manager.add_media_file(temp_file)

        # Now should be detected as added
        assert media_manager.is_file_added(temp_file) is True

    def test_clear_cache(self, media_manager: MediaManager, temp_file: str) -> None:
        """Test clearing the deduplication cache."""
        # Add file
        media_manager.add_media_file(temp_file)
        assert media_manager.is_file_added(temp_file) is True

        # Clear cache
        media_manager.clear_cache()
        assert media_manager.is_file_added(temp_file) is False
        assert media_manager.get_added_files() == []

    def test_get_detailed_stats_with_service(
        self, media_manager: MediaManager, mock_media_service: Mock, temp_file: str
    ) -> None:
        """Test detailed statistics including service stats."""
        # Add a file to generate some stats
        media_manager.add_media_file(temp_file)

        stats = media_manager.get_detailed_stats()

        # Should include media manager stats
        assert "media_stats" in stats
        media_stats = stats["media_stats"]
        assert media_stats["files_added"] == 1

        # Should include media service stats
        assert "media_generation_stats" in stats
        service_stats = stats["media_generation_stats"]
        assert service_stats["audio_generated"] == 2
        assert service_stats["total_media_generated"] == 3  # 2 + 1
        assert service_stats["total_media_reused"] == 1  # 1 + 0

    def test_get_detailed_stats_without_service(self, mock_backend: Mock) -> None:
        """Test detailed statistics when no MediaService is available."""
        manager = MediaManager(mock_backend)  # No MediaService

        stats = manager.get_detailed_stats()

        # Should only include media manager stats
        assert "media_stats" in stats
        assert "media_generation_stats" not in stats

    def test_file_hash_calculation(
        self, media_manager: MediaManager, temp_file: str
    ) -> None:
        """Test that file hashing works for deduplication."""
        # Create another file with same content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f2:
            f2.write(b"fake audio content")  # Same content
            temp_file2 = f2.name

        try:
            # Add first file
            media_file1 = media_manager.add_media_file(temp_file)
            assert media_file1 is not None

            # Try to add second file with same content - should be detected as duplicate
            media_file2 = media_manager.add_media_file(temp_file2)
            assert media_file2 is None

            stats = media_manager.get_media_stats()
            assert stats.files_added == 1
            assert stats.duplicates_skipped == 1

        finally:
            Path(temp_file2).unlink(missing_ok=True)
