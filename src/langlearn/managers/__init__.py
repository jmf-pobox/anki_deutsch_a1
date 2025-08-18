"""Orchestration layer for coordinating services and backends.

This package contains manager classes that orchestrate multiple services
and backends to provide higher-level functionality while maintaining
clean separation of concerns.

Managers handle coordination logic that doesn't belong in domain services
or infrastructure backends.
"""

from .deck_manager import DeckManager
from .media_manager import MediaManager

__all__ = ["DeckManager", "MediaManager"]
