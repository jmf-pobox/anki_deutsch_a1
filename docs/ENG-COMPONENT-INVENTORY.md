# Component Inventory - Infrastructure/Platform/Languages Architecture

This document provides a comprehensive inventory of the langlearn codebase organized by the **Infrastructure/Platform/Languages** architectural pattern. Each component is categorized by its role in the three-tier system that enables extensible language learning deck generation.

**Updated**: 2024-09-18 to reflect Infrastructure/Platform/Languages migration

---

## Architecture Overview

The langlearn system follows a three-tier architecture with clear separation of concerns:

- **🏗️ Infrastructure Layer** (`langlearn.infrastructure.*`): "You use this" - Stable, concrete implementations
- **🎯 Platform Layer** (`langlearn.core.*`): "You extend this" - Extension points and orchestration
- **🌍 Languages Layer** (`langlearn.languages.*`): "You implement this" - Language-specific implementations

---

## 🏗️ Infrastructure Layer - "You use this"

**Package**: `src/langlearn/infrastructure/`
**Purpose**: Provides stable, concrete implementations that all languages use without modification

### Backend Implementations

**Location**: `src/langlearn/infrastructure/backends/`

| **Component** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`DeckBackend`** | `base.py` | Abstract interface defining deck creation contract. Specifies methods for note types, media files, and deck export that all backends must implement. |
| **`AnkiBackend`** | `anki_backend.py` | Concrete implementation creating `.apkg` files from card data. Handles Anki collection management, note type creation, media packaging, and deck export with comprehensive error handling. |
| **`MediaFile`** | `base.py` | Value object representing media files with path and Anki reference. Provides type-safe media file handling across the system. |
| **`NoteType`** | `base.py` | Value object defining Anki note type structure with fields and templates. Encapsulates card type definitions for consistent deck generation. |
| **`CardTemplate`** | `base.py` | Value object for Anki card templates with HTML, CSS, and metadata. Provides structured template definitions for card rendering. |

### Service Implementations

**Location**: `src/langlearn/infrastructure/services/`

| **Service** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`AudioService`** | `audio_service.py` | AWS Polly integration for German text-to-speech. Handles SSML generation, audio file caching with MD5 hashing, and pronunciation optimization for language learning. |
| **`PexelsService`** | `image_service.py` | Pexels API integration for vocabulary image search and download. Implements rate limiting, retry logic with exponential backoff, and image optimization for educational content. |
| **`AnthropicService`** | `ai_service.py` | Anthropic Claude API integration for AI-enhanced content generation. Provides context-aware image queries and content validation for vocabulary learning. |
| **`MediaEnricher`** | `media_enricher.py` | Orchestrates audio and image generation with intelligent caching and deduplication. Coordinates between AudioService and PexelsService for efficient media creation. |
| **`StandardMediaEnricher`** | `media_enricher.py` | Standard implementation of MediaEnricher with full audio and image generation capabilities. Used by all language implementations for consistent media handling. |
| **`CSVService`** | `csv_service.py` | Generic CSV reading with automatic Pydantic model conversion. Provides type-safe data loading from vocabulary files with comprehensive validation and error reporting. |
| **`TemplateService`** | `template_service.py` | Anki card template loading and NoteType creation. Manages HTML/CSS template files with caching and provides card formatting services for all languages. |
| **`NamingService`** | `naming_service.py` | Standardized filename and path generation for media assets. Ensures consistent naming conventions across audio files, images, and deck outputs. |
| **`MediaFileRegistrar`** | `media_file_registrar.py` | Tracks and manages media file relationships and dependencies. Prevents duplicate media generation and maintains media file integrity across deck builds. |
| **`ServiceContainer`** | `service_container.py` | Dependency injection container for infrastructure services. Provides singleton pattern management and service lifecycle for AudioService, PexelsService, and AnthropicService. |
| **`DomainMediaGenerator`** | `domain_media_generator.py` | Bridge between domain models and media services. Handles protocol compliance and provides fallback strategies for media generation across different language implementations. |

---

## 🎯 Platform Layer - "You extend this"

**Package**: `src/langlearn/core/`
**Purpose**: Provides extension points, orchestration, and contracts that languages implement

### Deck Management and Orchestration

**Location**: `src/langlearn/core/deck/`

| **Component** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`DeckBuilderAPI`** | `builder.py` | Observable 5-phase deck generation pipeline. Orchestrates data loading, model creation, media enrichment, card building, and deck export with comprehensive progress tracking and error handling. |
| **`DeckPhases`** | `phases.py` | State management for deck generation phases (INITIALIZED → DATA_LOADED → MODELS_BUILT → MEDIA_ENRICHED → CARDS_BUILT → EXPORTED). Enforces valid phase transitions and provides phase validation. |
| **`BuiltCards`** | `data_types.py` | Type-safe container for generated card data with metadata. Encapsulates cards, categorization by type, template usage statistics, and build errors for comprehensive deck analysis. |
| **`DeckProgress`** | `progress.py` | Progress tracking and reporting for deck generation operations. Provides percentage completion, phase timing, and detailed progress information for user feedback. |
| **`DeckGenerationResult`** | `data_types.py` | Result object containing deck export metadata and statistics. Includes output path, cards exported count, media files included, and generation performance metrics. |

### Records and Data Validation

**Location**: `src/langlearn/core/records/`

| **Component** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`BaseRecord`** | `base_record.py` | Abstract foundation for all language record types with common validation patterns. Provides Pydantic-based validation, field transformation utilities, and integration with platform systems. |

### Extension Protocols

**Location**: `src/langlearn/core/protocols/`

| **Protocol** | **File** | **Single Responsibility** |
|--------------|----------|---------------------------|
| **`MediaGenerationCapable`** | `media_generation_protocol.py` | Contract for domain models requiring media generation. Defines `get_combined_audio_text()`, `get_image_search_strategy()`, and media-related methods that all vocabulary models must implement. |
| **`CardProcessorProtocol`** | `card_processor_protocol.py` | Contract for language-specific card processing. Defines methods for transforming domain models into Anki card fields with language-specific formatting and template selection. |
| **`TTSConfig`** | `tts_protocol.py` | Configuration protocol for text-to-speech services. Defines voice selection, language codes, and audio generation parameters for consistent pronunciation across languages. |
| **`ImageSearchCapable`** | `image_search_protocol.py` | Contract for AI-enhanced image query generation. Defines methods for creating context-aware image search queries using AI services for improved vocabulary visualization. |

### Pipeline Framework

**Location**: `src/langlearn/core/pipeline/`

| **Component** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`Pipeline`** | `pipeline.py` | Generic processing pipeline framework with task orchestration. Provides sequential task execution with state management and error propagation for extensible data processing workflows. |
| **`PipelineTask`** | `pipeline.py` | Base class for pipeline task implementations with input/output validation. Ensures type safety and proper state transitions in processing workflows. |
| **`PipelineObject`** | `pipeline.py` | Container for pipeline data with input/output aliasing. Provides consistent data flow through pipeline stages with comprehensive state tracking. |
| **`PipelineTaskState`** | `pipeline.py` | State tracking for individual pipeline tasks with completion status and logging. Enables progress monitoring and debugging of complex data processing operations. |

---

## 🌍 Languages Layer - "You implement this"

**Package**: `src/langlearn/languages/`
**Purpose**: Language-specific implementations using platform extension points

### German Language Implementation

**Location**: `src/langlearn/languages/german/`

#### Domain Models (`languages/german/models/`)

| **Model** | **File** | **Single Responsibility** |
|-----------|----------|---------------------------|
| **`Noun`** | `noun.py` | German noun representation with article/gender, plural forms, and case information. Implements MediaGenerationCapable with German-specific audio text generation and concreteness-based image search strategies. |
| **`Adjective`** | `adjective.py` | German adjective with comparative/superlative forms and declension rules. Provides German-specific pronunciation patterns and context-aware image search for descriptive vocabulary. |
| **`Adverb`** | `adverb.py` | German adverb with type classification (manner, time, place, degree). Implements conceptual image search strategies for abstract vocabulary concepts with MediaGenerationCapable compliance. |
| **`Verb`** | `verb.py` | German verb with conjugation patterns, separable prefixes, and auxiliary selection. Provides comprehensive German verb system support with pronunciation and visual learning aids. |
| **`Negation`** | `negation.py` | German negation patterns (nicht, kein, nie) with syntactic positioning rules. Implements German-specific negation grammar for accurate language learning content. |
| **`Article`** | `article.py` | German articles with complete case/gender declension system. Provides comprehensive German article support with context-sensitive pronunciation and usage examples. |
| **`Preposition`** | `preposition.py` | German prepositions with case governance and two-way preposition logic. Implements relationship-based image search and comprehensive German prepositional system. |
| **`Phrase`** | `phrase.py` | German phrases and expressions with contextual usage patterns. Provides situational media generation and communicative function support for practical German learning. |

#### Record Types (`languages/german/records/`)

| **Record** | **File** | **Single Responsibility** |
|------------|----------|---------------------------|
| **`GermanRecordFactory`** | `factory.py` | Factory for creating German-specific record types from CSV data with comprehensive validation. Maps CSV rows to appropriate German record classes with language-specific validation rules. |
| **`NounRecord`** | `noun_record.py` | Pydantic validation for German noun CSV data with article/gender validation. Ensures data integrity for German noun system with comprehensive field validation. |
| **`VerbRecord`** | `verb_record.py` | Pydantic validation for German verb CSV data with conjugation pattern validation. Handles German verb complexity with separable prefixes and auxiliary selection rules. |
| **`AdjectiveRecord`** | `adjective_record.py` | Pydantic validation for German adjective CSV data with comparative/superlative form validation. Ensures complete German adjective declension support. |

#### Language Services (`languages/german/services/`)

| **Service** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`CardBuilder`** | `card_builder.py` | German-specific card formatting and template selection. Transforms German domain models into Anki-ready card data with language-appropriate formatting and field mapping. |
| **`CardProcessor`** | `card_processor.py` | German vocabulary card processing with type-specific handling. Implements CardProcessorProtocol for German language with specialized processing for each word type. |
| **`ArticleApplicationService`** | `article_application_service.py` | German article application and declension logic. Handles complex German article system with case/gender agreement and contextual article selection. |
| **`ArticlePatternProcessor`** | `article_pattern_processor.py` | Pattern matching and processing for German articles in various contexts. Provides sophisticated article handling for German grammar complexity. |
| **`VerbConjugationProcessor`** | `verb_conjugation_processor.py` | German verb conjugation processing with comprehensive tense support. Handles German verb complexity including separable verbs and auxiliary selection. |

### Korean Language Implementation

**Location**: `src/langlearn/languages/korean/`

| **Component** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`KoreanLanguage`** | `language.py` | Korean language configuration with Hangul support and Korean-specific TTS settings. Provides Korean language integration with platform services. |
| **`CardBuilder`** | `services/card_builder.py` | Korean-specific card formatting with Hangul character handling. Transforms Korean domain models into Anki cards with proper Korean typography and layout. |
| **`CardProcessor`** | `services/card_processor.py` | Korean vocabulary card processing with language-specific formatting. Implements CardProcessorProtocol for Korean with specialized Hangul and romanization support. |
| **`GrammarService`** | `services/grammar_service.py` | Korean grammar processing and validation services. Handles Korean grammatical structures and language-specific validation rules. |

### Russian Language Implementation

**Location**: `src/langlearn/languages/russian/`

| **Component** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`RussianLanguage`** | `language.py` | Russian language configuration with Cyrillic support and native pronunciation settings. Provides Russian language integration with specialized voice and character handling. |
| **`CardBuilder`** | `services/card_builder.py` | Russian-specific card formatting with Cyrillic character support. Handles Russian typography, case system, and cultural context for effective language learning. |
| **`CardProcessor`** | `services/card_processor.py` | Russian vocabulary processing with case system support. Implements CardProcessorProtocol for Russian with comprehensive grammar and declension handling. |
| **`GrammarService`** | `services/grammar_service.py` | Russian grammar processing including case system and aspect handling. Provides sophisticated Russian grammatical analysis and validation. |

---

## Cross-Cutting Concerns

### Management Layer

**Location**: `src/langlearn/managers/`

| **Manager** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`DeckManager`** | `deck_manager.py` | High-level deck orchestration with subdeck management and export coordination. Bridges between platform layer and infrastructure backends for complete deck lifecycle management. |
| **`MediaManager`** | `media_manager.py` | Media asset coordination across infrastructure services with deduplication and optimization. Provides unified interface for all media operations with intelligent caching strategies. |

### Application Entry Points

**Location**: `src/langlearn/`

| **Component** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`main.py`** | `main.py` | Primary application entry point with command-line interface. Coordinates deck generation workflow with user feedback and comprehensive error handling. |

---

## Quality Metrics

### Architecture Compliance

- **✅ Layer Separation**: No circular dependencies between Infrastructure/Platform/Languages
- **✅ Protocol Compliance**: All language implementations properly implement platform protocols
- **✅ Single Responsibility**: Each component has one clear, well-defined purpose
- **✅ Open-Closed Principle**: Infrastructure closed for modification, languages open for extension

### Testing Coverage

- **Unit Tests**: 672 tests covering all layers with comprehensive mocking of external dependencies
- **Integration Tests**: 19 tests for end-to-end pipeline validation with live service integration
- **Protocol Tests**: Dedicated test suites ensuring language implementations comply with platform contracts

### Code Quality

- **Type Safety**: MyPy strict mode with zero type errors across 163 source files
- **Linting**: Ruff with zero violations, consistent code style across all layers
- **Documentation**: Comprehensive docstrings and architectural documentation for all components

---

## Extension Guidelines

### Adding New Languages

1. **Implement Domain Models**: Extend platform protocols (`MediaGenerationCapable`)
2. **Create Record Classes**: Extend platform `BaseRecord` for data validation
3. **Build Language Services**: Implement `CardProcessorProtocol` and `TTSConfig`
4. **Register with Platform**: Add to language discovery system

### Adding New Infrastructure Services

1. **Define Clear Interface**: Create protocol or abstract base class
2. **Implement Service**: Add to `infrastructure/services/`
3. **Update ServiceContainer**: Add dependency injection support
4. **Integrate with Platform**: Connect to orchestration layer

### Adding New Platform Features

1. **Design Extension Points**: Create protocols for language implementation
2. **Build Orchestration Logic**: Add to platform layer
3. **Update Documentation**: Document new extension capabilities
4. **Provide Examples**: Show usage in existing language implementations

The Infrastructure/Platform/Languages architecture enables clean separation of concerns while providing powerful extension capabilities for new languages and features.