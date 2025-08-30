# Single Responsibility Principle - Codebase Inventory

This document provides a comprehensive inventory of the German A1 vocabulary deck generator codebase, organized by the Single Responsibility Principle (SRP). Each component has been analyzed for its specific responsibility and adherence to clean architecture principles.

## Architecture Overview

The langlearn codebase follows clean architecture with clear separation of concerns across distinct layers: **Domain Models**, **Business Services**, **Infrastructure Backends**, **Orchestration Managers**, **Presentation Cards**, and **Cross-cutting Utils**. The architecture enables flexible German language learning content generation with strong type safety and extensibility.

---

## 📁 Package Structure and Responsibilities

### `/src/langlearn/` - Root Package
**Primary Responsibility**: Top-level namespace for the German language learning Anki deck generation system. Coordinates all subsystems for creating vocabulary learning materials with German-specific grammar rules and media integration.

---

### 🏗️ `/src/langlearn/models/` - Domain Models Layer

**Package Responsibility**: Contains Pydantic domain models representing German vocabulary with language-specific validation and behavior. These are rich domain models that encapsulate German grammar rules, not just data containers.

#### Core German Vocabulary Models

| **Class** | **File** | **Single Responsibility** |
|-----------|----------|---------------------------|
| **`Noun`** | `noun.py:6` | Represents German nouns with article/gender, plural forms, and case information. Provides `get_combined_audio_text()`, `is_concrete()`, and `get_image_search_terms()` methods for German-specific processing. |
| **`Adjective`** | `adjective.py:6` | Handles German adjectives with comparative/superlative forms and declension validation. Includes `get_combined_audio_text()`, `validate_comparative()`, and `validate_superlative()` methods. |
| **`Adverb`** | `adverb.py:6` | Models German adverbs with type classification (time, place, manner, degree). Includes `AdverbType` enum for categorization. |
| **`Negation`** | `negation.py:6` | Represents German negation patterns and words (nicht, kein, nie, etc.). Includes `NegationType` enum for different negation categories. |

#### Verb Hierarchy (German Verb System)

| **Class** | **File** | **Single Responsibility** |
|-----------|----------|---------------------------|
| **`Verb`** | `verb.py:6` | Abstract base class for German verbs with common conjugation fields and validation methods. |
| **`RegularVerb`** | `regular_verb.py:6` | Handles regular German verb conjugation patterns with standard -en, -t, -st endings. |
| **`IrregularVerb`** | `irregular_verb.py:6` | Manages irregular German verbs with non-standard conjugation patterns and stem changes. |
| **`SeparableVerb`** | `separable_verb.py:6` | Specialized handling for German separable prefix verbs (aufstehen → ich stehe auf). |

#### Grammar and Function Words

| **Class** | **File** | **Single Responsibility** |
|-----------|----------|---------------------------|
| **`Preposition`** | `preposition.py:6` | German prepositions with case dependency (Akkusativ, Dativ, Genitiv) information. |
| **`Conjunction`** | `conjunction.py:6` | German conjunctions and their syntactic behavior for sentence construction. |
| **`Interjection`** | `interjection.py:6` | German interjections and exclamations with contextual usage information. |
| **`PersonalPronoun`** | `personal_pronoun.py:6` | German personal pronouns with complete case/gender declension tables. |
| **`PossessivePronoun`** | `possessive_pronoun.py:6` | German possessive pronouns with agreement rules for gender and case. |
| **`OtherPronoun`** | `other_pronoun.py:6` | Miscellaneous German pronouns (demonstrative, interrogative, indefinite). |
| **`CardinalNumber`** | `cardinal_number.py:6` | German cardinal numbers (1, 2, 3...) with spelling and usage rules. |
| **`OrdinalNumber`** | `ordinal_number.py:6` | German ordinal numbers (1st, 2nd, 3rd...) with proper German endings. |

---

### ⚙️ `/src/langlearn/services/` - Business Logic Layer

**Package Responsibility**: Contains business logic services and external API integrations. Each service handles one specific capability while maintaining clean boundaries and single responsibilities.

#### External API Integration Services

| **Service** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`AudioService`** | `audio.py:10` | Integrates with AWS Polly for German text-to-speech generation. Handles audio file creation, caching, and German pronunciation optimization. |
| **`PexelsService`** | `pexels_service.py:15` | Manages Pexels API integration for vocabulary image search and download. Implements rate limiting, error handling, and image optimization. |
| **`AnthropicService`** | `anthropic_service.py:8` | Provides AI-powered content enhancement and validation using Anthropic's Claude API for German language processing. |

#### Data and Content Services

| **Service** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`CSVService`** | `csv_service.py:12` | Generic CSV reading with automatic Pydantic model conversion and validation. Provides type-safe data loading from vocabulary files. |
| **`MediaService`** | `media_service.py:20` | Orchestrates audio and image generation with intelligent caching, deduplication, and batch processing. Coordinates between AudioService and PexelsService. |
| **`TemplateService`** | `template_service.py:13` | Manages Anki card template loading, caching, and NoteType creation. Handles HTML/CSS template files and card formatting. |
| **`GermanLanguageService`** | `german_language_service.py:26` | Provides German-specific language processing including context extraction, grammar validation, and linguistic analysis for enhanced media search. |

---

### 🔧 `/src/langlearn/backends/` - Infrastructure Layer  

**Package Responsibility**: Anki deck generation backend implementations using the Strategy pattern. Provides clean abstraction over different Anki libraries while maintaining identical interfaces.

#### Backend Implementation Classes

| **Backend** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`DeckBackend`** | `base.py:15` | Abstract base class defining the interface for all deck generation backends. Includes supporting classes `MediaFile`, `CardTemplate`, and `NoteType`. |
| **`GenankiBackend`** | `genanki_backend.py:21` | Concrete implementation using the genanki library for Anki deck generation. Handles genanki-specific API calls and media packaging. |
| **`AnkiBackend`** | `anki_backend.py:26` | Concrete implementation using the official Anki library with full collection management and advanced features. |

---

### 🎯 `/src/langlearn/managers/` - Orchestration Layer

**Package Responsibility**: Higher-level orchestration components that coordinate multiple services while maintaining clean boundaries and avoiding implementation details.

#### Management Classes

| **Manager** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`DeckManager`** | `deck_manager.py:15` | Manages deck organization, subdeck hierarchy, naming conventions, and structural operations. Delegates actual deck operations to backends. |
| **`MediaManager`** | `media_manager.py:12` | Coordinates comprehensive media generation workflows across multiple services. Orchestrates audio, image, and metadata generation for vocabulary items. |

---

### 🃏 `/src/langlearn/cards/` - Presentation Layer

**Package Responsibility**: Type-specific Anki card generators that convert domain models into properly formatted Anki cards with appropriate templates and field mappings.

#### Card Generator Classes

| **Generator** | **File** | **Single Responsibility** |
|---------------|----------|---------------------------|
| **`BaseCardGenerator`** | `base.py:10` | Abstract generic base class providing common card generation infrastructure with type safety (`Generic[T]`). Defines the contract for all card generators. |
| **`NounCardGenerator`** | `noun.py:8` | Specialized card generation for German nouns with proper article display, plural forms, case information, and noun-specific media integration. |
| **`AdjectiveCardGenerator`** | `adjective.py:8` | Specialized card generation for German adjectives with comparative/superlative forms, declension examples, and adjective-specific formatting. |

#### 🔄 **Planned MVP Reintegration**

**Status**: Currently unused (bypassed by GermanDeckBuilder direct implementation)  
**Plan**: Reintegrate as MVP Presenter layer to eliminate god class anti-pattern

**Benefits of Reintegration**:
- **Eliminate Code Duplication**: 90% reduction in GermanDeckBuilder method sizes
- **Grammar Extensibility**: Add new word types with minimal code
- **Clean Architecture**: Proper separation between Models (domain), Views (templates), and Presenters (card generators)

(Historical note) MVP reintegration plan has been archived; see ENG-ARCHITECTURE.md and ENG-DEVELOPMENT-STANDARDS.md for current guidance.

---

### 🛠️ `/src/langlearn/utils/` - Cross-Cutting Concerns

**Package Responsibility**: Utility classes and cross-cutting concerns that support the application without containing domain-specific logic.

#### Utility Classes

| **Utility** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`CredentialManager`** | `api_keyring.py:15` | Secure API key management using the system keyring. Provides encrypted credential storage for AWS, Pexels, and other external services. |

#### Support Scripts

| **Script** | **File** | **Single Responsibility** |
|------------|----------|---------------------------|
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

## 🎨 `/src/langlearn/examples/` - Usage Examples

**Package Responsibility**: Demonstration code and usage examples for library consumers.

| **Example** | **File** | **Single Responsibility** |
|-------------|----------|---------------------------|
| **`create_sample_deck()`** | `create_sample_deck.py:5` | Demonstrates complete library usage with sample German vocabulary to help new users understand the API and workflow. |

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