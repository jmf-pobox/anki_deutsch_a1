# Plan: Refactor to Protocol-Based MediaGeneration Architecture

## Overview
Refactor the MediaEnricher to use dependency injection and a common protocol interface across all domain models, eliminating type-specific branching and improving testability.

## Phase 1: Foundation Setup

### Step 1.1: Create MediaGenerationCapable Protocol
**Files to Create/Modify:**
- Create `src/langlearn/protocols/media_generation_protocol.py`

**Implementation:**
```python
from typing import Protocol

class MediaGenerationCapable(Protocol):
    def get_audio_text(self) -> str:
        """Return text for audio generation."""
        ...
    
    def get_image_search_terms(self) -> str:
        """Return search terms for image generation."""
        ...
    
    def get_context_hint(self) -> str | None:
        """Return contextual hint for media generation."""
        ...
```

**Quality Gates:**
- `hatch run format`
- `hatch run ruff check --fix`
- `hatch run type`
- `hatch run test-unit`

### Step 1.2: Create Service Injection Container
**Files to Create/Modify:**
- Create `src/langlearn/services/media_service_container.py`

**Implementation:**
```python
@dataclass
class MediaServiceContainer:
    translation_service: TranslationService
    audio_service: AudioService
    image_service: PexelsService
```

**Quality Gates:** Same as Step 1.1

## Phase 2: Domain Model Refactoring (One by One)

### Step 2.1: Refactor Noun Domain Model
**Files to Modify:**
- `src/langlearn/models/noun.py`
- `tests/test_noun_domain.py`

**Implementation:**
1. Add MediaServiceContainer dependency to `__init__`
2. Implement `MediaGenerationCapable` protocol methods:
   - `get_audio_text()` → existing `get_combined_audio_text()` logic
   - `get_image_search_terms()` → translate article + noun to English
   - `get_context_hint()` → return example or related fields
3. Update tests to inject mock services
4. Add protocol compliance test

**MediaEnricher Changes:**
- Add fallback branch for Noun that uses protocol methods
- Keep existing logic as primary path during transition

**Quality Gates:**
- `hatch run format`
- `hatch run ruff check --fix` 
- `hatch run type`
- `hatch run test-unit`
- `hatch run app` (verify system still works end-to-end)

### Step 2.2: Refactor Adjective Domain Model
**Files to Modify:**
- `src/langlearn/models/adjective.py`
- `tests/test_adjective_domain.py`

**Implementation:**
1. Add MediaServiceContainer dependency
2. Implement protocol methods:
   - `get_audio_text()` → word + comparative + superlative
   - `get_image_search_terms()` → translate adjective + example context
   - `get_context_hint()` → return example field
3. Update tests with dependency injection
4. Add protocol compliance test

**MediaEnricher Changes:**
- Add protocol fallback for Adjective
- Keep existing branch during transition

**Quality Gates:** Same as Step 2.1

### Step 2.3: Refactor Adverb Domain Model
**Files to Modify:**
- `src/langlearn/models/adverb.py`
- `tests/test_adverb.py`

**Implementation:**
1. Add MediaServiceContainer dependency
2. Implement protocol methods:
   - `get_audio_text()` → adverb text
   - `get_image_search_terms()` → translate adverb + context
   - `get_context_hint()` → return example or usage context
3. Update tests with mocked services
4. Add protocol compliance test

**Quality Gates:** Same as Step 2.1

### Step 2.4: Refactor Negation Domain Model
**Files to Modify:**
- `src/langlearn/models/negation.py`
- `tests/test_negation.py`

**Implementation:**
1. Add MediaServiceContainer dependency
2. Implement protocol methods:
   - `get_audio_text()` → negation word/phrase
   - `get_image_search_terms()` → translate context or example
   - `get_context_hint()` → return usage context
3. Update tests with dependency injection
4. Add protocol compliance test

**Quality Gates:** Same as Step 2.1

### Step 2.5: Refactor Verb Domain Model
**Files to Modify:**
- `src/langlearn/models/verb.py`
- `tests/test_verb_field_processing.py`

**Implementation:**
1. Add MediaServiceContainer dependency
2. Implement protocol methods:
   - `get_audio_text()` → existing conjugation logic
   - `get_image_search_terms()` → translate verb + example context
   - `get_context_hint()` → return example field
3. Update tests with mocked services
4. Add protocol compliance test

**Quality Gates:** Same as Step 2.1

### Step 2.6: Refactor Phrase Domain Model
**Files to Modify:**
- `src/langlearn/models/phrase.py`
- `tests/test_phrase_field_processing.py`

**Implementation:**
1. Add MediaServiceContainer dependency
2. Implement protocol methods:
   - `get_audio_text()` → phrase text
   - `get_image_search_terms()` → use injected translation service instead of MediaEnricher's `_translate_for_search`
   - `get_context_hint()` → return context or related fields
3. Update tests with dependency injection
4. Add protocol compliance test

**Quality Gates:** Same as Step 2.1

### Step 2.7: Refactor Preposition Domain Model
**Files to Modify:**
- `src/langlearn/models/preposition.py`
- `tests/test_preposition_field_processing.py`

**Implementation:**
1. Add MediaServiceContainer dependency
2. Implement protocol methods:
   - `get_audio_text()` → preposition + example usage
   - `get_image_search_terms()` → translate preposition context
   - `get_context_hint()` → return case information or example
3. Update tests with dependency injection
4. Add protocol compliance test

**Quality Gates:** Same as Step 2.1

## Phase 3: MediaEnricher Refactoring

### Step 3.1: Create Protocol-Based MediaEnricher Methods
**Files to Modify:**
- `src/langlearn/services/media_enricher.py`

**Implementation:**
1. Add `_enrich_with_protocol()` method that uses MediaGenerationCapable interface
2. Inject MediaServiceContainer into domain models during instantiation
3. Add fallback logic: try protocol first, then existing type-specific methods

**Quality Gates:** Same as Step 2.1

### Step 3.2: Update MediaEnricher to Prefer Protocol Methods
**Files to Modify:**
- `src/langlearn/services/media_enricher.py`
- `tests/test_media_enricher.py`

**Implementation:**
1. Switch primary path to use protocol methods
2. Keep type-specific methods as fallback during transition
3. Update tests to verify protocol-based processing
4. Add integration tests with real domain models

**Quality Gates:** Same as Step 2.1

## Phase 4: Cleanup and Optimization

### Step 4.1: Remove Type-Specific MediaEnricher Branches
**Files to Modify:**
- `src/langlearn/services/media_enricher.py`
- Related tests

**Implementation:**
1. Remove all type-specific `_enrich_*_record` methods
2. Consolidate to single `_enrich_with_protocol` method
3. Remove scattered domain model imports
4. Update tests to reflect simplified architecture

**Quality Gates:** Same as Step 2.1

### Step 4.2: Update Service Container Integration
**Files to Modify:**
- `src/langlearn/services/service_container.py` (if exists)
- `src/langlearn/deck_builder.py`

**Implementation:**
1. Ensure MediaServiceContainer is properly wired through dependency injection
2. Update main application to provide services to MediaEnricher
3. Verify all external service dependencies are properly injected

**Quality Gates:** Same as Step 2.1

## Phase 5: Final Validation

### Step 5.1: Comprehensive Testing
**Tests to Run:**
1. `hatch run test-unit` (all unit tests)
2. `hatch run test-integration` (if applicable)
3. `hatch run app` (full end-to-end deck generation)
4. `hatch run app --generate-media` (with real API calls)

### Step 5.2: Performance Verification
**Validation Steps:**
1. Verify no performance regression in deck generation
2. Confirm all media files are generated correctly
3. Test with sample of each word type
4. Validate Anki card output matches previous behavior

### Step 5.3: Documentation Update
**Files to Update:**
- `CLAUDE.md` - Update architecture description
- `README.md` - Update if necessary
- `docs/ENG-DEVELOPMENT-STANDARDS.md` - Document new protocol pattern

## Success Criteria for Each Step
1. **All Quality Gates Pass**: format, lint, type check, unit tests
2. **System Functionality**: `hatch run app` completes successfully
3. **No Regressions**: Generated cards match previous output
4. **Test Coverage**: New protocol methods covered by tests
5. **Dependency Injection**: All external services mocked in tests

## Rollback Strategy
- Work in a single feature branch with commits for each step
- If any step fails quality gates, use `git revert` to undo the problematic commit
- Maintain parallel protocol + existing methods until all domain models converted
- Only remove old methods after all domain models successfully converted

This plan ensures the system remains functional at every step while gradually introducing the cleaner protocol-based architecture with proper dependency injection.