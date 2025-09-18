"""Progress reporting classes for deck building operations."""

from dataclasses import dataclass


@dataclass
class EnrichmentProgress:
    """Progress information during media enrichment."""
    record_type: str
    processed: int
    total: int
    media_created: int
