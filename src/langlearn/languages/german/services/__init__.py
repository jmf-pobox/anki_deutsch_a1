"""German language-specific services package.

This package contains business logic services that are specific to German language
learning, including record mapping, card building, media enrichment, and article
processing.
"""

# Import key German services for easier access
from .card_builder import CardBuilder
from .media_enricher import MediaEnricher, StandardMediaEnricher
from .record_mapper import RecordMapper

__all__ = [
    "CardBuilder",
    "MediaEnricher",
    "RecordMapper",
    "StandardMediaEnricher",
]
