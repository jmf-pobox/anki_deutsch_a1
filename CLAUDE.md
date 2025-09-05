# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Anki German Language Deck Generator

This project generates customized German language Anki decks, focusing on grammatical nuances specific to German such as noun genders, separable verbs, and case-dependent prepositions.

## CRITICAL DEBUGGING PRINCIPLES (READ FIRST - PREVENTS WASTED TIME)

### Johnson's Law (ABSOLUTE TRUTH)
**"Any property of software that has not been verified, does not exist."**
- This applies to: functionality, bug fixes, code quality, design compliance, EVERYTHING
- NEVER claim something works without user confirmation

### Root Cause First Protocol (MANDATORY)
When encountering errors, follow this EXACT sequence:

1. **READ THE ERROR MESSAGE** - It tells you EXACTLY what to fix
   - Example: "Field 'DuForm' not found" → Fix the field name in templates
   - Example: "KeyError: 'english'" → Add the missing key
   - Example: "Template syntax error" → Fix the template syntax

2. **VERIFY WITH MINIMAL TESTING** - Test ONLY the broken functionality
   - Add targeted logging/debugging at the error point
   - Run the specific failing operation
   - Confirm error is resolved

3. **KEEP DEBUGGING TOOLS** - NEVER remove logging until user confirms 
    success
   - Debugging code stays until user says "it works"
   - Better to have extra logging than to be blind

4. **REQUEST USER VERIFICATION** - You cannot determine if it works
   - "Please test [specific functionality] and confirm"
   - "Check if [specific error] still occurs"
   - Wait for explicit confirmation before proceeding

### Prohibited Behaviors That Waste Time
- ❌ Claiming "I've fixed it" without user confirmation
- ❌ Removing debugging tools before user verifies the fix
- ❌ Making assumptions about what "should" work

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

## DEVELOPMENT WORKFLOW (MANDATORY)

**🚨 CRITICAL: These workflows MUST be followed - NO EXCEPTIONS!**

### For Bug Fixes:
1. **Diagnose**: READ THE ERROR MESSAGE FIRST - it tells you exactly what to fix
2. **Plan**: Identify ONE specific change (5-10 minute scope max)  
3. **Implement**: Make the MINIMAL change that fixes the ROOT CAUSE
4. **Quality Gates**: Run all 5 commands below before commit
5. **Commit**: Create atomic commit with clear message on feature branch
6. **User Verification**: Request user confirmation before claiming success

### For Feature Development:
1. **Plan**: Update appropriate CSV files in `data/` for new vocabulary
2. **Validate**: Ensure Pydantic validation passes
3. **Enrich**: Use enrichment scripts to add audio/images
4. **Generate**: Create cards using card generators
5. **Quality Gates**: Run all 5 commands below before commit
6. **Build**: Use AnkiDeckGenerator to create final .apkg file

### Commit Standards:
- **Format**: `type(scope): description [impact]`
- **Examples**: 
  - `fix(pexels): handle empty API key [prevents KeyError]`
  - `feat(cards): add verb conjugation templates [+3 card types]`
  - `refactor(utils): extract rate_limit_reached() [no behavior change]`
- **Push frequency**: Every 3-5 commits OR every 30 minutes

### Required Quality Gates (MANDATORY):

```bash
# Run after EVERY code change - NO SHORTCUTS:
hatch run type                    # 1. ZERO MyPy errors (ABSOLUTE REQUIREMENT)
hatch run ruff check --fix       # 2. ZERO Ruff violations (ABSOLUTE REQUIREMENT) 
hatch run format                  # 3. Perfect formatting (ABSOLUTE REQUIREMENT)
hatch run test                    # 4. ALL tests pass (ABSOLUTE REQUIREMENT)
hatch run test-cov                # 5. Coverage maintained (ABSOLUTE REQUIREMENT)
```

### Branch Workflow (MANDATORY):
- **ALL development** must use feature branches - NO direct commits to main
- **Branch naming**: `feature/`, `fix/`, `refactor/`, `docs/`, `test/`
- **Micro-commits**: 1-2 files, <50 lines preferred, <100 lines max
- **Push frequency**: Every 3-5 commits OR every 30 minutes
- **Create draft PR early** for continuous CI feedback

**🚨 ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**
- **Error Messages First**: When fixing bugs, address the EXACT error shown
- **MyPy --strict**: ZERO errors allowed in any file
- **Ruff linting**: ZERO violations allowed  
- **Test suite**: ALL tests must pass
- **Coverage**: Must not decrease from current levels
- **User Verification**: Bug fixes require user confirmation before claiming success
- **Branch-based development**: Create branch → develop → test → PR → review → merge

**🚫 A CODE CHANGE IS NOT COMPLETE UNTIL ALL 5 QUALITY GATES PASS!**

## GITHUB ISSUE MANAGEMENT (MANDATORY)

**🚨 CRITICAL: GitHub issues are NOT documentation - they are brief pointers to misalignment**

### Purpose of GitHub Issues
GitHub issues serve as **state management markers** that identify where code diverges from authoritative specifications. They are NOT:
- ❌ Replacement for design documentation
- ❌ Duplicate of specification details
- ❌ Comprehensive implementation guides
- ❌ Alternative source of truth

### Issue Creation Principles (MANDATORY)

1. **Brief Summary Only**: Issues should contain:
   - **Problem**: One sentence describing the misalignment
   - **Location**: Which component/file is affected
   - **Reference**: Link to authoritative spec (e.g., PROD-CARD-SPEC.md)
   - **Impact**: What functionality is blocked or broken

2. **Defer to Authoritative Docs**: 
   - ✅ "Card generation missing required fields - see PROD-CARD-SPEC.md section 3.2"
   - ❌ "Card generation needs DuForm, SieForm, IhrForm fields with specific formatting..."

3. **Avoid Specification Duplication**:
   - Issues should NOT repeat detailed requirements from specs
   - This prevents conflicting directions when specs are updated
   - Single source of truth principle must be maintained

4. **State Management Focus**:
   - Issues track WHAT needs fixing, not HOW to fix it
   - Implementation details belong in documentation
   - Issues are checkpoints, not instruction manuals

### Issue Template (REQUIRED FORMAT)
```markdown
## Misalignment Detected
**Component**: [specific file/service]
**Specification**: [link to authoritative doc#section]
**Current Behavior**: [one sentence]
**Expected Behavior**: [one sentence referencing spec]
**Blocked Work**: [what can't proceed until fixed]

⚠️ See specification document for implementation requirements.
```

### Integration with Workflow

**When to Create Issues**:
- During code review when detecting spec violations
- When user reports functionality not matching requirements
- Before starting work that depends on unimplemented specs
- As markers for technical debt that blocks progress

**When NOT to Create Issues**:
- For bugs with clear error messages (fix immediately)
- For minor formatting or style violations (fix in current commit)
- To document how something should work (use design docs)
- As a todo list for features (use TodoWrite tool)

### Anti-Patterns to Avoid
- ❌ Creating issues that duplicate specification content
- ❌ Using issues as alternative documentation
- ❌ Writing implementation details in issue descriptions
- ❌ Creating issues for work you can complete immediately
- ❌ Closing issues without verifying alignment with specs

### Issue Lifecycle
1. **Create**: Brief pointer to misalignment
2. **Reference**: Link to authoritative specification
3. **Fix**: Implement according to specification (not issue description)
4. **Verify**: Confirm alignment with specification
5. **Close**: Only after verification against authoritative docs

**🚨 REMEMBER**: Issues expire, specifications endure. Always implement from specs, not from issue descriptions.

## CRITICAL COMMUNICATION PROTOCOL (MANDATORY)

**🚨 NEVER CLAIM "FIXED" WITHOUT USER VALIDATION**

**Johnson's Law Reminder**: You CANNOT verify if something works. Only the user can.

The following communication protocol is MANDATORY:

### ❌ PROHIBITED Communication Patterns:
```
"I've fixed the blank card issue"
"The duplicates are eliminated"  
"This should work now"
"The issue has been resolved"
"Everything is working perfectly"
"The problem is completely solved"
"All issues have been addressed"
Any claim of success without user confirmation
```

### ✅ REQUIRED Communication Protocol:
```
"I've implemented changes targeting the EXACT error you reported:

**Root Cause Addressed**:
- Error Message: [exact error from user/logs]
- Fix Applied: [specific change to address that exact error]
- File Modified: [specific file:line that had the error]

**Changes Made**:
- Modified: [specific files and line numbers]
- Logic: [brief explanation focusing on the root cause fix]

**Internal Validation**:
- ✅ Error-specific test: [tested the exact failing scenario]
- ✅ MyPy: All type checks pass
- ✅ Tests: All 772 tests pass  
- ⚠️  Debugging logs: KEPT IN PLACE for your verification

**Critical Limitation**: 
I cannot verify if this actually fixes your issue. Per Johnson's Law,
only you can confirm if the functionality works.

**Required User Testing**:
Please test the SPECIFIC issue that was failing:
1. [Exact operation that was broken]
2. [Expected vs actual behavior]
3. Report if the error message still appears

**Debugging Output**:
The code includes logging that will show:
- [What the logging will display]
- [Where to find the output]

**If Issues Persist**:
Please provide:
- The NEW error message (if different)
- Screenshot showing the issue
- Any debugging output from the logs
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

# Environment Testing
hatch run test-env          # Test all API keys (Anthropic + Pexels) setup and connectivity
```

### Testing Strategy
The project uses separate test categories with comprehensive coverage measurement:
- **Unit tests**: Mock external dependencies, run with `hatch run test-unit`
- **Integration tests**: Require live API keys, marked with `@pytest.mark.live`, run with `hatch run test-integration`
- **Coverage testing**: Use `hatch run test-cov` for complete measurement (target: >85%)
- **Ask the user**: The user will import the deck into Anki and verify actual functionality.
- API keys are managed via the system keyring using the `api_keyring.py` utility


Additional verification commands:
```bash
hatch run test-unit      # All tests must pass
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

### Core Components - System Architecture

The project uses a hybrid architecture for data processing:

**Data Flow**: CSV → RecordMapper → Records → MediaEnricher → Domain Models → Enriched Records → CardBuilder → AnkiBackend

1. **Models** (`src/langlearn/models/`): 
   - **Records**: Pydantic data transport objects (NounRecord, AdjectiveRecord, etc.) with validation
   - **Domain Models**: Objects with German language business logic methods (Noun, Adjective, etc.)
   - **Factory**: ModelFactory creates domain model instances for fallback processing

2. **Services** (`src/langlearn/services/`): 
   - **RecordMapper**: CSV → Records conversion
   - **MediaEnricher**: Converts Records → Domain Models, calls business logic methods, returns enriched Records
   - **CardBuilder**: Enriched Records → formatted card templates
   - **External APIs**: AWS Polly, Pexels, Anthropic integration

3. **Backends** (`src/langlearn/backends/`): 
   - **DeckBackend**: Abstract interface for deck generation
   - **AnkiBackend**: Uses enriched Records for card creation, falls back to ModelFactory when Records processing fails

4. **Utils** (`src/langlearn/utils/`): API key management, audio/image utilities

5. **Main Application** (`deck_builder.py`): High-level orchestrator

### Data Architecture
- **CSV Files** (`data/`): Source data for all parts of speech
- **Audio** (`data/audio/`): AWS Polly-generated pronunciation files
- **Images** (`data/images/`): Pexels-sourced images with automatic backup
- **Backups** (`data/backups/`): Automatic CSV backups during enrichment

### Key Design Patterns

- **Hybrid Architecture**: Data flows through both Records and Domain Models in sequence
  - **Records**: Pydantic objects for data validation and transport
  - **Domain Models**: Objects with German language business logic methods
  - **MediaEnricher**: Orchestrates Records → Domain Models → enriched Records conversion
  - **CardBuilder**: Transforms enriched Records into formatted card templates

- **Dual Processing System**: Records and Domain Models work together
  - **Record Types**: All word types use Pydantic BaseRecord models for validation
  - **Domain Models**: Contain German-specific business logic methods (get_combined_audio_text, etc.)
  - **MediaEnricher**: Bridges between the two systems for media generation

- **Performance Optimizations**: 
  - **Hash-based Caching**: Avoids duplicate API calls for media generation
  - **Existence Checking**: MediaEnricher checks for existing files before generation

- **German Language Specialization**: 
  - **Pydantic Validation**: German-specific rules in Records (article validation, case patterns)
  - **Template System**: HTML/CSS templates for different card types  
  - **Business Logic Methods**: Domain models contain German grammar processing logic

## API Key Management

The project uses the system keyring for secure credential storage:

```bash
# Add API keys
python scripts/api_keyring.py add ANTHROPIC_API_KEY your_key_here
python scripts/api_keyring.py add PEXELS_API_KEY your_key_here

# View stored keys
python scripts/api_keyring.py view ANTHROPIC_API_KEY

# Remove keys
python scripts/api_keyring.py remove ANTHROPIC_API_KEY

# Sync keys to environment (for scripts)
python scripts/sync_api_key.py

# Test API key environment setup
hatch run test-env
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


## Current Status

### Supported Word Types
- **Fully Supported**: noun, adjective, adverb, negation, verb (via Records + CardBuilder)
- **Legacy Support**: preposition, phrase (via fallback system)
- **Total Coverage**: All 7 German A1 word types functional

## Project Structure

See `docs/ENG-DEVELOPMENT-GUIDE.md` for complete project structure details.

Key directories:
- `src/langlearn/` - Main application code
- `data/` - CSV vocabulary files and generated media
- `tests/` - Unit and integration tests  
- `docs/` - Comprehensive documentation

## Quality Maintenance

### Absolute Requirements (NO EXCEPTIONS)

1. **MyPy Compliance**: 0 errors required in strict mode
2. **Ruff Linting**: 0 violations required
3. **Test Suite**: All tests must pass
4. **Coverage**: Must not decrease from 74%
5. **Branch Workflow**: All changes via feature branches

See `docs/ENG-DEVELOPMENT-GUIDE.md` for complete quality gate requirements and workflow.

## SUCCESS RATE TRACKING

### Red Flags That Indicate Batch Accumulation (STOP IMMEDIATELY):
- 🚩 More than 5 files in staging area
- 🚩 More than 200 lines of changes
- 🚩 Multiple unrelated fixes in progress  
- 🚩 Cross-layer modifications (utils + services + tests)
- 🚩 "Let me just fix one more thing" mentality

**⚠️ QUALITY GATE ENFORCEMENT**: The micro-commit workflow + progressive quality gates are NOT optional - they prevent the massive time waste we just experienced.

- always run the formatter immediately before committing
- Always follow Python PEP 8 standards on imports. Imports are always put at the top of the fileV, just after any module comments and docstrings, and before module globals and constants.

- Imports should be grouped in the following order:

Standard library imports.
Related third party imports.
Local application/library specific imports.
You should put a blank line between each group of imports.

Absolute imports are recommended
- do not exceed 88 characters per line to meet the ruff check guidelines.

## Environment Troubleshooting (Hatch + PyCharm)

Recommended setup
- Prefer Hatch-managed environments: Let `hatch env create` manage the venv outside the repo (default). You do not need a project-local .venv for Hatch.
- Always run hatch from PATH (e.g., `hatch run type`), not from `.venv/bin/hatch`.

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
- do not say things are solved unless you have proven it or the user has confirmed it.
- always run the app before stating you have complete work.  Look for obvious errors and address them before declaring the job is done.
## FINAL REMINDERS - CORE PRINCIPLES

### Johnson's Law (NEVER FORGET)
**"Any property of software that has not been verified, does not exist."**
- You CANNOT verify end-to-end functionality - only the user can
- Do NOT claim bugs are fixed until the user confirms
- Do NOT remove debugging code until the user confirms the fix works
- Do NOT declare victory based on unit tests alone

### Error Messages Are Sacred
When you see an error like "Field 'DuForm' not found":
1. That IS the problem - fix THAT field name
2. Do NOT fix unit tests first
3. Do NOT refactor code first  
4. Do NOT clean up formatting first
5. Fix the EXACT issue the error describes, THEN handle other concerns

### Communication Discipline
- State what you changed and why
- Explain what needs user verification
- Never claim success without user confirmation
- Keep responses focused on solving the actual problem
- Do not make value judgements about the code quality unless asked to do so.  Only write factual statements into documentation.
- never use meaningless terms like enterprise grade.  never respond to criticism with your are right and other platitudes.
- Prefer well defined protocols over duck typing and hasattr.
- Using None sparingly and do not declare parameters to take a type or None unless there is no alternative.
- never write inline import statements.
- never use mock objects in production code, only test code.
- ask me for design direction, do not come up with your own ideas of what good is.
- make your commit messages modest and relatively short.
- always us direct imports using __future__ in Python
- do not code hacks, defensive coding, fallbacks. 
- the goal is to write well-typed code with low conditional complexity 
  that fails (e.g., throws and exception) when validation fails.