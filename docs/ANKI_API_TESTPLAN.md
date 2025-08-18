# AnkiBackend Test Coverage Plan

## 📋 Executive Summary

This document provides a structured test plan to address the significant test coverage gaps in the official Anki library backend (`AnkiBackend`). Currently, ~70% of advanced AnkiBackend functionality is untested, creating production readiness risks.

**Goal**: Achieve comprehensive test coverage for AnkiBackend to enable safe production migration from GenanKiBackend.

---

## 🎯 Current Status

### Test Coverage Assessment (August 2025)
- **GenanKiBackend**: ✅ 100% coverage (simple implementation)
- **AnkiBackend**: ❌ ~30% coverage (complex implementation)
- **Coverage Gap**: 13+ untested methods with advanced functionality

### Risk Analysis
- **Current Risk Level**: MEDIUM (untested advanced features)
- **Target Risk Level**: LOW (comprehensive test coverage)
- **Blocking Migration**: YES - testing required before production use

---

## 🧪 Test Coverage Gaps Analysis

### **Priority 1: Critical Media Processing Pipeline** 🔴

#### **Untested Methods:**
```python
# Field Processing Methods (NOT directly tested)
def _process_adjective_fields(self, fields: list[str]) -> list[str]
def _process_noun_fields(self, fields: list[str]) -> list[str]  
def _process_verb_fields(self, fields: list[str]) -> list[str]
def _process_preposition_fields(self, fields: list[str]) -> list[str]
def _process_phrase_fields(self, fields: list[str]) -> list[str]
def _process_adverb_fields(self, fields: list[str]) -> list[str]
def _process_negation_fields(self, fields: list[str]) -> list[str]
```

**Current Coverage**: ❌ No direct testing
**Risk**: HIGH - Core media generation logic untested

#### **Partially Tested Methods:**
```python
def _process_fields_with_media(self, note_type_name: str, fields: list[str]) -> list[str]
def _generate_or_get_audio(self, text: str) -> str | None
def _generate_or_get_image(self, query: str, fallback_query: str = None) -> str | None
```

**Current Coverage**: ⚠️ Basic coverage only
**Risk**: MEDIUM - Limited test scenarios

### **Priority 2: German Language Integration** 🟡

#### **Untested Integration:**
- `GermanLanguageService` integration in AnkiBackend constructor
- German-specific processing in field methods
- Linguistic processing in media generation
- German grammar validation in card creation

**Current Coverage**: ❌ No integration testing
**Risk**: MEDIUM - Language features may not work correctly

### **Priority 3: Advanced Analytics & Performance** 🟢

#### **Untested Features:**
- Media generation statistics tracking
- Performance metrics collection  
- Database optimization features
- Bulk operations performance
- Error recovery and fallback mechanisms

**Current Coverage**: ❌ No testing
**Risk**: LOW - Non-critical features

---

## 📝 Structured Test Plan

### **Phase 1: Critical Media Processing** (Week 1)

#### **Test File**: `tests/test_anki_backend_media_processing.py`

**Test Coverage Goals:**
- ✅ All 7 `_process_*_fields()` methods individually tested
- ✅ Media pipeline integration testing
- ✅ Error handling and fallback scenarios
- ✅ German vocabulary data integration

#### **Test Cases:**

##### **TC-MP-001: Adjective Field Processing**
```python
def test_process_adjective_fields_complete():
    """Test complete adjective field processing with all variants."""
    # Input: [Word, English, Example, Comparative, Superlative, Image, WordAudio, ExampleAudio]
    # Expected: Media-enhanced fields with audio/image references
    
def test_process_adjective_fields_missing_forms():
    """Test adjective processing with missing comparative/superlative."""
    
def test_process_adjective_fields_media_failure():
    """Test adjective processing when media generation fails."""
```

##### **TC-MP-002: Noun Field Processing**  
```python
def test_process_noun_fields_with_gender():
    """Test noun processing with German gender/article handling."""
    # Test: die Katze -> "die Katze, die Katzen" audio
    
def test_process_noun_fields_concrete_vs_abstract():
    """Test concrete noun detection for image generation."""
    
def test_process_noun_fields_plural_variants():
    """Test handling of irregular German plurals."""
```

##### **TC-MP-003: Verb Field Processing**
```python
def test_process_verb_fields_separable():
    """Test processing of German separable verbs."""
    
def test_process_verb_fields_irregular():
    """Test processing of irregular German verbs."""
    
def test_process_verb_fields_conjugation():
    """Test verb conjugation audio generation."""
```

##### **TC-MP-004: Media Pipeline Integration**
```python
def test_media_pipeline_end_to_end():
    """Test complete pipeline from raw fields to media-enhanced output."""
    
def test_media_pipeline_partial_failure():
    """Test pipeline behavior when some media generation fails."""
    
def test_media_pipeline_performance():
    """Test pipeline performance with large vocabulary datasets."""
```

#### **Success Criteria:**
- [ ] All 7 field processing methods have >90% code coverage
- [ ] Integration tests pass with real German vocabulary
- [ ] Error scenarios handled gracefully
- [ ] Performance acceptable for production use

### **Phase 2: German Language Integration** (Week 2)

#### **Test File**: `tests/test_anki_backend_german_integration.py`

**Test Coverage Goals:**
- ✅ GermanLanguageService integration tested
- ✅ German-specific processing validated
- ✅ Linguistic accuracy verified
- ✅ Cross-service communication tested

#### **Test Cases:**

##### **TC-GI-001: Service Integration**
```python
def test_german_service_initialization():
    """Test AnkiBackend correctly initializes with GermanLanguageService."""
    
def test_german_service_field_processing():
    """Test German service is used during field processing."""
    
def test_german_service_audio_generation():
    """Test German service provides combined audio text."""
```

##### **TC-GI-002: Linguistic Processing**
```python
def test_noun_gender_detection():
    """Test correct German gender detection and article usage."""
    
def test_adjective_declension():
    """Test adjective declension forms in audio generation."""
    
def test_verb_conjugation_patterns():
    """Test German verb conjugation patterns."""
```

##### **TC-GI-003: Media Enhancement**
```python
def test_german_context_image_search():
    """Test German cultural context in image searches."""
    
def test_german_pronunciation_audio():
    """Test German-specific pronunciation in audio generation."""
```

#### **Success Criteria:**
- [ ] German language features work correctly in AnkiBackend
- [ ] Cross-service integration tested
- [ ] Linguistic accuracy validated
- [ ] German-specific media generation verified

### **Phase 3: Advanced Features & Performance** (Week 3)

#### **Test File**: `tests/test_anki_backend_advanced.py`

**Test Coverage Goals:**
- ✅ Advanced statistics and analytics tested
- ✅ Performance characteristics validated
- ✅ Bulk operations tested
- ✅ Error recovery mechanisms verified

#### **Test Cases:**

##### **TC-AF-001: Statistics & Analytics**
```python
def test_media_generation_statistics():
    """Test media generation statistics tracking."""
    
def test_performance_metrics_collection():
    """Test performance metrics are collected correctly."""
    
def test_advanced_stats_in_get_stats():
    """Test advanced statistics are included in get_stats() output."""
```

##### **TC-AF-002: Performance & Scale**
```python
def test_bulk_operations_performance():
    """Test performance with large German vocabulary datasets."""
    
def test_memory_usage_optimization():
    """Test memory efficiency with large media files."""
    
def test_concurrent_media_generation():
    """Test concurrent media generation scenarios."""
```

##### **TC-AF-003: Error Recovery**
```python
def test_media_service_failure_recovery():
    """Test recovery when MediaService fails."""
    
def test_german_service_failure_fallback():
    """Test fallback when GermanLanguageService fails."""
    
def test_partial_media_generation_success():
    """Test handling when only some media generation succeeds."""
```

#### **Success Criteria:**
- [ ] Advanced features work as documented
- [ ] Performance meets production requirements
- [ ] Error recovery mechanisms function correctly
- [ ] System remains stable under stress

---

## 🚀 Implementation Strategy

### **Development Approach**

#### **1. Test-Driven Validation**
- Write tests first, then validate against existing implementation
- Use real German vocabulary data from project's CSV files
- Mock external services (AWS Polly, Pexels) for unit tests
- Create integration tests with actual service calls

#### **2. Incremental Coverage**
- Phase-by-phase implementation
- Continuous integration validation  
- Coverage metrics tracking
- Regular progress assessment

#### **3. Real-World Testing**
```python
# Use project's actual German vocabulary
test_nouns = load_test_data("data/nouns.csv")
test_adjectives = load_test_data("data/adjectives.csv")
test_verbs = load_test_data("data/verbs.csv")
```

### **Testing Tools & Framework**

#### **Primary Framework**: pytest
```bash
# Run AnkiBackend-specific tests
hatch run pytest tests/test_anki_backend_*.py -v

# Coverage analysis
hatch run pytest --cov=langlearn.backends.anki_backend tests/test_anki_backend_*.py

# Performance testing  
hatch run pytest tests/test_anki_backend_*.py -k "performance" --durations=10
```

#### **Mocking Strategy**
- Mock external APIs (AWS Polly, Pexels) for unit tests
- Use real services for integration tests (marked with `@pytest.mark.integration`)
- Mock file system operations where appropriate

#### **Test Data Management**
```python
@pytest.fixture
def german_vocabulary_sample():
    """Load representative German vocabulary for testing."""
    return {
        'nouns': load_nouns_sample(),
        'adjectives': load_adjectives_sample(),
        'verbs': load_verbs_sample()
    }
```

---

## 📊 Success Metrics & Acceptance Criteria

### **Coverage Targets**

| Component | Current Coverage | Target Coverage |
|-----------|------------------|-----------------|
| Field Processing Methods | 0% | >90% |
| German Integration | <10% | >85% |
| Media Pipeline | 30% | >90% |
| Advanced Features | 0% | >75% |
| **Overall AnkiBackend** | **~30%** | **>85%** |

### **Performance Benchmarks**
- [ ] Process 1000+ German vocabulary entries in <60 seconds
- [ ] Memory usage <500MB for standard vocabulary dataset
- [ ] Media generation success rate >95%
- [ ] Error recovery time <5 seconds

### **Quality Gates**
- [ ] All critical path methods covered by tests
- [ ] Integration tests pass with real German data
- [ ] No regressions in existing GenanKiBackend functionality
- [ ] Performance meets or exceeds GenanKiBackend benchmarks

### **Production Readiness Checklist**
- [ ] **Phase 1**: ✅ Media processing pipeline fully tested
- [ ] **Phase 2**: ✅ German language integration validated  
- [ ] **Phase 3**: ✅ Advanced features and performance verified
- [ ] **Final**: ✅ End-to-end testing with complete German A1 dataset
- [ ] **Migration**: ✅ Safe to change `backend_type="anki"` in production

---

## 🔄 Continuous Integration

### **Automated Testing Pipeline**
```yaml
# .github/workflows/anki-backend-tests.yml
name: AnkiBackend Test Coverage
on: [push, pull_request]

jobs:
  anki-backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v3
      - name: Install dependencies
        run: hatch env create
      - name: Run AnkiBackend tests
        run: hatch run pytest tests/test_anki_backend_*.py
      - name: Coverage report
        run: hatch run pytest --cov=langlearn.backends.anki_backend
```

### **Coverage Monitoring**
- Minimum 85% coverage required for CI pass
- Coverage reports generated for each test run
- Regression detection for coverage decreases

---

## 📚 Documentation & Knowledge Transfer

### **Test Documentation Requirements**
- [ ] Each test method documented with purpose and expected behavior
- [ ] Complex test scenarios explained with German language examples
- [ ] Performance test results documented with benchmarks
- [ ] Integration test setup instructions provided

### **Knowledge Transfer Plan**
1. **Test Plan Review**: Team review of this document
2. **Implementation Kickoff**: Development approach alignment
3. **Progress Check-ins**: Weekly progress and blocker identification
4. **Final Review**: Complete coverage validation before migration

---

## 🏁 Timeline & Milestones

| Week | Phase | Deliverables | Success Criteria |
|------|-------|--------------|------------------|
| 1 | Media Processing | `test_anki_backend_media_processing.py` | All field processing methods >90% covered |
| 2 | German Integration | `test_anki_backend_german_integration.py` | German language features validated |
| 3 | Advanced Features | `test_anki_backend_advanced.py` | Performance and analytics tested |
| 4 | Integration & Validation | End-to-end testing | Production readiness achieved |

**Total Effort**: ~4 weeks
**Resource Requirement**: 1 developer, ~40 hours
**Risk**: Low (structured approach, existing working implementation to validate against)

---

## ✅ Conclusion

This test plan provides a structured approach to achieving comprehensive AnkiBackend test coverage. Upon completion:

- **Risk Level**: MEDIUM → LOW
- **Production Readiness**: NO → YES  
- **Migration Safety**: CAUTION → RECOMMENDED
- **Confidence Level**: MEDIUM → HIGH

**Next Steps**: 
1. Review and approve this test plan
2. Begin Phase 1 implementation
3. Track progress against success metrics
4. Execute safe migration upon completion