"""Clean, observable deck building API with phase-based architecture.

This package provides a comprehensive interface for creating language learning
Anki decks with clear phases, read access to intermediate work, and observable
progress tracking.
"""

# Core API
from .builder import DeckBuilderAPI

# Data types for structured access to pipeline state
from .data_types import (
    BuiltCards,
    Card,
    CardPreview,
    EnrichedData,
    ExportResult,
    LoadedData,
    MediaFile,
    PipelineSummary,
)

# Phase management
from .phases import InvalidPhaseError, Phase

# Progress reporting
from .progress import EnrichmentProgress

__all__ = [
    "BuiltCards",
    "Card",
    "CardPreview",
    "DeckBuilderAPI",
    "EnrichedData",
    "EnrichmentProgress",
    "ExportResult",
    "InvalidPhaseError",
    "LoadedData",
    "MediaFile",
    "Phase",
    "PipelineSummary",
]
