"""Service protocols for dependency injection."""

from langlearn.protocols.domain_model_protocol import LanguageDomainModel
from langlearn.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)
from langlearn.protocols.image_search_protocol import ImageSearchProtocol
from langlearn.protocols.language_protocol import Language
from langlearn.protocols.media_enricher_protocol import MediaEnricherProtocol
from langlearn.protocols.media_generation_protocol import MediaGenerationCapable

__all__ = [
    "ImageQueryGenerationProtocol",
    "ImageSearchProtocol",
    "Language",
    "LanguageDomainModel",
    "MediaEnricherProtocol",
    "MediaGenerationCapable",
]
