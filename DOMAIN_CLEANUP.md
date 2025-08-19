# Domain Model Cleanup Plan

## Overview

This document outlines a comprehensive refactoring to separate domain concerns from presentation concerns in the German vocabulary learning application. The goal is to create pure domain models that focus solely on German language rules and grammar, while moving media generation and Anki-specific logic to appropriate presentation layers.

## Current Architecture Problems

### 1. **Domain Models Coupled to External Services**
```python
# PROBLEM: Domain models directly call external APIs
class Noun(BaseModel):
    def get_image_search_terms(self):
        service = AnthropicService()  # 🔴 Domain model calling external service
        return service.generate_pexels_query(self)
```

### 2. **Missing Card Abstraction**
- No explicit representation of Anki cards as distinct from domain words
- Media concerns mixed directly into domain models
- Field arrays passed around instead of typed objects

### 3. **Dual Media Generation Paths**
- Card generators handle media (primary path)
- Field processors handle media (fallback path)
- Confusing responsibility overlap

### 4. **Violation of Clean Architecture**
- Domain models depend on infrastructure
- Mixed concerns across layers
- Difficult to test domain logic in isolation

## Target Architecture

### **Clean Layer Separation**
```
Domain Layer:       Pure German language models (Noun, Adjective, etc.)
Presentation Layer: Anki-specific cards with media (NounCard, AdjectiveCard)
Infrastructure:     Media generation services (AWS Polly, Pexels, etc.)
Storage:           Anki backend persistence
```

### **Performance Characteristics**
- **Domain Object Creation**: Fast (pure data, no I/O)
- **Card Object Creation**: Expensive (media generation)
- **Clear Cost Model**: Expensive operations are explicit and contained

## Implementation Plan

### **Phase 1: Create Card Abstraction Layer** 
*Estimated Time: 4-6 hours*

#### 1.1 Create Base Card Classes
- [ ] Create `src/langlearn/cards/models/` directory
- [ ] Implement `BaseCard` abstract base class
- [ ] Define common card interface (`to_anki_fields()`, etc.)

#### 1.2 Implement Specific Card Types
- [ ] `NounCard` - Noun domain model + media references
- [ ] `AdjectiveCard` - Adjective domain model + media references  
- [ ] `AdverbCard` - Adverb domain model + media references
- [ ] `NegationCard` - Negation domain model + media references

#### 1.3 Card Model Structure
```python
@dataclass
class NounCard(BaseCard):
    """Anki card representation of a German noun with media."""
    noun: Noun  # Pure domain model
    image_path: str | None = None
    word_audio_path: str | None = None
    example_audio_path: str | None = None
    
    def to_anki_fields(self) -> list[str]:
        """Convert card to Anki field array for backend."""
        return [
            self.noun.noun,
            self.noun.article,
            self.noun.english,
            self.noun.plural, 
            self.noun.example,
            self.noun.related,
            self._format_image(),
            self._format_word_audio(),
            self._format_example_audio(),
        ]
```

### **Phase 2: Update Card Generators**
*Estimated Time: 6-8 hours*

#### 2.1 Refactor Card Generator Interface
- [ ] Update `BaseCardGenerator` to return `Card` objects
- [ ] Implement `create_card(domain_model) -> Card` pattern
- [ ] Move all media generation logic into card generators

#### 2.2 Update Specific Card Generators  
- [ ] `NounCardGenerator.create_card(noun: Noun) -> NounCard`
- [ ] `AdjectiveCardGenerator.create_card(adjective: Adjective) -> AdjectiveCard`
- [ ] `AdverbCardGenerator.create_card(adverb: Adverb) -> AdverbCard`
- [ ] `NegationCardGenerator.create_card(negation: Negation) -> NegationCard`

#### 2.3 Media Generation in Card Layer
```python
class NounCardGenerator:
    def create_card(self, noun: Noun) -> NounCard:
        """Create Anki card with media generation."""
        return NounCard(
            noun=noun,
            image_path=self._generate_image_for_noun(noun),
            word_audio_path=self._generate_word_audio(noun),
            example_audio_path=self._generate_example_audio(noun),
        )
    
    def _generate_image_for_noun(self, noun: Noun) -> str | None:
        """Generate image using noun's domain logic for search terms."""
        if noun.is_concrete():  # Domain logic determines if image appropriate
            search_terms = self._create_search_terms(noun)
            return self._media_service.generate_image(search_terms)
        return None
```

### **Phase 3: Clean Up Domain Models**
*Estimated Time: 4-6 hours*

#### 3.1 Remove External Service Dependencies
- [ ] Remove all `from langlearn.services.*` imports from domain models
- [ ] Remove `AnthropicService` calls from domain models
- [ ] Remove media generation methods from domain models

#### 3.2 Keep Pure Domain Logic
- [ ] Retain German grammar validation (article checking, etc.)
- [ ] Keep linguistic analysis methods (`is_concrete()`, `get_combined_audio_text()`)
- [ ] Maintain domain-specific business rules

#### 3.3 Update Domain Model Structure
```python
# AFTER: Pure domain model
class Noun(BaseModel):
    """Pure German noun domain model - no external dependencies."""
    noun: str = Field(..., description="The German noun")
    article: str = Field(..., description="The definite article (der/die/das)")
    english: str = Field(..., description="English translation")
    plural: str = Field(..., description="Plural form")
    example: str = Field(..., description="Example sentence")
    related: str = Field(default="", description="Related words")
    
    def get_combined_audio_text(self) -> str:
        """Pure domain logic - no external calls."""
        return f"{self.article} {self.noun}, die {self.plural}"
    
    def is_concrete(self) -> bool:
        """Domain logic to determine if noun represents concrete object."""
        # German linguistic analysis - no external dependencies
        return self._analyze_concreteness()
```

### **Phase 4: Update Integration Points**
*Estimated Time: 3-4 hours*

#### 4.1 Update Deck Builder
- [ ] Change deck builder to use `CardGenerator.create_card()` pattern
- [ ] Remove direct domain model to backend passing
- [ ] Use Card objects throughout the deck building process

#### 4.2 Update Backend Interface
- [ ] Backend accepts `Card.to_anki_fields()` output
- [ ] Remove field processor fallback logic
- [ ] Simplify backend to pure persistence layer

#### 4.3 Update Tests
- [ ] Domain model tests: Fast, no mocking (pure domain logic)
- [ ] Card generator tests: Integration tests with media service mocking
- [ ] Clear test boundaries matching architectural layers

### **Phase 5: Remove Legacy Code**
*Estimated Time: 2-3 hours*

#### 5.1 Remove Field Processor System
- [ ] Delete `process_fields_for_media_generation()` methods from domain models
- [ ] Remove `FieldProcessor` interface from domain models
- [ ] Remove `DomainMediaGenerator` adapter class
- [ ] Clean up unused field processing utilities

#### 5.2 Remove Dual Media Paths
- [ ] Remove media generation fallbacks from backend
- [ ] Single responsibility: Card generators handle all media
- [ ] Simplify backend to pure data persistence

## Benefits of New Architecture

### **1. Separation of Concerns**
- **Domain Models**: German language rules only
- **Card Models**: Anki presentation + media references
- **Card Generators**: Media generation + card creation
- **Backend**: Pure persistence

### **2. Improved Testability**
```python
# Fast domain model tests (no I/O)
def test_noun_concreteness():
    noun = Noun(noun="Katze", article="die", english="cat", ...)
    assert noun.is_concrete() == True  # Pure logic test

# Integration tests for media generation
def test_noun_card_creation(mock_media_service):
    noun = Noun(...)
    generator = NounCardGenerator(mock_media_service)
    card = generator.create_card(noun)  # Tests media integration
    assert card.image_path is not None
```

### **3. Clear Performance Model**
- Creating domain objects: Fast
- Creating cards: Expensive (explicit)
- No hidden I/O in domain layer

### **4. Better Maintainability**
- Domain changes don't affect media generation
- Media service changes don't affect domain logic
- Clear boundaries for different types of changes

## Migration Strategy

### **Parallel Implementation**
1. Implement new Card system alongside existing system
2. Migrate one word type at a time (start with Noun)
3. Run both systems in parallel during transition
4. Remove old system once all word types migrated

### **Testing Strategy**
- Comprehensive tests for new Card models
- Integration tests comparing old vs new output
- Performance tests to verify domain model speed improvements
- Media generation tests isolated to card layer

### **Rollback Plan**
- Keep old system during migration
- Feature flags to switch between old/new implementations
- Easy rollback if issues discovered

## Success Criteria

### **Architecture Quality**
- [ ] Zero external service imports in `src/langlearn/models/`
- [ ] All media generation isolated to card generators
- [ ] Fast domain model unit tests (< 1ms each)
- [ ] Clear, single-responsibility classes

### **Functionality Preservation**
- [ ] All existing Anki cards generate correctly
- [ ] Media generation produces same quality output
- [ ] Performance meets or exceeds current system
- [ ] All existing tests pass (after migration)

### **Code Quality**
- [ ] Improved test coverage for domain logic
- [ ] Reduced coupling between layers
- [ ] Clearer error handling and debugging
- [ ] Better documentation and code clarity

## Timeline

**Total Estimated Time: 19-27 hours**

- **Phase 1**: 4-6 hours (Card abstraction)
- **Phase 2**: 6-8 hours (Card generators) 
- **Phase 3**: 4-6 hours (Domain cleanup)
- **Phase 4**: 3-4 hours (Integration)
- **Phase 5**: 2-3 hours (Legacy removal)

**Recommended Schedule**: 
- Week 1: Phases 1-2 (Card system)
- Week 2: Phase 3 (Domain cleanup) 
- Week 3: Phases 4-5 (Integration and cleanup)

This plan will result in a much cleaner, more maintainable architecture that properly separates domain concerns from presentation concerns while maintaining all existing functionality.