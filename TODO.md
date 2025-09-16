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

**Step 3: Replace Direct German Model Imports** (Risk: Medium, 2-3 days)
- Remove lines 28-34 hardcoded German model imports from `anki_backend.py`
- Replace with language-agnostic domain model creation via protocol
- Modify `__init__()` to accept language parameter and resolve domain models via registry
- **Quality Gates**: All existing tests pass, deck generation works

**Step 4: Abstract Note Type Names** (Risk: Medium, 2-3 days)
- Remove hardcoded German note type names (lines 308-326)
- Move note type naming to language protocol (`get_note_type_name(card_type)`)
- Update German language to provide German-specific naming
- **Quality Gates**: Generated decks have correct note type names

**Step 5: Replace German Record Factory** (Risk: Medium, 1-2 days)
- Remove line 35 German record factory import
- Use language protocol `get_record_factory()` method
- **Quality Gates**: Record processing works through language resolution

**Step 6: Replace German MediaEnricher** (Risk: High, 2-3 days)
- Remove line 36 hardcoded German media enricher import
- Create media enricher factory in language protocol
- Refactor media generation to work through language protocol
- **Quality Gates**: Media generation works, audio/image files generated correctly

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