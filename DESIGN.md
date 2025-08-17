# DESIGN.md - Original Architecture Analysis

This document analyzes the original well-designed architecture of the German A1 Anki deck project to understand what the intended design patterns and principles were.

## Executive Summary

The original codebase demonstrates excellent software engineering principles with clear separation of concerns, proper abstraction layers, and adherence to SOLID principles. The architecture follows a **domain-driven design** approach with **service-oriented architecture** patterns.

## Core Architectural Principles

### 1. Separation of Concerns (SoC)
The original design clearly separates different responsibilities:

- **Data Models** (`src/langlearn/models/`): Pure Pydantic models handling validation and data structure
- **Services** (`src/langlearn/services/`): External API integrations and business logic
- **Utilities** (`src/langlearn/utils/`): Generic helper functions and enrichment operations
- **Backend Abstraction** (`src/langlearn/backends/`): Deck generation interface abstraction
- **Card Generators** (`src/langlearn/cards/`): Specialized card creation logic

### 2. Abstract Base Classes and Polymorphism

**Backend Abstraction Layer** (`src/langlearn/backends/base.py`):
```python
class DeckBackend(ABC):
    @abstractmethod
    def create_note_type(self, note_type: NoteType) -> str: ...
    
    @abstractmethod  
    def add_note(self, note_type_id: str, fields: list[str], tags: list[str] | None = None) -> None: ...
```

This demonstrates **Strategy Pattern** - different deck generation strategies (genanki, official Anki) can be swapped without changing client code.

**Card Generator Abstraction** (`src/langlearn/cards/base.py`):
```python
class BaseCardGenerator(ABC):
    @abstractmethod
    def create_note(self, data: Any) -> genanki.Note: ...
```

This follows **Template Method Pattern** - common card creation structure with specialized implementations.

### 3. Generic, Reusable Components

**CSV Service** (`src/langlearn/services/csv_service.py`):
```python
def read_csv(self, file_path: Path, model_class: type[T]) -> list[T]:
    # Generic, type-safe CSV processing with Pydantic validation
```

This demonstrates **Generic Programming** - works with any Pydantic model type, not hard-coded to specific data structures.

**Audio Enricher** (`src/langlearn/utils/audio_enricher.py`):
```python
class AudioEnricher:
    def enrich_adjectives(self, csv_file: Path) -> None:
        # Specific to adjectives but uses generic services
```

This follows **Single Responsibility Principle** - each enricher handles one data type but delegates to reusable services.

### 4. Data Model Excellence

**Pydantic Models with German-Specific Validation** (`src/langlearn/models/adjective.py`):
```python
class Adjective(BaseModel):
    word: str = Field(..., description="The German adjective")
    english: str = Field(..., description="English translation")
    
    def validate_comparative(self) -> bool:
        # German grammar validation logic
        irregular_comparatives = {
            "gut": "besser",
            "viel": "mehr",
            # ...
        }
```

This demonstrates:
- **Domain-Driven Design** - models encode German language rules
- **Validation at the boundary** - data integrity enforced at model level
- **Self-documenting code** - field descriptions provide context

### 5. Service Layer Pattern

**Audio Service** (`src/langlearn/services/audio.py`):
- Encapsulates AWS Polly integration
- Handles file naming, caching, error handling
- No German-specific logic - pure technical service

**CSV Service** (`src/langlearn/services/csv_service.py`):
- Generic data loading with proper error handling
- Type-safe with generics
- Logging and monitoring built-in

### 6. Configuration-Driven Approach

**Template System** (`src/langlearn/templates/`):
- HTML/CSS templates stored as files
- Separates presentation from logic
- Easy to modify without code changes

**Backend Demonstration** (`examples/backend_demonstration.py`):
```python
def create_sample_note_type() -> NoteType:
    template = CardTemplate(
        name="German Adjective",
        front_html="""...""",  # Configurable templates
        css="""..."""
    )
```

This follows **Configuration over Convention** - templates are data, not code.

## Intended Architecture Layers

```
┌─────────────────────────────────────────────┐
│                Application Layer             │
│  (create_deck.py, examples/, scripts)       │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│              Domain Layer                   │
│  (models/, cards/, business logic)          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Service Layer                    │
│  (services/, backend abstraction)           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Infrastructure Layer               │
│  (utils/, external APIs, file I/O)          │
└─────────────────────────────────────────────┘
```

### Application Layer
- **Orchestration**: Coordinates domain and service layers
- **Configuration**: Loads CSV files, creates note types
- **User Interface**: CLI scripts and examples

### Domain Layer  
- **Models**: German language domain objects with validation
- **Card Generators**: Business logic for different card types
- **Business Rules**: German grammar validation, formatting rules

### Service Layer
- **Backend Abstraction**: Polymorphic deck generation interfaces
- **External Services**: API integrations (AWS Polly, Pexels)
- **Data Access**: CSV reading with generic type handling

### Infrastructure Layer
- **Utilities**: Generic helper functions
- **File Management**: Path handling, media organization
- **API Clients**: Low-level external service interaction

## Design Patterns Identified

### 1. Strategy Pattern
**Backend abstraction** allows switching between genanki and official Anki libraries without changing application code.

### 2. Template Method Pattern
**BaseCardGenerator** defines the card creation skeleton, with concrete implementations filling in specific details.

### 3. Factory Pattern
**Note type creation functions** encapsulate the complex process of creating card templates.

### 4. Service Locator Pattern
**Services are injected** rather than hard-coded, allowing for testability and flexibility.

### 5. Repository Pattern
**CSV Service** abstracts data access, making it easy to switch data sources.

## Key Design Decisions

### 1. Type Safety with Generics
```python
T = TypeVar("T")
def read_csv(self, file_path: Path, model_class: type[T]) -> list[T]:
```
This ensures compile-time type checking and prevents runtime errors.

### 2. Validation at Boundaries
Pydantic models validate data when entering the system, preventing invalid data from propagating.

### 3. Dependency Injection
Services are passed as constructor parameters rather than created internally, improving testability.

### 4. Configuration Externalization
Templates, CSS, and other configuration stored as files rather than embedded in code.

### 5. Logging and Monitoring
Comprehensive logging throughout the service layer for debugging and monitoring.

## Contrast with Current Implementation Problems

The original design **avoids** all the problems identified in DESIGN-REVIEW.md:

❌ **Problem**: Monolithic AnkiBackend class (1800+ lines)  
✅ **Solution**: Separate concerns into models, services, cards, and backends

❌ **Problem**: Hard-coded German pattern matching  
✅ **Solution**: Domain models with configurable validation rules

❌ **Problem**: Tight coupling between media generation and deck creation  
✅ **Solution**: Service layer abstraction with dependency injection

❌ **Problem**: Non-extensible card templates  
✅ **Solution**: Template files with configurable HTML/CSS

❌ **Problem**: Inflexible configuration  
✅ **Solution**: Configuration-driven approach with external files

## Intended Usage Pattern

### 1. Application Layer Creates Domain Objects
```python
# Load and validate data
adjectives = csv_service.read_csv(csv_path, Adjective)

# Create domain-specific card generators
card_generator = AdjectiveCardGenerator(template_service, audio_service)
```

### 2. Domain Objects Handle Business Logic
```python
# Validation happens at the domain level
for adj in adjectives:
    if adj.validate_comparative():
        card = card_generator.create_note(adj)
```

### 3. Services Handle External Concerns  
```python
# Services are injected and configurable
audio_service = AudioService(voice="Vicki", sample_rate=16000)
backend = AnkiBackend(deck_name, description)
```

### 4. Clean Extension Points
```python
# New card types added by extending base classes
class NounCardGenerator(BaseCardGenerator):
    def create_note(self, noun: Noun) -> genanki.Note:
        # Noun-specific logic only
```

## Conclusion

The original architecture demonstrates **production-quality software engineering practices**:

- **Modular design** with clear boundaries
- **Extensibility** through abstract base classes
- **Testability** through dependency injection
- **Maintainability** through separation of concerns
- **Type safety** through generic programming
- **Configuration flexibility** through external templates

The current implementation should be refactored to restore these architectural principles, eliminating the monolithic AnkiBackend class and restoring the clean separation of concerns that made the original code base maintainable and extensible.