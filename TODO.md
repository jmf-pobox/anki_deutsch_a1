# Project TODO - Current Status

Last updated: 2025-01-15

## 🚨 CRITICAL PRIORITY

### **PRIORITY 1: AnkiBackend Language-Agnostic Refactoring** 🔴 **CRITICAL**

**Problem**: `src/langlearn/core/backends/anki_backend.py` has extensive hardcoded German imports that violate the multi-language architecture and block adding new languages.

**Status**: ✅ **Multi-language foundation 75% complete**, ⚠️ **AnkiBackend refactoring pending**

#### **Incremental Implementation Plan**

Each step must pass quality gates before proceeding to the next:

**Step 1: Abstract Domain Model Interface** (Risk: Low, 1-2 days)
- Create `LanguageDomainModel` protocol in `src/langlearn/protocols/domain_model_protocol.py`
- Define common methods all domain models must implement (`get_combined_audio_text()`, etc.)
- Validate protocol compiles and imports work
- **Quality Gates**: `hatch run check` passes

**Step 2: Create Domain Model Factory Protocol** (Risk: Low, 1 day)
- Create `DomainModelFactory` protocol in language protocol
- Add `get_domain_model_factory()` method to `Language` protocol
- Update `GermanLanguage` to return German domain model factory
- **Quality Gates**: All tests pass, no MyPy errors

**Step 3: Update AnkiBackend to use domain model factory** ✅ **PARTIALLY COMPLETE**
- ✅ Updated AnkiBackend constructor to accept Language parameter
- ✅ Replaced `_create_domain_model_from_record()` with `language.create_domain_model()`
- ✅ All tests pass with zero MyPy errors
- ⚠️ **DESIGN VIOLATION DISCOVERED**: AnkiBackend still has German-specific imports and logic

**Step 3b: Complete AnkiBackend Language-Agnostic Design** (Risk: Medium, 1-2 days)
- Remove German imports that violate architecture:
  - `from langlearn.languages.german.records.factory import create_record`
  - `from langlearn.languages.german.services.media_enricher import StandardMediaEnricher`
- Remove hardcoded German note type mapping logic (lines ~306-326):
  - `"German Noun": "noun"`, `"German Adjective": "adjective"`, etc.
- Add missing Language protocol methods:
  - `create_record_from_csv(record_type, fields) -> BaseRecord`
  - `get_media_enricher() -> MediaEnricherProtocol`
  - `get_note_type_mappings() -> dict[str, str]`
- **Quality Gates**: AnkiBackend has zero German imports, all language logic delegated to protocols

**Step 4: Replace German Record Factory** (Risk: Low, 1 day)
- Move record creation from German factory to Language protocol
- Add `create_record_from_csv()` method to Language protocol
- Update GermanLanguage to implement record creation
- **Quality Gates**: Record processing works through language protocol

**Step 5: Replace German MediaEnricher** (Risk: Medium, 1-2 days)
- Create `MediaEnricherProtocol` for language-agnostic media enrichment
- Add `get_media_enricher()` method to Language protocol
- Update GermanLanguage to provide StandardMediaEnricher
- **Quality Gates**: Media generation works, audio/image files generated correctly

**Step 6: Move German Note Type Mappings** (Risk: Low, 1 day)
- Add `get_note_type_mappings()` method to Language protocol
- Move hardcoded German mappings to GermanLanguage implementation
- **Quality Gates**: Generated decks have correct note type names

**Total Estimated Duration**: 7-12 days with proper testing between each step

### **PRIORITY 2: COMPLETED WORK** ✅
**Multi-Language Architecture Foundation**:
- ✅ Records: Core infrastructure extracted, German records properly organized
- ✅ Language System: Protocol-based registry with German implementation
- ✅ Template System: Language-agnostic resolution via protocol
- ✅ German Package: Models, services, records, templates properly located
- ✅ Data Structure: Already organized as `languages/{language}/{deck}/`

### **PRIORITY 3: Future Enhancement Opportunities** 🟡 LOW PRIORITY

**Article Cloze System Enhancement**:
- Re-enable ArticleApplicationService for noun-article practice cards
- Fix Context card unique audio generation (currently produces blank audio)
- Architectural redesign for cloze card media processing

**Code Quality Improvements**:
- ServiceContainer refactoring - Remove Optional/None abuse patterns
- Legacy code removal - Any remaining commented out or deprecated patterns

## 🎯 SUCCESS METRICS

**Current State (2025-01-15)**:
- ✅ Multi-language architecture: 75% complete
- ✅ All 617 unit tests passing + 16 integration tests
- ✅ MyPy strict mode: 0 errors across 122 files
- ✅ Code quality: Perfect Ruff compliance
- ✅ Language-agnostic template system implemented
- ✅ German package properly organized per ENG-PACKAGING.md

**Target State**:
- 🎯 AnkiBackend language-agnostic refactoring complete
- 🎯 Multi-language architecture 100% compliant
- 🎯 Ready for Russian/Korean language addition
- 🎯 Zero hardcoded language references in core components

---

## 📚 ARCHIVED: COMPLETED WORK

### **Documentation Consolidation (2025-01-14)**
- ✅ **Technical debt documents** - 3 documents consolidated into ENG-TECHNICAL-DEBT.md
- ✅ **Coding standards documents** - 4 documents consolidated into ENG-CODING-STANDARDS.md
- ✅ **Component inventory verification** - All components verified against actual codebase
- ✅ **Architecture status updates** - Implementation status accurately documented

### **Multi-Language Architecture Phase 2 (2025-01-08)**
- ✅ **German Record System** - 13 record classes extracted and organized
- ✅ **Template Migration** - 54 German templates moved to language-specific package
- ✅ **Architecture Foundation** - Language-first organization established

### **Previous Major Milestones**
- ✅ **MediaGenerationCapable Protocol Migration** - Modern dataclass + protocol pattern implemented
- ✅ **Legacy Code Removal** - Significant codebase cleanup and modernization
- ✅ **Code Quality Standards** - PEP 8 compliance and type safety achieved