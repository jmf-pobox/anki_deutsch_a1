# Single Responsibility Principle - Codebase Inventory

This document provides a comprehensive inventory of the German A1 vocabulary deck generator codebase, organized by the Single Responsibility Principle (SRP). Each component has been analyzed for its specific responsibility and adherence to clean architecture principles.

## Architecture Overview

The langlearn codebase follows clean architecture with clear separation of concerns across distinct layers: **Domain Models**, **Business Services**, **Infrastructure Backends**, **Orchestration Managers**, **Presentation Cards**, and **Cross-cutting Utils**. The architecture enables flexible German language learning content generation with strong type safety and extensibility.

---

## 📁 Package Structure and Responsibilities

### `/src/langlearn/` - Root Package
**Primary Responsibility**: Top-level namespace for the German language learning Anki deck generation system. Coordinates all subsystems for creating vocabulary learning materials with German-specific grammar rules and media integration.

---

### 🏗️ `/src/langlearn/languages/german/models/` - German Domain Models Layer

**Package Responsibility**: Contains modern Python dataclass-based domain models representing German vocabulary with language-specific validation and behavior. Features MediaGenerationCapable protocol compliance that encapsulates German grammar rules and linguistic expertise.

#### Core German Vocabulary Models

| **Class** | **File** | **Single Responsibility** |
|-----------|----------|---------------------------|
| **`Noun`** | `languages/german/models/noun.py` | Dataclass representing German nouns with article/gender, plural forms, and case information. Implements MediaGenerationCapable with `get_combined_audio_text()`, `is_concrete()`, and `get_image_search_strategy()` methods for German-specific media generation. |
| **`Adjective`** | `languages/german/models/adjective.py` | Dataclass handling German adjectives with comparative/superlative forms and declension validation. MediaGenerationCapable with `get_combined_audio_text()`, `validate_comparative()`, and `validate_superlative()` methods. |
| **`Adverb`** | `languages/german/models/adverb.py` | Dataclass modeling German adverbs with type classification (time, place, manner, degree). MediaGenerationCapable with `AdverbType` enum for categorization and context-aware media generation. |
| **`Negation`** | `languages/german/models/negation.py` | Dataclass representing German negation patterns and words (nicht, kein, nie, etc.). MediaGenerationCapable with `NegationType` enum and position validation for German syntax rules. |

#### Verb Hierarchy (German Verb System)

| **Class** | **File** | **Single Responsibility** |
|-----------|----------|---------------------------|
| **`Verb`** | `languages/german/models/verb.py` | Dataclass for German verbs with conjugation patterns, tense forms, and auxiliary selection. MediaGenerationCapable with comprehensive German verb validation and pronunciation support. |

#### Grammar and Function Words

| **Class** | **File** | **Single Responsibility** |
|-----------|----------|---------------------------|
| **`Article`** | `languages/german/models/article.py` | Dataclass for German articles with case/gender declensions. MediaGenerationCapable with article-specific formatting and context generation. |
| **`Preposition`** | `languages/german/models/preposition.py` | Dataclass for German prepositions with case governance (Akkusativ, Dativ, Genitiv) and two-way preposition logic. MediaGenerationCapable with relationship-based image search and pronunciation support. |
| **`Phrase`** | `languages/german/models/phrase.py` | Dataclass for German phrases and expressions with contextual usage information. MediaGenerationCapable with situational media generation and communicative function support. |

### 📋 `/src/langlearn/languages/german/records/` - German Record Types

**Package Responsibility**: Pydantic-based record classes for CSV data validation and transport. Contains 15+ German-specific record types with validation rules.

#### Key Record Classes

| **Class** | **File** | **Single Responsibility** |
|-----------|----------|---------------------------|
| **`BaseRecord`** | `languages/german/records/base.py` | Abstract base for all German record types with common validation patterns. |
| **`GermanRecordFactory`** | `languages/german/records/factory.py` | Factory for creating appropriate record types from CSV data with German-specific validation. |
| **`NounRecord`** | `languages/german/records/noun_record.py` | Pydantic model for German noun CSV data with article validation. |
| **`VerbRecord`** | `languages/german/records/verb_record.py` | Pydantic model for German verb CSV data with conjugation patterns. |
| **`AdjectiveRecord`** | `languages/german/records/adjective_record.py` | Pydantic model for German adjective CSV data with comparative/superlative forms. |

### 🔄 `/src/langlearn/models/` - Backward Compatibility Layer

**Package Responsibility**: Provides backward compatibility imports from German-specific packages. Contains only `__init__.py` with re-exports for legacy code compatibility.

#### **REMOVED Legacy Architecture** ❌

**Migration Completed (2025-09-02)**: All domain models migrated from Pydantic to modern Python patterns.

*Legacy Components Eliminated:*
- ~~`FieldProcessor` interface~~ → Replaced by Clean Pipeline Architecture
- ~~`ModelFactory` class~~ → Eliminated factory pattern, direct protocol compliance
- ~~Pydantic BaseModel inheritance~~ → Migrated to @dataclass + MediaGenerationCapable
- ~~Dual inheritance (BaseModel + FieldProcessor)~~ → Single MediaGenerationCapable protocol
- ~~Metaclass conflicts~~ → Resolved with protocol-based design

*Legacy Domain Models Removed (2025-08-30):*
- ~~`RegularVerb`, `IrregularVerb`, `SeparableVerb`~~ → Replaced by VerbConjugationRecord
- ~~`Conjunction`, `Interjection`~~ → Not used in production 
- ~~`PersonalPronoun`, `PossessivePronoun`, `OtherPronoun`~~ → Not used in production
- ~~`CardinalNumber`, `OrdinalNumber`~~ → Not used in production

---

### ⚙️ `/src/langlearn/services/` - Business Logic Layer

**Package Responsibility**: Contains business logic services and external API integrations. Each service handles one specific capability while maintaining clean boundaries and single responsibilities.

#### External API Integration Services

| **Service** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`AudioService`** | `audio.py` | Integrates with AWS Polly for German text-to-speech generation. Handles audio file creation, caching, and German pronunciation optimization. |
| **`PexelsService`** | `pexels_service.py` | Manages Pexels API integration for vocabulary image search and download. Implements rate limiting, error handling, and image optimization. |
| **`AnthropicService`** | `anthropic_service.py` | Provides AI-powered content enhancement and validation using Anthropic's Claude API for German language processing. |

#### Data and Content Services

| **Service** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`CSVService`** | `csv_service.py` | Generic CSV reading with automatic Pydantic model conversion and validation. Provides type-safe data loading from vocabulary files. |
| **`MediaService`** | `media_service.py` | Orchestrates audio and image generation with intelligent caching, deduplication, and batch processing. Coordinates between AudioService and PexelsService. |
| **`TemplateService`** | `template_service.py` | Manages Anki card template loading, caching, and NoteType creation. Handles HTML/CSS template files and card formatting. |
| **`CardBuilder`** | `card_builder.py` | Transforms enriched records into formatted Anki cards with appropriate templates and field mappings. Core service for card generation. |
| **`MediaEnricher`** | `media_enricher.py` | Orchestrates Records → Domain Models conversion and media generation with existence checking and caching. |
| **`RecordMapper`** | `record_mapper.py` | Maps CSV data to appropriate Record types using factory patterns and validation. |
| **`DomainMediaGenerator`** | `domain_media_generator.py` | Adapter that provides MediaGenerator interface to domain models, bridging clean domain interfaces with existing service layer. |
| **`MediaFileRegistrar`** | `media_file_registrar.py` | Manages media file registration and tracking for deck generation. |

#### German-Specific Services

| **Service** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`ArticleApplicationService`** | `article_application_service.py` | Applies German article rules and patterns to vocabulary items. |
| **`ArticlePatternProcessor`** | `article_pattern_processor.py` | Processes German article patterns and validates grammatical correctness. |
| **`GermanExplanationFactory`** | `german_explanation_factory.py` | Creates German-specific explanations and contextual information for vocabulary. |
| **`VerbConjugationProcessor`** | `verb_conjugation_processor.py` | Handles German verb conjugation patterns and tense processing. |

#### Infrastructure Services

| **Service** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`ServiceContainer`** | `service_container.py` | Dependency injection container for managing service instances and configurations. |
| **`TranslationService`** | `translation_service.py` | Translation services using AI providers for content enhancement. |
| **`RecordToModelFactory`** | `record_to_model_factory.py` | Factory service for converting Record objects to Domain Models. |

---

### 🔧 `/src/langlearn/backends/` - Infrastructure Layer

**Package Responsibility**: Anki deck generation backend infrastructure with Strategy pattern foundation. Currently provides one concrete implementation of the deck generation interface.

#### Backend Implementation Classes

| **Backend** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`DeckBackend`** | `base.py:70` | Abstract base class defining the interface for all deck generation backends. Includes supporting classes `MediaFile`, `CardTemplate`, and `NoteType`. |
| **`AnkiBackend`** | `anki_backend.py:44` | **Only concrete implementation** - uses the official Anki library with full collection management and advanced features. Includes Clean Pipeline Architecture with domain model delegation. |

---

### 🎯 `/src/langlearn/managers/` - Orchestration Layer

**Package Responsibility**: Higher-level orchestration components that coordinate multiple services while maintaining clean boundaries and avoiding implementation details.

#### Management Classes

| **Manager** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`DeckManager`** | `deck_manager.py:15` | Manages deck organization, subdeck hierarchy, naming conventions, and structural operations. Delegates actual deck operations to backends. |
| **`MediaManager`** | `media_manager.py:12` | Coordinates comprehensive media generation workflows across multiple services. Orchestrates audio, image, and metadata generation for vocabulary items. |

---

### 🃏 `/src/langlearn/cards/` - Presentation Layer **[REMOVED]**

**Status**: This package no longer exists in the current codebase. Card generation functionality has been integrated directly into the AnkiBackend using Clean Pipeline Architecture.

---

### 🛠️ `/src/langlearn/utils/` - Cross-Cutting Concerns

**Package Responsibility**: Utility classes and cross-cutting concerns that support the application without containing domain-specific logic.

#### Utility Classes

| **Utility** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`Environment utilities`** | `environment.py` | Environment setup and configuration utilities. |

#### Support Scripts (in `/scripts/`)

| **Script** | **File** | **Single Responsibility** |
|------------|----------|---------------------------|
| **`CredentialManager`** | `api_keyring.py:15` | Secure API key management using the system keyring. Provides encrypted credential storage for AWS, Pexels, and other external services. |
| **`sync_api_key.py`** | `sync_api_key.py:1` | Synchronizes API keys from secure keyring to environment variables for development workflows. |
| **`test_api_key.py`** | `test_api_key.py:1` | Validates API key functionality and connectivity for external services during setup and troubleshooting. |

---


## 🏛️ Root Level Components

### Primary Application Classes

| **Component** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`GermanDeckBuilder`** | `deck_builder.py:20` | High-level orchestrator and main public API for comprehensive German vocabulary deck creation. Coordinates all subsystems while providing a clean, user-friendly interface. |
| **`AnkiDeckGenerator`** | `generator.py:25` | Legacy deck generator class (being phased out). Provides backward compatibility during migration to the new architecture. |
| **`main`** | `main.py:10` | Application entry point and command-line interface. Coordinates initialization, configuration, and execution of the deck building process. |

---

## 🎨 `/src/langlearn/examples/` - Usage Examples **[REMOVED]**

**Status**: This package no longer exists in the current codebase. Example usage is documented in CLAUDE.md and the main application entry point demonstrates usage patterns.

---

## 📊 Architecture Quality Assessment

### ✅ Single Responsibility Principle Adherence: **EXCELLENT**

- **Domain Models**: Each model represents exactly one German part of speech with its specific grammar rules and behavior
- **Services**: Each service handles precisely one external integration or business capability  
- **Backends**: Clean abstraction with single implementations per Anki library
- **Managers**: Focused orchestration without mixing implementation details
- **Cards**: Type-specific card generation with shared base functionality

### ✅ Separation of Concerns: **EXCELLENT**

- **Clear Layer Boundaries**: Domain → Services → Infrastructure → Orchestration → Presentation
- **Proper Dependency Direction**: Higher-level components depend on abstractions, not concrete implementations
- **External Integration Isolation**: All external APIs cleanly isolated in the services layer

### 🎯 Key Design Patterns Implemented

1. **Strategy Pattern**: Backend abstraction enables switching between genanki and official Anki library implementations
2. **Template Method Pattern**: BaseCardGenerator provides common workflow with type-specific implementations  
3. **Dependency Injection**: Services and backends are injected rather than hard-coded dependencies
4. **Repository Pattern**: CSVService acts as a data repository with automatic model conversion
5. **Facade Pattern**: GermanDeckBuilder provides a simplified interface to the complex subsystem
6. **Domain-Driven Design**: Rich domain models with German language behavior, not anemic data containers

### 🏆 Architecture Strengths

- **Type Safety**: Comprehensive use of Pydantic models, generics, and Python typing
- **German Language Focus**: Domain models capture German-specific grammar rules and linguistic patterns
- **Media Integration**: Sophisticated audio/image generation with intelligent caching and deduplication  
- **Backend Flexibility**: Clean abstraction supports multiple Anki deck generation libraries
- **Rich Domain Models**: Models contain behavior and business logic, not just data
- **Clean Interfaces**: All public interfaces are focused, minimal, and purpose-built

### 📈 Maintainability Indicators

- **Low Coupling**: Components interact through well-defined interfaces
- **High Cohesion**: Each class and module has a single, clear purpose  
- **Testability**: Clear separation enables easy unit testing of individual components
- **Extensibility**: New German word types or backends can be added without modifying existing code
- **Readability**: Component responsibilities are immediately clear from naming and organization

This codebase demonstrates exemplary adherence to the Single Responsibility Principle with excellent separation of concerns, making it maintainable, testable, and extensible for German language learning applications.