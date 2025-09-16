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

**Step 3b: Complete AnkiBackend Language-Agnostic Design** ✅ **COMPLETED**
- ✅ Remove German imports that violate architecture:
  - ✅ `from langlearn.languages.german.records.factory import create_record`
  - ✅ `from langlearn.languages.german.services.media_enricher import StandardMediaEnricher`
- ✅ Remove hardcoded German note type mapping logic (lines ~306-326):
  - ✅ `"German Noun": "noun"`, `"German Adjective": "adjective"`, etc.
- ✅ Add missing Language protocol methods:
  - ✅ `create_record_from_csv(record_type, fields) -> BaseRecord`
  - ✅ `get_media_enricher() -> MediaEnricherProtocol`
  - ✅ `create_media_enricher() -> MediaEnricherProtocol`
  - ✅ `get_note_type_mappings() -> dict[str, str]`
- ✅ **Quality Gates**: AnkiBackend basic imports removed, protocol methods implemented

**Step 4: Complete `_process_fields_with_media` Language-Agnostic Refactoring** ✅ **COMPLETED**
**Problem**: Method contained extensive German-specific business logic that broke language-agnostic architecture

**Violations Resolved**:
- ✅ Removed hardcoded German note type names: `"German Artikel Gender Cloze"`, `"German Artikel Context Cloze"`
- ✅ Removed direct German model import: `from langlearn.languages.german.models.article import Article`
- ✅ Removed German grammatical logic: `artikel_typ="bestimmt"`, `geschlecht="maskulin"`, cases
- ✅ Removed German audio combination: `f"{article} {noun}, {plural}"`
- ✅ Removed hardcoded field ordering per record type: `if record_type == "noun": return [...]`

**Design Solution Implemented**: **Field Processing Delegation Pattern**
- ✅ Added `process_fields_for_anki()` method to Language protocol
- ✅ Moved all German logic from `_process_fields_with_media` to `GermanLanguage.process_fields_for_anki()`
- ✅ Updated AnkiBackend to pure delegation: `return self._language.process_fields_for_anki(note_type_name, fields, media_enricher)`
- ✅ **Quality Gates Passed**: AnkiBackend has zero German business logic, ~200 lines reduced to ~37 lines

**Step 5: German Field Processing Implementation** ✅ **COMPLETED**
- ✅ Moved cloze handling logic to GermanLanguage
- ✅ Moved record-specific field formatting to GermanLanguage
- ✅ Preserved German audio combination logic in German domain models
- ✅ All German note types handled correctly in language-specific code
- ✅ **Quality Gates Passed**: Deck generation produces identical output, all 636 tests pass

**ARCHITECTURAL ACHIEVEMENT**:
**AnkiBackend is now a pure, language-agnostic Anki API**
- Zero German imports or hardcoded logic
- Complete protocol-based delegation
- Ready for multi-language support (Russian, Korean, etc.)
- ~83% code reduction in critical method (240 lines → 37 lines)

**Step 6: Future Optimization - German Service Architecture** 🟡 **LOWER PRIORITY**
- Move German-specific field processing to dedicated service
- Create `GermanFieldProcessor` to handle cloze and record formatting
- Extract German audio generation patterns to reusable utility
- **Quality Gates**: Code organization follows German language package standards

**Total Duration**: ✅ **COMPLETED** - All critical language-agnostic refactoring complete

---

## 🏗️ ARCHITECTURAL DESIGN ANALYSIS

### **Field Processing Delegation Pattern** (Step 4 Solution)

**Current Problem**: `AnkiBackend._process_fields_with_media()` contains ~200 lines of German-specific business logic:

```python
# VIOLATIONS (to be removed):
if note_type_name in {"German Artikel Gender Cloze", "German Artikel Context Cloze"}:
    from langlearn.languages.german.models.article import Article  # Direct import!
    article_model = Article(artikel_typ="bestimmt", geschlecht="maskulin", ...)  # German grammar!

if record_type == "noun":
    combined = f"{article} {noun}, {plural}"  # German audio pattern!
    return [noun, article, english, plural, ...]  # German field order!
```

**Proposed Solution**: **Complete Delegation to Language Layer**

```python
# AnkiBackend (language-agnostic):
def _process_fields_with_media(self, note_type_name: str, fields: list[str]) -> list[str]:
    return self._language.process_fields_for_anki(note_type_name, fields)
```

```python
# GermanLanguage (German-specific logic):
def process_fields_for_anki(self, note_type_name: str, fields: list[str]) -> list[str]:
    # Handle all German note types, cloze logic, field formatting
    # Import German models locally within this method
    # Apply German grammatical rules and audio patterns
```

**Benefits**:
- ✅ **Zero German Logic in AnkiBackend**: Pure Anki API for any language
- ✅ **Language Encapsulation**: All German knowledge in German package
- ✅ **Future Language Support**: Russian/Korean can implement their own field processing
- ✅ **Maintainability**: German changes don't affect core Anki backend
- ✅ **Type Safety**: Protocol ensures all languages implement field processing

**Migration Strategy**:
1. Add `process_fields_for_anki()` to Language protocol
2. Copy existing German logic to `GermanLanguage.process_fields_for_anki()`
3. Replace AnkiBackend method body with single delegation call
4. Test identical deck generation output
5. Remove all German imports from AnkiBackend

---

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

**Current State (2025-01-16)**:
- ✅ Multi-language architecture: **100% complete**
- ✅ All 636 unit tests passing + 19 integration tests
- ✅ MyPy strict mode: 0 errors across 126 files
- ✅ Code quality: Perfect Ruff compliance
- ✅ Language-agnostic template system implemented
- ✅ German package properly organized per ENG-PACKAGING.md
- ✅ **AnkiBackend language-agnostic refactoring complete**
- ✅ **Zero hardcoded language references in core components**

**Achieved Target State**:
- ✅ AnkiBackend is now a pure, language-agnostic Anki API
- ✅ Multi-language architecture 100% compliant with protocols
- ✅ Ready for Russian/Korean language addition
- ✅ Complete separation of concerns: language logic in language packages

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