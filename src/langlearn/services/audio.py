"""Audio service for text-to-speech conversion using AWS Polly."""

import hashlib
import logging
import logging.handlers
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

import boto3  # type: ignore[import-untyped]  # External dependency boundary - no stubs available
from botocore.exceptions import ClientError, NoCredentialsError  # type: ignore[import-untyped]  # External dependency boundary - no stubs available
from mypy_boto3_polly.literals import (
    EngineType,
    LanguageCodeType,
    OutputFormatType,
    TextTypeType,
    VoiceIdType,
)
from mypy_boto3_polly.type_defs import SynthesizeSpeechOutputTypeDef

if TYPE_CHECKING:
    from mypy_boto3_polly.client import PollyClient

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Add file handler for audio.log
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "audio.log",
    maxBytes=1024 * 1024,
    backupCount=5,  # 1MB
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)


class PollyRequestParams(TypedDict):
    Text: str
    TextType: TextTypeType
    VoiceId: VoiceIdType
    LanguageCode: LanguageCodeType
    OutputFormat: OutputFormatType
    Engine: EngineType
    SampleRate: str


class AudioService:
    """Service for generating audio files using AWS Polly.

    This service provides text-to-speech functionality using AWS Polly with configurable
    voice, language, and speech rate settings.
    """

    def __init__(
        self,
        output_dir: str = "audio",
        voice_id: VoiceIdType = "Daniel",
        language_code: LanguageCodeType = "de-DE",
        speech_rate: int = 75,
    ) -> None:
        """Initialize the AudioService.

        Args:
            output_dir: Directory to store generated audio files
            voice_id: AWS Polly voice ID (default: "Daniel")
            language_code: Language code (default: "de-DE")
            speech_rate: Speech rate in percentage (default: 75)
        """
        if TYPE_CHECKING:
            self.client: PollyClient
        self.client = boto3.client("polly")
        self.output_dir = Path(output_dir)
        self.voice_id = voice_id
        self.language_code = language_code
        self.speech_rate = speech_rate
        self.output_dir.mkdir(exist_ok=True)
        logger.info(
            "AudioService initialized with voice_id=%s, language_code=%s, "
            "speech_rate=%d",
            voice_id,
            language_code,
            speech_rate,
        )

    def generate_audio(self, text: str) -> str:
        """Generate audio file from text using AWS Polly.

        Args:
            text: Text to convert to speech

        Returns:
            Path to generated audio file

        Raises:
            NoCredentialsError: If AWS credentials are not found
            ClientError: If there is an error with the AWS Polly service
            RuntimeError: If there is an error saving the audio file
        """
        logger.info("Generating audio for text: %s", text)
        try:
            # Use SSML for better audio quality and speech rate control
            ssml_text = (
                f'<speak><prosody rate="{self.speech_rate}%">{text}</prosody></speak>'
            )
            logger.debug("Generated SSML: %s", ssml_text)
            logger.debug("SSML length: %d", len(ssml_text))

            # Log the full request parameters
            request_params: PollyRequestParams = {
                "Text": ssml_text,
                "TextType": "ssml",
                "VoiceId": self.voice_id,
                "LanguageCode": self.language_code,
                "OutputFormat": "mp3",
                "Engine": "neural",  # Daniel requires neural
                "SampleRate": "16000",  # Lower sample rate for smaller files (was 22050 default)
            }
            logger.debug("AWS Polly request parameters: %s", request_params)

            try:
                response = self.client.synthesize_speech(**request_params)
            except NoCredentialsError:
                logger.error(
                    "AWS credentials not found. Please configure your AWS credentials."
                )
                raise

            filepath = self._save_audio_file(text, response)
            if filepath is None:
                raise RuntimeError("Failed to save audio file")
            return filepath

        except ClientError as e:
            logger.error("Error generating audio: %s", e)
            logger.error("Error details: %s", e.response)
            logger.error("Failed SSML: %s", ssml_text)  # Log the SSML that failed
            raise

    def _save_audio_file(
        self, text: str, response: SynthesizeSpeechOutputTypeDef
    ) -> str | None:
        """Save the audio stream to a file.

        Args:
            text: The original text (used for filename generation)
            response: The AWS Polly response containing the audio stream

        Returns:
            Path to the saved audio file, or None if saving failed
        """
        # Generate unique filename based on text content
        filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
        filepath = self.output_dir / filename

        try:
            # Write the audio stream to a file
            with open(filepath, "wb") as f:
                audio_stream = response["AudioStream"]
                f.write(audio_stream.read())
            logger.info("Successfully saved audio file to: %s", filepath)
            return str(filepath)
        except OSError as e:
            logger.error("Error saving audio file: %s", e)
            return None
