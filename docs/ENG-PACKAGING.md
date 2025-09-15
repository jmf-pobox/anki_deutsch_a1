# Multi-Language Package Organization Standards and Migration Plan

**Document Status**: IN PROGRESS  
**Version**: 2.4.0  
**Last Updated**: 2025-01-08  
**Owner**: Architecture Team

## Executive Summary

This document establishes the definitive standard for package organization in the Multi-Language Anki Deck Generator project and provides a comprehensive migration plan for restructuring the current German-centric architecture to support multiple languages (German, Russian, Korean).

The current architecture is fundamentally flawed for multi-language support:
- Language-specific logic is scattered across generic packages (`services/`, `models/`, `templates/`)
- No clear separation between language-agnostic infrastructure and language-specific domain logic
- Adding new languages requires modifying core packages, violating Open/Closed Principle
- Templates and grammar rules are not organized by language

**Key Outcomes**:
- **Language-First Architecture**: Language becomes the primary organizing principle  
- **Data/Source Separation**: Data organized separately as `data/{language}/{deck}/` to support multiple decks per language
- **Clear Separation**: Language-agnostic infrastructure vs language-specific domain logic
- **Extension Framework**: Protocol-based system for adding new languages
- **Flexible Configuration**: Application supports --language and --deck parameters for user choice
- **Maintainable Growth**: Each language is self-contained and independently maintainable
- **Backward Compatibility**: Preserve existing German functionality during migration

---

## 1. Multi-Language Architecture Principles

### 1.1 Language as Primary Organizing Principle

Language must be the most visible aspect of the package structure, not buried within generic names like "models" or "services".

**Core Tenet**: If you can't immediately see where German, Russian, and Korean components live, the architecture has failed.

### 1.2 Language-Agnostic vs Language-Specific Separation

#### Language-Agnostic Components (Shared Infrastructure)
- Pipeline orchestration (CSV → Records → Cards)
- External API integrations (AWS Polly, Pexels, Anthropic)
- Anki backend interfaces and implementations
- Base Pydantic record types and validation frameworks
- File management and media coordination

#### Language-Specific Components (Per-Language)
- Domain models with linguistic business logic
- Grammar processors and linguistic rules
- Language-specific Pydantic records and validation
- Card builders with language-specific logic
- Anki card templates
- Vocabulary CSV files

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

### 2.1 Complete Multi-Language Architecture

```
src/langlearn/
├── __init__.py
├── exceptions.py                    # Language-agnostic exceptions
├── main.py                         # Application entry point
├── deck_builder.py                 # Multi-language orchestrator
│
├── core/                           # LANGUAGE-AGNOSTIC INFRASTRUCTURE
│   ├── __init__.py
│   ├── pipeline/                   # Generic data transformation pipeline
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Language-agnostic pipeline coordination
│   │   └── base_enricher.py        # Base media enrichment logic
│   │
│   ├── services/                   # External API integrations
│   │   ├── __init__.py
│   │   ├── audio_service.py        # AWS Polly integration
│   │   ├── image_service.py        # Pexels integration  
│   │   ├── ai_service.py           # Anthropic integration
│   │   ├── media_service.py        # Media orchestration and caching
│   │   ├── csv_service.py          # Generic CSV operations
│   │   └── service_container.py    # Dependency injection
│   │
│   ├── backends/                   # Deck generation backends
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract deck backend interface
│   │   └── anki_backend.py         # Anki implementation
│   │
│   └── records/                    # Base record types and validation
│       ├── __init__.py
│       └── base_record.py          # BaseRecord (Pydantic) for all languages
│
├── languages/                      # LANGUAGE-SPECIFIC IMPLEMENTATIONS
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
│   │   ├── records/                # German Pydantic records (validation)
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
│   │   ├── records/                # Russian Pydantic records
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
│       ├── records/                # Korean Pydantic records
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

### 2.1.1 Data Architecture (Separate from Source Code)

Data remains organized separately to support multiple languages AND multiple decks per language:

```
data/                               # DATA DIRECTORY (Separate from src/)
├── german/                         # GERMAN LANGUAGE DATA
│   ├── a1/                        # German A1 Level Deck
│   │   ├── nouns.csv
│   │   ├── verbs.csv
│   │   ├── adjectives.csv
│   │   ├── adverbs.csv
│   │   ├── articles.csv
│   │   ├── negations.csv
│   │   ├── prepositions.csv
│   │   ├── phrases.csv
│   │   ├── audio/                 # German A1 audio files
│   │   ├── images/                # German A1 images
│   │   └── backups/               # German A1 CSV backups
│   │
│   ├── a2/                        # German A2 Level Deck (Future)
│   │   ├── nouns.csv
│   │   ├── verbs.csv
│   │   └── ...
│   │
│   └── business/                   # German Business Deck (Future)
│       ├── terminology.csv
│       └── ...
│
├── russian/                        # RUSSIAN LANGUAGE DATA (Future)
│   ├── a1/                        # Russian A1 Level Deck
│   │   ├── nouns.csv
│   │   ├── verbs.csv
│   │   ├── audio/
│   │   ├── images/
│   │   └── ...
│   │
│   └── intermediate/               # Russian Intermediate Deck
│       └── ...
│
└── korean/                         # KOREAN LANGUAGE DATA (Future)
    ├── basic/                     # Korean Basic Level Deck
    │   ├── nouns.csv
    │   ├── verbs.csv
    │   └── ...
    │
    └── hanja/                     # Korean Hanja Deck
        └── ...
```

**Application Configuration**:
The application accepts language and deck parameters:
```bash
# Command line interface
langlearn generate --language=german --deck=a1 --output=german_a1.apkg
langlearn generate --language=russian --deck=a1 --output=russian_a1.apkg
langlearn generate --language=korean --deck=basic --output=korean_basic.apkg

# Configuration file approach
langlearn generate --config=configs/german_a1.yaml
```

### 2.2 Key Design Decisions

#### Language Registry Pattern
```python
# src/langlearn/languages/registry.py
from typing import Protocol, Type
from langlearn.protocols.language_protocol import Language

class LanguageRegistry:
    """Central registry for available languages."""
    
    _languages: dict[str, Type[Language]] = {}
    
    @classmethod
    def register(cls, language_code: str, language_class: Type[Language]):
        """Register a language implementation."""
        cls._languages[language_code] = language_class
    
    @classmethod
    def get(cls, language_code: str) -> Language:
        """Get a language implementation by code."""
        if language_code not in cls._languages:
            raise ValueError(f"Language {language_code} not registered")
        return cls._languages[language_code]()
    
    @classmethod
    def list_available(cls) -> list[str]:
        """List all registered language codes."""
        return list(cls._languages.keys())
```

#### Language Protocol Definition
```python
# src/langlearn/protocols/language_protocol.py
from typing import Protocol, Type, Any
from abc import abstractmethod

class Language(Protocol):
    """Protocol defining what each language must implement."""
    
    @property
    @abstractmethod
    def code(self) -> str:
        """ISO language code (e.g., 'de', 'ru', 'ko')."""
        ...
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable language name (e.g., 'German', 'Russian', 'Korean')."""
        ...
    
    @abstractmethod
    def get_supported_record_types(self) -> list[str]:
        """Get record types this language supports (e.g., ['noun', 'verb', 'adjective'])."""
        ...
    
    @abstractmethod
    def get_card_builder(self) -> Any:
        """Get the card builder for this language."""
        ...
    
    @abstractmethod
    def get_grammar_service(self) -> Any:
        """Get language-specific grammar service."""
        ...
    
    @abstractmethod
    def get_record_mapper(self) -> Any:
        """Get language-specific record mapper."""
        ...
    
    @abstractmethod
    def get_template_path(self, record_type: str, side: str) -> str:
        """Get template path for record type and side (front/back)."""
        ...
```

#### Template Naming Convention
Templates follow a consistent multi-language naming pattern:
```
<word_type>_<LANG_CODE>_<locale>_<side>.html
```

Examples:
- `noun_DE_de_front.html` - German noun front template
- `noun_RU_ru_front.html` - Russian noun front template  
- `verb_KO_ko_back.html` - Korean verb back template

#### Model vs Record Clarification

**Records (Pydantic Data Models)**:
- Live in `languages/<lang>/records/`
- Pure data validation and transport containers
- Language-specific validation rules (e.g., German article validation, Russian case validation)
- No business logic - just data structures

**Models (Domain Objects)**:  
- Live in `languages/<lang>/models/`
- Contain language-specific linguistic business logic
- Implement media generation protocols
- Domain expertise about grammar, pronunciation, visualization

---

## 2.3 Migration Progress Status

### Phase 2 Progress: German Language Package Creation

**Record Extraction (COMPLETED 2025-01-08)**:
- ✅ **Created German Records Structure**: Full `src/langlearn/languages/german/records/` package
- ✅ **Extracted 13 Record Classes**: All record classes moved from monolithic `records.py` to individual modules
- ✅ **Fixed Circular Import**: Created `base.py` module with shared base classes
- ✅ **Modernized Pydantic**: Updated from deprecated class Config to ConfigDict pattern
- ✅ **Maintained Quality**: All 648 tests pass, zero MyPy errors, zero Ruff violations
- ✅ **Preserved Functionality**: All existing functionality maintained during extraction

**Completed Record Files**:
```
src/langlearn/languages/german/records/
├── base.py                      # Shared BaseRecord, RecordType, RecordClassProtocol
├── adverb_record.py            # Simple record (4 fields)
├── negation_record.py          # Simple record (4 fields)
├── phrase_record.py            # Simple record (4 fields)
├── preposition_record.py       # Simple record with case validation
├── noun_record.py              # Record with gender/plural validation
├── adjective_record.py         # Record with comparative forms
├── verb_record.py              # Complex verb record with separable verb logic
├── verb_conjugation_record.py  # Most complex record with multiple validators
├── verb_imperative_record.py   # Imperative form record
├── article_record.py           # Article record with gender validation
├── indefinite_article_record.py # Indefinite article (no plural)
├── negative_article_record.py  # Negative article with plural support
├── unified_article_record.py   # Complex unified record with legacy compatibility
└── records.py                  # Factory-only module with registry and factory functions
```

**Technical Implementation Details**:
- **Incremental Approach**: Extracted one record at a time with testing between each step
- **Quality Gates**: Ran `hatch run type && hatch run ruff check --fix && hatch run format && hatch run test-unit` after each extraction
- **Complex Validator Handling**: Successfully preserved field_validator and model_validator decorators
- **Legacy Compatibility**: Maintained complex compatibility properties in UnifiedArticleRecord
- **Import Management**: Updated all imports while preserving __all__ exports

**Quality Metrics Maintained**:
- ✅ MyPy strict mode: 0 errors
- ✅ Ruff linting: 0 violations
- ✅ Test suite: All 648 tests pass
- ✅ Code formatting: Perfect compliance
- ✅ No regression in functionality

**Template Move (COMPLETED 2025-01-08)**:
- ✅ **Moved German Templates**: All 54 template files relocated to `src/langlearn/languages/german/templates/`
- ✅ **Updated Configuration**: Modified `deck_builder.py` to use new template path
- ✅ **Preserved Functionality**: All template service and deck builder tests pass
- ✅ **Clean Architecture**: Templates now properly contained within German language package

**German Domain Models Move (COMPLETED 2025-01-08)**:
- ✅ **Domain Models Migrated**: All German domain models moved to `src/langlearn/languages/german/models/`
- ✅ **Import Updates**: All references updated to new package location
- ✅ **Functionality Preserved**: All model functionality maintained during migration

**Completed in Phase 2**:
1. ✅ **Multi-Deck Architecture**: Implemented `data/{language}/{deck}/` structure supporting arbitrary decks per language
2. ✅ **CLI Multi-Deck Support**: Added --language and --deck parameters to main.py
3. ✅ **DeckBuilder Multi-Deck Support**: Updated DeckBuilder to accept language/deck configuration with proper path resolution
4. ✅ **Verified Functionality**: Successfully tested with multiple German decks (default, business, beginner)

**Next Steps in Phase 2**:
1. Move German-specific services to `src/langlearn/languages/german/services/`  
2. Implement GermanLanguage class and register in LanguageRegistry

### Multi-Deck Support Implementation Status (COMPLETED 2025-01-08)

The multi-deck per language functionality has been successfully implemented and tested:

#### ✅ Implementation Details:
- **Data Structure**: `languages/{language}/{deck}/` supports arbitrary deck names per language
- **CLI Interface**: `--language=<lang> --deck=<deck>` parameters with helpful error messages
- **DeckBuilder Integration**: Language/deck-aware path resolution for audio, images, and templates  
- **Media Organization**: Each deck maintains its own `audio/` and `images/` directories
- **Backward Compatibility**: Original German content moved to `languages/german/default/`

#### ✅ Verified Examples:
```bash
# German decks
hatch run python -m langlearn.main --language=german --deck=default    # Original A1 content
hatch run python -m langlearn.main --language=german --deck=business   # Business vocabulary  
hatch run python -m langlearn.main --language=german --deck=beginner   # Beginner content

# Future language support ready
hatch run python -m langlearn.main --language=russian --deck=basic
hatch run python -m langlearn.main --language=korean --deck=hanja
```

#### ✅ Error Handling:
```
❌ Error: Data directory not found: /path/to/languages/spanish/basic
Available languages/decks:
  Language: german
    Deck: business  
    Deck: default
    Deck: beginner
  Language: russian
    Deck: basic
```

#### ✅ Quality Gates Maintained:
- **MyPy**: 0 errors (119 source files)
- **Ruff**: 0 violations  
- **Tests**: All 648 tests pass
- **Functionality**: Full deck generation with media working correctly

---

## 3. Migration Strategy

### 3.1 Migration Overview

The migration follows a phased approach that minimizes disruption while systematically restructuring the architecture for multi-language support.

**Total Timeline**: 4-5 weeks
**Risk Profile**: Medium (architectural changes, but preserving functionality)

### 3.2 Migration Phases

#### Phase 0: Foundation Setup (Week 1, Days 1-2)
**Objective**: Create the basic multi-language structure and protocols  
**Risk**: Low  
**Duration**: 2 days

**Steps**:
1. **Create Core Package Structure**:
   ```bash
   mkdir -p src/langlearn/core/{pipeline,services,backends,records}
   mkdir -p src/langlearn/languages/{registry.py,german,russian,korean}
   mkdir -p src/langlearn/protocols
   ```

2. **Define Language Protocols**:
   ```bash
   # Create protocol definitions
   touch src/langlearn/protocols/{__init__.py,language_protocol.py,media_generation_protocol.py,record_protocol.py,card_builder_protocol.py,grammar_protocol.py}
   ```

3. **Create Language Registry System**:
   ```bash
   # Implement language registration and discovery
   touch src/langlearn/languages/{__init__.py,registry.py}
   ```

**Validation**:
- All protocols compile without errors
- Language registry can be imported
- Basic package structure is navigable

#### Phase 1: Core Infrastructure Migration (Week 1, Days 3-5)
**Objective**: Move language-agnostic components to `core/`  
**Risk**: Medium (core infrastructure changes)  
**Duration**: 3 days

**Steps**:
1. **Move External API Services**:
   ```bash
   git mv src/langlearn/services/audio.py src/langlearn/core/services/audio_service.py
   git mv src/langlearn/services/pexels_service.py src/langlearn/core/services/image_service.py
   git mv src/langlearn/services/ai_service.py src/langlearn/core/services/ai_service.py
   git mv src/langlearn/services/media_service.py src/langlearn/core/services/media_service.py
   git mv src/langlearn/services/csv_service.py src/langlearn/core/services/csv_service.py
   git mv src/langlearn/services/service_container.py src/langlearn/core/services/service_container.py
   ```

2. **Move Backend Components**:
   ```bash
   git mv src/langlearn/backends/ src/langlearn/core/backends/
   ```

3. **Create Base Record Types**:
   ```bash
   # Extract common base from existing factory.py
   # Move to src/langlearn/core/records/base_record.py
   ```

4. **Update All Import Statements**:
   ```bash
   # Update imports across the entire codebase
   find src/ -name "*.py" -exec sed -i 's/from langlearn.services.audio/from langlearn.core.services.audio_service/g' {} \;
   # ... repeat for all moved modules
   ```

**Quality Gates**:
```bash
hatch run type          # Zero MyPy errors
hatch run ruff check    # Zero Ruff violations  
hatch run test          # All tests pass
hatch run format        # Code formatted
```

**Validation**:
- All external API integrations work from new locations
- Service container resolves dependencies correctly
- Anki backend functions properly
- All existing tests pass

#### Phase 2: German Language Package Creation (Week 2)
**Objective**: Move German-specific components to `languages/german/`  
**Risk**: High (major reorganization of existing functionality)  
**Duration**: 5 days

**Steps**:
1. **Create German Package Structure**:
   ```bash
   mkdir -p src/langlearn/languages/german/{models,records,services,templates,data}
   touch src/langlearn/languages/german/{__init__.py,language.py}
   ```

2. **Move German Domain Models**:
   ```bash
   # ✅ COMPLETED: Moved all German domain models to language package
   git mv src/langlearn/models/noun.py src/langlearn/languages/german/models/
   git mv src/langlearn/models/verb.py src/langlearn/languages/german/models/
   git mv src/langlearn/models/adjective.py src/langlearn/languages/german/models/
   git mv src/langlearn/models/adverb.py src/langlearn/languages/german/models/
   git mv src/langlearn/models/article.py src/langlearn/languages/german/models/
   git mv src/langlearn/models/negation.py src/langlearn/languages/german/models/
   git mv src/langlearn/models/preposition.py src/langlearn/languages/german/models/
   git mv src/langlearn/models/phrase.py src/langlearn/languages/german/models/
   # All import statements updated, functionality preserved
   ```

3. **Extract German Records from models/records.py**:
   ```bash
   # ✅ COMPLETED: Split src/langlearn/models/factory.py into individual German record files
   # Created src/langlearn/languages/german/records/ with 13 individual record files:
   # - base.py (shared BaseRecord, RecordType, RecordClassProtocol)
   # - adverb_record.py, negation_record.py, phrase_record.py, preposition_record.py
   # - noun_record.py, adjective_record.py (simple records with field validation)
   # - verb_record.py, verb_conjugation_record.py, verb_imperative_record.py (complex verb records)
   # - article_record.py, indefinite_article_record.py, negative_article_record.py, unified_article_record.py
   # - Updated src/langlearn/languages/german/records/factory.py to factory-only module
   # All 648 tests pass, Pydantic deprecation warning fixed with ConfigDict
   ```

4. **Move German-Specific Services**:
   ```bash
   git mv src/langlearn/services/record_mapper.py src/langlearn/languages/german/services/
   git mv src/langlearn/services/card_builder.py src/langlearn/languages/german/services/
   git mv src/langlearn/services/media_enricher.py src/langlearn/languages/german/services/
   git mv src/langlearn/services/verb_conjugation_processor.py src/langlearn/languages/german/services/verb_processor.py
   git mv src/langlearn/services/article_pattern_processor.py src/langlearn/languages/german/services/article_processor.py
   git mv src/langlearn/services/article_application_service.py src/langlearn/languages/german/services/
   git mv src/langlearn/services/german_explanation_factory.py src/langlearn/languages/german/services/
   ```

5. **Move German Templates**:
   ```bash
   # ✅ COMPLETED: Moved German templates to language package
   git mv src/langlearn/templates/ src/langlearn/languages/german/templates/
   # Updated src/langlearn/deck_builder.py path configuration
   # All 54 template files (HTML/CSS) successfully moved
   # Template service tests pass, deck builder tests pass
   # Zero functional regression - templates load correctly from new location
   ```

6. **Reorganize Data Architecture for Multi-Language/Multi-Deck Support**:
   ```bash
   # ✅ COMPLETED 2025-01-08: Data reorganized for multi-language/multi-deck support
   mkdir -p languages/german/default
   mv data/*.csv languages/german/default/
   mv data/audio languages/german/default/
   mv data/images languages/german/default/
   mv data/backups languages/german/default/
   
   # ✅ IMPLEMENTED: Multi-deck structure now supports arbitrary decks per language:
   # languages/german/default/    - German default deck (original A1 content)
   # languages/german/business/   - German business vocabulary deck
   # languages/german/beginner/   - German beginner deck
   # languages/russian/basic/     - Russian basic level deck (sample)
   # languages/korean/hanja/      - Korean hanja deck (sample)
   ```

7. **Implement GermanLanguage Class**:
   ```python
   # src/langlearn/languages/german/language.py
   from langlearn.protocols.language_protocol import Language
   
   class GermanLanguage(Language):
       @property
       def code(self) -> str:
           return "de"
       
       @property 
       def name(self) -> str:
           return "German"
       
       def get_supported_record_types(self) -> list[str]:
           return ["noun", "verb", "adjective", "adverb", "article", "negation", "preposition", "phrase"]
       
       # ... implement all protocol methods
   ```

8. **Register German Language**:
   ```python
   # src/langlearn/languages/__init__.py
   from langlearn.languages.registry import LanguageRegistry
   from langlearn.languages.german.language import GermanLanguage
   
   # Register German language
   LanguageRegistry.register("de", GermanLanguage)
   ```

9. **Update All Import Statements**:
   ```bash
   # Comprehensive import updates across entire codebase
   # This is the most error-prone step and requires careful testing
   ```

**Quality Gates** (Run after EACH step):
```bash
hatch run type          # Zero MyPy errors
hatch run ruff check    # Zero Ruff violations  
hatch run test          # All tests pass
hatch run format        # Code formatted
```

**Validation**:
- German language is properly registered
- All German functionality works from new location
- Templates are accessible from German package
- CSV data is readable from German package
- Media generation works with German models
- All existing German tests pass

#### Phase 3: Infrastructure Cleanup (Week 3)
**Objective**: Clean up remaining services and organize infrastructure  
**Risk**: Low (cleanup of remaining components)  
**Duration**: 5 days

**Steps**:
1. **Move Remaining Infrastructure Services**:
   ```bash
   git mv src/langlearn/services/domain_media_generator.py src/langlearn/core/services/
   git mv src/langlearn/services/template_service.py src/langlearn/core/services/
   git mv src/langlearn/services/media_file_registrar.py src/langlearn/core/services/
   git mv src/langlearn/services/translation_service.py src/langlearn/core/services/
   ```

2. **Remove Empty services/ Directory**:
   ```bash
   # Verify services/ is empty, then remove
   rmdir src/langlearn/services/
   ```

3. **Update Core Pipeline**:
   ```bash
   # Create src/langlearn/core/pipeline/orchestrator.py
   # Implement language-agnostic pipeline that uses Language protocol
   ```

4. **Update Main Orchestrator**:
   ```bash
   # Modify src/langlearn/deck_builder.py to work with LanguageRegistry
   # Support multiple languages through protocol-based approach
   ```

**Quality Gates**:
```bash
hatch run type          # Zero MyPy errors
hatch run ruff check    # Zero Ruff violations  
hatch run test          # All tests pass
hatch run format        # Code formatted
```

**Validation**:
- No orphaned files remain in old locations
- Core pipeline works with German through protocol
- All infrastructure services accessible
- Performance maintained (no regression)

#### Phase 4: Russian Foundation (Week 4)
**Objective**: Create basic Russian language support as proof of concept  
**Risk**: Low (additive changes only)  
**Duration**: 5 days

**Steps**:
1. **Create Russian Package Structure**:
   ```bash
   mkdir -p src/langlearn/languages/russian/{models,records,services,templates,data}
   touch src/langlearn/languages/russian/{__init__.py,language.py}
   ```

2. **Implement Basic Russian Noun Model**:
   ```python
   # src/langlearn/languages/russian/models/noun.py
   # Implement Russian noun with 6-case system
   ```

3. **Create Russian Records**:
   ```python
   # src/langlearn/languages/russian/records/noun_record.py
   # Pydantic validation for Russian nouns
   ```

4. **Implement Russian Services**:
   ```python
   # src/langlearn/languages/russian/services/case_service.py
   # 6-case system processor
   ```

5. **Create Basic Russian Templates**:
   ```html
   <!-- src/langlearn/languages/russian/templates/noun_RU_ru_front.html -->
   <!-- Basic Russian noun card template -->
   ```

6. **Add Sample Russian Data**:
   ```csv
   # src/langlearn/languages/russian/data/nouns.csv
   # Sample Russian nouns with case information
   ```

7. **Register Russian Language**:
   ```python
   # Register in LanguageRegistry
   LanguageRegistry.register("ru", RussianLanguage)
   ```

**Quality Gates**:
```bash
hatch run type          # Zero MyPy errors
hatch run ruff check    # Zero Ruff violations  
hatch run test          # All tests pass (including new Russian tests)
hatch run format        # Code formatted
```

**Validation**:
- Russian language is registered and discoverable
- Basic Russian noun cards can be generated
- Russian 6-case system works correctly
- No impact on existing German functionality

#### Phase 5: Korean Foundation (Week 5)
**Objective**: Create basic Korean language support  
**Risk**: Low (additive changes only)  
**Duration**: 3 days

**Steps**:
1. **Create Korean Package Structure**:
   ```bash
   mkdir -p src/langlearn/languages/korean/{models,records,services,templates,data}
   touch src/langlearn/languages/korean/{__init__.py,language.py}
   ```

2. **Implement Basic Korean Models**:
   ```python
   # Korean noun with particle system
   # Korean verb with honorific levels
   ```

3. **Create Korean Services**:
   ```python
   # Honorific service
   # Particle service  
   ```

4. **Register Korean Language**:
   ```python
   LanguageRegistry.register("ko", KoreanLanguage)
   ```

**Quality Gates**:
```bash
hatch run type          # Zero MyPy errors
hatch run ruff check    # Zero Ruff violations  
hatch run test          # All tests pass
hatch run format        # Code formatted
```

### 3.3 Risk Mitigation

#### Technical Risks

**Risk**: Import statement updates cause widespread breakage  
**Mitigation**: 
- Incremental updates with testing after each module move
- Automated import replacement scripts with verification
- Rollback procedures for each phase

**Risk**: Template path resolution breaks  
**Mitigation**:
- Template service updated to use language-aware path resolution
- Backward compatibility layer during transition
- Comprehensive template loading tests

**Risk**: CSV data path resolution breaks  
**Mitigation**:
- Update CSV service to use language-aware path resolution
- Maintain data directory structure integrity
- Data loading tests for each language

#### Process Risks

**Risk**: Migration takes longer than estimated  
**Mitigation**:
- Each phase is independently valuable
- Can halt after any completed phase
- Rollback procedures for incomplete phases

**Risk**: Team confusion during transition  
**Mitigation**:
- Clear documentation of current state
- Regular communication of progress
- Pair programming for complex changes

### 3.4 Rollback Procedures

Each phase has a defined rollback procedure:

#### Phase 0 Rollback:
```bash
git checkout HEAD~N  # Where N is number of commits in phase
# Remove created directories
rm -rf src/langlearn/core src/langlearn/languages src/langlearn/protocols
```

#### Phase 1-5 Rollback:
```bash
# Revert git moves
git log --oneline | grep "Phase X"  # Identify phase commits
git revert <commit-hash-range>      # Revert in reverse order

# Restore import statements
git checkout HEAD~N -- <affected-files>
```

---

## 4. Implementation Guidelines

### 4.1 Git History Preservation

**Use `git mv` for all file moves** to preserve history:
```bash
git mv src/langlearn/services/audio.py src/langlearn/core/services/audio_service.py
```

**Never use `cp` + `rm`** as this loses git history.

### 4.2 Import Statement Updates

**Systematic approach**:
1. **Identify all import statements** for moved modules
2. **Create replacement scripts** for bulk updates
3. **Test after each batch** of replacements
4. **Verify no broken imports** remain

**Example replacement script**:
```bash
#!/bin/bash
find src/ -name "*.py" -exec sed -i 's/from langlearn.services.audio/from langlearn.core.services.audio_service/g' {} \;
find src/ -name "*.py" -exec sed -i 's/import langlearn.services.audio/import langlearn.core.services.audio_service/g' {} \;
```

### 4.3 Quality Gate Enforcement

**After EVERY file move**:
```bash
hatch run type          # Must pass - zero MyPy errors
hatch run ruff check    # Must pass - zero Ruff violations
hatch run format        # Apply formatting
hatch run test          # Must pass - all tests
```

**No exceptions** - quality gates are absolute requirements.

### 4.4 Documentation Updates

**Update during migration**:
- README.md - reflect new package structure
- API documentation - update import examples
- Development guides - update package references
- Architecture diagrams - reflect new organization

---

## 5. Success Metrics

### 5.1 Structural Metrics

**Package Organization**:
- ✅ No package with >10 modules (cognitive load limit)
- ✅ Language clearly visible in directory structure
- ✅ Clear separation between language-agnostic and language-specific code
- ✅ Protocol-based interfaces between layers

**Dependency Health**:
- ✅ No circular dependencies between packages
- ✅ Clean import statements (no relative imports across packages)
- ✅ Dependency flow follows clean architecture (inward dependencies)

### 5.2 Quality Metrics

**Code Quality** (Must not regress):
- ✅ MyPy: 0 errors in strict mode (currently 0)
- ✅ Ruff: 0 violations (currently 0)
- ✅ Test Coverage: ≥73.84% (current baseline)
- ✅ All tests pass: 772+ tests

**Performance** (Must not regress):
- ✅ Deck generation time maintained or improved
- ✅ Media generation performance maintained
- ✅ Import time not significantly increased

### 5.3 Multi-Language Readiness

**German** (Must maintain existing functionality):
- ✅ All existing German functionality preserved
- ✅ All German tests pass
- ✅ German templates load correctly
- ✅ German media generation works

**Russian** (Basic functionality):
- ✅ Russian language registered and discoverable
- ✅ Basic Russian noun model with 6 cases
- ✅ Sample Russian cards generate successfully

**Korean** (Basic functionality):
- ✅ Korean language registered and discoverable
- ✅ Basic Korean noun model with particles
- ✅ Sample Korean cards generate successfully

**Extension Framework**:
- ✅ New languages can be added without modifying core code
- ✅ Language registry system works correctly
- ✅ Protocol-based extension points function

---

## 6. Post-Migration Benefits

### 6.1 Multi-Language Support

**Language Addition Process**:
1. Create `src/langlearn/languages/<new_language>/` package
2. Implement Language protocol
3. Add language-specific models, records, services
4. Create language-specific templates
5. Register in LanguageRegistry
6. No changes required to core infrastructure

**Language Isolation**:
- Each language is completely self-contained
- Grammar changes in one language don't affect others
- Independent development and testing per language
- Clear ownership boundaries for language-specific features

### 6.2 Improved Code Navigation

**Before** (German-centric):
```
services/ (20+ modules with mixed responsibilities)
├── record_mapper.py          # Pipeline
├── media_enricher.py         # Pipeline  
├── card_builder.py           # Pipeline
├── audio.py                  # External API
├── pexels_service.py         # External API
├── verb_conjugation_processor.py  # German grammar
├── article_pattern_processor.py   # German grammar
└── ... (13 more mixed modules)
```

**After** (Multi-language):
```
languages/
├── german/                   # All German code here
│   ├── models/              # German domain objects
│   ├── services/            # German processors  
│   └── templates/           # German templates
├── russian/                 # All Russian code here
└── korean/                  # All Korean code here

core/                        # Language-agnostic infrastructure  
├── services/                # External APIs
├── pipeline/                # Generic pipeline
└── backends/                # Anki backend
```

**Navigation Benefits**:
- **German developers**: Go directly to `languages/german/`
- **Russian developers**: Go directly to `languages/russian/`
- **Infrastructure developers**: Work in `core/`
- **Clear boundaries**: No confusion about where code belongs

### 6.3 Enhanced Testing and Mocking

**Language-Specific Testing**:
- German tests in `languages/german/tests/`
- Russian tests in `languages/russian/tests/`
- Core infrastructure tests in `core/tests/`
- No cross-language test interference

**Mocking Strategies**:
- Mock entire languages for core infrastructure tests
- Mock core infrastructure for language-specific tests
- Integration tests can test language combinations

### 6.4 Maintainability Improvements

**Team Specialization**:
- Language experts focus on their language packages
- Infrastructure team focuses on core services
- Clear ownership and responsibility boundaries

**Independent Evolution**:
- German grammar improvements don't affect Russian
- Core infrastructure improvements benefit all languages
- Language packages can evolve at different rates

**Reduced Cognitive Load**:
- Developers only need to understand their relevant packages
- No need to navigate through irrelevant language-specific code
- Clear mental model of system organization

---

## Conclusion

This multi-language restructuring represents a fundamental architectural shift from a German-centric design to a truly extensible multi-language platform. The migration is complex but provides enormous long-term benefits:

**Immediate Benefits**:
- Clear organization of existing German code
- Elimination of confusing service package structure
- Better code navigation and maintainability

**Long-term Benefits**:
- Seamless addition of Russian and Korean languages
- Protocol-based extension framework for future languages
- Independent evolution of language-specific features
- Clear team ownership boundaries

The phased migration approach minimizes risk while providing incremental value. Each phase can stand alone, allowing for flexible timing and resource allocation.

**Next Steps**:
1. **Review and approve** this architectural design
2. **Begin Phase 0**: Foundation setup and protocol definition
3. **Execute migration** following the detailed phase plan
4. **Add Russian/Korean** languages using the new framework

This architecture positions the project for sustainable growth across multiple languages while maintaining the high quality standards established in the German implementation.