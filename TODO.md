# Project TODO - Remaining Tasks

Last updated: 2025-01-23

## 🚨 HIGH PRIORITY - Anki Validation Layer Implementation

**BACKGROUND**: After experiencing many false "fix" claims, a verification gap was identified. Current approach validates Python code but cannot verify actual Anki application behavior.

### **TASK 1.1: Create AnkiValidator Class** ✅ COMPLETED
- **File**: `src/langlearn/validators/anki_validator.py`  
- **Purpose**: Validate content will work correctly in Anki application
- **Functions Needed**:
  - ✅ `validate_cloze_card(content: str, fields: dict) -> tuple[bool, list[str]]`
  - ✅ `validate_field_references(template: str, fields: dict) -> bool`
  - ✅ `validate_media_paths(card_content: str) -> bool`
  - ✅ `detect_blank_cards(rendered: str) -> bool`

### **TASK 1.2: Create AnkiRenderSimulator Class** ✅ COMPLETED
- **File**: `src/langlearn/testing/anki_simulator.py`
- **Purpose**: Simulate exactly what Anki will display to users
- **Functions Needed**:
  - ✅ `simulate_card_display(note_data: dict, template: str) -> str`
  - ✅ `render_cloze_deletion(content: str) -> str` 
  - ✅ `apply_field_substitution(template: str, fields: dict) -> str`
  - ✅ `detect_rendering_issues(rendered: str) -> list[str]`

### **TASK 1.3: Create Validation Test Suite** ✅ COMPLETED
- **File**: `tests/test_anki_validator.py`
- **Purpose**: Comprehensive testing of validation logic
- **Test Cases Needed**:
  - ✅ Blank card detection (empty fields, missing cloze)
  - ✅ Invalid cloze syntax (`{{c1:}}`, nested cloze)
  - ✅ Missing field references (`{{NonExistentField}}`)
  - ✅ Media path validation (`[sound:missing.mp3]`)

### **TASK 1.4: Integrate with Hatch Commands** ✅ COMPLETED  
- **Files**: `pyproject.toml`, validation scripts
- **Purpose**: Add `validate-anki` and `simulate-cards` commands
- **Implementation**:
  - ✅ `hatch run validate-anki` → Run AnkiValidator on all generated cards
  - ✅ `hatch run simulate-cards` → Run AnkiRenderSimulator on test cases
  - ✅ Integrate with existing quality gate workflow

### **TASK 1.5: Create Debug Deck Generator** ✅ COMPLETED
- **File**: `src/langlearn/debug/debug_deck_generator.py`  
- **Purpose**: Generate minimal decks for user issue reproduction
- **Use Cases**:
  - ✅ Blank card reproduction
  - ✅ Template syntax validation
  - ✅ User-reported issue isolation

---

## 🔍 PHASE 1: VALIDATION INTEGRATION (IMMEDIATE PRIORITY)

### **TASK 2.1: Integrate Validation into Card Generation Pipeline** ✅ COMPLETED
**Current Status**: Validation classes exist but are not integrated into the main card generation workflow.

**Why This Must Come First**: Without validation integration, you cannot safely detect problems when making other changes.

**Implementation Needed**:
- **File**: `src/langlearn/services/card_builder.py`
- **Purpose**: Add validation hooks after card generation to catch issues before deck creation
- **Functions Needed**:
  - ✅ `validate_generated_card(card_data: dict) -> tuple[bool, list[str]]`
  - ✅ `validate_deck_before_export(deck: Deck) -> tuple[bool, list[str]]`
  - ✅ Integration with existing quality gates

**Success Criteria**: 
- ✅ All generated cards pass validation before deck export
- ✅ Validation failures are logged with actionable error messages
- ✅ Integration maintains current performance levels

---

## 🔍 PHASE 2: COMPLETE ARTICLE SYSTEM (AFTER VALIDATION WORKS)

### **TASK 3.1: Re-enable ArticleApplicationService** 🔴 HIGH PRIORITY
**Current Status**: ArticleApplicationService is commented out, preventing noun-article practice cards.

**Why This Must Come Second**: This is the main missing functionality that affects A1 learners, but you need validation working first to ensure the fix actually works.

**Implementation Needed**:
- **File**: `src/langlearn/deck_builder.py` (lines 790-803)
- **Purpose**: Re-enable ArticleApplicationService for noun-article integration
- **Functions Needed**:
  - Uncomment ArticleApplicationService integration
  - Convert ArticleApplicationService to use cloze deletion format
  - Ensure noun-article cards generate correctly
  - Test integration with existing noun records

**Success Criteria**: Noun-article practice cards generate successfully and pass validation.

### **TASK 3.2: Fix Article Media Generation** 🔴 HIGH PRIORITY
**Current Status**: Article cloze cards have empty Image/Audio fields despite MediaEnricher support.

**Implementation Needed**:
- **File**: `src/langlearn/services/media_enricher.py`
- **Purpose**: Ensure article cards get proper media enrichment
- **Functions Needed**:
  - Debug why MediaEnricher doesn't populate article card media
  - Add proper UnifiedArticleRecord support to MediaEnricher
  - Verify media fields are correctly mapped in CardBuilder
  - Test media generation for article cards

**Success Criteria**: Article cloze cards display with images and audio.

---

## 🔍 PHASE 3: LEGACY CODE REMOVAL (AFTER ARTICLE SYSTEM WORKS)

### **TASK 4.1: Remove Legacy Domain Models and Card Generators** 🔴 HIGH PRIORITY
**Current Status**: Legacy domain models and card generators still exist but are not used.

**Why This Must Come Third**: Only after validation confirms the new system works perfectly and article system is complete.

**Files to Delete**:
```
src/langlearn/models/
├── noun.py                    # Legacy domain model
├── adjective.py               # Legacy domain model  
├── adverb.py                  # Legacy domain model
├── negation.py                # Legacy domain model
└── model_factory.py           # Legacy model factory

src/langlearn/cards/
├── base.py                    # Legacy card generator base
├── noun.py                    # Legacy noun card generator
├── adjective.py               # Legacy adjective card generator
├── adverb.py                  # Legacy adverb card generator
├── negation.py                # Legacy negation card generator
└── factory.py                 # Legacy card generator factory
```

### **TASK 4.2: Remove Legacy Infrastructure** 🔴 HIGH PRIORITY
**Current Status**: Legacy compatibility layer and fallback methods still exist.

**Methods to Remove**:
```
src/langlearn/services/article_pattern_processor.py:
├── _create_gender_recognition_card()    # Legacy non-cloze method
└── _create_case_context_card()          # Legacy non-cloze method

src/langlearn/services/card_builder.py:
├── _load_legacy_models_from_records()   # Legacy compatibility layer
└── _generate_all_cards_legacy()         # Legacy fallback method

src/langlearn/deck_builder.py:
├── _load_legacy_models_from_records()   # Legacy model loading
├── _generate_all_cards_legacy()         # Legacy card generation
└── _record_to_domain_model()            # Legacy conversion method
```

### **TASK 4.3: Remove Legacy Templates and Field Mappings** 🔴 HIGH PRIORITY
**Current Status**: Legacy templates and complex field mappings still exist.

**Files to Delete**:
```
src/langlearn/templates/
├── artikel_gender_DE_de_*.html     # Legacy article templates
├── artikel_context_DE_de_*.html    # Legacy article templates
├── noun_article_recognition_DE_de_*.html  # Legacy noun templates
└── noun_case_context_DE_de_*.html  # Legacy noun templates
```

**Field Mappings to Remove from CardBuilder**:
```
src/langlearn/services/card_builder.py:
├── "artikel_gender": [22 legacy fields]           # Replace with cloze mapping
├── "artikel_context": [25 legacy fields]          # Replace with cloze mapping  
├── "noun_article_recognition": [12 legacy fields] # Replace with cloze mapping
└── "noun_case_context": [17 legacy fields]        # Replace with cloze mapping
```

### **TASK 4.4: Remove Additional Dead Code** 🔴 HIGH PRIORITY
**Current Status**: Additional dead code identified in ENG-DEAD-CODE.md analysis.

**Files to Delete**:
```
src/langlearn/services/
├── domain_media_generator.py  # Legacy media generation
└── verb_card_multiplier.py    # Dead code (71 statements, 0% coverage)

src/langlearn/testing/
└── card_specification_generator.py  # Dead code (180 statements, 0% coverage)

src/langlearn/utils/
└── sync_api_key.py            # Dead code (24 statements, 0% coverage)
```

**Total Additional Dead Code**: 3 files (~275 statements)

### **TASK 4.5: Clean Up Dual Storage Pattern** 🔴 HIGH PRIORITY
**Current Status**: Records are stored in both new format AND converted to legacy domain models.

**Implementation Needed**:
- Remove parallel data storage
- Remove legacy media generation (`domain_media_generator.py`)
- Clean up imports and references
- Update test suite to remove legacy-only tests
- Remove legacy model factory references
- Clean up __init__.py files for removed modules

---

## 🔍 PHASE 4: PERFORMANCE & POLISH (FINAL)

### **TASK 5.1: Create Validation Report System** 🟡 MEDIUM PRIORITY
**Purpose**: Provide detailed feedback on validation failures to help users fix issues.

**Implementation Needed**:
- **File**: `src/langlearn/validators/validation_reporter.py`
- **Functions Needed**:
  - `generate_validation_report(validation_results: list) -> str`
  - `export_validation_log(deck_name: str, results: list) -> Path`
  - Integration with logging system

### **TASK 5.2: Performance Optimization** 🟡 MEDIUM PRIORITY
**Current Issue**: Validation runs after card generation, which could be expensive for large decks.

**Implementation Needed**:
- **File**: `src/langlearn/validators/validation_optimizer.py`
- **Functions Needed**:
  - `batch_validate_cards(cards: list) -> list[tuple[bool, list[str]]]`
  - `parallel_validation_worker(card_batch: list) -> list[tuple[bool, list[str]]]`
  - Integration with existing async patterns

### **TASK 5.3: Documentation Updates** 🟡 MEDIUM PRIORITY
- **Update ARTICLE.md**: Mark legacy sections as deprecated  
- **Update code comments**: Remove outdated comments about template field mappings
- **Update README**: Reflect new cloze deletion approach
- **Update PROD-CARD-SPEC.md**: Remove references to disabled/inactive card types

---

## 📋 PRIORITY SUMMARY

**🔴 HIGH PRIORITY**:
1. ~~AnkiValidator Class implementation~~ ✅ **COMPLETED**
2. ~~AnkiRenderSimulator Class implementation~~ ✅ **COMPLETED**  
3. ~~Validation Test Suite creation~~ ✅ **COMPLETED**
4. ~~Hatch command integration~~ ✅ **COMPLETED**
5. ~~**PHASE 1**: Integrate validation into card generation pipeline~~ ✅ **COMPLETED**
6. **PHASE 2**: Complete Article System Migration (re-enable ArticleApplicationService)
7. **PHASE 2**: Fix Article Media Generation (ensure cloze cards get media)
8. **PHASE 3**: Complete legacy code removal (21+ files, 20+ methods, ~1000+ statements)

**🟡 MEDIUM PRIORITY**:
1. **PHASE 4**: Create validation report system
2. **PHASE 4**: Performance optimization for validation
3. **PHASE 4**: Documentation updates

**🔵 LOW PRIORITY / FUTURE**:
1. Validation system scope expansion
2. Next phase feature planning

---

## 🎯 IMMEDIATE NEXT ACTION

**TASK 2.1 COMPLETED** ✅ - Validation integration is now complete and working!

**Next Focus: TASK 3.1**: Re-enable ArticleApplicationService for noun-article integration. With validation now working, we can safely proceed to fix the article system.

**Success Criteria**: 
- Noun-article practice cards generate successfully and pass validation
- Article cloze cards display with images and audio

---

## ⚠️ CRITICAL DEPENDENCY WARNING

**The current TODO organization had logical ordering problems that could cause system failures:**

- ❌ **Legacy cleanup was scheduled BEFORE validation integration**
- ❌ **Article system fixes were mixed with validation tasks**
- ❌ **No clear dependency chain between tasks**

**New organization ensures:**
- ✅ **Validation works FIRST** (safety net)
- ✅ **Article system completes SECOND** (core functionality)
- ✅ **Legacy cleanup happens THIRD** (after system is stable)
- ✅ **Performance optimization comes LAST** (after system is complete)

---

## 🎯 COMPLETE MIGRATION ROADMAP

**To achieve 100% Clean Pipeline Architecture, follow this exact order:**

1. **Phase 1 (IMMEDIATE)**: Validation Integration
   - Integrate AnkiValidator into card generation pipeline
   - This gives you the safety net to detect problems

2. **Phase 2 (NEXT)**: Complete Article System
   - Re-enable ArticleApplicationService
   - Fix media generation for article cards
   - Validate that the fix works using the new validation system

3. **Phase 3 (AFTER ARTICLE SYSTEM WORKS)**: Legacy Code Removal
   - Remove 21+ legacy files (~1000+ statements)
   - Remove legacy domain models and card generators
   - Remove legacy templates and field mappings
   - Remove additional dead code identified in analysis
   - Clean up dual storage pattern

4. **Phase 4 (FINAL)**: Performance & Polish
   - Validation report system
   - Performance optimization
   - Documentation updates

**Current Migration Status**: ~85% complete (Clean Pipeline works, but legacy code remains and ArticleApplicationService is disabled)

**Next Milestone**: Complete Phase 1 (Validation Integration) to enable safe migration of remaining components.

**Expected Code Reduction**: ~1000+ statements (18-20% of codebase) after Phase 3 completion.