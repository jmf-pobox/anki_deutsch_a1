"""TTS (Text-to-Speech) configuration protocol for language implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_polly.literals import (
        EngineType,
        LanguageCodeType,
        VoiceIdType,
    )


@dataclass(frozen=True)
class TTSConfig:
    """Configuration for Text-to-Speech audio generation.

    This dataclass encapsulates the TTS settings that each language
    implementation should provide for generating audio content.
    """

    voice_id: VoiceIdType
    """AWS Polly voice ID (e.g., 'Marlene', 'Tatyana', 'Seoyeon')"""

    language_code: LanguageCodeType
    """ISO language code (e.g., 'de-DE', 'ru-RU', 'ko-KR')"""

    engine: EngineType = "standard"
    """Polly engine type - 'standard' or 'neural' (default: 'standard')"""
