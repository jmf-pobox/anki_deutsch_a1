# MVP Reintegration Plan - Card Generators

**Status**: Planning Phase  
**Goal**: Transform GermanDeckBuilder from god class to clean MVP architecture  
**Timeline**: 4 phases, 2-3 weeks implementation  

## 🎯 **Problem Statement**

### Current Architecture Issues
1. **GermanDeckBuilder God Class** - 1,000+ lines handling:
   - Data loading
   - Media generation 
   - Field extraction
   - Template management
   - Deck orchestration
   - Subdeck management

2. **Code Duplication** - 4 nearly identical methods:
   - `generate_noun_cards()` - 117 lines
   - `generate_adjective_cards()` - 100 lines  
   - `generate_adverb_cards()` - 118 lines
   - `generate_negation_cards()` - 113 lines
   
3. **Poor Extensibility** - Adding new grammar types requires:
   - Duplicating complex logic in GermanDeckBuilder
   - Manual field extraction code
   - Template service method additions

4. **Abandoned Architecture** - Well-designed card generators exist but are unused

## 🏗️ **Target MVP Architecture**

### **Model-View-Presenter Design**

```
Models (Domain)          Presenters (Data Binding)      Views (Templates)
│                        │                               │
├── Noun                 ├── NounCardGenerator ────────► noun_front.html
├── Adjective            ├── AdjectiveCardGenerator ───► adjective_front.html  
├── Verb                 ├── VerbCardGenerator ────────► verb_front.html
├── Adverb               ├── AdverbCardGenerator ──────► adverb_front.html
└── ...                  └── ...                         └── ...
                         
                         Orchestrator (Coordination)
                         │
                         └── GermanDeckBuilder (slimmed)
```

### **Clear Responsibilities**

| Component | Responsibility | Examples |
|-----------|----------------|----------|
| **Models** | Domain logic, validation | `Noun.get_combined_audio_text()` |
| **Views** | Pure presentation | `{{Word}}`, `{{#Image}}{{Image}}{{/Image}}` |
| **Presenters** | Data binding, field mapping | `extract_fields(noun) → ["Katze", "die", "cat"]` |
| **Orchestrator** | Coordination, media, subdecks | Load data, manage media, export deck |

## 📋 **Implementation Phases**

---

## **Phase 1: Enhance Existing Card Generators** (Week 1)

### Goals
- Upgrade existing `NounCardGenerator` and `AdjectiveCardGenerator`
- Add media generation support
- Create consistent interface

### Tasks

#### 1.1 Enhance BaseCardGenerator
```python
class BaseCardGenerator(ABC, Generic[T]):
    def __init__(self, backend: DeckBackend, template_service: TemplateService, 
                 media_manager: MediaManager = None):
        # Add media support to base class
        
    def add_card(self, data: T, generate_media: bool = True) -> None:
        """Enhanced with media generation support."""
        fields = self._extract_fields(data)
        if generate_media and self._media_manager:
            fields = self._enhance_fields_with_media(data, fields)
        self._backend.add_note(self.note_type_id, fields)
        
    @abstractmethod
    def _enhance_fields_with_media(self, data: T, fields: list[str]) -> list[str]:
        """Add media generation logic."""
```

#### 1.2 Upgrade NounCardGenerator
```python
class NounCardGenerator(BaseCardGenerator[Noun]):
    def _enhance_fields_with_media(self, noun: Noun, fields: list[str]) -> list[str]:
        # Move media logic from GermanDeckBuilder here
        enhanced_fields = fields.copy()
        
        # Handle word audio (index 7)
        if not enhanced_fields[7] and self._media_manager:
            audio_text = self._get_combined_noun_audio_text(noun)
            audio_file = self._media_manager.generate_and_add_audio(audio_text)
            if audio_file:
                enhanced_fields[7] = audio_file.reference
                
        # Handle image (index 6) 
        # Handle example audio (index 8)
        
        return enhanced_fields
```

#### 1.3 Create Comprehensive Tests
- Test media integration in card generators
- Test field extraction accuracy
- Test template service integration

### **Deliverables Phase 1**
- ✅ Enhanced `BaseCardGenerator` with media support
- ✅ Upgraded `NounCardGenerator` with media logic  
- ✅ Upgraded `AdjectiveCardGenerator` with media logic
- ✅ Comprehensive test coverage
- ✅ Documentation updates

---

## **Phase 2: Integrate into GermanDeckBuilder** (Week 2)

### Goals
- Replace manual field extraction with card generators
- Slim down GermanDeckBuilder methods
- Maintain backward compatibility

### Tasks

#### 2.1 Create CardGeneratorFactory
```python
class CardGeneratorFactory:
    """Factory for creating card generators with proper dependencies."""
    
    def __init__(self, backend: DeckBackend, template_service: TemplateService, 
                 media_manager: MediaManager):
        self._backend = backend
        self._template_service = template_service
        self._media_manager = media_manager
        
    def create_noun_generator(self) -> NounCardGenerator:
        return NounCardGenerator(self._backend, self._template_service, self._media_manager)
        
    def create_adjective_generator(self) -> AdjectiveCardGenerator:
        return AdjectiveCardGenerator(self._backend, self._template_service, self._media_manager)
```

#### 2.2 Refactor GermanDeckBuilder Methods
```python
# Before: 117 lines of complex logic
def generate_noun_cards(self, generate_media: bool = True) -> int:
    """Generate Anki cards for loaded nouns."""
    if not self._loaded_nouns:
        logger.warning("No nouns loaded")
        return 0
        
    self.create_subdeck("Nouns")
    generator = self._card_factory.create_noun_generator()
    
    cards_created = 0
    for noun in self._loaded_nouns:
        generator.add_card(noun, generate_media)
        cards_created += 1
        
    self.reset_to_main_deck()
    logger.info(f"Generated {cards_created} noun cards")
    return cards_created

# After: 15 lines, clear and maintainable
```

#### 2.3 Add Generic Card Generation Method
```python
def _generate_cards_for_type(self, data: list[T], subdeck_name: str, 
                           generator_factory: Callable[[], BaseCardGenerator[T]], 
                           generate_media: bool = True) -> int:
    """Generic card generation method to eliminate duplication."""
    if not data:
        logger.warning(f"No {subdeck_name.lower()} loaded")
        return 0
        
    self.create_subdeck(subdeck_name)
    generator = generator_factory()
    
    for item in data:
        generator.add_card(item, generate_media)
        
    self.reset_to_main_deck()
    return len(data)

# Usage:
def generate_noun_cards(self, generate_media: bool = True) -> int:
    return self._generate_cards_for_type(
        self._loaded_nouns, "Nouns", 
        self._card_factory.create_noun_generator, generate_media
    )
```

### **Deliverables Phase 2**
- ✅ `CardGeneratorFactory` for dependency injection
- ✅ Refactored `generate_noun_cards()` and `generate_adjective_cards()` 
- ✅ Generic card generation template method
- ✅ All tests passing
- ✅ 90% reduction in GermanDeckBuilder method sizes

---

## **Phase 3: Add Missing Card Generators** (Week 2-3)

### Goals
- Complete the card generator suite
- Achieve full feature parity
- Eliminate remaining code duplication

### Tasks

#### 3.1 Create AdverbCardGenerator
```python
class AdverbCardGenerator(BaseCardGenerator[Adverb]):
    def _get_field_names(self) -> list[str]:
        return ["Word", "English", "Type", "Example", "Image", "WordAudio", "ExampleAudio"]
        
    def _extract_fields(self, adverb: Adverb) -> list[str]:
        return [adverb.word, adverb.english, adverb.type.value, adverb.example, "", "", ""]
        
    def _enhance_fields_with_media(self, adverb: Adverb, fields: list[str]) -> list[str]:
        # Move adverb media logic from GermanDeckBuilder
```

#### 3.2 Create NegationCardGenerator
```python
class NegationCardGenerator(BaseCardGenerator[Negation]):
    def _get_field_names(self) -> list[str]:
        return ["Word", "English", "Type", "Example", "Image", "WordAudio", "ExampleAudio"]
```

#### 3.3 Update Factory and GermanDeckBuilder
- Add new generators to factory
- Refactor remaining methods
- Update exports and imports

### **Deliverables Phase 3**
- ✅ `AdverbCardGenerator` with media support
- ✅ `NegationCardGenerator` with media support  
- ✅ All 4 card types using generator architecture
- ✅ GermanDeckBuilder methods reduced to ~15 lines each
- ✅ Zero code duplication in card generation

---

## **Phase 4: Grammar Extension Framework** (Week 3)

### Goals
- Create extension points for new grammar types
- Document extensibility patterns
- Future-proof the architecture

### Tasks

#### 4.1 Create Grammar Extension Interface
```python
from typing import Protocol

class GrammarCardGenerator(Protocol[T]):
    """Protocol for grammar-specific card generators."""
    
    def get_card_type_name(self) -> str: ...
    def get_subdeck_name(self) -> str: ...
    def supports_media_generation(self) -> bool: ...

class GrammarRegistry:
    """Registry for grammar card generators."""
    
    def register_generator(self, data_type: type, generator_class: type):
        self._generators[data_type] = generator_class
        
    def create_generator(self, data_type: type) -> BaseCardGenerator:
        generator_class = self._generators.get(data_type)
        if not generator_class:
            raise ValueError(f"No generator registered for {data_type}")
        return generator_class(self._backend, self._template_service, self._media_manager)
```

#### 4.2 Make GermanDeckBuilder Generic
```python
def generate_cards_for_grammar_type(self, data: list[T], data_type: type[T], 
                                  generate_media: bool = True) -> int:
    """Generic method that works for any registered grammar type."""
    generator = self._grammar_registry.create_generator(data_type)
    subdeck_name = generator.get_subdeck_name()
    
    return self._generate_cards_for_type(data, subdeck_name, 
                                       lambda: generator, generate_media)
```

#### 4.3 Create Extension Examples
```python
# Future grammar extensions made easy:

class ConditionalClause(BaseModel):
    condition: str
    result: str
    english: str
    formality: str

class ConditionalCardGenerator(BaseCardGenerator[ConditionalClause]):
    def get_subdeck_name(self) -> str: return "Conditional Clauses"
    def _get_field_names(self) -> list[str]:
        return ["Condition", "Result", "English", "Formality"]

# Register and use:
deck_builder.register_grammar_type(ConditionalClause, ConditionalCardGenerator)
deck_builder.load_conditionals_from_csv("conditionals.csv")
deck_builder.generate_cards_for_grammar_type(conditionals, ConditionalClause)
```

### **Deliverables Phase 4**
- ✅ `GrammarRegistry` for runtime extension
- ✅ Generic card generation for any grammar type
- ✅ Extension documentation and examples
- ✅ Future-ready architecture

---

## 📊 **Success Metrics**

### **Code Quality Improvements**
- **Lines of Code**: GermanDeckBuilder methods: 450+ lines → ~60 lines (-87%)
- **Cyclomatic Complexity**: Reduced method complexity from 15+ to 3-5
- **Code Duplication**: 90% duplicate code eliminated
- **Test Coverage**: Maintain 100% test coverage throughout

### **Extensibility Improvements**
- **New Grammar Types**: From 4-hour implementation → 30-minute implementation
- **Template Changes**: Zero code changes needed for template updates
- **Field Modifications**: Isolated to single card generator class

### **Architecture Benefits**
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed Principle**: Open for extension, closed for modification
- **Dependency Injection**: Clean testable dependencies
- **Type Safety**: Generic type parameters prevent field mismatches

## 🚀 **Implementation Timeline**

```
Week 1: Phase 1 - Enhance Base Classes
├── Day 1-2: BaseCardGenerator media support
├── Day 3-4: NounCardGenerator upgrade  
├── Day 5-7: AdjectiveCardGenerator upgrade + tests

Week 2: Phase 2 & 3 - Integration & Completion
├── Day 1-3: Factory pattern + GermanDeckBuilder integration
├── Day 4-5: AdverbCardGenerator + NegationCardGenerator
├── Day 6-7: Testing & documentation

Week 3: Phase 4 - Extension Framework
├── Day 1-3: Grammar registry and generic methods
├── Day 4-5: Extension examples and documentation
├── Day 6-7: Final testing and cleanup
```

## 📚 **Documentation Updates Required**

1. **`DESIGN.md`** - Update architecture diagrams
2. **`README.md`** - Update usage examples with new API
3. **`DESIGN-SRP.md`** - Update component descriptions
4. **Create `EXTENSION_GUIDE.md`** - How to add new grammar types
5. **Update docstrings** - All card generators and GermanDeckBuilder

---

This plan transforms GermanDeckBuilder from a god class into a clean, extensible MVP architecture while maintaining full backward compatibility and adding powerful extension capabilities for future grammar types.