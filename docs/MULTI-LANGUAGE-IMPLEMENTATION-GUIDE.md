# Multi-Language Implementation Guide

## Overview

This guide demonstrates how to add new language support to the Anki language learning system using the proven multi-language architecture. The Russian noun implementation serves as a complete reference example.

## Architecture Proof

**✅ Multi-Language Architecture Success**: Russian language support was successfully implemented with **zero modifications** to AnkiBackend, proving the Field Processing Delegation Pattern works as designed.

### Key Achievement Metrics

- **🇩🇪 German Language**: Complete with 7+ word types, 54 templates, full media pipeline
- **🇷🇺 Russian Language**: Proof-of-concept with noun support, case system handling
- **🏗️ AnkiBackend**: 100% language-agnostic, no modifications required for new languages
- **📊 Code Reuse**: ~90% of core infrastructure shared between languages
- **🧪 Test Coverage**: Full type safety, unit tests pass, integration tests successful

## Russian Implementation Structure

```
src/langlearn/languages/russian/
├── __init__.py                  # Package initialization
├── language.py                  # RussianLanguage class (Language protocol)
├── records/
│   ├── __init__.py
│   └── noun_record.py          # RussianNounRecord (BaseRecord)
├── models/
│   ├── __init__.py
│   └── noun.py                 # RussianNoun (MediaGenerationCapable)
└── templates/
    ├── noun_RU_ru_front.html   # Russian noun front template
    ├── noun_RU_ru_back.html    # Russian noun back template
    └── noun_RU_ru.css          # Russian styling with Cyrillic fonts
```

## Step-by-Step Implementation Guide

### 1. Create Language Package Structure

```bash
mkdir -p src/langlearn/languages/{language_code}/{records,models,templates}
touch src/langlearn/languages/{language_code}/__init__.py
touch src/langlearn/languages/{language_code}/records/__init__.py
touch src/langlearn/languages/{language_code}/models/__init__.py
```

### 2. Implement Language Class

Create `language.py` implementing the `Language` protocol:

```python
from langlearn.protocols.language_protocol import Language

class YourLanguage:
    @property
    def code(self) -> str:
        return "xx"  # ISO language code

    @property
    def name(self) -> str:
        return "Your Language"

    def get_supported_record_types(self) -> list[str]:
        return ["noun"]  # Start with one type

    def create_record_from_csv(self, record_type: str, fields: list[str]) -> BaseRecord:
        # Language-specific CSV parsing logic

    def create_domain_model(self, record_type: str, record: BaseRecord) -> LanguageDomainModel:
        # Language-specific domain model creation

    def process_fields_for_anki(self, note_type_name: str, fields: list[str], media_enricher: Any) -> list[str]:
        # Language-specific field processing for Anki
```

### 3. Create Record Classes

In `records/noun_record.py`:

```python
from langlearn.core.records.base_record import BaseRecord, RecordType
from typing import Literal

class YourNounRecord(BaseRecord):
    # Core fields
    noun: str
    english: str

    # Language-specific grammatical features
    # (e.g., gender, case forms, etc.)

    @classmethod
    def get_record_type(cls) -> RecordType:
        return RecordType.NOUN

    @classmethod
    def from_csv_fields(cls, fields: list[str]) -> "YourNounRecord":
        # Parse CSV fields with language-specific validation

    def to_dict(self) -> dict[str, Any]:
        # Convert to dictionary for processing
```

### 4. Create Domain Models

In `models/noun.py`:

```python
from langlearn.protocols.media_generation_protocol import MediaGenerationCapable

@dataclass
class YourNoun(MediaGenerationCapable):
    # Core data matching record fields

    def get_combined_audio_text(self) -> str:
        # Language-specific pronunciation patterns

    def get_image_search_strategy(self, anthropic_service) -> Callable[[], str]:
        # Language-specific image search strategy

    def get_audio_segments(self) -> dict[str, str]:
        # All audio needed for card templates

    def get_primary_word(self) -> str:
        # Primary word for file naming
```

### 5. Create Anki Templates

Create language-specific templates in `templates/`:
- `noun_{LANG_CODE}_{lang_code}_front.html`
- `noun_{LANG_CODE}_{lang_code}_back.html`
- `noun_{LANG_CODE}_{lang_code}.css`

### 6. Language-Specific Features

#### Russian Case System Example
```python
# In RussianNounRecord
class RussianNounRecord(BaseRecord):
    gender: Literal["masculine", "feminine", "neuter"]
    animacy: Literal["animate", "inanimate"] = "inanimate"

    # Case declensions
    nominative: str  # Base form
    genitive: str    # Родительный падеж
    accusative: str = ""  # Auto-calculated based on animacy
    instrumental: str = ""
    prepositional: str = ""
    dative: str = ""
```

#### Language-Specific Audio Generation
```python
def get_combined_audio_text(self) -> str:
    # Russian: Clear pronunciation of base form
    return self.noun

def get_case_pattern_text(self) -> str:
    # Show key case forms for pronunciation learning
    cases = []
    if self.nominative:
        cases.append(f"именительный {self.nominative}")
    if self.genitive:
        cases.append(f"родительный {self.genitive}")
    return ", ".join(cases) if cases else self.noun
```

## Integration with AnkiBackend

The beauty of this architecture is that **no AnkiBackend modifications are required**. The Field Processing Delegation Pattern automatically handles new languages:

```python
# In AnkiBackend._process_fields_with_media()
processed_fields = self._language.process_fields_for_anki(
    note_type_name, fields, media_enricher
)
# ^ This call works for ANY language implementing the protocol
```

## Verification Testing

Create test files to verify your implementation:

```python
# test_your_language_integration.py
def test_language_with_anki_backend():
    language = YourLanguage()

    # Test record creation
    record = language.create_record_from_csv("noun", test_fields)

    # Test domain model creation
    domain_model = language.create_domain_model("noun", record)

    # Test AnkiBackend integration
    anki_backend = AnkiBackend(
        deck_name="Test Deck",
        language=language,  # <- No special handling needed!
        media_service=mock_media_service
    )

    # Verify field processing works
    processed_fields = language.process_fields_for_anki(
        "Your Noun", test_fields, mock_media_enricher
    )
```

## Language-Specific Considerations

### Typography & Fonts
- **Russian**: Use serif fonts (Times New Roman) for Cyrillic readability
- **Arabic**: Right-to-left text support in CSS
- **Chinese**: Appropriate font selection for character rendering
- **German**: Special character support (ü, ö, ä, ß)

### Grammatical Features
- **Russian**: 6-case system, gender, animacy
- **German**: 4-case system, gender, separable verbs
- **Spanish**: Ser/estar distinction, gendered adjectives
- **French**: Complex verb conjugations, liaison rules

### Media Generation
- **Image Search**: Use English translations for better international image matching
- **Audio Generation**: Language-specific pronunciation patterns and stress
- **Example Sentences**: Cultural context and natural language patterns

## Success Criteria

A successful language implementation should demonstrate:

✅ **Protocol Compliance**: All methods implement required interfaces
✅ **Type Safety**: Zero MyPy errors in strict mode
✅ **AnkiBackend Integration**: Works without backend modifications
✅ **Template Rendering**: Proper display in Anki cards
✅ **Media Generation**: Audio and image enrichment works
✅ **Test Coverage**: Unit and integration tests pass

## Future Extensions

The architecture supports easy addition of:
- **New Word Types**: verbs, adjectives, adverbs per language
- **Advanced Features**: Grammar exercises, pronunciation guides
- **Regional Variants**: American vs British English, etc.
- **Script Support**: Cyrillic, Arabic, Chinese characters
- **Audio Variants**: Multiple voices, dialects, pronunciation styles

## Conclusion

The multi-language architecture successfully scales to new languages with minimal effort. The Russian implementation proves that complex grammatical systems (6-case declensions, gender, animacy) integrate seamlessly with the existing infrastructure.

**Key Achievement**: Adding Russian noun support required **zero changes to AnkiBackend** - exactly as the architecture was designed.