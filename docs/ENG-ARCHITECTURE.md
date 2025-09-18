# System Architecture - Infrastructure/Platform/Languages

**Purpose**: Document the Infrastructure/Platform/Languages architectural pattern and how it enables extensible language learning deck generation
**Audience**: Engineers working on the system, adding new languages, or understanding the architectural design
**Status**: Updated 2024-09-18 to reflect Infrastructure/Platform/Languages migration

---

## Architectural Overview

The langlearn system follows a three-tier **Infrastructure/Platform/Languages** architecture that provides clear separation of concerns and extensibility:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          LANGUAGES LAYER                           │
│                        "You implement this"                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │     German      │  │     Korean      │  │     Russian     │    │
│  │   Implementation │  │   Implementation │  │   Implementation │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          PLATFORM LAYER                            │
│                         "You extend this"                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  DeckBuilder    │  │    Records      │  │   Protocols     │    │
│  │  Orchestration  │  │   Extension     │  │   Extension     │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       INFRASTRUCTURE LAYER                         │
│                          "You use this"                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   AnkiBackend   │  │  AudioService   │  │  PexelsService  │    │
│  │  Implementation │  │  Implementation │  │  Implementation │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Open-Closed Principle**: Open for extension (new languages), closed for modification (core infrastructure)
2. **Single Responsibility**: Each layer has distinct concerns and responsibilities
3. **Dependency Inversion**: Higher layers depend on abstractions, not concrete implementations
4. **Language Agnostic Core**: Infrastructure and platform layers work with any language

---

## Package Structure

```
src/langlearn/
├── infrastructure/              # "You use this" - Concrete implementations
│   ├── backends/               # AnkiBackend, deck file generation
│   └── services/               # AudioService, PexelsService, AI services
├── core/                       # "You extend this" - Platform extension points
│   ├── deck/                   # DeckBuilderAPI, orchestration pipeline
│   ├── records/                # BaseRecord system, data validation
│   ├── pipeline/               # Processing pipeline framework
│   └── protocols/              # Extension protocols and contracts
└── languages/                  # "You implement this" - Language-specific
    ├── german/                 # German language implementation
    ├── korean/                 # Korean language implementation
    └── russian/                # Russian language implementation
```

---

## Layer Responsibilities

### 🏗️ Infrastructure Layer (`langlearn.infrastructure.*`)

**Purpose**: Provides concrete implementations of core functionality that all languages use

**Characteristics**:
- Closed for modification, stable implementations
- No language-specific knowledge
- Service implementations with clear interfaces

#### Key Components:

**Backends** (`infrastructure/backends/`):
- `AnkiBackend`: Creates `.apkg` files from card data
- `DeckBackend`: Abstract interface for deck creation systems

**Services** (`infrastructure/services/`):
- `AudioService`: AWS Polly integration for text-to-speech
- `PexelsService`: Image search and download
- `MediaEnricher`: Orchestrates media generation
- `CSVService`: Generic CSV reading with validation
- `TemplateService`: Anki card template management

### 🎯 Platform Layer (`langlearn.core.*`)

**Purpose**: Provides extension points and orchestration for language implementations

**Characteristics**:
- Open for extension by language implementations
- Language-agnostic orchestration logic
- Protocol-based extension system

#### Key Components:

**Deck Management** (`core/deck/`):
- `DeckBuilderAPI`: Observable 5-phase deck generation pipeline
- `BuiltCards`: Type-safe card data structures
- `DeckPhases`: Phase management and transitions

**Records System** (`core/records/`):
- `BaseRecord`: Foundation for data validation
- Record factories and type system

**Protocols** (`core/protocols/`):
- `MediaGenerationCapable`: Contract for domain models
- `CardProcessorProtocol`: Language-specific card processing
- Extension contracts for new languages

**Pipeline** (`core/pipeline/`):
- Generic processing pipeline framework
- Task orchestration and state management

### 🌍 Languages Layer (`langlearn.languages.*`)

**Purpose**: Language-specific implementations using platform extension points

**Characteristics**:
- Implements protocols from platform layer
- Contains all language-specific business logic
- Extends platform capabilities with linguistic knowledge

#### Current Language Support:

**German** (`languages/german/`):
- Complete A1 vocabulary support (7 word types)
- German grammar rules and article handling
- Noun declension and verb conjugation logic

**Korean** (`languages/korean/`):
- Korean language models and processing
- Hangul character handling
- Korean-specific grammar rules

**Russian** (`languages/russian/`):
- Cyrillic alphabet support
- Russian grammar and case system
- Native audio and image filename handling

---

## Data Flow Pipeline

The system transforms vocabulary data through a clean pipeline:

```
CSV Data → Records (Platform) → Models (Language) → MediaEnricher (Infrastructure) →
CardBuilder (Language) → AnkiBackend (Infrastructure) → .apkg Files
```

### Pipeline Phases

1. **Data Loading**: CSV files → Platform Records (validation)
2. **Model Creation**: Records → Language Domain Models (business logic)
3. **Media Enrichment**: Models → Infrastructure Services (audio/images)
4. **Card Building**: Enriched Models → Language CardBuilders (formatting)
5. **Deck Export**: Cards → Infrastructure Backend (Anki files)

### Extension Points

**Adding New Languages**:
1. Implement `MediaGenerationCapable` protocol in domain models
2. Create language-specific record classes extending `BaseRecord`
3. Implement `CardProcessorProtocol` for card formatting
4. Register language with platform discovery system

**Adding New Services**:
1. Create service in infrastructure layer
2. Define clear interface/protocol
3. Integrate with MediaEnricher orchestration

---

## Quality Assurance

### Testing Strategy

**Unit Tests**: 672 tests with full coverage of:
- Infrastructure services (mocked external dependencies)
- Platform orchestration logic
- Language-specific business rules

**Integration Tests**: 19 tests covering:
- End-to-end pipeline from CSV to .apkg
- Live API integrations (AWS Polly, Pexels)
- Multi-language deck generation

### Quality Metrics

- **Type Safety**: MyPy strict mode, zero type errors across 163 source files
- **Code Quality**: Ruff linting with zero violations
- **Test Coverage**: 691 passing tests (672 unit + 19 integration)
- **Architecture Compliance**: Clear layer boundaries, no circular dependencies

---

## Migration History

### Infrastructure/Platform/Languages Migration (2024-09-18)

**Completed Migration**:
- Moved services: `langlearn.core.services.*` → `langlearn.infrastructure.services.*`
- Moved backends: `langlearn.core.backends.*` → `langlearn.infrastructure.backends.*`
- Resolved platform module naming conflict
- Updated 65+ import statements across codebase
- Maintained 100% backward compatibility

**Benefits Achieved**:
- Clear separation of concerns
- Improved extensibility for new languages
- Eliminated architectural technical debt
- Enhanced development experience

**Previous Architecture** (Legacy):
```
src/langlearn/
├── core/                       # Mixed concerns - confusing
│   ├── services/              # Infrastructure mixed with platform
│   └── backends/              # Infrastructure mixed with platform
├── models/                     # Legacy Pydantic models
└── languages/                  # Language implementations
```

---

## Development Patterns

### Open-Closed Principle in Practice

**Infrastructure Layer**: Closed for modification
```python
# You USE this - don't modify
from langlearn.infrastructure.services import AudioService
audio_service = AudioService(voice_id="Tatyana")
```

**Platform Layer**: Open for extension
```python
# You EXTEND this - implement protocols
from langlearn.core.protocols import MediaGenerationCapable

@dataclass
class MyLanguageWord(MediaGenerationCapable):
    def get_combined_audio_text(self) -> str:
        # Language-specific implementation
```

**Languages Layer**: Your implementations
```python
# You IMPLEMENT this - complete freedom within protocols
class GermanNoun(MediaGenerationCapable):
    def get_image_search_strategy(self, ai_service=None) -> str:
        return f"{self.english} German {self.get_concreteness()}"
```

### Adding New Languages

1. **Create Language Package**: `languages/mylanguage/`
2. **Implement Domain Models**: Extend platform protocols
3. **Create Record Classes**: Extend platform BaseRecord
4. **Build Card Processors**: Implement CardProcessorProtocol
5. **Register with Platform**: Use language discovery system

---

## Configuration and Environment

### Required Services
- **AWS Polly**: Text-to-speech generation (requires AWS credentials)
- **Pexels API**: Image search and download (requires API key)
- **Anthropic API**: AI-enhanced content generation (optional)

### Directory Structure
```
languages/{language}/{deck}/
├── *.csv                      # Vocabulary data files
├── audio/                     # Generated pronunciation files
└── images/                    # Generated vocabulary images
```

### Quality Gates
```bash
hatch run type                # MyPy type checking
hatch run ruff check          # Code linting
hatch run format              # Code formatting
hatch run test                # Full test suite
```

---

## Future Extensions

### Planned Enhancements
1. **Performance Optimization**: Async/await for I/O operations
2. **Caching Layer**: Redis integration for media file caching
3. **Analytics Platform**: Usage tracking and learning metrics
4. **Content Management**: Interactive vocabulary selection tools

### Language Roadmap
- **Spanish**: Using Germanic language patterns from German implementation
- **French**: Romance language with liaison handling
- **Italian**: Romance language with regional variations
- **Mandarin**: Character-based language with tone integration

The Infrastructure/Platform/Languages architecture provides the foundation for all these extensions while maintaining system stability and quality.