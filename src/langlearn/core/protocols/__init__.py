"""Service protocols for dependency injection."""

from langlearn.core.protocols.domain_model_protocol import LanguageDomainModel
from langlearn.core.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)
from langlearn.core.protocols.image_search_protocol import ImageSearchProtocol
from langlearn.core.protocols.language_protocol import Language
from langlearn.core.protocols.media_enricher_protocol import MediaEnricherProtocol
from langlearn.core.protocols.media_generation_protocol import MediaGenerationCapable

__all__ = [
    "ImageQueryGenerationProtocol",
    "ImageSearchProtocol",
    "Language",
    "LanguageDomainModel",
    "MediaEnricherProtocol",
    "MediaGenerationCapable",
]
