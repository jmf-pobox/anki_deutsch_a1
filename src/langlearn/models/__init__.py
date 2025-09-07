"""Models for German language learning data."""

# Clean Pipeline Architecture - Record system
from langlearn.languages.german.records.records import (
    AdjectiveRecord,
    AdverbRecord,
    BaseRecord,
    NegationRecord,
    NounRecord,
    create_record,
)

__all__ = [
    # Clean Pipeline Architecture
    "AdjectiveRecord",
    "AdverbRecord",
    "BaseRecord",
    "NegationRecord",
    "NounRecord",
    "create_record",
]
