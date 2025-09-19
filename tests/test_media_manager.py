"""Tests for MediaManager functionality."""

import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.infrastructure.backends.base import DeckBackend, MediaFile
from langlearn.infrastructure.managers.media_manager import MediaManager, MediaStats
from langlearn.infrastructure.services.media_service import (
    MediaGenerationStats,
    MediaService,
)


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
    def temp_file(self) -> Generator[str]:
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

        mock_backend.add_media_file.assert_called_once_with(temp_file, media_type="")

        # Check statistics
        stats = media_manager.get_media_stats()
        assert stats.files_added == 1

    def test_add_media_file_nonexistent(self, media_manager: MediaManager) -> None:
        """Test adding nonexistent media file."""
        media_file = media_manager.add_media_file("/nonexistent/file.mp3")

        assert media_file is None

        # Check statistics
        stats = media_manager.get_media_stats()
        assert stats.files_added == 0

    def test_add_media_file_multiple_times(
        self, media_manager: MediaManager, mock_backend: Mock, temp_file: str
    ) -> None:
        """Test that same file can be added multiple times."""
        # Add file first time
        media_file1 = media_manager.add_media_file(temp_file)
        assert media_file1 is not None

        # Add same file again - should succeed
        media_file2 = media_manager.add_media_file(temp_file)
        assert media_file2 is not None

        # Backend should be called twice
        assert mock_backend.add_media_file.call_count == 2

        # Check statistics
        stats = media_manager.get_media_stats()
        assert stats.files_added == 2

    def test_generate_and_add_audio_success(
        self, media_manager: MediaManager, mock_media_service: Mock, mock_backend: Mock
    ) -> None:
        """Test successful audio generation and addition."""
        with patch.object(Path, "exists", return_value=True):
            media_file = media_manager.generate_and_add_audio("test text")

        assert media_file is not None
        mock_media_service.generate_audio.assert_called_once_with("test text")
        mock_backend.add_media_file.assert_called_once_with(
            "/fake/audio.mp3", media_type="audio"
        )

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
        mock_backend.add_media_file.assert_called_once_with(
            "/fake/image.jpg", media_type="image"
        )

    def test_get_media_stats(self, media_manager: MediaManager, temp_file: str) -> None:
        """Test media statistics reporting."""
        # Add a file
        media_manager.add_media_file(temp_file)

        stats = media_manager.get_media_stats()

        assert isinstance(stats, MediaStats)
        assert stats.files_added == 1
        assert stats.total_size_bytes > 0  # File has content

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
