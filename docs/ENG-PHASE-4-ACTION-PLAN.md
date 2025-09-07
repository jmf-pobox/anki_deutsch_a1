# Phase 4 Action Plan - Technical Debt Elimination

**Phase**: 4 - Technical Debt Elimination  
**Priority**: CRITICAL - Blocking clean architecture  
**Timeline**: 1-2 weeks  
**Prerequisite**: Read ENG-TECHNICAL-DEBT-STATUS.md for full context

---

## 🎯 Objective

Eliminate the technical debt identified in the original audit (ENG-TECHNICAL-DEBT-AUDIT.md) that remains unresolved after Phase 3. Focus on implementing fail-fast patterns and removing all fallback logic per CLAUDE.md requirements.

---

## 🔴 Critical Success Criteria

Phase 4 is NOT complete until:
1. **ZERO fallback patterns remain** - All 32+ instances eliminated
2. **ZERO silent exceptions** - All ~20 handlers replaced with explicit error propagation
3. **ZERO hasattr/duck typing** - Type-safe dispatch throughout
4. **ZERO debug logging** in production code
5. **All tests pass** with no coverage decrease

---

## 📋 Task Breakdown by Category

### CATEGORY 1: Eliminate Fallback Patterns (Days 1-3)

#### Domain Models (7 files) - HIGHEST PRIORITY
Remove try/except blocks that return fallback values. Let exceptions propagate.

**Files to fix**:
1. `models/noun.py:269-281` - Remove fallback to English
2. `models/verb.py:187-193` - Remove fallback to English  
3. `models/phrase.py:144-150` - Remove fallback to English
4. `models/preposition.py:94-99` - Remove fallback to English
5. `models/adjective.py:279-309` - Remove fallback methods
6. `models/adverb.py:188-194` - Remove fallback to example
7. `models/negation.py:253-270` - Remove fallback execution

**Pattern to apply**:
```python
# BEFORE
try:
    result = ai_service.enhance_context(...)
except Exception as e:
    logger.warning(f"AI generation failed: {e}")
    return self.english  # REMOVE THIS

# AFTER
result = ai_service.enhance_context(...)  # Let exception propagate
return result
```

#### Services (4 files)
1. `services/domain_media_generator.py` - Remove 4 English fallback instances
2. `services/translation_service.py:96` - Propagate translation errors
3. `backends/anki_backend.py:341` - Remove fallback mentions
4. `services/template_service.py` - Remove naming convention fallbacks

---

### CATEGORY 2: Fix Exception Handling (Days 3-4)

Replace generic exception handlers with specific types from `exceptions.py`.

**Priority order**:
1. Domain models - Use `MediaGenerationError`, `DomainError`
2. Services - Use `ServiceError`, `ConfigurationError`
3. Backends - Use `CardGenerationError`, `DataProcessingError`

**Pattern to apply**:
```python
# BEFORE
except Exception as e:
    logger.error(f"Something failed: {e}")
    pass

# AFTER
except ServiceUnavailableError as e:
    logger.error(f"Service unavailable: {e}")
    raise MediaGenerationError(f"Cannot generate media: {e}") from e
```

---

### CATEGORY 3: Eliminate Duck Typing (Days 5-6)

Replace hasattr checks with type-safe dispatch.

**Files to fix**:
1. `services/media_enricher.py:185-198` - Use pattern matching or protocols
2. `managers/deck_manager.py` - Remove backend capability detection
3. `backends/anki_backend.py` - Remove multiple hasattr checks

**Pattern to apply**:
```python
# BEFORE
if hasattr(model, "noun"):
    return model.noun
elif hasattr(model, "verb"):
    return model.verb

# AFTER  
from typing import Protocol

class HasWord(Protocol):
    @property
    def word(self) -> str: ...

if isinstance(model, Noun):
    return model.noun
elif isinstance(model, Verb):
    return model.verb
else:
    raise ValueError(f"Unsupported model type: {type(model).__name__}")
```

---

### CATEGORY 4: Remove Debug Logging (Day 7)

Remove explicit DEBUG level settings and verbose debug messages.

**Files to clean**:
1. `services/audio.py:28` - Remove setLevel(DEBUG)
2. `services/anthropic_service.py:20` - Remove setLevel(DEBUG)
3. `services/pexels_service.py:18` - Remove setLevel(DEBUG)
4. `services/csv_service.py:14` - Remove setLevel(DEBUG)
5. `services/article_pattern_processor.py` - Remove verbose debug messages

---

### CATEGORY 5: Clean Legacy References (Day 7)

Remove backward compatibility and legacy mentions.

**Files to clean**:
1. `services/media_service.py` - Remove compatibility aliases
2. `services/domain_media_generator.py` - Remove legacy service comments
3. Clean up comments mentioning "removed" or "legacy"

---

### CATEGORY 6: Address TODOs (Day 8)

Either implement or remove with documentation.

**Files with TODOs**:
1. `pipeline/pipeline.py:43` - Remove or implement
2. `services/record_to_model_factory.py` - Fix placeholders

---

## 🧪 Testing Strategy

### After Each Category:
1. Run full test suite: `hatch run test`
2. Verify coverage: `hatch run test-cov`
3. Check type safety: `hatch run type`
4. Verify no linting issues: `hatch run lint`

### Integration Testing:
After all changes, test end-to-end deck generation:
```bash
hatch run app
# Import generated deck into Anki
# Verify all card types work correctly
```

---

## 📈 Progress Tracking

### Daily Checklist:
- [ ] Day 1: Domain models noun, verb, phrase - fallback removal
- [ ] Day 2: Domain models preposition, adjective, adverb, negation - fallback removal  
- [ ] Day 3: Services fallback removal + start exception handling
- [ ] Day 4: Complete exception handling migration
- [ ] Day 5: Duck typing elimination part 1
- [ ] Day 6: Duck typing elimination part 2
- [ ] Day 7: Debug logging removal + legacy cleanup
- [ ] Day 8: TODO resolution + final testing

### Verification Commands:
```bash
# Verify fallbacks eliminated
grep -r "fallback\|except.*pass\|except.*return" src/langlearn/ | wc -l
# Should return 0

# Verify hasattr eliminated  
grep -r "hasattr\|getattr.*None" src/langlearn/ | wc -l
# Should return 0

# Verify debug logging removed
grep -r "setLevel.*DEBUG" src/langlearn/ | wc -l
# Should return 0
```

---

## ⚠️ Common Pitfalls to Avoid

1. **Don't add new fallbacks** while removing others
2. **Don't catch exceptions** just to log and re-raise (unless adding context)
3. **Don't use generic Exception** - use specific types from exceptions.py
4. **Don't remove tests** that expose the problems - fix the code instead
5. **Don't claim completion** without verification commands showing zero instances

---

## 🎯 Definition of Done

Phase 4 is complete when:
1. All verification commands return 0
2. All tests pass with no coverage decrease
3. Deck generation works end-to-end without silent failures
4. Documentation updated to reflect clean state
5. User confirms functionality in Anki application

---

## 📝 Commit Strategy

Use micro-commits per CLAUDE.md:
```bash
# After each file or logical group
git add -p  # Stage specific changes
git commit -m "fix(models): remove fallback pattern from Noun model"
git commit -m "fix(models): propagate exceptions in Verb.get_image_search_term()"
git commit -m "refactor(services): replace hasattr with isinstance in MediaEnricher"
```

Push every 3-5 commits or 30 minutes.

---

## 🔄 Next Phase

Only after Phase 4 completion:
- **Phase 5**: Complete architectural cleanup
- Remove any remaining legacy infrastructure
- Achieve true Clean Pipeline Architecture
- Update all documentation to reflect clean state

---

*This action plan provides concrete steps to eliminate technical debt. Follow it systematically for successful Phase 4 completion.*