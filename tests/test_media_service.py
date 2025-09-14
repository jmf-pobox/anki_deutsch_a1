"""Unit tests for MediaService."""

import hashlib
import tempfile
from collections.abc import Generator
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
    def temp_project_root(self) -> Generator[Path]:
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

    def test_audio_caching_behavior(self, tmp_path: Path) -> None:
        """Test that audio files are reused when they already exist."""
        # Setup services with real temp directory
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        mock_audio_service = Mock(spec=AudioService)
        mock_audio_service.generate_audio.return_value = str(audio_dir / "test.mp3")

        mock_pexels_service = Mock(spec=PexelsService)
        config = MediaGenerationConfig(audio_dir=str(audio_dir))

        media_service = MediaService(
            mock_audio_service, mock_pexels_service, config, tmp_path
        )

        # Create a fake existing audio file
        test_text = "Hello, world!"
        filename = f"{hashlib.md5(test_text.encode()).hexdigest()}.mp3"
        existing_file = audio_dir / filename
        existing_file.write_text("fake audio data")

        # First call should reuse existing file (no AudioService call)
        result1 = media_service.generate_audio(test_text)
        assert result1 == str(existing_file)
        mock_audio_service.generate_audio.assert_not_called()

        # Stats should show reuse
        stats = media_service.get_stats()
        assert stats.audio_reused == 1
        assert stats.audio_generated == 0

        # Second call should also reuse (still no AudioService call)
        result2 = media_service.generate_audio(test_text)
        assert result2 == str(existing_file)
        mock_audio_service.generate_audio.assert_not_called()

        # Stats should show second reuse
        stats = media_service.get_stats()
        assert stats.audio_reused == 2
        assert stats.audio_generated == 0
