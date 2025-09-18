"""Unit tests for MediaFileRegistrar service."""

import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock

import pytest

from langlearn.core.backends.base import DeckBackend
from langlearn.core.services.media_file_registrar import MediaFileRegistrar


class TestMediaFileRegistrar:
    """Test MediaFileRegistrar functionality."""

    @pytest.fixture
    def mock_backend(self) -> Mock:
        """Create a mock backend for testing."""
        backend = Mock(spec=DeckBackend)
        backend.add_media_file.return_value = Mock()
        return backend

    @pytest.fixture
    def temp_audio_dir(self) -> Generator[Path]:
        """Create temporary audio directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_dir = Path(temp_dir) / "audio"
            audio_dir.mkdir()

            # Create test audio files
            (audio_dir / "audio_test1.mp3").touch()
            (audio_dir / "audio_test2.mp3").touch()
            (audio_dir / "combined_audio.mp3").touch()

            yield audio_dir

    @pytest.fixture
    def temp_image_dir(self) -> Generator[Path]:
        """Create temporary image directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            image_dir = Path(temp_dir) / "images"
            image_dir.mkdir()

            # Create test image files
            (image_dir / "test_word.jpg").touch()
            (image_dir / "another_word.png").touch()

            yield image_dir

    def test_initialization(self, temp_audio_dir: Path, temp_image_dir: Path) -> None:
        """Test MediaFileRegistrar initialization."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        assert registrar._audio_base_path == temp_audio_dir
        assert registrar._image_base_path == temp_image_dir
        assert registrar._registered_files == set()

    def test_initialization_default_paths(self) -> None:
        """Test MediaFileRegistrar initialization with default paths."""
        registrar = MediaFileRegistrar()

        assert registrar._audio_base_path == Path("languages/audio")
        assert registrar._image_base_path == Path("languages/images")
        assert registrar._registered_files == set()

    def test_extract_audio_references(
        self, temp_audio_dir: Path, temp_image_dir: Path
    ) -> None:
        """Test extracting audio references from content."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        # Test single audio reference
        content = "Here is audio: [sound:audio_test1.mp3]"
        refs = registrar._extract_audio_references(content)
        assert refs == ["audio_test1.mp3"]

        # Test multiple audio references
        content = "[sound:audio_test1.mp3] and [sound:audio_test2.mp3]"
        refs = registrar._extract_audio_references(content)
        assert set(refs) == {"audio_test1.mp3", "audio_test2.mp3"}

        # Test no audio references
        content = "No audio here"
        refs = registrar._extract_audio_references(content)
        assert refs == []

        # Test malformed references
        content = "[sound:] and [audio:test.mp3] and sound:test.mp3"
        refs = registrar._extract_audio_references(content)
        assert refs == []  # Empty filename shouldn't be captured

    def test_extract_image_references(
        self, temp_audio_dir: Path, temp_image_dir: Path
    ) -> None:
        """Test extracting image references from content."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        # Test single image reference
        content = 'Here is image: <img src="test_word.jpg">'
        refs = registrar._extract_image_references(content)
        assert refs == ["test_word.jpg"]

        # Test image with attributes
        content = '<img class="card-image" src="another_word.png" alt="test">'
        refs = registrar._extract_image_references(content)
        assert refs == ["another_word.png"]

        # Test single quotes
        content = "<img src='test_word.jpg' class='image'>"
        refs = registrar._extract_image_references(content)
        assert refs == ["test_word.jpg"]

        # Test multiple images
        content = '<img src="test_word.jpg"> and <img src="another_word.png">'
        refs = registrar._extract_image_references(content)
        assert set(refs) == {"test_word.jpg", "another_word.png"}

        # Test no image references
        content = "No images here"
        refs = registrar._extract_image_references(content)
        assert refs == []

    def test_register_audio_file_success(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test successful audio file registration."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        result = registrar._register_audio_file("audio_test1.mp3", mock_backend)

        assert result is True
        assert "audio_test1.mp3" in registrar._registered_files
        mock_backend.add_media_file.assert_called_once_with(
            str(temp_audio_dir / "audio_test1.mp3"), media_type="audio"
        )

    def test_register_audio_file_not_found(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test audio file registration when file doesn't exist."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        result = registrar._register_audio_file("nonexistent.mp3", mock_backend)

        assert result is False
        assert "nonexistent.mp3" not in registrar._registered_files
        mock_backend.add_media_file.assert_not_called()

    def test_register_audio_file_already_registered(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test audio file registration when already registered."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)
        registrar._registered_files.add("audio_test1.mp3")

        result = registrar._register_audio_file("audio_test1.mp3", mock_backend)

        assert result is False
        mock_backend.add_media_file.assert_not_called()

    def test_register_audio_file_backend_error(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test audio file registration when backend fails."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)
        mock_backend.add_media_file.side_effect = Exception("Backend error")

        result = registrar._register_audio_file("audio_test1.mp3", mock_backend)

        assert result is False
        assert "audio_test1.mp3" not in registrar._registered_files

    def test_register_image_file_success(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test successful image file registration."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        result = registrar._register_image_file("test_word.jpg", mock_backend)

        assert result is True
        assert "test_word.jpg" in registrar._registered_files
        mock_backend.add_media_file.assert_called_once_with(
            str(temp_image_dir / "test_word.jpg"), media_type="image"
        )

    def test_register_image_file_not_found(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test image file registration when file doesn't exist."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        result = registrar._register_image_file("nonexistent.jpg", mock_backend)

        assert result is False
        assert "nonexistent.jpg" not in registrar._registered_files
        mock_backend.add_media_file.assert_not_called()

    def test_register_card_media_mixed_content(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test registering media from card with mixed audio and image content."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        field_values = [
            "German word with audio: [sound:audio_test1.mp3]",
            'Image example: <img src="test_word.jpg">',
            "Plain text field",
            'Multiple media: [sound:audio_test2.mp3] and <img src="another_word.png">',
        ]

        count = registrar.register_card_media(field_values, mock_backend)

        assert count == 4  # 2 audio + 2 image files
        assert len(registrar._registered_files) == 4
        assert mock_backend.add_media_file.call_count == 4

    def test_register_card_media_empty_fields(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test registering media from card with empty fields."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        field_values = ["", "", "No media content"]

        count = registrar.register_card_media(field_values, mock_backend)

        assert count == 0
        assert len(registrar._registered_files) == 0
        mock_backend.add_media_file.assert_not_called()

    def test_register_all_card_media(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test registering media from multiple cards."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        all_field_values = [
            ["[sound:audio_test1.mp3]", "Text field"],
            ['<img src="test_word.jpg">', "Another field"],
            ["[sound:audio_test2.mp3]", 'Image: <img src="another_word.png">'],
        ]

        total_count = registrar.register_all_card_media(all_field_values, mock_backend)

        assert total_count == 4  # 2 audio + 2 image files
        assert len(registrar._registered_files) == 4
        assert mock_backend.add_media_file.call_count == 4

    def test_get_registration_stats(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test getting registration statistics."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        # Register some files
        registrar._register_audio_file("audio_test1.mp3", mock_backend)
        registrar._register_image_file("test_word.jpg", mock_backend)

        stats = registrar.get_registration_stats()

        assert stats["total_files_registered"] == 2
        assert set(stats["registered_files"]) == {"audio_test1.mp3", "test_word.jpg"}

    def test_reset_registration_tracking(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test resetting registration tracking."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        # Register some files
        registrar._register_audio_file("audio_test1.mp3", mock_backend)
        registrar._register_image_file("test_word.jpg", mock_backend)

        assert len(registrar._registered_files) == 2

        # Reset tracking
        registrar.reset_registration_tracking()

        assert len(registrar._registered_files) == 0

    def test_duplicate_registration_prevention(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test that duplicate files are not registered multiple times."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        # Try to register the same file multiple times
        field_values = [
            "[sound:audio_test1.mp3] and [sound:audio_test1.mp3]",
            "[sound:audio_test1.mp3]",
        ]

        count = registrar.register_card_media(field_values, mock_backend)

        # Should only register once despite multiple references
        assert count == 1
        assert len(registrar._registered_files) == 1
        mock_backend.add_media_file.assert_called_once()

    def test_malformed_media_references(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test handling of malformed media references."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        field_values = [
            "[sound:]",  # Empty filename
            "<img src=''>",  # Empty src
            "[audio:test.mp3]",  # Wrong format
            "<image src='test.jpg'>",  # Wrong tag
            "sound:test.mp3",  # Missing brackets
        ]

        count = registrar.register_card_media(field_values, mock_backend)

        assert count == 0  # No valid references should be registered
        mock_backend.add_media_file.assert_not_called()

    def test_complex_html_image_extraction(
        self, temp_audio_dir: Path, temp_image_dir: Path, mock_backend: Mock
    ) -> None:
        """Test extracting images from complex HTML structures."""
        registrar = MediaFileRegistrar(temp_audio_dir, temp_image_dir)

        complex_html = """
        <div class="card-content">
            <img class="word-image" src="test_word.jpg" alt="Test word" />
            <p>Some text with <img src='another_word.png' class='inline-image'></p>
        </div>
        """

        refs = registrar._extract_image_references(complex_html)

        assert set(refs) == {"test_word.jpg", "another_word.png"}


class TestMediaFileRegistrarIntegration:
    """Integration tests for MediaFileRegistrar."""

    def test_end_to_end_registration_workflow(self) -> None:
        """Test complete workflow from card fields to backend registration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test directory structure
            temp_path = Path(temp_dir)
            audio_dir = temp_path / "audio"
            image_dir = temp_path / "images"
            audio_dir.mkdir()
            image_dir.mkdir()

            # Create test media files
            (audio_dir / "example_audio.mp3").write_text("fake audio")
            (image_dir / "example_image.jpg").write_text("fake image")

            # Create registrar and mock backend
            registrar = MediaFileRegistrar(audio_dir, image_dir)
            mock_backend = Mock(spec=DeckBackend)
            mock_backend.add_media_file.return_value = Mock()

            # Simulate card field data from record processing
            card_fields = [
                "Katze",  # German word
                "cat",  # English translation
                "[sound:example_audio.mp3]",  # Audio field
                '<img src="example_image.jpg">',  # Image field
                "Die Katze schläft.",  # Example sentence
            ]

            # Register media files
            count = registrar.register_card_media(card_fields, mock_backend)

            # Verify results
            assert count == 2  # One audio + one image
            assert mock_backend.add_media_file.call_count == 2

            # Verify correct file paths were registered
            calls = mock_backend.add_media_file.call_args_list
            registered_paths = [call[0][0] for call in calls]
            expected_paths = {
                str(audio_dir / "example_audio.mp3"),
                str(image_dir / "example_image.jpg"),
            }
            assert set(registered_paths) == expected_paths

            # Verify media types
            media_types = [call[1]["media_type"] for call in calls]
            assert set(media_types) == {"audio", "image"}
