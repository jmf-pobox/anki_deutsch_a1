# Architectural Diagrams - Infrastructure/Platform/Languages

**Purpose**: Visual representation of the Infrastructure/Platform/Languages architecture
**Audience**: Engineers, architects, and stakeholders understanding system design
**Updated**: 2024-09-18 to reflect Infrastructure/Platform/Languages migration

---

## System Overview

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   LANGUAGES LAYER                                      │
│                                  "You implement this"                                  │
│                                                                                         │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐                │
│  │     German      │      │     Korean      │      │     Russian     │                │
│  │                 │      │                 │      │                 │                │
│  │ • Domain Models │      │ • Domain Models │      │ • Domain Models │                │
│  │ • Record Types  │      │ • Record Types  │      │ • Record Types  │                │
│  │ • Card Services │      │ • Card Services │      │ • Card Services │                │
│  │ • Grammar Logic │      │ • Grammar Logic │      │ • Grammar Logic │                │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PLATFORM LAYER                                       │
│                                   "You extend this"                                    │
│                                                                                         │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐                │
│  │  DeckBuilderAPI │      │    Protocols    │      │     Records     │                │
│  │                 │      │                 │      │                 │                │
│  │ • 5-Phase Pipeline │     │ • MediaGenCapable│      │ • BaseRecord    │                │
│  │ • Progress Tracking│     │ • CardProcessor │      │ • Validation    │                │
│  │ • Error Handling  │     │ • TTSConfig     │      │ • Type Safety   │                │
│  │ • Orchestration   │     │ • Extension API │      │ • CSV Mapping   │                │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                INFRASTRUCTURE LAYER                                    │
│                                   "You use this"                                      │
│                                                                                         │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐                │
│  │   AnkiBackend   │      │    Services     │      │   Managers      │                │
│  │                 │      │                 │      │                 │                │
│  │ • .apkg Creation │      │ • AudioService  │      │ • DeckManager   │                │
│  │ • Note Types     │      │ • PexelsService │      │ • MediaManager  │                │
│  │ • Media Packaging│      │ • MediaEnricher │      │ • Orchestration │                │
│  │ • Export Logic   │      │ • CSVService    │      │ • Coordination  │                │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Package Structure Diagram

### Directory Layout with Layer Assignment

```
src/langlearn/
│
├── infrastructure/                    # 🏗️ INFRASTRUCTURE LAYER
│   ├── backends/                      #    "You use this"
│   │   ├── __init__.py               #    Stable implementations
│   │   ├── base.py                   #    Language-agnostic
│   │   └── anki_backend.py           #    Concrete services
│   └── services/
│       ├── __init__.py
│       ├── audio_service.py          # AWS Polly integration
│       ├── image_service.py          # Pexels API integration
│       ├── media_enricher.py         # Media orchestration
│       ├── csv_service.py            # Generic CSV handling
│       ├── template_service.py       # Anki templates
│       ├── naming_service.py         # File naming conventions
│       ├── media_file_registrar.py   # Media tracking
│       ├── service_container.py      # Dependency injection
│       └── domain_media_generator.py # Protocol bridge
│
├── core/                             # 🎯 PLATFORM LAYER
│   ├── deck/                         #    "You extend this"
│   │   ├── __init__.py              #    Extension points
│   │   ├── builder.py               #    Orchestration
│   │   ├── phases.py                #    State management
│   │   ├── progress.py              #    Progress tracking
│   │   └── data_types.py            #    Type definitions
│   ├── records/
│   │   ├── __init__.py
│   │   └── base_record.py           # Foundation for all records
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── media_generation_protocol.py      # MediaGenerationCapable
│   │   ├── card_processor_protocol.py        # CardProcessorProtocol
│   │   ├── tts_protocol.py                   # TTSConfig
│   │   └── image_search_protocol.py          # ImageSearchCapable
│   └── pipeline/
│       ├── __init__.py
│       └── pipeline.py              # Generic processing framework
│
└── languages/                        # 🌍 LANGUAGES LAYER
    ├── german/                       #    "You implement this"
    │   ├── models/                   #    Complete implementation freedom
    │   │   ├── noun.py              #    Language-specific logic
    │   │   ├── adjective.py         #    Grammar rules
    │   │   ├── verb.py              #    Domain expertise
    │   │   └── ...
    │   ├── records/
    │   │   ├── factory.py           # German record creation
    │   │   ├── noun_record.py       # German noun validation
    │   │   └── ...
    │   ├── services/
    │   │   ├── card_builder.py      # German card formatting
    │   │   ├── card_processor.py    # German processing logic
    │   │   └── ...
    │   └── language.py              # German language config
    ├── korean/
    │   ├── models/
    │   ├── services/
    │   └── language.py              # Korean language config
    └── russian/
        ├── models/
        ├── services/
        └── language.py              # Russian language config
```

---

## Data Flow Architecture

### End-to-End Processing Pipeline

```
┌─────────────────┐
│   CSV Files     │
│  (Data Source)  │
└─────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                PLATFORM ORCHESTRATION                                  │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                        DeckBuilderAPI (5 Phases)                               │    │
│  │                                                                                 │    │
│  │  Phase 1: DATA_LOADED     │  Phase 2: MODELS_BUILT  │  Phase 3: MEDIA_ENRICHED │    │
│  │  ┌─────────────────┐     │  ┌─────────────────┐    │  ┌─────────────────┐     │    │
│  │  │   CSV Service   │────▶│  │ Language Models │───▶│  │ Media Enricher  │     │    │
│  │  │ (Infrastructure)│     │  │   (Languages)   │    │  │(Infrastructure) │     │    │
│  │  └─────────────────┘     │  └─────────────────┘    │  └─────────────────┘     │    │
│  │                          │                         │           │              │    │
│  │  Phase 4: CARDS_BUILT    │  Phase 5: EXPORTED     │           ▼              │    │
│  │  ┌─────────────────┐     │  ┌─────────────────┐    │  ┌─────────────────┐     │    │
│  │  │ Card Processor  │────▶│  │  Anki Backend   │    │  │  AWS Polly +    │     │    │
│  │  │  (Languages)    │     │  │(Infrastructure) │    │  │  Pexels APIs    │     │    │
│  │  └─────────────────┘     │  └─────────────────┘    │  └─────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────┐
│  .apkg Files    │
│   (Output)      │
└─────────────────┘
```

### Layer Interaction Details

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Languages    │    │    Platform     │    │ Infrastructure  │
│                 │    │                 │    │                 │
│ German Models   │───▶│ DeckBuilderAPI  │───▶│ AnkiBackend     │
│ Korean Models   │    │                 │    │                 │
│ Russian Models  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────▶│   Protocols     │◀─────────────┘
                        │                 │
                        │• MediaGenCapable│
                        │• CardProcessor  │
                        │• TTSConfig      │
                        └─────────────────┘
```

---

## Extension Architecture

### Adding New Languages

```
                    PLATFORM CONTRACTS
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Protocol Compliance                             │
│                                                                 │
│  MediaGenerationCapable     CardProcessorProtocol     TTSConfig│
│  ┌─────────────────┐        ┌─────────────────┐       ┌───────┐│
│  │get_audio_text() │        │process_noun()   │       │voice  ││
│  │get_image_query()│        │process_verb()   │       │lang   ││
│  │is_concrete()    │        │get_note_type()  │       │engine ││
│  └─────────────────┘        └─────────────────┘       └───────┘│
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Language Implementation                        │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Domain Models  │  │  Record Types   │  │  Card Services  │ │
│  │                 │  │                 │  │                 │ │
│  │ SpanishNoun     │  │ SpanishRecord   │  │ SpanishCards    │ │
│  │ FrenchVerb      │  │ FrenchRecord    │  │ FrenchCards     │ │
│  │ ItalianAdj      │  │ ItalianRecord   │  │ ItalianCards    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Language Extension Points

```
NEW LANGUAGE IMPLEMENTATION

Step 1: Models (Domain Logic)
┌─────────────────────────────────────┐
│ from langlearn.core.protocols import│
│     MediaGenerationCapable          │
│                                     │
│ @dataclass                          │
│ class NewLanguageWord(              │
│     MediaGenerationCapable):        │
│                                     │
│     def get_combined_audio_text():  │
│         # Language-specific logic   │
│                                     │
│     def get_image_search_strategy():│
│         # Language-specific logic   │
└─────────────────────────────────────┘

Step 2: Records (Data Validation)
┌─────────────────────────────────────┐
│ from langlearn.core.records import  │
│     BaseRecord                      │
│                                     │
│ class NewLanguageRecord(BaseRecord):│
│     field1: str                     │
│     field2: str                     │
│                                     │
│     @field_validator('field1')      │
│     def validate_field(cls, v):     │
│         # Language-specific rules   │
└─────────────────────────────────────┘

Step 3: Services (Processing Logic)
┌─────────────────────────────────────┐
│ from langlearn.core.protocols import│
│     CardProcessorProtocol           │
│                                     │
│ class NewLanguageProcessor(         │
│     CardProcessorProtocol):         │
│                                     │
│     def process_word_type(self, ...):│
│         # Language-specific cards   │
└─────────────────────────────────────┘
```

---

## Quality Architecture

### Testing Strategy Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  TEST COVERAGE                                         │
│                                                                                         │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐                │
│  │  Unit Tests     │      │ Integration     │      │  Architecture   │                │
│  │    672 tests    │      │    19 tests     │      │     Tests       │                │
│  │                 │      │                 │      │                 │                │
│  │ • All Layers    │      │ • End-to-End    │      │ • Layer Deps    │                │
│  │ • Mocked Deps   │      │ • Live APIs     │      │ • Protocol      │                │
│  │ • Fast Feedback │      │ • Real Files    │      │ • Compliance    │                │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               QUALITY GATES                                            │
│                                                                                         │
│  MyPy --strict    │   Ruff Linting   │   Test Coverage   │   Architecture             │
│  ┌─────────────┐  │  ┌─────────────┐  │  ┌─────────────┐  │  ┌─────────────┐           │
│  │Zero Errors  │  │  │Zero Issues  │  │  │>85% Overall │  │  │Layer        │           │
│  │163 Files    │  │  │All Files    │  │  │691 Tests    │  │  │Boundaries   │           │
│  │Type Safe    │  │  │Clean Code   │  │  │Maintained   │  │  │Enforced     │           │
│  └─────────────┘  │  └─────────────┘  │  └─────────────┘  │  └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Architectural Compliance

```
LAYER DEPENDENCY RULES

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  ALLOWED DEPENDENCIES                                  │
│                                                                                         │
│  Languages Layer  ──────────▶  Platform Layer  ──────────▶  Infrastructure Layer      │
│  (German, Korean,              (Protocols,                  (Services,                 │
│   Russian, ...)                 Records,                     Backends,                 │
│                                 DeckBuilder)                 Managers)                  │
│                                                                                         │
│  ✅ Higher layers can use lower layers                                                 │
│  ❌ Lower layers CANNOT use higher layers                                              │
│  ❌ No circular dependencies allowed                                                   │
│  ❌ No cross-layer violations permitted                                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

FORBIDDEN PATTERNS

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                ANTI-PATTERNS                                           │
│                                                                                         │
│  Infrastructure  ──X──▶  Platform       │  Infrastructure  ──X──▶  Languages          │
│  (Services cannot       (Extension       │  (Services cannot        (Cannot depend     │
│   depend on             points)          │   depend on              on German/Korean)  │
│   protocols)                             │   language logic)                           │
│                                                                                         │
│  Platform  ──X──▶  Languages             │  Circular Dependencies  ──X──              │
│  (Protocols cannot  (Cannot depend       │  (Any circular import   forbidden)         │
│   depend on         on specific          │                                             │
│   German logic)     implementations)     │                                             │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Migration Architecture

### Before and After Comparison

#### Legacy Architecture (Before 2024-09-18)
```
src/langlearn/
├── core/                          # ❌ Mixed concerns
│   ├── services/                  # Infrastructure + Platform mixed
│   └── backends/                  # Infrastructure + Platform mixed
├── models/                        # ❌ Legacy Pydantic patterns
└── languages/                     # ✅ Language implementations
```

#### Current Architecture (After Migration)
```
src/langlearn/
├── infrastructure/                # ✅ Clear infrastructure layer
│   ├── backends/                  # Pure infrastructure
│   └── services/                  # Pure infrastructure
├── core/                         # ✅ Clear platform layer
│   ├── deck/                      # Platform orchestration
│   ├── protocols/                 # Extension contracts
│   ├── records/                   # Platform data validation
│   └── pipeline/                  # Processing framework
└── languages/                     # ✅ Language implementations
    ├── german/                    # Complete implementation
    ├── korean/                    # Complete implementation
    └── russian/                   # Complete implementation
```

### Migration Benefits Achieved

```
TECHNICAL DEBT ELIMINATION
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               IMPROVEMENTS ACHIEVED                                    │
│                                                                                         │
│  ✅ Clear Separation of Concerns    │  ✅ Improved Extensibility                       │
│  ✅ Zero Architecture Violations    │  ✅ Enhanced Maintainability                     │
│  ✅ Protocol-Based Extension        │  ✅ Better Developer Experience                  │
│  ✅ Language-Agnostic Core          │  ✅ Simplified Testing Strategy                  │
│                                                                                         │
│  Quality Metrics:                                                                      │
│  • 691 Tests Passing (100%)                                                           │
│  • Zero MyPy Errors                                                                   │
│  • Zero Ruff Violations                                                               │
│  • Clean Git History Preserved                                                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Future Architecture Roadmap

### Planned Enhancements

```
EXTENSIBILITY ROADMAP

Phase 1: Performance Optimization (Next)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ • Async/Await for I/O Operations                                                       │
│ • Redis Caching Layer                                                                  │
│ • Batch Processing Optimization                                                        │
│ • Memory Usage Optimization                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Phase 2: Language Extension (Future)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ • Spanish Implementation                                                                │
│ • French Implementation                                                                 │
│ • Italian Implementation                                                                │
│ • Dynamic Language Discovery                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Phase 3: Platform Enhancement (Future)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ • Analytics and Metrics Platform                                                       │
│ • Content Management System                                                            │
│ • User Progress Tracking                                                               │
│ • Interactive Vocabulary Selection                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

The Infrastructure/Platform/Languages architecture provides a solid foundation for all these future enhancements while maintaining system stability and quality.

---

## Summary

The Infrastructure/Platform/Languages architecture successfully separates concerns across three distinct tiers:

1. **🏗️ Infrastructure**: Stable, reusable implementations
2. **🎯 Platform**: Extension points and orchestration
3. **🌍 Languages**: Complete implementation freedom

This design enables rapid language addition, maintains code quality, and provides clear architectural boundaries for sustainable development.