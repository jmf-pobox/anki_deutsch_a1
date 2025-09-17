# Project TODO - Current Status

Last updated: 2025-01-17

## 🚨 CRITICAL PRIORITY

### **PRIORITY 1: DeckBuilder Multi-Language Architecture Refactoring** 🔴 **CRITICAL**

**Problem**: `src/langlearn/deck_builder.py` violates Clean Architecture principles with extensive language-specific conditionals and hardcoded imports, making it difficult to scale to new languages.

**Status**: 🚧 **Design Analysis Complete** - Implementation Pending

#### **Architectural Violations Identified**

1. **Scattered Language Conditionals** (Lines 123-143)
   - Hardcoded voice selection: `if language.lower() in ("ru", "russian")`
   - Hardcoded TTS configuration per language
   - Default fallback to German configuration

2. **Language-Specific Service Imports** (Lines 325-346)
   - Direct imports in `generate_all_cards()`: `from .languages.german.services.record_to_model_factory`
   - Conditional factory selection based on language string
   - Violation of dependency injection principles

3. **Hardcoded German MediaEnricher** (Lines 173-188)
   - Forces all languages to use: `from .languages.german.services.media_enricher import StandardMediaEnricher`
   - Prevents language-specific media enrichment strategies

4. **Mixed Responsibilities**
   - DeckBuilder is simultaneously: orchestrator, service factory, language configurator
   - Violates Single Responsibility Principle

#### **Recommended Solution: Service Container Pattern**

**Design Pattern**: Abstract Factory + Dependency Injection + Strategy Pattern

**Implementation Plan** (4 Phases, ~3-4 days total):

##### **Phase 1: Extend Language Protocol** (Low Risk, 4 hours)
Add service creation responsibilities to Language protocol:

```python
# src/langlearn/protocols/language_protocol.py
class Language(Protocol):
    @abstractmethod
    def create_audio_service(self, output_dir: Path) -> AudioService:
        """Create language-configured audio service."""
        ...

    @abstractmethod
    def create_record_to_model_factory(self) -> RecordToModelFactory:
        """Create record to model factory."""
        ...

    @abstractmethod
    def create_service_container(
        self,
        audio_dir: Path,
        image_dir: Path,
        project_root: Path
    ) -> ServiceContainer:
        """Create complete service container for this language."""
        ...
```

**Quality Gates**:
- MyPy passes with new protocol methods
- No existing functionality broken

##### **Phase 2: Implement Service Container** (Medium Risk, 4 hours)

```python
# src/langlearn/core/services/service_container.py
@dataclass
class ServiceContainer:
    """Container for all language-specific services."""
    audio_service: AudioService
    pexels_service: PexelsService
    media_enricher: MediaEnricher
    record_mapper: RecordMapper
    card_builder: CardBuilder
    template_service: TemplateService
    grammar_service: Any
    record_to_model_factory: RecordToModelFactory
```

Update each language to implement `create_service_container()`:
- Move TTS configuration to GermanLanguage, RussianLanguage, KoreanLanguage
- Move service initialization to language implementations
- Return fully configured ServiceContainer

**Quality Gates**:
- All 636 unit tests pass
- Service creation works for all 3 languages

##### **Phase 3: Refactor DeckBuilder** (Higher Risk, 6 hours)

Transform DeckBuilder into pure orchestrator:

```python
class DeckBuilder:
    def __init__(self, deck_name: str, language: str, deck_type: str = "default"):
        # Single language lookup
        self._language = LanguageRegistry.get(language)

        # Get ALL services from language (no conditionals)
        paths = self._calculate_paths(language, deck_type)
        self._services = self._language.create_service_container(
            audio_dir=paths.audio_dir,
            image_dir=paths.image_dir,
            project_root=paths.project_root
        )

        # Pure delegation from here
        self._backend = self._create_backend(deck_name, self._language)
        # No more language-specific logic below this line
```

Remove ALL:
- Language conditionals (lines 123-143, 325-346)
- Direct language service imports
- Hardcoded German references

**Quality Gates**:
- Zero language conditionals in deck_builder.py
- All tests pass
- Deck generation produces identical output

##### **Phase 4: Cleanup and Documentation** (Low Risk, 2 hours)

- Remove obsolete imports
- Update architecture documentation
- Add integration tests for multi-language support
- Update ENG-SYSTEM-DESIGN.md with new architecture

**Quality Gates**:
- Full test suite passes
- Documentation reflects new design
- Code coverage maintained

#### **Success Metrics**

**Before Refactoring**:
- ❌ 3+ conditional blocks for language selection
- ❌ Direct imports of language-specific services
- ❌ Hardcoded German MediaEnricher for all languages
- ❌ Mixed orchestration and configuration responsibilities

**After Refactoring**:
- ✅ Zero language conditionals in DeckBuilder
- ✅ Pure delegation to ServiceContainer
- ✅ Each language fully encapsulates its configuration
- ✅ Single Responsibility: DeckBuilder only orchestrates
- ✅ New languages require zero changes to DeckBuilder

#### **Risk Mitigation**

1. **Incremental Approach**: Each phase independently deployable
2. **Backward Compatibility**: Maintain existing public API
3. **Test Coverage**: Run full test suite after each phase
4. **Feature Branch**: All work on `refactor/deck-builder-multi-language`

---

### **PRIORITY 2: COMPLETED WORK** ✅

**Korean Language Implementation**: ✅ **100% COMPLETE** (2025-01-17)
- ✅ Complete Korean language package with noun records, templates, and services
- ✅ Korean particle system (은/는, 이/가, 을/를) with phonological rules
- ✅ Counter/classifier system (개, 명, 마리, 채, 권) integration
- ✅ Hangul typography with proper font families
- ✅ Unicode filename validation for international languages (fixed MediaFileRegistrar)
- ✅ NamingService architecture for consistent multi-language naming
- ✅ Korean voice support (Seoyeon) for AWS Polly TTS
- ✅ Fail-fast template loading without fallbacks
- ✅ All three languages (German, Russian, Korean) verified working

**AnkiBackend Language-Agnostic Refactoring**: ✅ **100% COMPLETE**
- ✅ Removed all German imports from AnkiBackend
- ✅ Implemented field processing delegation pattern
- ✅ Complete protocol-based language abstraction
- ✅ ~83% code reduction in critical method (240 lines → 37 lines)

**Multi-Language Architecture Foundation**: ✅ **100% COMPLETE**
- ✅ Language protocol and registry system
- ✅ German, Russian, Korean language implementations
- ✅ Template system with language-specific resolution
- ✅ Data organization: `languages/{language}/{deck}/`

**Documentation Consolidation**: ✅ **100% COMPLETE** (2025-01-17)
- ✅ Updated existing docs to clarify German-specific scope
- ✅ Created minimal specs for Russian and Korean languages
- ✅ Enhanced multi-language CSV specification

---

### **PRIORITY 3: Future Enhancement Opportunities** 🟡 LOW PRIORITY

**Article Cloze System Enhancement**:
- Re-enable ArticleApplicationService for noun-article practice cards
- Fix Context card unique audio generation (currently produces blank audio)
- Architectural redesign for cloze card media processing

**Code Quality Improvements**:
- ServiceContainer refactoring - Remove Optional/None abuse patterns
- Legacy code removal - Any remaining commented out or deprecated patterns

---

## 🎯 SUCCESS METRICS

**Current State (2025-01-17)**:
- ✅ **Three working languages**: German (full), Russian (minimal), Korean (minimal)
- ✅ All languages verified working with media generation and Anki import
- ✅ Multi-language architecture: **95% complete** (DeckBuilder refactoring pending)
- ✅ All unit tests passing + integration tests
- ✅ MyPy strict mode: 0 errors across codebase
- ✅ AnkiBackend fully language-agnostic
- ✅ Unicode filename support for international scripts
- ⚠️ DeckBuilder contains language-specific conditionals (to be removed)

**Target State After DeckBuilder Refactoring**:
- ✅ 100% language-agnostic core components
- ✅ Zero conditionals or hardcoded language references
- ✅ Adding new language requires only creating language package
- ✅ Complete adherence to Clean Architecture principles

---

## 📚 ARCHIVED: COMPLETED WORK

### **AnkiBackend Refactoring (2025-01-16)**
- ✅ Complete language-agnostic transformation
- ✅ Field processing delegation pattern implemented
- ✅ Zero German business logic in backend

### **Documentation Consolidation (2025-01-14)**
- ✅ Technical debt documents consolidated
- ✅ Coding standards documents consolidated
- ✅ Component inventory verification complete

### **Multi-Language Architecture Phase 2 (2025-01-08)**
- ✅ German Record System - 13 record classes extracted
- ✅ Template Migration - 54 German templates moved
- ✅ Architecture Foundation established

### **Previous Major Milestones**
- ✅ MediaGenerationCapable Protocol Migration
- ✅ Legacy Code Removal
- ✅ Code Quality Standards achieved