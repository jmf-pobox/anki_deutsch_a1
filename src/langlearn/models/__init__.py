"""Language-agnostic model infrastructure.

This package contains shared model infrastructure that applies across
all languages. Language-specific models and records are now organized
under langlearn.languages.<language_code>.*

For German-specific models and records:
- Domain models: langlearn.languages.german.models.*
- Records: langlearn.languages.german.records.*

For backward compatibility during migration, key record types are still
available at this level, but new code should import directly from
language-specific packages.
"""

# Backward compatibility imports - these will be deprecated in future versions
from langlearn.languages.german.records.records import (
    AdjectiveRecord,
    AdverbRecord,
    BaseRecord,
    NegationRecord,
    NounRecord,
    create_record,
)

__all__ = [
    # Backward compatibility - prefer language-specific imports
    "AdjectiveRecord",
    "AdverbRecord", 
    "BaseRecord",
    "NegationRecord",
    "NounRecord",
    "create_record",
]
