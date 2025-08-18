"""Unit tests for AudioService."""

import tempfile
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
from botocore.exceptions import ClientError, NoCredentialsError  # type: ignore[import-untyped]  # External dependency boundary - no stubs available

from langlearn.services.audio import AudioService


class TestAudioService:
    """Test AudioService functionality."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def audio_service(self, temp_dir: Path) -> AudioService:
        """AudioService instance for testing."""
        with patch("langlearn.services.audio.boto3.client"):
            return AudioService(
                output_dir=str(temp_dir / "audio"),
                voice_id="Daniel",
                language_code="de-DE",
                speech_rate=75,
            )

    def test_init_creates_output_directory(self, temp_dir: Path) -> None:
        """Test that AudioService creates output directory."""
        output_dir = temp_dir / "audio_output"

        with patch("langlearn.services.audio.boto3.client"):
            service = AudioService(output_dir=str(output_dir))

        assert output_dir.exists()
        assert service.output_dir == output_dir
        assert service.voice_id == "Daniel"
        assert service.language_code == "de-DE"
        assert service.speech_rate == 75

    def test_init_with_custom_parameters(self, temp_dir: Path) -> None:
        """Test AudioService initialization with custom parameters."""
        output_dir = temp_dir / "custom_audio"

        with patch("langlearn.services.audio.boto3.client"):
            service = AudioService(
                output_dir=str(output_dir),
                voice_id="Marlene",
                language_code="de-AT",
                speech_rate=90,
            )

        assert service.output_dir == output_dir
        assert service.voice_id == "Marlene"
        assert service.language_code == "de-AT"
        assert service.speech_rate == 90

    @patch("langlearn.services.audio.boto3.client")
    def test_generate_audio_success(
        self, mock_boto_client: Mock, audio_service: AudioService
    ) -> None:
        """Test successful audio generation."""
        # Mock the Polly client
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        audio_service.client = mock_client

        # Mock the response with audio stream
        mock_audio_stream = BytesIO(b"fake audio data")
        mock_response = {"AudioStream": mock_audio_stream}
        mock_client.synthesize_speech.return_value = mock_response

        # Mock file operations
        with patch("builtins.open", mock_open()) as mock_file:
            result = audio_service.generate_audio("test text")

        # Verify the client was called with correct parameters
        mock_client.synthesize_speech.assert_called_once()
        call_args = mock_client.synthesize_speech.call_args[1]

        assert (
            call_args["Text"]
            == '<speak><prosody rate="75%">test text</prosody></speak>'
        )
        assert call_args["TextType"] == "ssml"
        assert call_args["VoiceId"] == "Daniel"
        assert call_args["LanguageCode"] == "de-DE"
        assert call_args["OutputFormat"] == "mp3"
        assert call_args["Engine"] == "neural"

        # Verify file was written
        mock_file.assert_called_once()
        assert result is not None
        assert result.endswith(".mp3")

    @patch("langlearn.services.audio.boto3.client")
    def test_generate_audio_no_credentials_error(
        self, mock_boto_client: Mock, audio_service: AudioService
    ) -> None:
        """Test NoCredentialsError exception handling."""
        # Mock the Polly client to raise NoCredentialsError
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        audio_service.client = mock_client

        mock_client.synthesize_speech.side_effect = NoCredentialsError()

        with pytest.raises(NoCredentialsError):
            audio_service.generate_audio("test text")

    @patch("langlearn.services.audio.boto3.client")
    def test_generate_audio_client_error(
        self, mock_boto_client: Mock, audio_service: AudioService
    ) -> None:
        """Test ClientError exception handling."""
        # Mock the Polly client to raise ClientError
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        audio_service.client = mock_client

        mock_error_response = {
            "Error": {"Code": "InvalidParameterValue", "Message": "Invalid voice ID"}
        }
        mock_client.synthesize_speech.side_effect = ClientError(
            mock_error_response, "SynthesizeSpeech"
        )

        with pytest.raises(ClientError):
            audio_service.generate_audio("test text")

    @patch("langlearn.services.audio.boto3.client")
    def test_generate_audio_save_file_fails(
        self, mock_boto_client: Mock, audio_service: AudioService
    ) -> None:
        """Test RuntimeError when save_audio_file returns None."""
        # Mock the Polly client
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        audio_service.client = mock_client

        # Mock successful Polly response
        mock_audio_stream = BytesIO(b"fake audio data")
        mock_response = {"AudioStream": mock_audio_stream}
        mock_client.synthesize_speech.return_value = mock_response

        # Mock _save_audio_file to return None (simulate failure)
        with patch.object(audio_service, "_save_audio_file", return_value=None):
            with pytest.raises(RuntimeError, match="Failed to save audio file"):
                audio_service.generate_audio("test text")

    def test_save_audio_file_success(self, audio_service: AudioService) -> None:
        """Test successful audio file saving."""
        # Mock response with audio stream
        mock_audio_stream = BytesIO(b"fake audio data")
        mock_response = {"AudioStream": mock_audio_stream}

        with patch("builtins.open", mock_open()) as mock_file:
            result = audio_service._save_audio_file("test text", mock_response)  # type: ignore[arg-type]  # Test boundary - mocking boto3 response

        # Verify file operations
        mock_file.assert_called_once()
        assert result is not None
        assert result.endswith(".mp3")

    def test_save_audio_file_os_error(self, audio_service: AudioService) -> None:
        """Test OSError exception handling in _save_audio_file."""
        # Mock response with audio stream
        mock_audio_stream = BytesIO(b"fake audio data")
        mock_response = {"AudioStream": mock_audio_stream}

        # Mock file operations to raise OSError
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            result = audio_service._save_audio_file("test text", mock_response)  # type: ignore[arg-type]  # Test boundary - mocking boto3 response

        # Should return None on OSError
        assert result is None

    def test_filename_generation(self, audio_service: AudioService) -> None:
        """Test that filename is generated consistently using MD5 hash."""
        # Mock response with audio stream
        mock_audio_stream = BytesIO(b"fake audio data")
        mock_response = {"AudioStream": mock_audio_stream}

        with patch("builtins.open", mock_open()):
            result1 = audio_service._save_audio_file("test text", mock_response)  # type: ignore[arg-type]  # Test boundary - mocking boto3 response
            result2 = audio_service._save_audio_file("test text", mock_response)  # type: ignore[arg-type]  # Test boundary - mocking boto3 response

        # Same text should generate same filename
        assert result1 == result2
        assert result1 is not None
        assert result1.endswith(".mp3")

    def test_ssml_generation(self, audio_service: AudioService) -> None:
        """Test SSML generation with different speech rates."""
        # Test with custom speech rate
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("langlearn.services.audio.boto3.client"):
                service = AudioService(output_dir=str(temp_dir), speech_rate=90)

            mock_client = Mock()
            service.client = mock_client

            mock_audio_stream = BytesIO(b"fake audio data")
            mock_response = {"AudioStream": mock_audio_stream}
            mock_client.synthesize_speech.return_value = mock_response

            with patch("builtins.open", mock_open()):
                service.generate_audio("Hallo Welt")

            # Verify SSML contains correct speech rate
            call_args = mock_client.synthesize_speech.call_args[1]
            expected_ssml = '<speak><prosody rate="90%">Hallo Welt</prosody></speak>'
            assert call_args["Text"] == expected_ssml

    def test_audio_parameters(self, audio_service: AudioService) -> None:
        """Test that correct audio parameters are sent to Polly."""
        mock_client = Mock()
        audio_service.client = mock_client

        mock_audio_stream = BytesIO(b"fake audio data")
        mock_response = {"AudioStream": mock_audio_stream}
        mock_client.synthesize_speech.return_value = mock_response

        with patch("builtins.open", mock_open()):
            audio_service.generate_audio("test")

        # Verify all required parameters are present
        call_args = mock_client.synthesize_speech.call_args[1]

        assert "Text" in call_args
        assert "TextType" in call_args
        assert "VoiceId" in call_args
        assert "LanguageCode" in call_args
        assert "OutputFormat" in call_args
        assert "Engine" in call_args
        assert "SampleRate" in call_args

        # Verify parameter values
        assert call_args["TextType"] == "ssml"
        assert call_args["VoiceId"] == "Daniel"
        assert call_args["LanguageCode"] == "de-DE"
        assert call_args["OutputFormat"] == "mp3"
        assert call_args["Engine"] == "neural"
        assert call_args["SampleRate"] == "16000"
