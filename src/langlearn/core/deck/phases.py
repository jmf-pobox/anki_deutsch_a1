"""Pipeline phases and phase management for deck building."""

from enum import Enum


class Phase(Enum):
    """Pipeline phases with clear transitions."""

    INITIALIZED = "initialized"
    DATA_LOADED = "data_loaded"
    MEDIA_ENRICHED = "media_enriched"
    CARDS_BUILT = "cards_built"
    DECK_EXPORTED = "deck_exported"


class InvalidPhaseError(Exception):
    """Raised when an operation is attempted in the wrong phase."""

    pass
