"""German language-specific services package.

This package contains business logic services that are specific to German language
learning, including record mapping, card building, and article processing.

Note: MediaEnricher has been moved to langlearn.core.services.media_enricher
"""

# Import key German services for easier access
from .card_builder import CardBuilder
from .record_mapper import RecordMapper

__all__ = [
    "CardBuilder",
    "RecordMapper",
]
