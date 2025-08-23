# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Anki German Language Deck Generator

This project generates customized German language Anki decks for A1-level learners, focusing on grammatical nuances specific to German such as noun genders, separable verbs, and case-dependent prepositions.

## REQUIRED READING

**🚨 MANDATORY: You MUST read, understand, and follow these files before any development work:**

1. **docs/ENG-PYTHON-STANDARDS.md** - General Python coding standards and development practices
2. **docs/ENG-DESIGN-INDEX.md** - Navigation guide for all design documentation
3. **docs/ENG-DEVELOPMENT-STANDARDS.md** - Project-specific development standards and architectural principles

These documents contain critical information about:
- Code quality requirements and mandatory workflows
- Architectural principles and design patterns to follow
- Component responsibilities and system organization
- Technical debt and current quality metrics
- Anti-patterns to avoid and best practices to implement

**⚠️  Failure to follow these documents will result in code that does not meet project standards.**

## MICRO-COMMIT DEVELOPMENT (MANDATORY)

**🚨 CRITICAL: Large batch changes are PROHIBITED - use micro-commits to prevent massive time waste**

**📈 SUCCESS RATE IMPROVEMENT**: This workflow moves us from 5-0% PR success rate to 90%+ by preventing large batch failures.

### Atomic Change Principle:
- **ONE change** = ONE commit (extract function, fix bug, add test)
- **ONE concern** = ONE branch (refactoring, feature, fix)  
- **ONE layer** = ONE PR (services, models, tests - not mixed)

### Commit Size Limits (STRICTLY ENFORCED):
- ✅ **Micro**: 1-2 files, <50 lines (PREFERRED - fastest feedback)
- ⚠️ **Small**: 3-5 files, <100 lines (ACCEPTABLE - use sparingly)
- ❌ **Large**: >5 files, >200 lines (PROHIBITED - causes time waste)

### Progressive Quality Gates (FAST FEEDBACK):

#### Tier 1: Instant Feedback (<5 seconds) - While coding every 2-3 minutes:
```bash
hatch run type-quick    # Type check current file only
hatch run format-check  # Format check (no write)
```

#### Tier 2: Fast Validation (<30 seconds) - Before each micro-commit:
```bash
hatch run type          # Full type checking
hatch run test-unit     # Core unit tests only  
```

#### Tier 3: Comprehensive (<5 minutes) - Before push every 30-45 minutes:
```bash
hatch run format        # Apply formatting
hatch run test-cov      # Full test suite with coverage
```

### Micro-Commit Development Flow:
1. **Plan**: Identify ONE specific change (5-10 minute scope max)
2. **Implement**: Make the minimal change required
3. **Verify**: Run Tier 1 checks (instant feedback)
4. **Commit**: Create atomic commit with clear message
5. **Iterate**: Repeat for next micro-change
6. **Push**: Every 3-5 commits OR every 30 minutes

### Commit Message Standards:
- Format: `type(scope): description [impact]`
- Examples:
  - `refactor(utils): extract rate_limit_reached() [no behavior change]`
  - `fix(pexels): handle empty API key [prevents KeyError]`
  - `test(utils): add environment detection tests [+15 tests]`

## MANDATORY DEVELOPMENT WORKFLOW

**🚨 CRITICAL: These steps MUST be followed but applied to MICRO-COMMITS - NO EXCEPTIONS!**

**⚠️ WARNING: We cannot allow MyPy/Ruff/Test degradation. Quality gates are ABSOLUTE.**

### Required Quality Gate Steps (MANDATORY AFTER EVERY CODE CHANGE):

**⚠️ CRITICAL NEW REQUIREMENT**: After experiencing $566 in wasted costs from false "fix" claims, an additional validation layer is now MANDATORY.

#### Standard Code Quality Gates (Layers 1-2):

1. **Run MyPy Type Check**: `hatch run type`
   - ✅ **ZERO MyPy errors allowed** - Must show "Success: no issues found in 112 source files"
   - ❌ **STOP IMMEDIATELY** if ANY MyPy error exists - Fix before proceeding
   - 🚫 **NO CODE CHANGES** are allowed that introduce MyPy errors

2. **Run Linting with Auto-fix**: `hatch run ruff check --fix`
   - ✅ **ZERO Ruff errors allowed** - Fix all automatically fixable issues
   - ❌ **STOP IMMEDIATELY** if unfixable issues remain - Address manually
   - 🚫 **NO CODE CHANGES** are allowed that introduce Ruff violations

3. **Run Code Formatting**: `hatch run format`
   - ✅ **Perfect formatting required** - All code must be properly formatted
   - ❌ **STOP IMMEDIATELY** if formatting issues exist - Fix them

4. **Run Full Tests**: `hatch run test`
   - ✅ **ALL tests must pass** - Currently 772 unit + integration tests
   - ❌ **STOP IMMEDIATELY** if ANY test fails - Fix before proceeding
   - 🚫 **NO CODE CHANGES** are allowed that break existing tests

5. **Check Coverage**: `hatch run test-cov`
   - ✅ **Coverage must not decrease** (currently >73%)
   - ✅ View detailed report in `htmlcov/index.html`
   - ❌ **STOP IMMEDIATELY** if coverage drops - Add tests to maintain quality gate

#### NEW MANDATORY: Anki Application Validation (Layer 3):

6. **Run Anki Format Validation**: `hatch run validate-anki` *(IMPLEMENTATION REQUIRED)*
   - ✅ **Cloze deletion syntax validated** - Verify {{c1::text}} format correctness
   - ✅ **Field references validated** - Ensure all {{Field}} references exist
   - ✅ **Media paths validated** - Verify [sound:...] and <img src="..."> paths
   - ❌ **STOP IMMEDIATELY** if validation fails - Fix Anki compatibility issues

7. **Run Card Rendering Simulation**: `hatch run simulate-cards` *(IMPLEMENTATION REQUIRED)*
   - ✅ **No blank cards detected** - Simulate Anki's rendering to catch display issues
   - ✅ **No duplicate notes detected** - Verify uniqueness in generated content
   - ✅ **Template syntax validated** - Ensure HTML/CSS will render correctly in Anki
   - ❌ **STOP IMMEDIATELY** if simulation shows user-facing issues

8. **Verify Final State**: `hatch run type && hatch run test && hatch run validate-anki`
   - ✅ **Final verification** - All layers pass before claiming any fix works
   - ❌ If anything broke during workflow, investigate and fix immediately

### Workflow Summary (MANDATORY - NO SHORTCUTS):
```bash
# MANDATORY workflow after ANY code change - NO EXCEPTIONS:
hatch run type                         # 1. ZERO MyPy errors (ABSOLUTE REQUIREMENT)
hatch run ruff check --fix            # 2. ZERO Ruff violations (ABSOLUTE REQUIREMENT)
hatch run format                       # 3. Perfect formatting (ABSOLUTE REQUIREMENT)
hatch run test                         # 4. ALL tests pass (ABSOLUTE REQUIREMENT)
hatch run test-cov                     # 5. Coverage maintained (ABSOLUTE REQUIREMENT)
hatch run validate-anki                # 6. Anki format validation (NEW REQUIREMENT)
hatch run simulate-cards               # 7. Card rendering simulation (NEW REQUIREMENT)  
hatch run type && hatch run test && hatch run validate-anki  # 8. Final verification
```

**🚨 ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**
- **MyPy --strict**: ZERO errors allowed in any file
- **Ruff linting**: ZERO violations allowed
- **Test suite**: ALL tests must pass (667 unit + 24 integration)
- **Coverage**: Must not decrease from current levels
- **Complete workflow**: ALL 6 steps must pass before code change is complete

**⚠️ CRITICAL**: Use `hatch run test-cov` (not `test-unit-cov`) for accurate coverage measurement.

**🚫 A CODE CHANGE IS NOT COMPLETE UNTIL ALL 8 STEPS PASS SUCCESSFULLY!**

## CRITICAL COMMUNICATION PROTOCOL (MANDATORY)

**🚨 NEVER CLAIM "FIXED" WITHOUT ANKI VALIDATION**

After experiencing $566 in wasted costs from false success claims, the following communication protocol is MANDATORY:

### ❌ PROHIBITED Communication Patterns:
```
"I've fixed the blank card issue"
"The duplicates are eliminated"  
"This should work now"
"The issue has been resolved"
"You are right" followed by overly sycophantic responses
```

### ✅ REQUIRED Communication Protocol:
```
"I've implemented changes that SHOULD address the issue:

**Changes Made**:
- Modified: [specific files and line numbers]
- Logic: [brief explanation of what changed]

**Internal Validation**:
- ✅ MyPy: All type checks pass
- ✅ Tests: All 772 tests pass  
- ✅ Anki Format: [validation results when implemented]
- ✅ Simulation: [rendering results when implemented]

**Critical Limitation**: 
Cannot verify actual Anki application behavior without importing the deck.

**Required User Testing**:
Please import the fresh german_a1_vocabulary.apkg (35MB) and verify:
1. [Specific behavior to check]
2. [Another specific behavior]
3. [Screenshot/report what you see]

**If Issues Persist**:
Please provide:
- Screenshot of problematic card(s)
- Card template from Anki browser (Tools > Manage Note Types)
- Exact field values shown in browser
- Console errors if any (Tools > Debug Console)
```

### 🔄 Iterative Problem Solving:
1. **Report findings** → "Based on your screenshot, I can see..."
2. **Implement targeted fix** → "This specific change should address..."
3. **Request focused testing** → "Please test these 3 specific cards..."
4. **Repeat until confirmed** → Never claim success without user confirmation

**🚫 ABSOLUTE PROHIBITION**: Never claim any fix works in the Anki application without user confirmation.**

## Development Commands

### Hatch Environment Management
```bash
# Create environment
hatch env create

# Run tests
hatch run test               # All tests (unit + integration)
hatch run test-unit         # Unit tests only (no live API calls)
hatch run test-integration  # Integration tests (requires API keys)

# Code Quality
hatch run lint              # Ruff linting
hatch run format            # Ruff formatting  
hatch run type              # MyPy type checking
hatch run check             # All checks (lint + type + test)
hatch run check-unit        # All checks with unit tests only

# Application Scripts
hatch run app               # Run main deck creation
hatch run run-sample        # Run example deck creation
hatch run run-adjectives    # Run adjectives-only deck creation
```

### Testing Strategy
The project uses separate test categories with comprehensive coverage measurement:
- **Unit tests**: Mock external dependencies, run with `hatch run test-unit` (562 tests passing)
- **Integration tests**: Require live API keys, marked with `@pytest.mark.live`, run with `hatch run test-integration` (24 tests)
- **Coverage testing**: Use `hatch run test-cov` for complete measurement (current: **81.69%**, target: >85%)
  - **CardBuilder Service**: 97.83% coverage with 15 comprehensive tests
  - **Clean Pipeline Architecture**: Full test coverage for all components
- API keys are managed via the system keyring using the `api_keyring.py` utility

### Code Quality Standards
**CRITICAL**: A change is not considered complete unless it meets ALL of the following ABSOLUTE requirements:

1. **MyPy Type Checking**: `hatch run type` - **ZERO errors allowed** (mypy --strict mode)
   - ✅ Must show "Success: no issues found in 112 source files"
   - 🚫 **NO EXCEPTIONS** - ANY MyPy error means STOP and fix immediately

2. **Ruff Linting**: `hatch run ruff check --fix` - **ZERO violations allowed**
   - ✅ All linting rules must pass
   - 🚫 **NO EXCEPTIONS** - ANY Ruff violation means STOP and fix immediately

3. **All Tests Pass**: `hatch run test` - **ALL tests must pass**
   - ✅ Currently 667 unit + 24 integration tests (691 total)
   - 🚫 **NO EXCEPTIONS** - ANY test failure means STOP and fix immediately

4. **Test Coverage**: `hatch run test-cov` - **Coverage must not decrease**
   - ✅ Currently >73% - must maintain or improve
   - 🚫 **NO EXCEPTIONS** - Coverage drops mean STOP and add tests

5. **Code Formatting**: `hatch run format` - **Perfect formatting required**
   - ✅ All code must be properly formatted
   - 🚫 **NO EXCEPTIONS** - Formatting issues mean STOP and fix

6. **Unit Tests for New Code**: All new code must have comprehensive unit tests
   - ✅ High coverage with edge cases and error handling
   - 🚫 **NO EXCEPTIONS** - New code without tests is not allowed

**🔄 REFERENCE THE MANDATORY DEVELOPMENT WORKFLOW ABOVE** - ALL 6 quality gate steps must pass after every single code change.

**🚨 DEGRADATION IS NOT ALLOWED**: We will never allow MyPy/Ruff/Test quality to degrade again.

Additional verification commands:
```bash
hatch run test-unit      # All tests must pass (452 tests)
hatch run test-unit-cov  # Run tests with coverage report
hatch run format         # Auto-fix formatting
hatch run lint           # Check linting rules
hatch run type           # Verify type safety
```

## Project Architecture

**📋 For detailed architecture information, see the comprehensive design documentation in `docs/`:**
- **`docs/ENG-COMPONENT-INVENTORY.md`** - Complete component inventory and responsibilities
- **`docs/ENG-QUALITY-METRICS.md`** - Current quality metrics and technical debt analysis
- **`docs/ENG-DEVELOPMENT-STANDARDS.md`** - Architectural principles and development standards

### Core Components - Clean Pipeline Architecture

The project uses **Clean Pipeline Architecture** for data processing with clear separation of concerns:

**Clean Pipeline Flow**: CSV → Records → Domain Models → MediaEnricher → Enriched Records → CardBuilder

1. **Models** (`src/langlearn/models/`): 
   - **Records System**: Lightweight Pydantic records (NounRecord, AdjectiveRecord, etc.) for data transport
   - **Domain Models**: Rich models with German-specific validation (legacy compatibility for verb, preposition, phrase)
   - **Factory**: Record creation and model factory patterns

2. **Services** (`src/langlearn/services/`): 
   - **CardBuilder**: Final assembly service (Records → Formatted Cards)
   - **MediaEnricher**: Audio/image generation with existence checking  
   - **RecordMapper**: CSV → Records conversion
   - **External APIs**: AWS Polly, Pexels, Anthropic integration

3. **Backends** (`src/langlearn/backends/`): 
   - **AnkiBackend**: Official Anki library with MediaEnricher integration
   - **Clean Pipeline Support**: Automatic delegation to Clean Pipeline Architecture
   - **Legacy Fallback**: Graceful fallback to FieldProcessor for unsupported types

4. **Utils** (`src/langlearn/utils/`): API key management, audio/image utilities

5. **Main Application** (`deck_builder.py`): High-level orchestrator with MVP architecture support

### Data Architecture
- **CSV Files** (`data/`): Source data for all parts of speech
- **Audio** (`data/audio/`): AWS Polly-generated pronunciation files
- **Images** (`data/images/`): Pexels-sourced images with automatic backup
- **Backups** (`data/backups/`): Automatic CSV backups during enrichment

### Key Design Patterns - Clean Architecture Implementation

- **Clean Pipeline Architecture**: Clear data flow with single responsibility at each step
  - **Records**: Lightweight data transfer objects (DTOs) for pure data transport
  - **MediaEnricher**: Infrastructure service with existence checking and caching
  - **CardBuilder**: Pure transformation service (Records → Formatted Cards)
  - **Separation of Concerns**: German grammar logic separate from infrastructure

- **Dual Architecture Support**: Hybrid system supporting both modern and legacy patterns
  - **Clean Pipeline**: noun, adjective, adverb, negation (fully migrated)
  - **Legacy FieldProcessor**: verb, preposition, phrase (backward compatibility)
  - **Automatic Delegation**: AnkiBackend automatically chooses appropriate architecture

- **Performance Optimizations**: 
  - **Hash-based Caching**: Avoids duplicate API calls for media generation
  - **Existence Checking**: MediaEnricher checks for existing files before generation
  - **Optimized Field Processing**: Clean Pipeline reduces processing overhead

- **German Language Specialization**: 
  - **Pydantic Validation**: German-specific rules (article validation, case patterns)
  - **Template System**: HTML/CSS templates for different card types  
  - **Rich Domain Models**: Context-aware German grammar handling

## API Key Management

The project uses the system keyring for secure credential storage:

```bash
# Add API keys
python src/langlearn/utils/api_keyring.py add ANTHROPIC_API_KEY your_key_here
python src/langlearn/utils/api_keyring.py add PEXELS_API_KEY your_key_here

# View stored keys
python src/langlearn/utils/api_keyring.py view ANTHROPIC_API_KEY

# Remove keys
python src/langlearn/utils/api_keyring.py remove ANTHROPIC_API_KEY

# Sync keys to environment (for scripts)
python src/langlearn/utils/sync_api_key.py
```

AWS credentials are managed via standard environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key  
export AWS_DEFAULT_REGION=your_region
```

## German Language Specifics

This project addresses unique aspects of German language learning:

### Noun Challenges
- **Gender memorization**: Cards test article recall separately from noun meaning
- **Case declensions**: All four cases (Nominativ, Akkusativ, Dativ, Genitiv) are included
- **Plural forms**: Irregular plurals are validated against German patterns

### Verb Complexities  
- **Separable verbs**: Special handling for verbs like "aufstehen" (ich stehe auf)
- **Irregular conjugations**: Models validate against known irregular patterns
- **Perfect tense**: Automatic auxiliary verb selection (haben vs sein)

### Other Features
- **Case-dependent prepositions**: Models track which case each preposition requires
- **Adjective declensions**: Support for all declension patterns
- **Audio pronunciation**: All words include AWS Polly audio with German voice

## Development Workflow

1. **Add new vocabulary**: Update appropriate CSV files in `data/`
2. **Validate models**: Run `hatch run test-unit` to ensure Pydantic validation passes
3. **Enrich content**: Use enrichment scripts to add audio/images
4. **Generate cards**: Create cards using the card generators (in development)
5. **Build deck**: Use `AnkiDeckGenerator` to create final .apkg file
6. **Quality assurance**: Run full test suite with `hatch run check`

## Current Status - Clean Pipeline Architecture Migration ✅ COMPLETE

✅ **Complete**: Clean Pipeline Architecture migration with comprehensive test coverage and backward compatibility
✅ **Complete**: All Pydantic models, CSV data, AWS Polly integration, Pexels integration, CardBuilder service
✅ **Complete**: Official Anki backend with MediaEnricher integration, 586 tests, 81.69% coverage
📋 **Planned**: CLI interface, multi-language support, advanced scheduling algorithms

### Clean Pipeline Architecture Migration Status ✅ COMPLETE
- ✅ **Phase 1 Complete**: Record system (NounRecord, AdjectiveRecord, AdverbRecord, NegationRecord)
- ✅ **Phase 2 Complete**: RecordMapper service for CSV → Records conversion  
- ✅ **Phase 3 Complete**: MediaEnricher integration with existence checking and caching
- ✅ **Phase 4 Complete**: CardBuilder service with 97.83% test coverage
- ✅ **Phase 5 Complete**: Documentation updated, imports organized, backward compatibility maintained

### Architecture Support Status
- ✅ **Clean Pipeline Architecture**: noun, adjective, adverb, negation (4/7 word types)
- ✅ **Legacy FieldProcessor**: verb, preposition, phrase (3/7 word types - graceful fallback)
- ✅ **Automatic Delegation**: AnkiBackend seamlessly chooses appropriate architecture

## RECENT FIXES - ISSUES RESOLVED ✅

### Media Integration Test Failure - RESOLVED
**STATUS**: ✅ **FIXED** - Domain model architecture compatibility issue resolved

**Problem Resolved**: Test failure due to architectural mismatch after domain model delegation:
- ✅ **Root Cause**: Test was mocking old backend methods instead of new domain model services  
- ✅ **Architecture Fix**: Updated test to mock MediaService used by DomainMediaGenerator
- ✅ **Clean Architecture**: Domain models properly delegate to MediaGenerator interface
- ✅ **Test Coverage**: All 496 tests now pass including previously failing media integration test

**Successful Fix**:
1. **Test Architecture Alignment**: Updated `test_process_fields_with_media_noun()` to mock correct service layer ✅
2. **Domain Model Validation**: Confirmed Noun field processing works correctly with real services ✅
3. **Infrastructure Separation**: Maintained clean separation between domain logic and infrastructure ✅
4. **Backward Compatibility**: Old and new architectures work together seamlessly ✅

**Current State**: 
- Tests: ✅ All 496 tests passing
- Domain Models: ✅ Working correctly with proper media generation
- Architecture: ✅ Clean separation of concerns maintained
- Integration: ✅ Domain models properly integrated with infrastructure services

**Project Status**: All technical issues resolved - architecture refactoring successful

## PRIORITY 1 CODE QUALITY - COMPLETED ✅

### Test Coverage Improvements - COMPLETED
**STATUS**: ✅ **MAJOR SUCCESS** - All Priority 1 test coverage targets exceeded

**Achievement Summary**:
- ✅ **Overall Coverage**: 56.27% → **73.84%** (+17.57 percentage points)
- ✅ **Total Tests**: 263 → **401** tests (138 new comprehensive test cases)
- ✅ **New Test Files**: 3 dedicated unit test files created
- ✅ **All Targets Exceeded**: Every priority file achieved 85%+ or perfect 100% coverage

**Priority Files Completed**:
- ✅ `german_deck_builder.py`: 54.36% → **81.79%** (main orchestrator)
- ✅ `audio.py`: 54.93% → **100%** (AWS Polly service)  
- ✅ `csv_service.py`: 50.00% → **100%** (data loading)
- ✅ `german_language_service.py`: 40.98% → **95.61%** (language logic)
- ✅ `pexels_service.py`: 43.61% → **100%** (Pexels API service)

**Quality Improvements**:
- ✅ **Comprehensive Exception Handling**: Rate limits, network errors, API failures, file system errors
- ✅ **Edge Case Coverage**: Empty inputs, malformed data, missing resources, invalid configurations
- ✅ **Business Logic Testing**: German language patterns, context extraction, backoff strategies
- ✅ **Integration Scenarios**: Service interactions, configuration variations, backend compatibility

**Test Coverage Tracking**:
- ✅ **Coverage Reports**: Use `hatch run test-cov` for complete measurement (includes integration tests)
- ✅ **HTML Reports**: Detailed coverage available in `htmlcov/index.html`
- ✅ **Quality Gate**: Coverage must not decrease with any code changes

## MYPY --STRICT COMPLIANCE - ACHIEVED ✅

**STATUS**: ✅ **ULTIMATE SUCCESS** - Complete MyPy --strict compliance achieved!

**Final Achievement**:
- ✅ **MyPy Errors**: 502 → **0 errors** (100% elimination!)
- ✅ **Source Files**: All 112 files pass strict type checking
- ✅ **Test Coverage**: All 667 unit tests + 24 integration tests pass
- ✅ **Quality Gates**: Perfect MyPy + Ruff + Test compliance maintained

**Key Success Factors**:
1. **Systematic Pattern Recognition**: Fixed repetitive errors in batches rather than individually
2. **Deprecated Code Cleanup**: Removed all legacy FieldProcessor tests and patterns
3. **Type Safety Excellence**: Proper union type handling, mock typing, and strict compliance
4. **Zero Tolerance Policy**: Complete elimination of all type checking errors

**CRITICAL MAINTENANCE**: This achievement must be preserved - NO degradation allowed!

## File Structure Notes

- `src/langlearn/backends/`: Backend abstraction layer for different Anki libraries
  - `base.py`: Abstract base classes for deck generation
  - `genanki_backend.py`: genanki library implementation
  - `anki_backend.py`: Official Anki library implementation (Phase 1 prototype)
- `src/langlearn/genanki.pyi`: Type stubs for the genanki library
- `pytest.ini`: Configures test markers for live API tests
- `languages/`: Language-specific documentation for grammar rules and CSV structures
- `output/`: Generated Anki deck files (.apkg format)
- `examples/backend_demonstration.py`: Demo script showing backend abstraction
## BRANCH-BASED DEVELOPMENT WORKFLOW (MANDATORY)

**🚨 CRITICAL: ALL development MUST use feature branches - NO direct commits to main**

**🛡️ PROTECTION**: This workflow protects our hard-won quality achievements (502→0 MyPy errors, 691 passing tests)**

### Feature Branch Workflow (IMPROVED):

1. **Create Micro-Feature Branch**:
   ```bash
   git checkout -b feature/extract-rate-limit-util  # Single focused change
   # OR for micro-fixes:
   git checkout -b fix/handle-empty-api-key        # One specific bug
   # OR for micro-refactor:
   git checkout -b refactor/consolidate-env-detection  # One architectural improvement
   ```

2. **Develop with Micro-Commits**:
   - Make ONE focused change (5-10 minutes max)
   - Run Tier 2 validation (type + test-unit) 
   - Commit immediately if passing
   - Repeat for next micro-change
   - Push every 3-5 commits

3. **Create "Draft PR" Early**:
   ```bash
   git push -u origin feature/extract-rate-limit-util
   gh pr create --draft --title "Extract rate limit utility" --body "WIP: Micro-commits in progress"
   ```

4. **Progressive Development**:
   - Continue micro-commits on branch
   - Get CI feedback continuously 
   - Convert to "Ready for Review" when complete
   - Maximum 10 commits per PR
   - Maximum 200 lines of change per PR

5. **Quality Gate Enforcement**:
   - Run Tier 3 comprehensive checks before "Ready for Review"
   - Verify all CI/CD checks pass: MyPy ✅ Ruff ✅ Tests ✅ Coverage ✅
   - Self-review against architectural principles

6. **Fast Merge Process**:
   - PRs with <50 lines: immediate merge after CI passes
   - PRs with 50-200 lines: brief review then merge
   - Use "Squash and merge" for clean history
   - Delete branch after merge

### Branch Naming Convention:
- `feature/` - New features or enhancements
- `fix/` - Bug fixes  
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions or fixes

### PROHIBITED Actions (🚫 NEVER ALLOWED):
- ❌ Direct commits to main branch
- ❌ Large batch commits (>200 lines or >5 files)
- ❌ Cross-layer changes in single commit (services + models + tests)
- ❌ Merging without passing quality gates  
- ❌ Bypassing branch protection rules
- ❌ Force pushing to main
- ❌ Merging PRs with failing CI/CD checks
- ❌ "Fix everything" commits that accumulate multiple changes

## CRITICAL QUALITY MAINTENANCE RULES

**🚨 ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**

1. **MyPy --Strict Compliance**: Run `hatch run type` after EVERY code change
   - ✅ Must show "Success: no issues found in 112 source files"
   - 🚫 **ZERO tolerance** for any MyPy errors - fix immediately regardless of cause
   - 🚨 **NO DEGRADATION ALLOWED** - we will never allow quality to degrade again

2. **Ruff Linting Compliance**: Run `hatch run ruff check --fix` after EVERY code change
   - ✅ Must show zero violations
   - 🚫 **ZERO tolerance** for any Ruff violations - fix immediately

3. **Test Suite Integrity**: Run `hatch run test` after EVERY code change
   - ✅ ALL 691 tests must pass (667 unit + 24 integration)
   - 🚫 **ZERO tolerance** for any test failures - fix immediately

4. **Branch-Based Development**: ALL changes must go through feature branches and PRs
   - ✅ Create branch → develop → test → PR → review → merge
   - 🚫 **ZERO direct commits to main** - use branch workflow

5. **Micro-Commit Discipline**: All changes must be broken into atomic commits
   - ✅ Single responsibility per commit
   - 🚫 **ZERO tolerance** for large batch changes - split immediately

6. **Design Consultation**: Ask for design direction when facing new issues
   - Present multiple options with pros and cons  
   - Get approval before implementing significant changes

## SUCCESS RATE TRACKING

**📈 GOAL**: Move from 5-0% PR success rate to 90%+ through micro-commits

### Time Waste Prevention Checklist:
- [ ] Commit affects only 1-2 files
- [ ] Change is <50 lines (preferred) or <100 lines (max)
- [ ] Single architectural layer modified
- [ ] Tier 2 validation passes before commit
- [ ] Clear, specific commit message
- [ ] Push frequency: every 3-5 commits

### Red Flags That Indicate Batch Accumulation (STOP IMMEDIATELY):
- 🚩 More than 5 files in staging area
- 🚩 More than 200 lines of changes
- 🚩 Multiple unrelated fixes in progress  
- 🚩 Cross-layer modifications (utils + services + tests)
- 🚩 "Let me just fix one more thing" mentality

**⚠️ QUALITY GATE ENFORCEMENT**: The micro-commit workflow + progressive quality gates are NOT optional - they prevent the massive time waste we just experienced.

**🚨 LESSON LEARNED**: We achieved 502→0 MyPy errors through discipline. We must apply the same discipline to commit size to prevent 5% success rates!
- always run the formatter immediately before committing
- Always follow Python PEP 8 standards on imports. Imports are always put at the top of the fileV, just after any module comments and docstrings, and before module globals and constants.
Imports should be grouped in the following order:

Standard library imports.
Related third party imports.
Local application/library specific imports.
You should put a blank line between each group of imports.

Absolute imports are recommended
- do not exceed 88 characters per line to meet the ruff check guidelines.



## Environment Troubleshooting (Hatch + PyCharm)

Why you might see: bad interpreter: ...python3.13: no such file or directory
- Root cause: A stale project-local .venv (or its hatch shim) pointing to a removed Python 3.13 interpreter. Even if Hatch uses its own managed env elsewhere, shells or IDEs may still pick up .venv/bin/hatch and print the noisy prefix before running the real command.

Recommended setup
- Prefer Hatch-managed environments: Let `hatch env create` manage the venv outside the repo (default). You do not need a project-local .venv for Hatch.
- If a `.venv` directory exists in the project and causes noise, either remove it or rename it (e.g., `.venv.bck`).
- Always run hatch from PATH (e.g., `hatch run type`), not from `.venv/bin/hatch`.

One-time cleanup (if you see the bad interpreter prefix)
1) Move/Remove the local venv: `rm -rf .venv` (or rename to `.venv.bck`)
2) Create/verify Hatch env: `hatch env create`
3) Validate: `hatch run type && hatch run test-unit`

PyCharm configuration
- Preferences > Project > Python Interpreter: select the interpreter provided by Hatch (or a fresh local one you trust), not the old `.venv` that referenced Python 3.13.
- Run/Debug Configurations: set the Working directory to the project root and ensure the selected interpreter matches the above.

Team practice to avoid friction
- Do not commit or rely on a project-local `.venv` for Hatch-driven workflows.
- Avoid re-running `hatch` commands repeatedly; use the micro-commit workflow:
  - Tier 1 (fast, on current file) when coding
  - Tier 2 (type + unit tests) before each micro-commit
  - Tier 3 (format + full tests + coverage) before PR

With this setup, the noisy interpreter message disappears, and Hatch commands behave consistently across CLI and PyCharm.

- do not exaggerate or declare enthusiastically results that have not been verified by the user
- unless you have tested something and can prove it works or you have asked me to confirm it works, do not declare arrogantly that issues are resolved.  It is sloppy work that is not acceptable.
- always read the design documentation in docs/*.md and always updated the design documentation in docs/*.md when making changes. This way you do not have search the codebase blindly over and over again.
- always run the code quality tools after each 2-4 edits
- do not say things are solved unless you have proven it or I have confirmed it.
- always run the app before stating you have complete work.  Look for obvious errors and address them before declaring the job is done.