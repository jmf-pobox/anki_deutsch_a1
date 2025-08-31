"""Service protocols for dependency injection."""

from .audio_protocol import AudioServiceProtocol
from .media_generation_protocol import MediaGenerationCapable
from .media_protocol import MediaServiceProtocol
from .pexels_protocol import PexelsServiceProtocol

__all__ = [
    "AudioServiceProtocol",
    "MediaGenerationCapable",
    "MediaServiceProtocol",
    "PexelsServiceProtocol",
]
