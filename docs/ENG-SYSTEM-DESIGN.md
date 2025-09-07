# System Design - CSV to Anki Card Pipeline

**Document Type**: System Design Guide  
**Purpose**: Explain how CSV data becomes Anki cards through Clean Pipeline Architecture  
**Audience**: Engineers implementing new features or card types

---

## Executive Summary

The Anki German Language Deck Generator transforms CSV vocabulary data into production-ready Anki flashcard decks through a **Clean Pipeline Architecture** with clear separation of concerns. Each component has a single, well-defined responsibility in the data transformation pipeline.

---

## System Architecture Overview

### Data Flow Pipeline
```
CSV File → Domain Models → MediaEnricher → AnkiBackend → .apkg File
```

### Architecture Principles
- **Single Responsibility Principle (SRP)**: Each component has one clear purpose
- **Separation of Concerns**: Domain logic, services, and infrastructure are isolated
- **Dependency Inversion**: High-level modules depend on abstractions, not implementations
- **Open/Closed Principle**: System is extensible without modifying existing code

---

## Pipeline Components and Responsibilities

### 1. CSV Data Source
**Responsibility**: Provide structured vocabulary data in standard CSV format

**Location**: `/data/*.csv`

**Structure Example** (nouns.csv):
```csv
Substantiv,Artikel,Genus,Plural,Englisch,Beispiel,Kategorie,Notizen
Mann,der,Maskulinum,Männer,man,Der Mann arbeitet.,Familie & Beziehungen,
```

**Key Points**:
- UTF-8 encoding required
- Headers define field mappings
- One row = one vocabulary item
- See `docs/PROD-CSV-SPEC.md` for complete specifications

---

### 2. Domain Model Creation
**Responsibility**: Transform CSV rows into rich domain model instances

**Location**: `src/langlearn/models/` (noun.py, adjective.py, etc.)

**Process**:
```python
# Direct domain model instantiation from CSV
def create_noun_from_csv(csv_row: list[str]) -> Noun:
    """Create Noun domain model from CSV data."""
    return Noun(
        noun=csv_row[0],
        article=csv_row[1], 
        english=csv_row[4],
        plural=csv_row[3],
        example=csv_row[5]
        # Validation occurs in __post_init__
    )
```

**Key Points**:
- Direct instantiation of dataclass domain models
- Automatic validation in `__post_init__` methods
- MediaGenerationCapable protocol compliance
- Currently supports all 7 word types with uniform architecture

---

### 3. Domain Models
**Responsibility**: Rich German language models with MediaGenerationCapable protocol

**Location**: `src/langlearn/models/` (individual files per word type)

**Example Structure**:
```python
@dataclass
class Noun(MediaGenerationCapable):
    """Modern dataclass model for German nouns."""
    noun: str
    article: str
    english: str
    plural: str
    example: str
    related: str = field(default="")
    
    def __post_init__(self) -> None:
        """Validate noun data after initialization."""
        required_fields = ["noun", "article", "english", "example"]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Required field '{field_name}' cannot be empty")
    
    def get_combined_audio_text(self) -> str:
        """Get text for audio generation."""
        return f"{self.article} {self.noun}. {self.example}"
    
    def get_image_search_strategy(self) -> str:
        """Get search strategy for image generation."""
        return f"{self.english} concrete object"
```

**Key Points**:
- Modern Python dataclass architecture
- Inline validation in `__post_init__` methods
- MediaGenerationCapable protocol implementation
- German language expertise built into models
- Zero external dependencies (no Pydantic)

---

### 4. MediaEnricher Service
**Responsibility**: Generate and attach media files using MediaGenerationCapable protocol

**Location**: `src/langlearn/services/media_enricher.py`

**Process**:
```python
def enrich_model(model: MediaGenerationCapable) -> dict[str, str]:
    """Generate media for any MediaGenerationCapable model."""
    enriched_data = {}
    
    # Use protocol methods for intelligent generation
    audio_text = model.get_combined_audio_text()
    image_strategy = model.get_image_search_strategy()
    
    # Generate audio if needed
    if not self._audio_exists(audio_text):
        audio_path = self._generate_audio(audio_text)
        enriched_data["word_audio"] = audio_path
    
    # Generate image if needed
    if not self._image_exists(image_strategy):
        image_path = self._generate_image(image_strategy)
        enriched_data["image"] = image_path
    
    return enriched_data
```

**Key Points**:
- Checks for existing media before generating (existence checking)
- Integrates with AWS Polly for audio
- Uses Pexels API for images
- Returns paths to generated media files
- Hash-based caching to prevent duplicates

---

### 5. AnkiBackend Direct Processing
**Responsibility**: Create Anki cards directly from domain models

**Location**: `src/langlearn/backends/anki_backend.py`

**Process**:
```python
def process_noun(self, noun_data: list[str]) -> tuple[list[str], NoteType]:
    """Process noun using domain model."""
    
    # Create domain model (validation in __post_init__)
    noun = Noun(
        noun=noun_data[0],
        article=noun_data[1],
        english=noun_data[4],
        plural=noun_data[3],
        example=noun_data[5]
    )
    
    # Generate media using protocol methods
    enriched_data = self._media_enricher.enrich_model(noun)
    
    # Format card fields directly from model
    field_values = [
        f"{noun.article} {noun.noun}",
        noun.english,
        noun.example,
        enriched_data.get("word_audio", ""),
        enriched_data.get("image", "")
        # ... additional fields
    ]
    
    return field_values, self._get_noun_note_type()
```

**Key Points**:
- Direct domain model processing (no intermediate DTOs)
- MediaGenerationCapable protocol for intelligent media generation
- Built-in German language expertise in models
- Validation occurs at model creation time

---

### 6. AnkiBackend Service
**Responsibility**: Create actual Anki deck files (.apkg) from card data

**Location**: `src/langlearn/backends/anki_backend.py`

**Process**:
```python
def process_vocabulary_item(fields: list[str], note_type_name: str):
    """Process single vocabulary item through pipeline."""
    
    # Try Clean Pipeline first
    try:
        # Create record from CSV
        record = self._record_mapper.create_record(note_type_name, fields)
        
        # Enrich with media
        enriched_data = self._media_enricher.enrich_record(record)
        
        # Build card
        field_values, note_type = self._card_builder.build_card_from_record(
            record, enriched_data
        )
        
        # Add to deck
        self._add_note_to_deck(field_values, note_type)
        
    except UnsupportedRecordType:
        # Fallback to legacy processing
        self._process_with_legacy_system(fields, note_type_name)
```

**Key Points**:
- Orchestrates the complete pipeline
- Creates Anki Collection and Deck objects
- Handles media file registration
- Exports final .apkg file
- Provides fallback for unsupported types

---

## Adding a New Card Type

### Step-by-Step Process

#### 1. Create CSV File
Create a new CSV file in `/data/` with appropriate headers:

```csv
Word,English,Property1,Property2,Example
example1,translation1,value1,value2,Example sentence.
```

#### 2. Define Record Type
Add new record class to `src/langlearn/models/records.py`:

```python
class NewTypeRecord(BaseRecord):
    """Record for new word type."""
    word: str = Field(..., description="Word in German")
    english: str = Field(..., description="English translation")
    property1: str = Field(..., description="Property 1")
    property2: str = Field(..., description="Property 2")
    example: str = Field(..., description="Example sentence")
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "word": self.word,
            "english": self.english,
            "property1": self.property1,
            "property2": self.property2,
            "example": self.example
        }
```

#### 3. Update RecordMapper
Add mapping in `src/langlearn/services/record_mapper.py`:

```python
def _create_newtype_record(self, row: list[str]) -> NewTypeRecord:
    """Create NewType record from CSV row."""
    return NewTypeRecord(
        word=row[0],
        english=row[1],
        property1=row[2],
        property2=row[3],
        example=row[4]
    )
```

#### 4. Update CardBuilder
Add field mapping in `src/langlearn/services/card_builder.py`:

```python
def _get_field_names_for_record_type(self, record_type: str) -> list[str]:
    field_mappings = {
        # ... existing mappings
        "newtype": [
            "Word", "English", "Property1", "Property2", 
            "Example", "Image", "WordAudio", "ExampleAudio"
        ],
    }
```

#### 5. Create Anki Template
Add HTML templates in `src/langlearn/templates/`:
- `newtype_front.html` - Front card template
- `newtype_back.html` - Back card template  
- `newtype_style.css` - Card styling

#### 6. Write Tests
Create comprehensive tests:

```python
def test_newtype_record_processing():
    """Test new type through complete pipeline."""
    record = create_record("newtype", ["word", "translation", ...])
    assert record.word == "word"
    
    # Test enrichment
    enriched = media_enricher.enrich_record(record)
    assert "word_audio" in enriched
    
    # Test card building
    fields, note_type = card_builder.build_card_from_record(record, enriched)
    assert len(fields) == 8  # Verify field count
```

---

## Single Responsibility in Practice

### Clear Component Boundaries

Each component has exactly one reason to change:

| Component | Single Responsibility | Change Trigger |
|-----------|----------------------|----------------|
| **CSV Files** | Define vocabulary data | New vocabulary items |
| **RecordMapper** | CSV → Record conversion | CSV format changes |
| **Records** | Data validation & transport | Field requirements change |
| **MediaEnricher** | Media generation | New media sources/types |
| **CardBuilder** | Record → Card formatting | Card template changes |
| **AnkiBackend** | Deck file generation | Anki format changes |

### Benefits of SRP Implementation

1. **Testability**: Each component can be tested in isolation
2. **Maintainability**: Changes are localized to specific components
3. **Extensibility**: New word types added without modifying existing code
4. **Debugging**: Clear boundaries make issues easy to locate
5. **Reusability**: Components can be reused in different contexts

---

## System Configuration

### Media Generation Settings

```python
# Audio configuration (AWS Polly)
AUDIO_SETTINGS = {
    "voice": "Daniel",  # German male voice
    "language": "de-DE",
    "format": "mp3",
    "cache_dir": "data/audio/"
}

# Image configuration (Pexels)
IMAGE_SETTINGS = {
    "quality": "medium",
    "orientation": "landscape",
    "cache_dir": "data/images/"
}
```

### Pipeline Configuration

```python
# Clean Pipeline supported types
CLEAN_PIPELINE_TYPES = [
    "noun", "adjective", "adverb", "negation", "verb"
]

# Legacy fallback types
LEGACY_TYPES = ["preposition", "phrase"]
```

---

## Performance Optimizations

### Caching Strategy
- **Existence Checking**: Check for existing files before generation
- **Hash-based Keys**: Use content hash for cache lookup
- **Batch Processing**: Process multiple items in parallel where possible

### Resource Management
- **Lazy Loading**: Services instantiated only when needed
- **Connection Pooling**: Reuse API connections
- **Memory Efficiency**: Use lightweight DTOs for data transport

---

## Error Handling

### Pipeline Error Recovery

```python
try:
    # Attempt Clean Pipeline processing
    record = record_mapper.create_record(type, data)
    enriched = media_enricher.enrich_record(record)
    card = card_builder.build_card_from_record(record, enriched)
except RecordValidationError:
    # Handle validation errors
    logger.error(f"Invalid data for {type}: {data}")
except MediaGenerationError:
    # Continue without media
    logger.warning(f"Media generation failed, continuing without")
except Exception as e:
    # Fallback to legacy system
    logger.info(f"Using legacy processing: {e}")
    process_with_legacy(data)
```

---

## Quality Assurance

### Required Quality Gates
1. **Type Safety**: All components must pass MyPy strict mode
2. **Test Coverage**: New components require 95%+ coverage
3. **Integration Tests**: End-to-end pipeline validation required
4. **Performance Tests**: Media generation must complete in <2s per item

### Development Workflow
```bash
# Before committing any changes
hatch run type          # Type checking
hatch run test-unit     # Unit tests
hatch run test          # All tests
hatch run test-cov      # Coverage report
```

---

## Future Enhancements

### Planned Improvements
1. **Parallel Processing**: Process multiple CSV rows concurrently
2. **Streaming Pipeline**: Process large CSV files without loading into memory
3. **Plugin Architecture**: Dynamic loading of new word type processors
4. **Multi-language Support**: Extend pipeline for languages beyond German

### Extension Points
- Custom media generators (video, pronunciation guides)
- Alternative card formats (cloze deletion, typing)
- Advanced scheduling algorithms
- Spaced repetition optimization

---

*This design ensures clean separation of concerns with each component having a single, well-defined responsibility in the CSV → Anki card transformation pipeline.*