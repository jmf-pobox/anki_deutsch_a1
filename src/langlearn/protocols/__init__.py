"""Service protocols for dependency injection."""

from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)
from langlearn.protocols.image_search_protocol import ImageSearchProtocol
from langlearn.protocols.media_generation_protocol import MediaGenerationCapable

__all__ = [
    "ImageQueryGenerationProtocol",
    "ImageSearchProtocol",
    "MediaGenerationCapable",
]
