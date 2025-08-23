# Project TODO - Article Card Cloze Deletion Implementation

Last updated: 2025-08-23

## 🚨 CURRENT PRIORITY - Article Card Redesign

**STATUS**: 🔄 **IN PROGRESS** - Phase 1 Cloze Deletion Implementation

### Context
The current article card system has critical issues:
- Templates reference non-existent fields (`{{NounOnly}}`, `{{NounEnglish}}`) causing blank cards
- Pedagogically weak: shows "_____ Haus" with no grammatical context  
- Complex 5-template system with 22+ field mappings prone to errors

**Solution**: Migrate to Anki's native Cloze Deletion feature with German explanations

---

## 📋 PHASE 1: CLOZE DELETION IMPLEMENTATION

### 🎯 CURRENT TASKS (Week 1)

**TASK 1.1: Design and Documentation (IN PROGRESS)**
- [x] Phase 0: Create comprehensive ArticlePatternProcessor test coverage  
- [x] Fix all failing tests in test suite (6/6 tests now passing)
- [x] Design cloze deletion system with German explanations
- [x] Update ARTICLE.md with German explanation system
- [x] Update TODO.md with current task list
- [ ] Get design-guardian review of updated documentation

**TASK 1.2: German Explanation System (PENDING)**
- [ ] Implement German case explanation generator
- [ ] Create gender + case combination explanations
- [ ] Add article type explanations (bestimmt/unbestimmt/verneinend)

**TASK 1.3: Cloze Template Creation (PENDING)**
- [ ] Create cloze deletion templates for Anki
- [ ] Add "Text", "Explanation", "Image", "Audio" field structure
- [ ] Test cloze template rendering in Anki

**TASK 1.4: ArticlePatternProcessor Rewrite (PENDING)**
- [ ] Add `_create_gender_cloze_card()` method
- [ ] Add `_create_case_cloze_card()` method  
- [ ] Replace template-based card generation with cloze generation
- [ ] Update field mappings to use cloze structure

### 🎯 PHASE 1 SUCCESS CRITERIA

#### Technical Requirements
- [ ] **Zero template-field mismatches**: No more blank cards
- [ ] **German explanations**: All explanations in German for immersive learning
- [ ] **Maintained functionality**: Still 5 cards per article record
- [ ] **Simplified architecture**: Single "Text" field vs 22+ field mappings
- [ ] **Test coverage**: All cloze generation methods tested

#### Pedagogical Requirements  
- [ ] **Contextual learning**: Full sentences instead of "_____ Haus"
- [ ] **Case understanding**: Clear German explanations of when to use each case
- [ ] **Grammar reinforcement**: "Akkusativ (wen/was? direktes Objekt)" format
- [ ] **Article comprehension**: Students understand why specific articles are used

#### Examples of Success
**Before (Broken)**:
- Card shows: "_____ Haus" (no context)
- No explanation of why "das" is correct
- Template-field mismatch causes blank cards

**After (Cloze)**:
- Card shows: "_____ Haus ist sehr groß" (contextual)
- Answer: "**Das** Haus ist sehr groß"  
- Explanation: "Neutrum - Nominativ (wer/was? Subjekt des Satzes)"

---

## 📋 PHASE 2: INTEGRATION & TESTING (Week 2)

### 🎯 INTEGRATION TASKS (PLANNED)

**TASK 2.1: CardBuilder Integration**
- [ ] Update CardBuilder field mappings for cloze cards
- [ ] Add "artikel_gender_cloze" and "artikel_context_cloze" support
- [ ] Simplify from 22+ fields to 4 fields: Text, Explanation, Image, Audio

**TASK 2.2: Backend Integration**  
- [ ] Update AnkiBackend note type mappings
- [ ] Add cloze deletion note type support
- [ ] Test Anki deck generation with cloze cards

**TASK 2.3: Template System Cleanup**
- [ ] Remove 6 obsolete article template files
- [ ] Clean up complex field mappings  
- [ ] Update template service for cloze support

### 🎯 TESTING & VALIDATION

**TASK 2.4: Comprehensive Testing**
- [ ] Unit tests for cloze text generation
- [ ] Integration tests with real German sentences
- [ ] Manual testing: Import deck and verify in Anki
- [ ] Verify all quality gates pass (MyPy, Ruff, tests)

---

## 📋 PHASE 3: VALIDATION & DEPLOYMENT (Week 3)

### 🎯 VALIDATION TASKS (PLANNED)

**TASK 3.1: End-to-End Testing**
- [ ] Generate complete article deck with cloze cards
- [ ] Test all article types: bestimmt, unbestimmt, verneinend
- [ ] Test all cases: Nominativ, Akkusativ, Dativ, Genitiv  
- [ ] Test all genders: Maskulin, Feminin, Neutrum

**TASK 3.2: Performance & Quality**
- [ ] Measure card generation performance improvement
- [ ] Verify reduced complexity (6 templates → 0, 44+ fields → 8)
- [ ] Confirm maintained test coverage  
- [ ] Document lessons learned

---

## 📈 SUCCESS METRICS

### Technical Metrics
- [ ] **Zero Template Errors**: No more field mismatch issues
- [ ] **Reduced Complexity**: 85% reduction in field mappings
- [ ] **Test Coverage**: Maintained 100% ArticlePatternProcessor coverage
- [ ] **Quality Gates**: All MyPy, Ruff, test requirements met

### Pedagogical Metrics
- [ ] **Contextual Learning**: Students see complete German sentences
- [ ] **Case Comprehension**: Clear German explanations for each case
- [ ] **Grammar Retention**: Immersive German explanations reinforce learning
- [ ] **User Experience**: Cards provide enough context to answer correctly

---

## 🔥 RISK ASSESSMENT

### LOW RISK  
- **Cloze deletion is native Anki**: Well-tested, reliable feature
- **Comprehensive test coverage**: 21 tests covering all edge cases
- **Gradual implementation**: Can implement alongside existing system

### MEDIUM RISK
- **ArticlePatternProcessor rewrite**: Core logic changes need thorough testing
- **Field mapping updates**: Must ensure CardBuilder handles cloze fields correctly

### MITIGATION STRATEGY
- **Test-first approach**: Modify existing tests before changing implementation
- **Parallel development**: Keep old system running while building new
- **Quality gates**: No code changes without passing all tests

---

## 📋 IMMEDIATE NEXT ACTIONS (TODAY)

1. **GET DESIGN REVIEW**: Have design-guardian review ARTICLE.md and TODO.md
2. **IMPLEMENT GERMAN EXPLANATIONS**: Create explanation generation system
3. **CREATE CLOZE TEMPLATES**: Build Anki cloze deletion templates  
4. **START PROCESSOR REWRITE**: Begin ArticlePatternProcessor cloze methods

---

## 🎯 LONG-TERM VISION

**Phase 1 Complete**: Article cards use pedagogically sound cloze deletion
**Phase 2 Future**: Apply same cloze approach to other word types (verbs, prepositions)
**Phase 3 Future**: German grammar alignment and CSV standardization

**Target Completion**: 3 weeks for complete article card redesign
**Current Priority**: Get design approval and implement German explanation system

---

*Once article cards are pedagogically sound, we can address the broader German grammar alignment identified in previous analysis.*