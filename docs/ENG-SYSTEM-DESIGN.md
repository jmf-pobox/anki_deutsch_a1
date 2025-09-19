# System Design - CSV to Anki Card Pipeline

**Purpose**: Explain how CSV vocabulary data becomes Anki flashcard decks
**Audience**: Engineers implementing features or troubleshooting issues

---

## Data Flow Overview

The system transforms CSV vocabulary files into Anki deck files through these steps:

```
CSV Files → Records (validation) → Domain Models (business logic) → MediaEnricher → CardBuilder → AnkiBackend → .apkg Files
```

Each component handles one specific responsibility in the data transformation process.

---

## Component Responsibilities

### 1. CSV Data Source
**Purpose**: Provide structured vocabulary data

**Location**: `languages/{language}/{deck}/*.csv`

**Structure Example** (nouns.csv):
```csv
noun,article,english,plural,example
Mann,der,man,Männer,Der Mann arbeitet.
```

**Requirements**:
- UTF-8 encoding for German special characters (ä, ö, ü, ß)
- Header row defines field mappings
- One row per vocabulary item
- See `docs/PM-CSV-SPEC.md` for complete field specifications

### 2. Records (Dataclass Models)
**Purpose**: Validate CSV data and provide type safety

**Location**: `src/langlearn/languages/german/records/`

**Process**:
```python
# CSV row → validated Record
record = create_record("noun", ["Mann", "der", "man", "Männer", "Der Mann arbeitet."])
# Returns NounRecord with validated fields
```

**Key Functions**:
- Data validation using dataclass models
- Type conversion and field validation
- Transport layer between CSV and domain models

### 3. Domain Models (Business Logic)
**Purpose**: German language-specific business logic and media generation

**Location**: `src/langlearn/models/`

**Process**:
```python
# Record → Domain Model with German logic
noun = Noun.from_record(noun_record)
audio_text = noun.get_combined_audio_text()  # "der Mann. Der Mann arbeitet."
image_query = noun.get_image_search_strategy()  # "German man person"
```

**Key Functions**:
- MediaGenerationCapable protocol implementation
- German grammar rules and logic
- Audio text and image search strategy generation

### 4. MediaEnricher Service
**Purpose**: Generate audio and image files for vocabulary items

**Location**: `src/langlearn/services/media_enricher.py`

**Process**:
```python
# Domain Model → Enriched data with media files
enriched_data = media_enricher.enrich_model(noun)
# Returns: {"word_audio": "path/to/audio.mp3", "image": "path/to/image.jpg"}
```

**Key Functions**:
- Checks for existing media files before generation
- AWS Polly for German audio pronunciation
- Pexels API for relevant images
- Hash-based caching to avoid duplicates

### 5. CardBuilder Service
**Purpose**: Transform data into Anki card format

**Location**: `src/langlearn/services/card_builder.py`

**Process**:
```python
# Domain Model + Media → Anki card fields
field_values, note_type = card_builder.build_card_from_model(noun, enriched_data)
# Returns formatted field values and note type definition
```

**Key Functions**:
- Field mapping (CSV lowercase_underscore → Anki PascalCase)
- Template selection based on card type
- Media path integration

### 6. AnkiBackend
**Purpose**: Create .apkg file from formatted cards

**Location**: `src/langlearn/backends/anki_backend.py`

**Process**:
```python
# Card data → .apkg file
backend.add_card(field_values, note_type)
backend.save_deck("output.apkg")
```

**Key Functions**:
- Anki note type creation
- Media file packaging
- .apkg file generation

---

## Directory Structure

```
languages/german/
├── default/                    # Complete A1 content (15 CSV files)
│   ├── nouns.csv
│   ├── verbs.csv
│   ├── adjectives.csv
│   ├── audio/                  # Generated pronunciation files
│   └── images/                 # Generated vocabulary images
├── a1.1/                       # A1.1 level content (11 CSV files)
├── a1/                         # A1 level content (10 CSV files)
└── business/                   # Business vocabulary (1 CSV file)
```

**Media Organization**:
- Audio files: `{deck}/audio/{hash}.mp3`
- Image files: `{deck}/images/{word}.jpg`
- Automatic directory creation per deck

---

## Adding New Card Types

### Step 1: Create Record Model
```python
# File: src/langlearn/languages/german/records/new_type.py
class NewTypeRecord(BaseRecord):
    field1: str
    field2: str

    @field_validator('field1')
    def validate_field1(cls, v):
        # Add validation logic
        return v
```

### Step 2: Create Domain Model
```python
# File: src/langlearn/models/new_type.py
@dataclass
class NewType(MediaGenerationCapable):
    field1: str
    field2: str

    def get_combined_audio_text(self) -> str:
        return f"{self.field1}. {self.field2}"

    def get_image_search_strategy(self) -> str:
        return f"{self.field1} German vocabulary"
```

### Step 3: Add Processing Logic
```python
# File: src/langlearn/backends/anki_backend.py
def process_new_type(self, data: list[str]) -> tuple[list[str], NoteType]:
    record = create_record("new_type", data)
    model = NewType.from_record(record)
    enriched_data = self._media_enricher.enrich_model(model)
    return self._card_builder.build_card_from_model(model, enriched_data)
```

### Step 4: Create Templates
Create template files in `src/langlearn/languages/german/templates/`:
- `new_type_DE_de_front.html`
- `new_type_DE_de_back.html`
- `new_type_DE_de.css`

---

## Current Word Type Support

| Word Type | CSV File | Record Class | Domain Model | Status |
|-----------|----------|--------------|--------------|---------|
| Noun | nouns.csv | NounRecord | Noun | Active |
| Adjective | adjectives.csv | AdjectiveRecord | Adjective | Active |
| Verb | verbs.csv | VerbRecord | Verb | Active |
| Adverb | adverbs.csv | AdverbRecord | Adverb | Active |
| Negation | negations.csv | NegationRecord | Negation | Active |
| Preposition | prepositions.csv | PrepositionRecord | Preposition | Active |
| Phrase | phrases.csv | PhraseRecord | Phrase | Active |

**Total**: 7 word types with complete media generation support

---

## Media Generation Details

### Audio Generation
- **Service**: AWS Polly
- **Voice**: German neural voice
- **Format**: MP3
- **Naming**: MD5 hash of text content
- **Storage**: `languages/{language}/{deck}/audio/{hash}.mp3`

### Image Generation
- **Service**: Pexels API
- **Search**: English translations + context keywords
- **Format**: JPEG
- **Naming**: Based on vocabulary word
- **Storage**: `languages/{language}/{deck}/images/{word}.jpg`

### Caching Strategy
- Audio: Hash-based filename prevents duplicate generation
- Images: Existence check before API call
- MediaEnricher checks file system before generating new media

---

## Configuration Files

### CSV Specifications
- `docs/PM-CSV-SPEC.md` - Field definitions and validation rules
- `docs/ENG-DATA-DICTIONARY.md` - Authoritative field reference

### Card Specifications
- `docs/PM-CARD-SPEC.md` - Anki card type definitions and templates

### Development Standards
- `docs/ENG-DEVELOPMENT-GUIDE.md` - Development workflow and quality gates
- `docs/ENG-COMPONENT-INVENTORY.md` - Component responsibilities

---

## Error Handling

### Fail-Fast Principle
The system follows fail-fast error handling - operations stop immediately when validation fails or required services are unavailable.

### Validation Errors
- **Records**: Dataclass validation raises exceptions for malformed CSV data
- **Domain Models**: `__post_init__` validation raises exceptions for invalid business rules
- **Media Services**: Raise exceptions when API services are unavailable or return errors

### Media Generation Failures
- **Audio**: Process stops with exception if AWS Polly fails
- **Images**: Process stops with exception if Pexels fails
- **API Keys**: Process stops with clear error message if credentials missing

### Exception Types
- `ValueError`: Dataclass validation failures
- `ValueError`: Domain model validation failures
- `RuntimeError`: Service unavailability or API failures
- `KeyError`: Missing required configuration or API keys

**See [ENG-EXCEPTIONS.md](./ENG-EXCEPTIONS.md) for complete exception handling standards and custom exception hierarchy.**

### Debugging
- Enable detailed logging: `export LOG_LEVEL=DEBUG`
- Check media generation: Process stops if files cannot be created
- Validate CSV: Fix validation errors before continuing - process will not proceed with invalid data

---

## Performance Considerations

### File System Optimization
- Media files generated once and reused across builds
- Hash-based audio filenames prevent duplicate storage
- Directory structure optimizes file access patterns

### Memory Management
- Records processed individually, not loaded in bulk
- MediaEnricher processes one item at a time
- Temporary objects garbage collected after each card

### API Rate Limits
- AWS Polly: Uses boto3 default retry behavior (legacy mode: 5 total attempts with exponential backoff)
- Pexels: Custom retry logic with exponential backoff, jitter, and rate limiting
- Caching prevents unnecessary API calls

**Note**: Inconsistent retry handling between services. AWS Polly uses boto3's basic retries while Pexels has more sophisticated retry logic with jitter and rate limiting.

---

## Testing Strategy

### Unit Tests
- **Records**: Validation logic and field conversion
- **Domain Models**: Business logic and protocol compliance
- **Services**: Individual component functionality
- **Coverage**: >80% overall, >95% for new components

### Integration Tests
- **End-to-end**: CSV → .apkg file generation
- **Media Services**: Live API calls with valid credentials
- **File System**: Directory creation and media file generation

### Mocking Strategy
- **Unit Tests**: Mock external dependencies (AWS, Pexels)
- **Integration Tests**: Use real services with test credentials
- **File System**: Use temporary directories in tests