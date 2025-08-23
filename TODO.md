# Project TODO - Remaining Tasks

Last updated: 2025-08-23

## 🚨 HIGH PRIORITY - Anki Validation Layer Implementation

**BACKGROUND**: After experiencing $791 in wasted costs from false "fix" claims, a verification gap was identified. Current approach validates Python code but cannot verify actual Anki application behavior.

### **TASK 1.1: Create AnkiValidator Class** 🔴 HIGH PRIORITY
- **File**: `src/langlearn/validators/anki_validator.py`  
- **Purpose**: Validate content will work correctly in Anki application
- **Functions Needed**:
  - `validate_cloze_card(content: str, fields: dict) -> tuple[bool, list[str]]`
  - `validate_field_references(template: str, fields: dict) -> bool`
  - `validate_media_paths(card_content: str) -> bool`
  - `detect_blank_cards(rendered: str) -> bool`

### **TASK 1.2: Create AnkiRenderSimulator Class** 🔴 HIGH PRIORITY
- **File**: `src/langlearn/testing/anki_simulator.py`
- **Purpose**: Simulate exactly what Anki will display to users
- **Functions Needed**:
  - `simulate_card_display(note_data: dict, template: str) -> str`
  - `render_cloze_deletion(content: str) -> str` 
  - `apply_field_substitution(template: str, fields: dict) -> str`
  - `detect_rendering_issues(rendered: str) -> list[str]`

### **TASK 1.3: Create Validation Test Suite** 🔴 HIGH PRIORITY
- **File**: `tests/test_anki_validator.py`
- **Purpose**: Comprehensive testing of validation logic
- **Test Cases Needed**:
  - Blank card detection (empty fields, missing cloze)
  - Invalid cloze syntax (`{{c1:}}`, nested cloze)
  - Missing field references (`{{NonExistentField}}`)
  - Media path validation (`[sound:missing.mp3]`)

### **TASK 1.4: Integrate with Hatch Commands** 🔴 HIGH PRIORITY  
- **Files**: `pyproject.toml`, validation scripts
- **Purpose**: Add `validate-anki` and `simulate-cards` commands
- **Implementation**:
  - `hatch run validate-anki` → Run AnkiValidator on all generated cards
  - `hatch run simulate-cards` → Run AnkiRenderSimulator on test cases
  - Integrate with existing quality gate workflow

### **TASK 1.5: Create Debug Deck Generator** 🟡 MEDIUM PRIORITY
- **File**: `src/langlearn/debug/debug_deck_generator.py`  
- **Purpose**: Generate minimal decks for user issue reproduction
- **Use Cases**:
  - Blank card reproduction
  - Template syntax validation
  - User-reported issue isolation

---

## 🎯 LEGACY CODE CLEANUP

### **TASK 2.1: Legacy Template Cleanup** 🟡 MEDIUM PRIORITY
- [ ] **Remove obsolete article templates**: Clean up old template files that are no longer used
  - `artikel_gender_DE_de_*.html` (replaced by cloze templates)  
  - `artikel_context_DE_de_*.html` (replaced by cloze templates)
  - `noun_article_recognition_DE_de_*.html` (old system)
  - `noun_case_context_DE_de_*.html` (old system)
- [ ] **Clean up legacy field mappings**: Remove complex field mappings from CardBuilder

### **TASK 2.2: Legacy Code Identification** 🟡 MEDIUM PRIORITY
- [ ] **Audit ArticlePatternProcessor**: Remove old template-based methods (`_create_gender_recognition_card`, `_create_case_context_card`)
- [ ] **Clean up field mappings**: Remove complex article template field mappings
- [ ] **Legacy test cleanup**: Update or remove tests that cover obsolete functionality

### **TASK 2.3: Documentation Updates** 🟡 MEDIUM PRIORITY
- [ ] **Update ARTICLE.md**: Mark legacy sections as deprecated  
- [ ] **Update code comments**: Remove outdated comments about template field mappings
- [ ] **Update README**: Reflect new cloze deletion approach

---

## 🔍 FUTURE CONSIDERATIONS

### **Validation System Scope Expansion** (Evaluate Priority)
**MISSING COVERAGE** for 20+ word types:
- **Verb cards**: Conjugation validation, separable verb handling, irregular forms
- **Noun cards**: Gender/case template validation, plural forms, article consistency  
- **Adjective cards**: Declension validation, comparative forms
- **Preposition cards**: Case dependency validation, usage contexts
- **Template validation**: HTML/CSS syntax, field mapping correctness

**RECOMMENDATION**: Prioritize based on user feedback and actual validation failures.

### **Next Phase Planning**
**Future Enhancements**:
- **Phase 4**: Apply cloze deletion approach to verbs and prepositions
- **Phase 5**: Comprehensive German grammar standardization  
- **Phase 6**: Audio integration, image optimization, multi-level learning

---

## 📋 PRIORITY SUMMARY

**🔴 HIGH PRIORITY**:
1. AnkiValidator Class implementation
2. AnkiRenderSimulator Class implementation  
3. Validation Test Suite creation
4. Hatch command integration

**🟡 MEDIUM PRIORITY**:
1. Legacy template cleanup
2. Legacy code identification and removal
3. Documentation updates
4. Debug deck generator

**🔵 LOW PRIORITY / FUTURE**:
1. Validation system scope expansion
2. Next phase feature planning