"""Models for German language learning data."""

# Field processing interfaces (legacy - kept for backward compatibility)
from .field_processor import (
    FieldProcessingError,
    FieldProcessor,
    MediaGenerator,
    format_media_reference,
    validate_minimum_fields,
)

# Model factory (legacy - kept for backward compatibility)
from .model_factory import ModelFactory

# Clean Pipeline Architecture - Record system
from .records import (
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
    # Legacy interfaces
    "FieldProcessingError",
    "FieldProcessor",
    "MediaGenerator",
    "ModelFactory",
    "NegationRecord",
    "NounRecord",
    "create_record",
    "format_media_reference",
    "validate_minimum_fields",
]
