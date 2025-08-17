"""Unit tests for MediaService."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from langlearn.services.audio import AudioService
from langlearn.services.media_service import MediaGenerationConfig, MediaService
from langlearn.services.pexels_service import PexelsService


class TestMediaService:
    """Test MediaService functionality."""

    @pytest.fixture
    def mock_audio_service(self) -> Mock:
        """Mock AudioService for testing."""
        service = Mock(spec=AudioService)
        service.generate_audio.return_value = "data/audio/test.mp3"
        return service

    @pytest.fixture
    def mock_pexels_service(self) -> Mock:
        """Mock PexelsService for testing."""
        service = Mock(spec=PexelsService)
        service.download_image.return_value = True
        return service

    @pytest.fixture
    def config(self) -> MediaGenerationConfig:
        """Test configuration."""
        return MediaGenerationConfig(
            audio_dir="test_audio", images_dir="test_images", image_size="medium"
        )

    @pytest.fixture
    def temp_project_root(self) -> Path:
        """Temporary project root for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def media_service(
        self,
        mock_audio_service: Mock,
        mock_pexels_service: Mock,
        config: MediaGenerationConfig,
        temp_project_root: Path,
    ) -> MediaService:
        """MediaService instance for testing."""
        return MediaService(
            audio_service=mock_audio_service,
            pexels_service=mock_pexels_service,
            config=config,
            project_root=temp_project_root,
        )

    def test_init_creates_directories(
        self, media_service: MediaService, temp_project_root: Path
    ) -> None:
        """Test that MediaService creates required directories."""
        assert (temp_project_root / "test_audio").exists()
        assert (temp_project_root / "test_images").exists()

    def test_generate_audio_calls_service(
        self, media_service: MediaService, mock_audio_service: Mock
    ) -> None:
        """Test that generate_audio delegates to AudioService."""
        result = media_service.generate_audio("test text")

        mock_audio_service.generate_audio.assert_called_once_with("test text")
        assert result == "data/audio/test.mp3"

    def test_generate_image_calls_service(
        self, media_service: MediaService, mock_pexels_service: Mock
    ) -> None:
        """Test that generate_image delegates to PexelsService."""
        result = media_service.generate_image("test", "test query")

        mock_pexels_service.download_image.assert_called_once()
        args = mock_pexels_service.download_image.call_args[0]
        assert args[0] == "test query"  # search query
        assert "test" in args[1]  # image path contains word
        assert result is not None

    def test_generate_media_for_word(
        self,
        media_service: MediaService,
        mock_audio_service: Mock,
        mock_pexels_service: Mock,
    ) -> None:
        """Test generate_media_for_word returns MediaAssets."""
        result = media_service.generate_media_for_word(
            word="test", audio_text="audio text", search_query="search query"
        )

        mock_audio_service.generate_audio.assert_called_once_with("audio text")
        mock_pexels_service.download_image.assert_called_once()

        assert result.audio_path == "data/audio/test.mp3"
        assert result.image_path is not None

    def test_stats_tracking(self, media_service: MediaService) -> None:
        """Test statistics tracking functionality."""
        initial_stats = media_service.get_stats()

        assert initial_stats.audio_generated == 0
        assert initial_stats.audio_reused == 0
        assert initial_stats.images_downloaded == 0
        assert initial_stats.images_reused == 0
        assert initial_stats.generation_errors == 0

    def test_reset_stats(self, media_service: MediaService) -> None:
        """Test stats reset functionality."""
        # Generate some media to have non-zero stats
        media_service.generate_audio("test")

        # Reset stats
        media_service.reset_stats()
        stats = media_service.get_stats()

        assert stats.audio_generated == 0
        assert stats.audio_reused == 0
