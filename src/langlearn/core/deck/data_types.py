"""Data types for deck building pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from langlearn.core.records import BaseRecord

if TYPE_CHECKING:
    from .phases import Phase


@dataclass
class ValidationError:
    """Represents a validation error during data loading."""

    record_index: int
    field_name: str
    message: str


@dataclass
class LoadedData:
    """Results from data loading phase."""

    records_by_type: dict[str, list[BaseRecord]]
    total_records: int
    source_paths: list[Path]
    validation_errors: list[ValidationError]


@dataclass
class MediaFile:
    """Represents a created media file."""

    path: Path
    type: str  # "audio" or "image"
    reference: str  # Anki reference like "[sound:file.mp3]"


@dataclass
class EnrichmentError:
    """Represents an error during media enrichment."""

    record_index: int
    error_type: str
    message: str


@dataclass
class EnrichedData:
    """Results from media enrichment phase."""

    records: list[BaseRecord]
    media_data: list[dict[str, str]]  # Parallel to records
    media_files_created: list[MediaFile]
    enrichment_errors: list[EnrichmentError]


@dataclass
class BuildError:
    """Represents an error during card building."""

    record_index: int
    record_type: str
    message: str


@dataclass
class Card:
    """Represents a built card."""

    fields: dict[str, str]
    note_type_name: str
    template_name: str


@dataclass
class BuiltCards:
    """Results from card building phase."""

    cards: list[tuple[list[str], Any]]  # (field_values, note_type)
    cards_by_type: dict[str, list[Card]]
    template_usage: dict[str, int]
    build_errors: list[BuildError]


@dataclass
class CardPreview:
    """Preview of a specific card."""

    front: str
    back: str
    fields: dict[str, str]
    note_type: str


@dataclass
class ExportResult:
    """Results from deck export phase."""

    output_path: Path
    file_size: int
    cards_exported: int


@dataclass
class PipelineSummary:
    """Summary of entire pipeline state."""

    phase: "Phase"  # Forward reference
    loaded: int
    enriched: int
    built: int
    exported: bool
