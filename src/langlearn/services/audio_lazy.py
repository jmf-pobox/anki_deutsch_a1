"""Audio service with lazy initialization for better test isolation.

This module demonstrates the lazy loading pattern for external services,
allowing unit tests to run without requiring AWS credentials.
"""

import hashlib
import logging
import logging.handlers
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import (  # type: ignore[import-untyped]
    ClientError,
    NoCredentialsError,
)
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
    backupCount=5,
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
    """Type definition for Polly synthesize_speech parameters."""

    Text: str
    TextType: TextTypeType
    VoiceId: VoiceIdType
    LanguageCode: LanguageCodeType
    OutputFormat: OutputFormatType
    Engine: EngineType
    SampleRate: str


class AudioServiceLazy:
    """Service for generating audio files using AWS Polly with lazy initialization.

    This service provides text-to-speech functionality using AWS Polly with configurable
    voice, language, and speech rate settings. The AWS Polly client is initialized
    lazily on first use, allowing unit tests to run without AWS credentials.

    Key Features:
        - Lazy initialization of AWS Polly client
        - Hash-based caching to avoid duplicate API calls
        - Configurable voice, language, and speech rate
        - Proper error handling and logging
    """

    def __init__(
        self,
        output_dir: str = "audio",
        voice_id: VoiceIdType = "Daniel",
        language_code: LanguageCodeType = "de-DE",
        speech_rate: int = 75,
    ) -> None:
        """Initialize the AudioService with lazy client loading.

        Args:
            output_dir: Directory to store generated audio files
            voice_id: AWS Polly voice ID (default: "Daniel" for German)
            language_code: Language code (default: "de-DE" for German)
            speech_rate: Speech rate in percentage (default: 75 for slower speech)
        """
        self.output_dir = Path(output_dir)
        self.voice_id = voice_id
        self.language_code = language_code
        self.speech_rate = speech_rate
        self.output_dir.mkdir(exist_ok=True)

        # Lazy initialization - client created on first use
        self._client: PollyClient | None = None

        logger.info(
            "AudioService initialized (lazy mode) with voice_id=%s, language_code=%s, "
            "speech_rate=%d",
            voice_id,
            language_code,
            speech_rate,
        )

    @property
    def client(self) -> "PollyClient":
        """Lazy load the Polly client on first access.

        Returns:
            PollyClient: The AWS Polly client instance

        Raises:
            NoCredentialsError: If AWS credentials are not configured
            ClientError: If there's an error creating the client
        """
        if self._client is None:
            logger.debug("Initializing AWS Polly client on first use")
            try:
                self._client = boto3.client("polly")
                logger.info("AWS Polly client initialized successfully")
            except NoCredentialsError:
                logger.error("AWS credentials not found")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize Polly client: {e}")
                raise
        return self._client

    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key for the given text.

        Args:
            text: The text to generate a cache key for

        Returns:
            str: A hash-based cache key
        """
        # Include voice settings in the cache key
        cache_input = f"{text}:{self.voice_id}:{self.language_code}:{self.speech_rate}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    def _get_cached_file_path(self, text: str) -> Path | None:
        """Check if audio for this text already exists.

        Args:
            text: The text to check for cached audio

        Returns:
            Path | None: Path to cached file if it exists, None otherwise
        """
        cache_key = self._get_cache_key(text)
        possible_path = self.output_dir / f"{cache_key}.mp3"

        if possible_path.exists():
            logger.debug(f"Found cached audio file: {possible_path}")
            return possible_path

        return None

    def generate_audio(self, text: str, filename: str | None = None) -> Path:
        """Generate audio file from text using AWS Polly.

        This method uses lazy initialization - the Polly client is only created
        when this method is called for the first time.

        Args:
            text: The text to convert to speech
            filename: Optional custom filename (without extension)

        Returns:
            Path: Path to the generated audio file

        Raises:
            NoCredentialsError: If AWS credentials are not configured
            ClientError: If there's an error with the Polly service
        """
        # Check cache first
        cached_file = self._get_cached_file_path(text)
        if cached_file:
            logger.info(f"Using cached audio for text: {text[:50]}...")
            return cached_file

        # Generate filename if not provided
        if filename is None:
            filename = self._get_cache_key(text)

        output_path = self.output_dir / f"{filename}.mp3"

        try:
            # Client is only created here when actually needed
            logger.debug(f"Generating audio for text: {text[:50]}...")

            # Prepare SSML text with speech rate
            ssml_text = (
                f'<speak><prosody rate="{self.speech_rate}%">{text}</prosody></speak>'
            )

            # Create Polly request parameters
            params: PollyRequestParams = {
                "Text": ssml_text,
                "TextType": "ssml",
                "VoiceId": self.voice_id,
                "LanguageCode": self.language_code,
                "OutputFormat": "mp3",
                "Engine": "neural",
                "SampleRate": "24000",
            }

            # Make the API call (lazy client initialization happens here)
            response: SynthesizeSpeechOutputTypeDef = self.client.synthesize_speech(
                **params
            )

            # Save the audio stream to file
            with open(output_path, "wb") as file:
                file.write(response["AudioStream"].read())

            logger.info(f"Audio generated successfully: {output_path}")
            return output_path

        except NoCredentialsError:
            logger.error("AWS credentials not configured")
            raise
        except ClientError as e:
            logger.error(f"AWS Polly error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating audio: {e}")
            raise

    def validate_configuration(self) -> bool:
        """Validate that the service is properly configured.

        This method attempts to create the Polly client to verify credentials
        and configuration are correct.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # This will trigger lazy initialization
            _ = self.client
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
