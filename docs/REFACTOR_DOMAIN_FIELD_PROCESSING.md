# Domain Field Processing Refactoring Plan

**Document Type**: Architecture Refactoring Plan  
**Status**: ✅ **PHASE 2 COMPLETE** - Adjective Model Migrated  
**Scope**: Both GenanKiBackend and AnkiBackend  
**Timeline**: Phase 1 & 2 Complete (1 week), Phase 3 & 4 Remaining

---

## 🎯 **Executive Summary**

**Problem**: The `AnkiBackend` violates Single Responsibility Principle by containing German grammar logic that belongs in domain models. This creates coupling, reduces testability, and violates clean architecture.

**Solution**: Move all field processing logic from infrastructure layer (backends) into domain models where it belongs, creating a clean separation of concerns.

**Impact**: Both backends must be refactored to ensure consistency before migration decision.

---

## 📊 **PROGRESS STATUS**

### ✅ **COMPLETED PHASES**

**Phase 1: Foundation Interfaces (COMPLETE)**
- ✅ `FieldProcessor` abstract base class created
- ✅ `MediaGenerator` protocol defined  
- ✅ `DomainMediaGenerator` adapter implemented
- ✅ `MockDomainMediaGenerator` for testing created
- ✅ Utility functions (`format_media_reference`, `validate_minimum_fields`)
- ✅ `FieldProcessingError` exception handling
- ✅ 21 comprehensive interface tests added
- ✅ All tests passing (433/433 → 452/452)

**Phase 2: Adjective Model Migration (COMPLETE)**
- ✅ `Adjective` class implements `FieldProcessor` interface
- ✅ German grammar logic moved from `AnkiBackend` to `Adjective` model
- ✅ `ModelFactory` created for note type detection
- ✅ Field layout preserved: `[Word, English, Example, Comparative, Superlative, Image, WordAudio, ExampleAudio]`
- ✅ Combined audio text logic: "schön, schöner, am schönsten"
- ✅ Context-enhanced image search integration
- ✅ 19 new tests added (10 Adjective + 9 Factory tests)
- ✅ All code quality standards met (linting, formatting, type checking)

### 🔄 **REMAINING PHASES**

**Phase 3: Backend Integration (PENDING)**
- Update backends to use `ModelFactory` and delegate to domain models
- Create clean delegation pattern for supported vs unsupported note types
- Maintain backward compatibility during transition

**Phase 4: Other Model Migration (PENDING)**
- Migrate Noun, Verb, Preposition, Phrase, Adverb, Negation models
- Expand `ModelFactory` to support all German word types
- Ensure consistent behavior across all model types

---

## 🔍 **Current Architecture Violation**

### **What's Wrong:**
```python
# ❌ VIOLATION: Infrastructure doing domain logic
class AnkiBackend:
    def _process_adjective_fields(self, fields: list[str]) -> list[str]:
        # Creating domain models in infrastructure
        adjective = Adjective(word=word, english=english, ...)
        # Calling domain methods from infrastructure  
        combined_text = adjective.get_combined_audio_text()
        # German-specific field processing logic
        if len(fields) > 6 and not fields[6]:  # WordAudio field
            # ... complex German grammar logic ...
```

### **SRP Violations Identified:**
1. **Domain Logic in Infrastructure**: Field processing rules based on German grammar
2. **Model Creation in Wrong Layer**: Infrastructure creating domain models
3. **Duplicated Logic Risk**: Same logic may exist differently in GenanKiBackend
4. **Testing Complexity**: Cannot test German logic independently of Anki infrastructure

---

## 🏗️ **Target Architecture**

### **Clean Separation:**
```python
# ✅ CORRECT: Domain models handle their own field processing
class Adjective(BaseModel):
    def process_fields_for_media_generation(
        self, 
        fields: list[str], 
        media_generator: MediaGenerator
    ) -> list[str]:
        """Process adjective-specific field layout with German grammar rules."""
        # German-specific logic belongs here
        
# ✅ CORRECT: Infrastructure delegates to domain
class AnkiBackend:
    def _process_fields_with_media(self, note_type_name: str, fields: list[str]) -> list[str]:
        model = self._create_domain_model(note_type_name, fields)
        return model.process_fields_for_media_generation(fields, self._media_generator)
```

---

## 📋 **Refactoring Plan - Phase by Phase**

### **Phase 1: Create Domain Field Processing Interface ✅ COMPLETE**

#### **1.1 Create Abstract Base Class**
**File**: `src/langlearn/models/field_processor.py` (NEW)
```python
from abc import ABC, abstractmethod
from typing import Protocol

class MediaGenerator(Protocol):
    """Interface for media generation services."""
    def generate_audio(self, text: str) -> str | None: ...
    def generate_image(self, query: str, backup_query: str = None) -> str | None: ...

class FieldProcessor(ABC):
    """Abstract base for domain models that can process their own fields."""
    
    @abstractmethod
    def process_fields_for_media_generation(
        self, 
        fields: list[str], 
        media_generator: MediaGenerator
    ) -> list[str]:
        """Process model-specific field layout with media generation."""
        
    @abstractmethod  
    def get_expected_field_count(self) -> int:
        """Return expected number of fields for this model type."""
        
    @abstractmethod
    def validate_field_structure(self, fields: list[str]) -> bool:
        """Validate that fields match expected structure for this model."""
```

#### **1.2 Create Media Generator Interface Implementation**
**File**: `src/langlearn/services/domain_media_generator.py` (NEW)
```python
class DomainMediaGenerator:
    """Adapter that provides MediaGenerator interface to domain models."""
    
    def __init__(self, media_service: MediaService, german_service: GermanLanguageService):
        self._media_service = media_service
        self._german_service = german_service
        
    def generate_audio(self, text: str) -> str | None:
        return self._media_service.generate_audio(text)
        
    def generate_image(self, query: str, backup_query: str = None) -> str | None:
        return self._media_service.generate_image(query, backup_query)
        
    def get_context_enhanced_query(self, word: str, english: str, example: str) -> str:
        return self._german_service.extract_context_from_sentence(example, word, english)
        
    def get_conceptual_search_terms(self, word_type: str, word: str, english: str) -> str:
        return self._german_service.get_conceptual_image_search_terms(word_type, word, english)
```

### **Phase 2: Migrate Domain Models ✅ ADJECTIVE COMPLETE**

**STATUS**: Adjective model successfully migrated with full FieldProcessor implementation. All German grammar logic moved from backend to domain model. Field layout preserved, combined audio logic working, context-enhanced image search integrated.

#### **2.1 Update Adjective Model ✅ IMPLEMENTED**
**File**: `src/langlearn/models/adjective.py` - **IMPLEMENTED with 10 comprehensive tests**
```python
class Adjective(BaseModel, FieldProcessor):
    # ... existing fields ...
    
    def process_fields_for_media_generation(
        self, 
        fields: list[str], 
        media_generator: MediaGenerator
    ) -> list[str]:
        """Process adjective fields: [Word, English, Example, Comparative, Superlative, Image, WordAudio, ExampleAudio]"""
        if len(fields) < 8:
            return fields  # Insufficient fields
            
        processed = fields.copy()
        
        # Generate combined adjective audio if WordAudio is empty
        if not processed[6]:  # WordAudio field
            combined_text = self.get_combined_audio_text()
            audio_path = media_generator.generate_audio(combined_text)
            if audio_path:
                processed[6] = f"[sound:{os.path.basename(audio_path)}]"
        
        # Generate example audio if ExampleAudio is empty  
        if not processed[7]:  # ExampleAudio field
            audio_path = media_generator.generate_audio(self.example)
            if audio_path:
                processed[7] = f"[sound:{os.path.basename(audio_path)}]"
                
        # Generate image if Image field is empty
        if not processed[5]:  # Image field
            context_query = media_generator.get_context_enhanced_query(
                self.word, self.english, self.example
            )
            image_path = media_generator.generate_image(self.english, context_query)
            if image_path:
                processed[5] = f'<img src="{os.path.basename(image_path)}">'
                
        return processed
        
    def get_expected_field_count(self) -> int:
        return 8
        
    def validate_field_structure(self, fields: list[str]) -> bool:
        return len(fields) >= 8
```

#### **2.2 Update Noun Model**
**File**: `src/langlearn/models/noun.py`
```python
class Noun(BaseModel, FieldProcessor):
    # ... existing fields ...
    
    def process_fields_for_media_generation(
        self, 
        fields: list[str], 
        media_generator: MediaGenerator
    ) -> list[str]:
        """Process noun fields: [Noun, Article, Plural, English, Example, Image, WordAudio, ExampleAudio]"""
        if len(fields) < 8:
            return fields
            
        processed = fields.copy()
        
        # Generate combined noun audio if WordAudio is empty
        if not processed[6]:  # WordAudio field  
            combined_text = self.get_combined_audio_text()
            audio_path = media_generator.generate_audio(combined_text)
            if audio_path:
                processed[6] = f"[sound:{os.path.basename(audio_path)}]"
        
        # Generate example audio if ExampleAudio is empty
        if not processed[7]:  # ExampleAudio field
            audio_path = media_generator.generate_audio(self.example)
            if audio_path:
                processed[7] = f"[sound:{os.path.basename(audio_path)}]"
                
        # Generate image if Image field is empty AND noun is concrete
        if not processed[5] and self.is_concrete():  # Image field
            context_query = media_generator.get_context_enhanced_query(
                self.noun, self.english, self.example
            )
            image_path = media_generator.generate_image(self.english, context_query)
            if image_path:
                processed[5] = f'<img src="{os.path.basename(image_path)}">'
                
        return processed
        
    def get_expected_field_count(self) -> int:
        return 8
        
    def validate_field_structure(self, fields: list[str]) -> bool:
        return len(fields) >= 8
```

#### **2.3 Implement Remaining Models**
Similar implementations for:
- **`Verb`** and subclasses (`RegularVerb`, `IrregularVerb`, `SeparableVerb`)
- **`Adverb`** (with conceptual image search)  
- **`Negation`** (with conceptual image search)
- **`Preposition`**, **`Conjunction`**, etc.

### **Phase 3: Create Model Factory ✅ COMPLETE**

**STATUS**: ModelFactory successfully implemented with note type detection, case-insensitive matching, and clean extensibility pattern for future model types. Full test coverage with 9 comprehensive tests.

#### **3.1 Domain Model Factory ✅ IMPLEMENTED**
**File**: `src/langlearn/models/model_factory.py` - **IMPLEMENTED with 9 comprehensive tests**
```python
class ModelFactory:
    """Factory for creating domain models from field data and note type."""
    
    @staticmethod
    def create_from_note_type(note_type_name: str, fields: list[str]) -> FieldProcessor | None:
        """Create appropriate domain model from note type name and field data."""
        note_type_lower = note_type_name.lower()
        
        try:
            if "adjective" in note_type_lower and len(fields) >= 5:
                return Adjective(
                    word=fields[0],
                    english=fields[1], 
                    example=fields[2],
                    comparative=fields[3] if len(fields) > 3 else "",
                    superlative=fields[4] if len(fields) > 4 else "",
                    word_audio="", example_audio="", image_path=""
                )
                
            elif "noun" in note_type_lower and len(fields) >= 5:
                return Noun(
                    noun=fields[0],
                    article=fields[1],
                    plural=fields[2], 
                    english=fields[3],
                    example=fields[4],
                    word_audio="", example_audio="", image_path=""
                )
                
            elif "verb" in note_type_lower and len(fields) >= 3:
                # Determine verb type based on word content
                verb_word = fields[0]
                if any(prefix in verb_word for prefix in ["auf", "an", "ein", "aus", "mit"]):
                    return SeparableVerb(
                        verb=verb_word, english=fields[1], example=fields[2],
                        word_audio="", example_audio="", image_path=""
                    )
                else:
                    return RegularVerb(
                        verb=verb_word, english=fields[1], example=fields[2],
                        word_audio="", example_audio="", image_path=""
                    )
                    
            elif "adverb" in note_type_lower and len(fields) >= 4:
                return Adverb(
                    word=fields[0], english=fields[1], 
                    type=fields[2], example=fields[3],
                    word_audio="", example_audio="", image_path=""
                )
                
            elif "negation" in note_type_lower and len(fields) >= 3:
                return Negation(
                    word=fields[0], english=fields[1], example=fields[2],
                    word_audio="", example_audio="", image_path=""
                )
                
            # Add other model types as needed...
            
        except Exception as e:
            logger.warning(f"Could not create domain model for {note_type_name}: {e}")
            return None
            
        return None
```

### **Phase 4: Update Backend Implementations 🔄 PENDING**

#### **4.1 Refactor AnkiBackend**
**File**: `src/langlearn/backends/anki_backend.py`

**REMOVE** these methods entirely:
- `_process_adjective_fields()`
- `_process_noun_fields()`
- `_process_verb_fields()`
- `_process_preposition_fields()`
- `_process_phrase_fields()`
- `_process_adverb_fields()`
- `_process_negation_fields()`

**REPLACE** with clean delegation:
```python
from langlearn.services.model_factory import ModelFactory
from langlearn.services.domain_media_generator import DomainMediaGenerator

class AnkiBackend(DeckBackend):
    def __init__(self, ...):
        # ... existing initialization ...
        self._domain_media_generator = DomainMediaGenerator(
            self._media_service, 
            self._german_service
        )
    
    def _process_fields_with_media(self, note_type_name: str, fields: list[str]) -> list[str]:
        """Delegate field processing to appropriate domain model."""
        # Create domain model
        model = ModelFactory.create_from_note_type(note_type_name, fields)
        if not model:
            return fields  # No processing for unknown types
            
        # Validate field structure
        if not model.validate_field_structure(fields):
            logger.warning(f"Invalid field structure for {note_type_name}: {len(fields)} fields")
            return fields
            
        # Delegate to domain model
        try:
            return model.process_fields_for_media_generation(fields, self._domain_media_generator)
        except Exception as e:
            logger.error(f"Error processing {note_type_name} fields: {e}")
            return fields  # Return original on error
```

#### **4.2 Update GenanKiBackend** 
**File**: `src/langlearn/backends/genanki_backend.py`

Apply the **same exact refactoring** to ensure both backends behave identically:
```python
class GenanKiBackend(DeckBackend):
    def __init__(self, ...):
        # ... existing initialization ...
        # Add domain media generator
        self._domain_media_generator = DomainMediaGenerator(
            self._media_service, 
            self._german_service  
        )
    
    # Use IDENTICAL _process_fields_with_media implementation
    def _process_fields_with_media(self, note_type_name: str, fields: list[str]) -> list[str]:
        # Same implementation as AnkiBackend
```

---

## 🧪 **Testing Strategy**

### **Phase 1: Domain Model Testing**
**New Test Files:**
- `tests/test_domain_field_processing.py` - Test each model's field processing
- `tests/test_model_factory.py` - Test model creation from note types
- `tests/test_domain_media_generator.py` - Test media generator adapter

**Test Categories:**
```python
class TestAdjectiveFieldProcessing:
    def test_complete_adjective_field_processing(self):
        """Test adjective processes all fields correctly."""
        
    def test_adjective_missing_comparative_superlative(self):
        """Test adjective handles missing forms."""
        
    def test_adjective_media_generation_failure(self):
        """Test adjective handles media generation errors."""

class TestNounFieldProcessing:
    def test_concrete_noun_with_image_generation(self):
        """Test concrete nouns generate images."""
        
    def test_abstract_noun_no_image_generation(self):
        """Test abstract nouns don't generate images."""
```

### **Phase 2: Backend Integration Testing**
**Updated Test Files:**
- `tests/test_anki_backend_refactored.py` - Test clean AnkiBackend delegation
- `tests/test_genanki_backend_refactored.py` - Test GenanKiBackend delegation  
- `tests/test_backend_consistency.py` - Ensure both backends behave identically

### **Phase 3: Coverage Validation**
- **Target**: Maintain >75% coverage while improving architecture
- **Focus**: Domain logic now testable independently of infrastructure
- **Regression**: Ensure existing functionality unchanged

---

## 📊 **Success Metrics**

### **Architecture Quality**
- ✅ **SRP Compliance**: No domain logic in infrastructure layer
- ✅ **DRY Principle**: Single implementation of field processing logic
- ✅ **Testability**: Domain logic testable without Anki infrastructure
- ✅ **Consistency**: Both backends use identical field processing

### **Code Quality**  
- ✅ **Coverage Maintained**: >75% overall coverage preserved
- ✅ **Type Safety**: Full MyPy compliance maintained
- ✅ **Performance**: No performance regression in deck generation
- ✅ **Error Handling**: Graceful degradation preserved

### **Migration Readiness**
- ✅ **Backend Parity**: GenanKiBackend and AnkiBackend behaviorally identical  
- ✅ **Risk Reduction**: Domain logic thoroughly tested before migration
- ✅ **Maintainability**: Single source of truth for German grammar rules

---

## ⚠️ **Risks and Mitigations**

### **Risk 1: Breaking Changes During Refactoring**
**Mitigation**: 
- Implement with feature flags
- Run parallel processing (old + new) during transition
- Comprehensive regression testing at each phase

### **Risk 2: Performance Impact**
**Mitigation**:
- Benchmark before/after each phase
- Profile media generation performance 
- Optimize domain model creation if needed

### **Risk 3: Complex Field Layout Edge Cases**
**Mitigation**:
- Catalog all existing field layouts before starting
- Test with real German A1 dataset at each phase
- Maintain backward compatibility during transition

---

## 📅 **Implementation Timeline**

| **Week** | **Phase** | **Deliverables** | **Validation** |
|----------|-----------|------------------|----------------|
| **1** | Domain Interface | `FieldProcessor` interface, `DomainMediaGenerator` | Unit tests pass |
| **1-2** | Domain Models | All models implement `process_fields_for_media_generation()` | Domain tests comprehensive |
| **2** | Model Factory | `ModelFactory` with note type detection | Factory tests pass |
| **2-3** | Backend Refactor | Clean AnkiBackend + GenanKiBackend delegation | Integration tests pass |
| **3** | Validation | Full regression testing, performance validation | Production readiness achieved |

**Total Duration**: 3 weeks  
**Prerequisites**: Complete current type safety work
**Success Gate**: All tests pass, no behavioral changes, architecture clean

---

## 🎯 **Post-Refactoring Benefits**

### **Immediate Benefits**
1. **Clean Architecture**: Proper separation of domain and infrastructure
2. **Better Testability**: German grammar logic testable independently  
3. **Reduced Duplication**: Single field processing implementation
4. **Migration Safety**: Both backends guaranteed identical behavior

### **Long-term Benefits**
1. **Maintainability**: German grammar changes localized to domain models
2. **Extensibility**: Easy to add new part-of-speech types
3. **Multi-language Ready**: Domain pattern applies to other languages
4. **Quality**: Architecture supports clean growth

---

## ✅ **Acceptance Criteria**

**This refactoring is complete when:**
1. ✅ **No German grammar logic exists in backend files**
2. ✅ **All domain models implement `FieldProcessor` interface**  
3. ✅ **Both backends use identical field processing delegation**
4. ✅ **All existing tests continue to pass**
5. ✅ **New domain-focused tests achieve >90% coverage**
6. ✅ **Performance benchmarks show no regression**
7. ✅ **Migration readiness assessment can proceed confidently**

This refactoring is **essential** before Anki migration to ensure we're migrating clean, well-architected code rather than perpetuating technical debt.