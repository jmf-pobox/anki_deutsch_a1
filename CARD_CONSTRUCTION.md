# Card Construction Architecture Analysis

## Current State Analysis

### Current Flow (Problematic)
```
CSV Data → Raw Fields → Domain Model Creation → Field Processing → Media Generation → Cards
```

The current architecture has several architectural problems:

1. **Domain Models as Infrastructure**: Domain models (Noun, Adjective, etc.) are handling field processing and media generation, violating single responsibility principle
2. **Existence Checks in Domain Logic**: Image existence checks scattered throughout domain models
3. **Mixed Responsibilities**: Domain models contain both business logic (German grammar validation) AND infrastructure concerns (media file paths, field formatting)
4. **Testing Complexity**: Tests need complex fixtures to hide existing files to test generation paths
5. **Performance Hacks**: Image existence checks added as band-aids rather than proper architectural solution

### Current Architecture Issues

**Domain Model Pollution:**
```python
# This should NOT be in a domain model
def process_fields_for_media_generation(self, fields, media_generator):
    # Domain models shouldn't know about file paths or media generation
    expected_image_path = Path(f"data/images/{word.lower()}.jpg")  # WRONG
    if expected_image_path.exists():  # WRONG
        processed_fields[5] = format_media_reference(...)  # WRONG
```

**Responsibilities Violation:**
- Domain models handle German grammar validation ✅ (correct)
- Domain models handle CSV field processing ❌ (infrastructure)
- Domain models check file system for existing media ❌ (infrastructure)
- Domain models format media references ❌ (presentation)

## Proposed Solutions

## Solution 1: Clean Pipeline Architecture

### Architecture
```
CSV Data → Raw Records → Domain Models → Enriched Records → Cards
    ↓           ↓            ↓              ↓           ↓
CSVLoader → RecordMapper → Validator → MediaEnricher → CardBuilder
```

### Flow Description
1. **CSVLoader**: Pure CSV parsing, returns raw field arrays
2. **RecordMapper**: Converts field arrays to structured records (not domain models)
3. **Domain Models**: Pure business logic for validation and grammar rules
4. **MediaEnricher**: Infrastructure service that checks existing media and generates missing media
5. **CardBuilder**: Assembles final cards with all data

### Implementation Structure
```python
# Pure domain models (no infrastructure)
class Noun:
    word: str
    article: str
    english: str
    
    def validate_article(self) -> bool:
        """Pure business logic only"""
        return self.article in ["der", "die", "das"]
    
    def is_concrete(self) -> bool:
        """Domain logic for concreteness"""
        # Grammar-based logic only

# Infrastructure services
class MediaEnricher:
    def enrich_record(self, record: dict, domain_model: Noun) -> dict:
        """Add media to record based on business rules"""
        if self._should_generate_image(domain_model):
            if not self._image_exists(record['word']):
                record['image'] = self._generate_image(domain_model)
            else:
                record['image'] = self._load_existing_image(record['word'])
        return record

# Clean card construction
class CardBuilder:
    def build_card(self, enriched_record: dict) -> Card:
        """Pure assembly logic"""
        return Card(fields=enriched_record)
```

### Pros
- **Clear Separation**: Domain models handle only business logic
- **Testable**: Each component can be tested independently
- **Performance**: MediaEnricher handles all existence checks in one place
- **Maintainable**: Changes to media handling don't affect domain models
- **Extensible**: Easy to add new enrichment steps

### Cons
- **More Components**: Additional classes to maintain
- **Data Transformation**: Multiple transformations between layers
- **Potential Over-engineering**: May be complex for simple use cases

## Solution 2: Factory Pattern with Enrichment Strategy

### Architecture
```
CSV Data → CardFactory.create() → [Domain Model + Enrichment Strategy] → Cards
```

### Flow Description
1. **CardFactory**: Central factory that coordinates card creation
2. **Domain Models**: Pure business logic only
3. **Enrichment Strategies**: Pluggable strategies for different media types
4. **Card Assembly**: Factory assembles final cards

### Implementation Structure
```python
# Pure domain models
class Noun:
    word: str
    article: str
    english: str
    
    def get_search_terms(self) -> str:
        """Return business-logic driven search terms"""
        if self.is_concrete():
            return self.english
        return self._get_abstract_concept_terms()

# Strategy pattern for enrichment
class MediaEnrichmentStrategy(ABC):
    @abstractmethod
    def enrich(self, domain_model, base_fields: dict) -> dict:
        pass

class NounMediaStrategy(MediaEnrichmentStrategy):
    def __init__(self, media_service: MediaService):
        self._media_service = media_service
    
    def enrich(self, noun: Noun, base_fields: dict) -> dict:
        enriched = base_fields.copy()
        
        # Check existing media first
        if not self._media_service.image_exists(noun.word):
            search_terms = noun.get_search_terms()  # Domain logic
            enriched['image'] = self._media_service.generate_image(search_terms)
        else:
            enriched['image'] = self._media_service.load_image(noun.word)
            
        return enriched

# Factory coordinates everything
class CardFactory:
    def create_noun_card(self, csv_fields: list[str]) -> Card:
        # Create domain model for validation
        noun = Noun.from_fields(csv_fields)
        noun.validate()  # Pure domain logic
        
        # Create base record
        base_fields = self._fields_to_dict(csv_fields)
        
        # Apply enrichment strategy
        strategy = self._strategy_registry.get_strategy('noun')
        enriched_fields = strategy.enrich(noun, base_fields)
        
        # Build final card
        return Card(fields=enriched_fields)
```

### Pros
- **Strategy Pattern**: Pluggable enrichment strategies
- **Factory Coordination**: Single point of creation logic
- **Domain Purity**: Domain models stay clean
- **Flexible**: Easy to swap enrichment strategies

### Cons
- **Factory Complexity**: Factory might become large
- **Strategy Overhead**: May be overkill for simple cases
- **Coupling**: Factory needs to know about all strategies

## Solution 3: Current Architecture (For Comparison)

### Current Implementation
```python
class Noun(BaseModel, FieldProcessor):
    """Domain model that also handles infrastructure"""
    
    def process_fields_for_media_generation(self, fields, media_generator):
        # Domain model doing infrastructure work
        expected_image_path = Path(f"data/images/{word.lower()}.jpg")  # FILE SYSTEM
        if expected_image_path.exists():  # FILE SYSTEM CHECK
            processed_fields[6] = format_media_reference(...)  # FORMATTING
        else:
            search_terms = self.get_image_search_terms()  # BUSINESS LOGIC
            image_path = media_generator.generate_image(...)  # INFRASTRUCTURE
```

### Current Pros
- **Simple**: Everything in one place
- **Direct**: No extra layers or transformations
- **Working**: Currently functional for basic use cases

### Current Cons
- **Responsibility Violation**: Domain models handle infrastructure
- **Testing Complexity**: Need to mock file system and media generation
- **Performance Hacks**: Existence checks scattered throughout
- **Maintenance Issues**: Changes to media handling affect domain models
- **Poor Separation**: Business and infrastructure logic mixed
- **Hard to Extend**: Adding new media types requires changing domain models

## Comparison Matrix

| Aspect | Current | Solution 1: Pipeline | Solution 2: Factory |
|--------|---------|---------------------|-------------------|
| **Separation of Concerns** | ❌ Poor | ✅ Excellent | ✅ Good |
| **Testability** | ❌ Complex | ✅ Excellent | ✅ Good |
| **Performance** | ❌ Requires hacks | ✅ Clean | ✅ Clean |
| **Maintainability** | ❌ Poor | ✅ Excellent | ✅ Good |
| **Complexity** | ✅ Simple | ❌ Higher | 🟡 Medium |
| **Extensibility** | ❌ Difficult | ✅ Excellent | ✅ Good |
| **Domain Model Purity** | ❌ Polluted | ✅ Pure | ✅ Pure |

## Recommendation

**Recommended Solution: Solution 1 (Clean Pipeline Architecture)**

### Rationale
1. **Best Separation**: Cleanest separation between domain logic and infrastructure
2. **Most Testable**: Each component can be tested independently without complex mocking
3. **Performance by Design**: MediaEnricher naturally handles existence checks efficiently
4. **Future-Proof**: Easy to add new enrichment steps (audio, images, AI enhancements)
5. **Maintainable**: Changes to media handling isolated from domain models

### Migration Strategy
1. **Phase 1**: Extract MediaEnricher service from domain models
2. **Phase 2**: Create clean RecordMapper for CSV → structured data
3. **Phase 3**: Clean up domain models to be pure business logic
4. **Phase 4**: Implement CardBuilder for final assembly
5. **Phase 5**: Remove field processing from domain models entirely

### Key Benefits of Recommended Solution
- **Domain models become pure**: Only German grammar and language rules
- **Performance naturally good**: MediaEnricher checks all media existence once
- **Tests become simple**: No need to hide existing files or complex mocking
- **Easy to extend**: Want to add video? Add to MediaEnricher, domain models unchanged
- **Clear data flow**: Each step has single responsibility

The current architecture's main problem is that domain models are doing infrastructure work. The solution isn't to add more hacks, but to properly separate concerns so each component has a single, clear responsibility.