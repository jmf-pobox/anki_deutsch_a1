"""Service protocols for dependency injection."""

from .anthropic_protocol import AnthropicServiceProtocol
from .audio_protocol import AudioServiceProtocol
from .media_generation_protocol import MediaGenerationCapable
from .media_protocol import MediaServiceProtocol
from .pexels_protocol import PexelsServiceProtocol

__all__ = [
    "AnthropicServiceProtocol",
    "AudioServiceProtocol",
    "MediaGenerationCapable",
    "MediaServiceProtocol",
    "PexelsServiceProtocol",
]
