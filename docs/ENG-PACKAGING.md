# Multi-Language Package Organization Standards

**Document Status**: CURRENT
**Version**: 4.0.0
**Last Updated**: 2025-01-18
**Owner**: Architecture Team

## Executive Summary

This document establishes the definitive standard for package organization in the Multi-Language Anki Deck Generator project based on **open-closed extensibility principles**. The architecture clearly separates what is **closed for modification** (infrastructure) from what is **open for extension** (platform) and actual **extensions** (languages).

**Current Status (2025-01-18)**:
✅ **ARCHITECTURE COMPLETE**: Multi-language foundation fully implemented
- ✅ Language System: Protocol-based language registry with German/Russian/Korean
- ✅ DeckBuilder API: Observable 5-phase pipeline with structured data access
- ✅ Template System: Language-agnostic resolution via protocols
- ✅ Data Structure: `languages/{language}/{deck}/` supporting multiple decks per language
- ✅ Quality Standards: All 672+ tests pass, MyPy strict mode clean

**Key Outcomes**:
- **Extension-First Architecture**: Clear separation of closed infrastructure vs open platform vs language extensions
- **Self-Documenting Structure**: Package names immediately indicate extensibility intent
- **Observable Pipeline**: 5-phase DeckBuilder API with read access to intermediate state
- **Protocol-Based Extension**: Adding new languages requires zero core code changes
- **Multi-Deck Support**: Flexible --language and --deck parameters for user choice

---

## 1. Open-Closed Architecture Principles

### 1.1 Extension Intent as Organizing Principle

Package structure must immediately communicate what can be extended and what cannot.

**Core Tenet**: Developers should instantly understand whether they're working with infrastructure they use, platform they extend, or extensions they implement.

### 1.2 Three-Tier Extensibility Model

#### Infrastructure (CLOSED) - "You Use This"
- External API integrations (AWS Polly, Pexels, Anthropic)
- Anki backend file format handling
- File management and media storage
- Pure technical utilities with no business logic

#### Platform (OPEN) - "You Extend This"
- DeckBuilder API orchestration and pipeline
- Base record system and protocols
- Data transformation framework
- Extension points and contracts

#### Languages (EXTENSIONS) - "You Implement This"
- Domain models with linguistic business logic
- Grammar processors and linguistic rules
- Language-specific records and validation
- Card builders and templates
- Vocabulary data

### 1.3 Protocol-Based Extensibility

Each language implements well-defined protocols that allow the language-agnostic infrastructure to work with any language without modification.

### 1.4 Language-Specific Challenges

#### German
- **Grammar Features**: Articles (der/die/das), 4 cases, separable verbs, compound nouns
- **Services Needed**: Article processors, verb conjugation, case declensions
- **Template Focus**: Gender drilling, case practice, separable verb patterns

#### Russian (Future)
- **Grammar Features**: 6 cases, aspect system (perfective/imperfective), palatalization, stress patterns
- **Services Needed**: 6-case processors, aspect processors, stress pattern services
- **Template Focus**: Case drilling, aspect distinction, stress indication

#### Korean (Future)
- **Grammar Features**: Honorific levels, agglutination, particles, sentence-final particles, no articles
- **Services Needed**: Honorific processors, particle services, agglutination handlers
- **Template Focus**: Honorific practice, particle usage, verb conjugation patterns

---

## 2. Target Package Structure

### 2.1 Open-Closed Extension Architecture

```
src/langlearn/
├── __init__.py
├── exceptions.py                    # Language-agnostic exceptions
├── main.py                         # Application entry point
│
├── infrastructure/                  # CLOSED - Pure technical services
│   ├── __init__.py
│   ├── services/                   # External API integrations
│   │   ├── __init__.py
│   │   ├── audio_service.py        # AWS Polly integration
│   │   ├── image_service.py        # Pexels integration
│   │   ├── ai_service.py           # Anthropic integration
│   │   ├── media_service.py        # Media orchestration and caching
│   │   ├── csv_service.py          # Generic CSV operations
│   │   └── service_container.py    # Dependency injection
│   │
│   ├── backends/                   # Anki integration
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract deck backend interface
│   │   └── anki_backend.py         # Anki implementation
│   │
│   └── storage/                    # File/media management
│       ├── __init__.py
│       ├── media_file_registrar.py # Media file registration
│       └── template_service.py     # Template resolution
│
├── platform/                       # OPEN - Extension points & orchestration
│   ├── __init__.py
│   ├── deck/                       # DeckBuilder API orchestration
│   │   ├── __init__.py
│   │   ├── builder.py              # Observable 5-phase pipeline
│   │   ├── phases.py               # Phase management
│   │   ├── data_types.py           # Structured data access
│   │   └── progress.py             # Progress reporting
│   │
│   ├── pipeline/                   # Data transformation framework
│   │   ├── __init__.py
│   │   ├── pipeline.py             # Generic pipeline coordination
│   │   └── media_enricher.py       # Base media enrichment logic
│   │
│   ├── records/                    # Base record system
│   │   ├── __init__.py
│   │   └── base_record.py          # BaseRecord for all languages
│   │
│   └── protocols/                  # Extension interfaces
│       ├── __init__.py
│       ├── language_protocol.py    # Core Language interface
│       ├── media_generation_protocol.py # Media generation interfaces
│       ├── record_protocol.py      # Record type protocols
│       ├── card_builder_protocol.py # Card building interfaces
│       └── grammar_protocol.py     # Grammar service interfaces
│
├── languages/                      # EXTENSIONS - Language implementations
│   ├── __init__.py
│   ├── registry.py                 # Language registration system
│   │
│   ├── german/                     # GERMAN LANGUAGE PACKAGE
│   │   ├── __init__.py
│   │   ├── language.py             # GermanLanguage class implementing protocols
│   │   │
│   │   ├── models/                 # German domain models (business logic)
│   │   │   ├── __init__.py
│   │   │   ├── noun.py             # German Noun with gender/case logic
│   │   │   ├── verb.py             # German Verb with separable logic
│   │   │   ├── adjective.py        # German Adjective with declensions
│   │   │   ├── adverb.py           # German Adverb
│   │   │   ├── article.py          # German Article
│   │   │   ├── negation.py         # German Negation
│   │   │   ├── preposition.py      # German Preposition with cases
│   │   │   └── phrase.py           # German Phrase
│   │   │
│   │   ├── records/                # German dataclass records (validation)
│   │   │   ├── __init__.py
│   │   │   ├── noun_record.py      # German noun validation rules
│   │   │   ├── verb_record.py      # German verb validation rules
│   │   │   ├── adjective_record.py
│   │   │   ├── adverb_record.py
│   │   │   ├── article_record.py
│   │   │   ├── negation_record.py
│   │   │   ├── preposition_record.py
│   │   │   └── phrase_record.py
│   │   │
│   │   ├── services/               # German-specific processing services
│   │   │   ├── __init__.py
│   │   │   ├── card_builder.py     # German card generation logic
│   │   │   ├── record_mapper.py    # German CSV → Record mapping
│   │   │   ├── grammar_service.py  # German grammar rules
│   │   │   ├── article_processor.py # German article processing
│   │   │   ├── verb_processor.py   # German verb conjugation
│   │   │   └── media_enricher.py   # German media enrichment
│   │   │
│   │   ├── templates/              # German Anki card templates
│   │   │   ├── __init__.py
│   │   │   ├── noun_DE_de_front.html
│   │   │   ├── noun_DE_de_back.html
│   │   │   ├── verb_DE_de_front.html
│   │   │   ├── verb_DE_de_back.html
│   │   │   ├── adjective_DE_de_front.html
│   │   │   └── ... (50+ existing templates)
│   │
│   ├── russian/                    # RUSSIAN LANGUAGE PACKAGE (Future)
│   │   ├── __init__.py
│   │   ├── language.py             # RussianLanguage class
│   │   │
│   │   ├── models/                 # Russian domain models
│   │   │   ├── __init__.py
│   │   │   ├── noun.py             # Russian Noun with 6 cases
│   │   │   ├── verb.py             # Russian Verb with aspects
│   │   │   ├── adjective.py        # Russian Adjective with agreements
│   │   │   └── ...
│   │   │
│   │   ├── records/                # Russian dataclass records
│   │   │   ├── __init__.py
│   │   │   ├── noun_record.py      # Russian noun validation (6 cases)
│   │   │   ├── verb_record.py      # Russian verb validation (aspects)
│   │   │   └── ...
│   │   │
│   │   ├── services/               # Russian-specific services
│   │   │   ├── __init__.py
│   │   │   ├── card_builder.py     # Russian card generation
│   │   │   ├── case_service.py     # 6-case system processor
│   │   │   ├── aspect_service.py   # Perfective/imperfective processor
│   │   │   ├── stress_service.py   # Stress pattern processor
│   │   │   └── grammar_service.py  # Russian grammar rules
│   │   │
│   │   └── templates/              # Russian Anki templates
│   │       ├── noun_RU_ru_front.html
│   │       ├── noun_RU_ru_back.html
│   │       ├── verb_RU_ru_front.html
│   │       └── ...
│   │
│   └── korean/                     # KOREAN LANGUAGE PACKAGE (Future)
│       ├── __init__.py
│       ├── language.py             # KoreanLanguage class
│       │
│       ├── models/                 # Korean domain models
│       │   ├── __init__.py
│       │   ├── noun.py             # Korean Noun with particles
│       │   ├── verb.py             # Korean Verb with honorifics
│       │   ├── adjective.py        # Korean Adjective
│       │   └── ...
│       │
│       ├── records/                # Korean dataclass records
│       │   ├── __init__.py
│       │   ├── noun_record.py      # Korean noun validation
│       │   ├── verb_record.py      # Korean verb validation (honorifics)
│       │   └── ...
│       │
│       ├── services/               # Korean-specific services
│       │   ├── __init__.py
│       │   ├── card_builder.py     # Korean card generation
│       │   ├── honorific_service.py # Honorific level processor
│       │   ├── particle_service.py # Particle processor
│       │   ├── conjugation_service.py # Korean conjugation patterns
│       │   └── grammar_service.py  # Korean grammar rules
│       │
│       └── templates/              # Korean Anki templates
│           ├── noun_KO_ko_front.html
│           ├── noun_KO_ko_back.html
│           ├── verb_KO_ko_front.html
│           └── ...
│
├── protocols/                      # LANGUAGE-AGNOSTIC PROTOCOLS
│   ├── __init__.py
│   ├── language_protocol.py        # Core Language interface
│   ├── media_generation_protocol.py # Media generation interfaces
│   ├── record_protocol.py          # Record type protocols
│   ├── card_builder_protocol.py    # Card building interfaces
│   └── grammar_protocol.py         # Grammar service interfaces
│
├── managers/                       # HIGH-LEVEL ORCHESTRATION (Keep as-is)
│   ├── __init__.py
│   ├── deck_manager.py             # High-level deck organization
│   └── media_manager.py            # Media file management orchestration
│
└── utils/                          # SHARED UTILITIES (Keep as-is)
    ├── __init__.py
    └── keyring_utils.py            # API key management
```

└── managers/                        # HIGH-LEVEL ORCHESTRATION
    ├── __init__.py
    ├── deck_manager.py              # High-level deck organization
    └── media_manager.py             # Media file management orchestration
```

### 2.2 Data Architecture (Separate from Source Code)

Data is organized separately to support multiple languages and multiple decks per language:

```
languages/                          # DATA DIRECTORY (Separate from src/)
├── german/                         # GERMAN LANGUAGE DATA
│   ├── default/                    # German default deck (A1 level)
│   │   ├── nouns.csv, verbs.csv, adjectives.csv, etc.
│   │   ├── audio/                  # Generated German audio files
│   │   └── images/                 # Generated German images
│   │
│   ├── business/                   # German business vocabulary
│   └── beginner/                   # German beginner deck
│
├── russian/                        # RUSSIAN LANGUAGE DATA
│   └── default/                    # Russian basic vocabulary
│       ├── nouns.csv
│       ├── audio/
│       └── images/
│
└── korean/                         # KOREAN LANGUAGE DATA
    └── default/                    # Korean basic vocabulary
        ├── nouns.csv
        ├── audio/
        └── images/
```

**Application Usage**:
```bash
# Command line interface
hatch run app --language=german --deck=default --output=german_default.apkg
hatch run app --language=russian --deck=default --output=russian_default.apkg
hatch run app --language=korean --deck=default --output=korean_default.apkg
```

### 2.3 Key Design Principles

#### Extension Point Clarity
Each package tier has clear responsibilities:
- **Infrastructure**: External APIs, file I/O, Anki integration - pure technical services
- **Platform**: DeckBuilder API, pipelines, protocols - designed for extension
- **Languages**: Domain models, templates, services - actual extensions

#### Protocol-Based Extension
Languages implement well-defined protocols enabling zero-modification extension:
```python
# New languages require no changes to infrastructure or platform
class SwedishLanguage(LanguageProtocol):
    def get_supported_record_types(self) -> list[str]:
        return ["noun", "verb", "adjective"]
    # ... implement other protocol methods
```

#### Observable Pipeline
The DeckBuilder API provides structured access to all pipeline phases:
```python
# 5-phase observable pipeline
builder = DeckBuilderAPI("Test Deck", "german")
loaded_data = builder.load_data(data_dir)          # Phase 1: DATA_LOADED
for progress in builder.enrich_media():            # Phase 2: MEDIA_ENRICHED
    print(f"Processing {progress.record_type}...")
built_cards = builder.build_cards()               # Phase 3: CARDS_BUILT
export_result = builder.export_deck(output_path)  # Phase 4: DECK_EXPORTED
```

---

## 3. Current Implementation Status

### ✅ Architecture Complete (January 2025)

**Multi-Language Foundation**:
- ✅ **Three Languages Implemented**: German (full), Russian (minimal), Korean (minimal)
- ✅ **Protocol-Based Extension**: LanguageRegistry with zero-modification language addition
- ✅ **Observable Pipeline**: 5-phase DeckBuilderAPI with structured data access
- ✅ **Multi-Deck Support**: `languages/{language}/{deck}/` structure with CLI parameters

**Quality Metrics**:
- ✅ **672+ Tests Passing**: Complete test coverage maintained
- ✅ **MyPy Strict Mode**: Zero type errors across all modules
- ✅ **File Logging**: Proper separation of API logging and user-facing output
- ✅ **Performance**: 53MB German deck generation, 213KB Russian deck generation

### ⚠️ Next Priority: Package Structure Refactoring

**Current Issue**: The `langlearn/core/` concept is too broad. The DeckBuilder API (application orchestration) doesn't belong in "infrastructure."

**Solution**: Implement Infrastructure/Platform/Languages structure per open-closed extensibility principles.

---

## 4. Benefits of the Extension-Based Architecture

### 4.1 Clear Mental Model
- **Infrastructure**: "You use this" - External APIs, file I/O, Anki integration
- **Platform**: "You extend this" - DeckBuilder API, protocols, pipelines
- **Languages**: "You implement this" - Domain models, templates, grammar rules

### 4.2 Self-Documenting Structure
Package names immediately indicate extensibility intent:
```
infrastructure/services/audio_service.py  # Clear: technical service
platform/deck/builder.py                  # Clear: extension point
languages/german/models/noun.py           # Clear: implementation
```

### 4.3 Maintainable Growth
- **Language specialists** work only in their language package
- **Platform developers** focus on extension points and orchestration
- **Infrastructure team** maintains external integrations and file handling
- **Zero coupling** between language implementations

---

## Conclusion

This packaging standard establishes a clear, extension-based architecture that eliminates confusion about where components belong. The three-tier model (Infrastructure/Platform/Languages) provides an intuitive framework for sustainable multi-language growth while maintaining high code quality standards.

**Key Outcomes**:
- **Self-documenting**: Package structure immediately communicates extension intent
- **Maintainable**: Clear separation of closed infrastructure vs open platform vs language extensions
- **Scalable**: New languages require zero modifications to infrastructure or platform code
- **Observable**: 5-phase pipeline provides structured access to all intermediate state

This standard provides the foundation for sustainable multi-language growth while maintaining the quality standards established in the current implementation.
