# German A1 Anki Project - Development Roadmap

## 🎯 Current Status: **FUNCTIONAL WITH TECHNICAL DEBT**

**Last Updated**: Current Date  
**Assessment**: Functional German A1 vocabulary deck generation with significant code quality gaps  
**Quality Score**: 4.5/10 (Functional but requires architectural improvements)  

### **Current State Summary**:
- ✅ **Functional**: 263 unit tests passing, deck generation working
- ❌ **Technical Debt**: 363 MyPy errors, 113 linting violations, 56.27% test coverage
- ⚠️ **Architecture**: Backend abstraction complete, but quality issues block production readiness

---

## 📊 **PRIORITY 1: Code Quality Foundation** 🚨

*Must complete before any new features - Production blocking issues*

### **1.1 Type Safety Recovery (Week 1-2)** - CRITICAL
**Priority**: HIGHEST - Blocks production deployment

- [ ] **Fix MyPy Strict Mode Violations**: 363 errors → 0 errors
  - [ ] Fix missing required arguments in model construction (37+ instances)
  - [ ] Remove unnecessary type ignore comments (25+ instances)
  - [ ] Add proper type hints to all functions and methods
  - [ ] Resolve generic type parameter issues
  - [ ] **Success Criteria**: `hatch run type` passes with zero errors

- [ ] **Import Structure Cleanup**: 26 relative imports → 0 relative imports
  - [ ] Convert all relative imports to absolute imports
  - [ ] Fix circular dependencies where they exist
  - [ ] Update all `from ..module` to `from langlearn.module` patterns
  - [ ] **Success Criteria**: `hatch run lint` passes import checks

### **1.2 Test Coverage Improvement (Week 2-3)** - CRITICAL
**Priority**: HIGHEST - Quality gate for all changes

- [ ] **Increase Overall Coverage**: 56.27% → 85%+ target
  - [ ] **Priority areas for coverage**:
    - [ ] `german_deck_builder.py`: 54.36% → 85%+ (main orchestrator)
    - [ ] `audio.py`: 54.93% → 85%+ (media generation)
    - [ ] `csv_service.py`: 50.00% → 85%+ (data loading)
    - [ ] `german_language_service.py`: 40.98% → 85%+ (language logic)
    - [ ] `pexels_service.py`: 43.61% → 85%+ (image integration)
  
- [ ] **Establish Coverage Gates**
  - [ ] Integrate `hatch run test-unit-cov` into mandatory workflow
  - [ ] Set up coverage reporting and tracking
  - [ ] Enforce coverage increase requirement for all PRs
  - [ ] **Success Criteria**: Coverage measured and improving with each change

### **1.3 Linting Compliance (Week 1)** - HIGH
**Priority**: HIGH - Code consistency and maintainability

- [ ] **Fix Linting Violations**: 113 violations → <10 target
  - [ ] Fix line length violations (46 instances)
  - [ ] Resolve import ordering and formatting issues  
  - [ ] Address variable naming and code style violations
  - [ ] **Success Criteria**: `hatch run ruff check --fix` resolves all auto-fixable issues

### **1.4 Mandatory Development Workflow Implementation**
- [ ] **Update Development Process**
  - [ ] Enforce workflow: tests → coverage → linting → formatting → tests
  - [ ] Add pre-commit hooks for quality gates
  - [ ] Document coverage requirements in development guides
  - [ ] **Success Criteria**: All developers follow consistent quality workflow

---

## 📊 **PRIORITY 2: Complete Anki API Migration** 🔄

*Architecture completion - Enable advanced features*

### **2.1 AnkiBackend Test Coverage (Week 4-6)**
**Goal**: Complete migration safety validation

- [ ] **Address AnkiBackend Coverage Gaps** (~30% → 85%+)
  - [ ] Test all 7 `_process_*_fields()` methods with German vocabulary data
  - [ ] Test German language service integration thoroughly
  - [ ] Test advanced features: media deduplication, database optimization
  - [ ] Test bulk operations and performance characteristics
  - [ ] **Reference**: Follow [`docs/ANKI_API_TESTPLAN.md`](docs/ANKI_API_TESTPLAN.md) structure

### **2.2 Production Migration Decision (Week 7)**
**Goal**: Safe backend selection based on comprehensive testing

- [ ] **Migration Readiness Assessment**
  - [ ] Compare backend performance and reliability metrics
  - [ ] Validate feature parity between genanki and AnkiBackend
  - [ ] Test production workloads with full German A1 dataset
  - [ ] **Success Criteria**: Clear recommendation for production backend

### **2.3 Backend Consolidation (Week 8)**
**Goal**: Streamline production architecture

- [ ] **Production Backend Selection**
  - [ ] Choose primary backend based on testing results
  - [ ] Update documentation and configuration
  - [ ] Plan deprecation timeline for secondary backend
  - [ ] **Success Criteria**: Single production backend with full confidence

---

## 📊 **PRIORITY 3: Multi-Language Architecture** 🌍

*Strategic foundation for expansion beyond German*

### **3.1 Language-Agnostic Design (Week 9-12)**
**Goal**: Support multiple languages without code changes

- [ ] **Externalize Hard-coded German Logic**
  - [ ] Move German-specific strings to configuration files
  - [ ] Create abstract language service interfaces
  - [ ] Implement language configuration loading system
  - [ ] Replace algorithmic grammar with external validated data
  - [ ] **Success Criteria**: Add new language by adding config files only

- [ ] **Multi-Language Service Architecture**
  - [ ] Create `LanguageService` abstract base class
  - [ ] Implement `GermanLanguageService` as concrete implementation
  - [ ] Design language configuration schema and validation
  - [ ] Create language-specific template systems
  - [ ] **Success Criteria**: Multi-language readiness score: 2/10 → 8/10

### **3.2 Configuration-Driven Grammar (Week 13-14)**
**Goal**: No hard-coded grammar rules in code

- [ ] **External Grammar Configuration**
  - [ ] Move German grammar rules to YAML/JSON configuration
  - [ ] Implement rule loading and validation system
  - [ ] Create grammar rule testing framework
  - [ ] Document grammar configuration schemas
  - [ ] **Success Criteria**: Zero hard-coded language strings in source code

---

## 📊 **PRIORITY 4: German Language Expansion** 🇩🇪

*Content expansion for comprehensive German A1+ support*

### **4.1 Additional Parts of Speech (Week 15-18)**
**Goal**: Complete German language coverage

- [ ] **Add Missing German Parts of Speech**
  - [ ] **Pronouns**: Personal, possessive, demonstrative, interrogative
    - [ ] Implement proper case declension handling
    - [ ] Add pronunciation integration for complex forms
  - [ ] **Articles**: Definite, indefinite with case system
    - [ ] Complete declension tables for all cases
    - [ ] Context-aware article selection
  - [ ] **Conjunctions**: Coordinating, subordinating with word order rules
    - [ ] Implement word order validation and examples
  - [ ] **Interjections**: Common German expressions
    - [ ] Audio integration for proper pronunciation

### **4.2 Advanced German Grammar Features (Week 19-22)**
**Goal**: Support intermediate (A2/B1) German features

- [ ] **Complex Grammar Support**
  - [ ] **Modal Verbs**: können, müssen, wollen, sollen, dürfen, mögen
    - [ ] Conjugation patterns and usage examples
  - [ ] **Past Tense**: Präteritum and Perfekt with proper auxiliary selection
  - [ ] **Subjunctive**: Konjunktiv II for polite requests
  - [ ] **Compound Words**: Recognition and breakdown for learning

- [ ] **Advanced Card Types**
  - [ ] Sentence construction exercises
  - [ ] Grammar pattern recognition cards
  - [ ] Contextual usage comparison cards
  - [ ] Cloze deletion exercises for grammar

### **4.3 German A1+ Content Expansion (Week 23-24)**
**Goal**: Complete A1 vocabulary with A2 foundation

- [ ] **Expand Vocabulary Categories**
  - [ ] **Thematic Vocabulary**: Family, food, travel, work, hobbies
  - [ ] **Frequency-Based Selection**: Most common 2000 German words
  - [ ] **Context Groups**: Related words with usage examples
  - [ ] **Cultural Context**: German-specific cultural references

---

## 🔧 **Continuous Quality Requirements**

*Must be maintained throughout all development phases*

### **Code Quality Gates (Every Change)**
- ✅ **Type Safety**: 100% MyPy strict compliance
- ✅ **Test Coverage**: Must increase with each change (use `hatch run test-unit-cov`)
- ✅ **All Tests Passing**: 263+ unit tests must pass
- ✅ **Linting**: Zero ruff violations
- ✅ **Documentation**: Update relevant docs/*.md files

### **Architecture Principles (Every Design Decision)**
- ✅ **Single Responsibility**: Each class has one clear purpose
- ✅ **Clean Architecture**: Proper dependency direction (Infrastructure → Domain)
- ✅ **Multi-Language Ready**: No hard-coded language logic
- ✅ **External Data**: Use validated data, never algorithmic grammar
- ✅ **Testability**: All business logic must be unit testable

---

## 🎯 **Success Metrics by Priority**

### **Priority 1 Success (Code Quality)**
- [ ] **Type Safety**: 0 MyPy errors (from 363)
- [ ] **Test Coverage**: 85%+ overall (from 56.27%)
- [ ] **Linting**: <10 violations (from 113)
- [ ] **Quality Score**: 8+/10 (from 4.5/10)

### **Priority 2 Success (Anki Migration)**
- [ ] **Backend Coverage**: AnkiBackend 85%+ tested
- [ ] **Production Ready**: Clear backend recommendation
- [ ] **Migration Complete**: Single production backend choice

### **Priority 3 Success (Multi-Language)**
- [ ] **Language Agnostic**: Add new language in <1 week
- [ ] **Configuration Driven**: Zero hard-coded language strings
- [ ] **Multi-Language Readiness**: 8+/10 (from 2/10)

### **Priority 4 Success (German Expansion)**
- [ ] **Complete A1 Coverage**: All major German parts of speech
- [ ] **A2 Foundation**: Basic intermediate grammar support
- [ ] **Cultural Context**: German-specific learning features

---

## 📋 **Implementation Notes**

### **Critical Path Dependencies**
1. **Must fix type safety** before adding new features (blocks development velocity)
2. **Must improve test coverage** before backend migration (safety requirement)
3. **Must complete backend migration** before multi-language work (architecture dependency)
4. **Must establish multi-language foundation** before German expansion (avoid rework)

### **Risk Mitigation**
- **Type Safety**: Incremental fixes with continuous validation
- **Coverage**: Focus on high-impact, untested areas first
- **Backend Migration**: Thorough testing before production switch
- **Multi-Language**: Design validation with second language prototype

### **Resource Requirements**
- **Weeks 1-3**: Code quality foundation (full focus)
- **Weeks 4-8**: Backend migration completion
- **Weeks 9-14**: Multi-language architecture
- **Weeks 15-24**: German language expansion

**Total Estimated Timeline**: 6 months with systematic quality-first approach

---

## 🔄 **Review and Update Schedule**

- **Weekly**: Progress review against quality metrics
- **Bi-weekly**: Architecture review and course corrections
- **Monthly**: Priority reassessment based on changing requirements
- **Quarterly**: Complete roadmap review and strategic alignment

*This roadmap prioritizes code quality and architectural soundness as prerequisites for feature development, ensuring long-term maintainability and extensibility.*