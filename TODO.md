# Project TODO - German Grammar Alignment & CSV Standardization

Last updated: 2025-08-22 

## 🚨 CRITICAL PRIORITY - German Grammar Alignment

**STATUS**: 📋 **ANALYSIS COMPLETE** - Major grammar alignment issues identified requiring immediate action

### Gap Analysis Summary:
- **Missing Files**: 8 critical files needed for proper German grammar
- **Files to Modify**: 3 files need major restructuring
- **Files to Deprecate**: 1 file (negations.csv) needs redistribution
- **Integration Needed**: 6 unintegrated files awaiting system integration

---

## 📊 DETAILED GAP ANALYSIS

### CRITICAL GAPS - Missing Files (8 files)

**PRIORITY 1: Articles System (2 files) - MOST CRITICAL**
- 🚨 **`articles.csv`** - Definite articles (der/die/das) with case declensions - **MISSING**
- 🚨 **`indefinite_articles.csv`** - Indefinite articles (ein/eine) with cases - **MISSING**
- **Impact**: Critical pedagogical gap - students cannot learn German gender/case system

**PRIORITY 2: Proper Pronoun Classification (5 files)**
- 📋 **`possessive_pronouns.csv`** - mein, dein, sein, etc. - **MISSING**
- 📋 **`demonstrative_pronouns.csv`** - dieser, jener, etc. - **MISSING**
- 📋 **`interrogative_pronouns.csv`** - wer, was, welcher, etc. - **MISSING**
- 📋 **`reflexive_pronouns.csv`** - mich, dich, sich, etc. - **MISSING**
- 📋 **`indefinite_pronouns.csv`** - man, jemand, etwas, etc. - **MISSING**

**PRIORITY 3: Negative Articles (1 file)**
- 📋 **`negative_articles.csv`** - kein, keine with declensions - **MISSING**

### MAJOR RESTRUCTURING - Files to Modify (3 files)

**CRITICAL REDISTRIBUTION**
- ⚠️ **`negations.csv`** - Contains 4 different grammar classes mixed together - **NEEDS REDISTRIBUTION**
  - `nicht, nie, niemals` → move to `adverbs.csv`
  - `kein, keine` → move to new `negative_articles.csv`
  - `nichts, niemand` → move to new `indefinite_pronouns.csv`
  - `weder...noch` → move to `conjunctions.csv`

**INTEGRATION NEEDED**
- 🔧 **`other_pronouns.csv`** - Arbitrary category, needs proper grammatical classification
- 🔧 **`personal_pronouns.csv`** - Valid but unintegrated

### SYSTEM INTEGRATION - Unintegrated Files (6 files)

**Ready for Integration**
- 🔧 **`cardinal_numbers.csv`** - Numbers 1-100 - **UNINTEGRATED**
- 🔧 **`ordinal_numbers.csv`** - First, second, third - **UNINTEGRATED**  
- 🔧 **`conjunctions.csv`** - und, aber, oder - **UNINTEGRATED**
- 🔧 **`interjections.csv`** - Ach, Oh, Na ja - **UNINTEGRATED**
- 🔧 **`personal_pronouns.csv`** - ich, du, er, sie - **UNINTEGRATED**
- 🔧 **`other_pronouns.csv`** - Needs reclassification first

---

## 🎯 IMPLEMENTATION PLAN

### Phase 1: CRITICAL FIXES (Week 1) - HIGHEST PRIORITY

**TASK 1.1: Create Articles System (4-6 hours)**
- [ ] Create `articles.csv` with definite articles (der/die/das) + all case declensions
- [ ] Create `indefinite_articles.csv` with ein/eine + all case declensions  
- [ ] Create `negative_articles.csv` with kein/keine + all case declensions
- [ ] Add ArticleRecord, IndefiniteArticleRecord, NegativeArticleRecord classes
- [ ] Create article card templates for gender/case practice

**TASK 1.2: Fix Negation Misclassification (2-3 hours)**
- [ ] Redistribute `negations.csv` content to proper grammatical categories:
  - [ ] Move `nicht, nie, niemals, nirgends` → `adverbs.csv`
  - [ ] Move `kein, keine, keinen` → `negative_articles.csv`
  - [ ] Move `nichts, niemand` → new `indefinite_pronouns.csv`
  - [ ] Move `weder...noch` → `conjunctions.csv`
- [ ] Update CSV specifications to reflect changes
- [ ] Deprecate `negations.csv` file

**TASK 1.3: Critical System Integration (3-4 hours)**
- [ ] Integrate `personal_pronouns.csv` - Create PersonalPronounRecord
- [ ] Integrate `conjunctions.csv` - Create ConjunctionRecord
- [ ] Update RecordMapper for new record types
- [ ] Add to deck_builder.py mapping

### Phase 2: PRONOUN SYSTEM RESTRUCTURING (Week 2)

**TASK 2.1: Complete Pronoun Classification (6-8 hours)**
- [ ] Analyze `other_pronouns.csv` and reclassify content
- [ ] Create proper pronoun category files:
  - [ ] `possessive_pronouns.csv` - mein, dein, sein
  - [ ] `demonstrative_pronouns.csv` - dieser, jener
  - [ ] `interrogative_pronouns.csv` - wer, was, welcher
  - [ ] `reflexive_pronouns.csv` - mich, dich, sich
  - [ ] `indefinite_pronouns.csv` - man, jemand, etwas
- [ ] Create corresponding Record classes for each type
- [ ] Add pronoun declension patterns for A1 level

**TASK 2.2: System Integration (4-5 hours)**
- [ ] Update RecordMapper to handle all new pronoun types
- [ ] Create card templates for each pronoun category
- [ ] Add comprehensive validation rules
- [ ] Update CSV specification documentation

### Phase 3: COMPLETE INTEGRATION (Week 3)

**TASK 3.1: Number System Integration (2-3 hours)**
- [ ] Integrate `cardinal_numbers.csv` - Create CardinalNumberRecord
- [ ] Integrate `ordinal_numbers.csv` - Create OrdinalNumberRecord
- [ ] Add number-specific validation rules
- [ ] Create number practice card templates

**TASK 3.2: Grammar Components Integration (2-3 hours)**  
- [ ] Integrate `interjections.csv` - Create InterjectionRecord
- [ ] Update system to handle all 14 word types
- [ ] Verify complete German grammar coverage per PM-GERMAN-GRAMMAR.md

**TASK 3.3: Final Validation & Testing (3-4 hours)**
- [ ] Verify all CSV files meet PROD-CSV-SPEC.md standards
- [ ] Ensure all "english" column naming is consistent
- [ ] Run comprehensive test suite
- [ ] Update documentation to reflect complete grammar coverage

---

## 📈 SUCCESS METRICS

### Technical Metrics
- [ ] **German Grammar Completeness**: 10/10 word classes properly represented
- [ ] **Article System**: 48+ article entries (4 cases × 3 genders × definite/indefinite)
- [ ] **Pronoun Coverage**: 5 proper pronoun categories with declensions
- [ ] **CSV Standards**: 100% compliance with PROD-CSV-SPEC.md
- [ ] **Quality Gates**: All tests pass, 0 MyPy errors, coverage maintained

### Pedagogical Metrics  
- [ ] **Gender Learning**: Students can practice articles separately from nouns
- [ ] **Case System**: Systematic coverage of all 4 German cases
- [ ] **Grammar Clarity**: No mixed grammatical categories
- [ ] **A1 Compliance**: Full coverage of CEFR A1 grammatical requirements

---

## 🔥 RISK ASSESSMENT

### HIGH RISK
- **Negation Redistribution**: Breaking change that affects existing cards
- **Pronoun Restructuring**: May impact existing other_pronouns.csv users

### MITIGATION STRATEGY
- **Dual Support Period**: Keep deprecated files while adding new structure
- **Migration Scripts**: Automatic conversion tools for existing decks
- **Backward Compatibility**: Maintain old paths during transition
- **Testing**: Comprehensive validation before removing deprecated files

---

## 📋 IMMEDIATE NEXT ACTIONS (TODAY)

1. **START HERE**: Create articles.csv with complete case declension system
2. **HIGH PRIORITY**: Redistribute negations.csv to proper grammatical categories  
3. **INTEGRATION**: Add personal_pronouns.csv and conjunctions.csv to system
4. **DOCUMENTATION**: Update CSV specs to reflect grammatical requirements

---

## 🎯 LONG-TERM VISION

Once grammar alignment is complete, system will provide:
- ✅ **Pedagogically Correct**: Proper German grammatical classification
- ✅ **Complete A1 Coverage**: All essential word types for basic German
- ✅ **Gender/Case Mastery**: Dedicated article practice system
- ✅ **Scalable Foundation**: Clean architecture for A2/B1 expansion

**Target Completion**: 3 weeks for complete German grammar alignment
**Current Priority**: Phase 1 critical fixes to address major pedagogical gaps

---

## 🚀 BEYOND GRAMMAR ALIGNMENT

### Phase 4: Multi-Deck Support (Future)
- Multiple proficiency levels (A1, A2, B1)
- Topic-based decks (Business, Travel, Academic)
- Custom vocabulary workflows

### Phase 5: Multi-Language Expansion (Future)  
- Russian: Cyrillic, 6-case system, verbal aspects
- Korean: Hangul, honorific system, complex verb endings
- Architecture ready for rapid language addition

---

*German grammar alignment is foundational - everything else builds upon this solid pedagogical base.*