# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Anki Foreign Language Learning Deck Generator

This project generates customized language learning Anki decks. One issue 
this system addresses is that many existing Anki decks do not reflect the 
specific challenges of the target language.  For example, memorizing 
German and irregular verb conjugations are two challenges. The grammar of 
the target language affects the best Anki deck design. This Anki deck 
generator seeks to address that challenge.  The primary user of this 
system is intended to be the language learner. A secondary user of the 
system is intended to be foreign language teachers. This system is 
inspired by Fluent Forever, a book by Gabriel Wyner.  

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

## CLEAN DESIGN IMPROVEMENT PROTOCOL (MANDATORY)

**🚨 CRITICAL: When improving designs, eliminate ALL traces of the old approach**

### Complete Removal Principle
When implementing design improvements, **delete everything** related to the old approach:

1. **Old Code Path**: Remove the entire old implementation - no fallbacks, no "just in case" code
2. **Old Tests**: Delete all tests for the deprecated approach - they test obsolete behavior
3. **Old Documentation**: Remove all references to the old design from docs and comments
4. **Old Interfaces**: Delete deprecated methods, classes, and APIs completely

### Why Complete Removal is Mandatory
- **Git preserves history** - the old implementation is permanently available in version control
- **Fallback code creates confusion** - multiple ways to do the same thing violates single responsibility
- **Deprecated tests mislead** - they validate behavior that should no longer exist
- **Stale docs confuse users** - mixed old/new guidance creates uncertainty

### Implementation Steps
1. **Implement new design** with comprehensive tests
2. **Update all callers** to use new approach
3. **Delete old implementation** completely (code + tests + docs)
4. **Verify removal** - ensure no references to old approach remain
5. **Commit with clear message** indicating complete migration

**🚫 NEVER**: Keep old code "just in case" or add fallback behavior during design improvements

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

# Additional verification commands:
hatch run test-unit              # Unit tests only (no live API calls)
hatch run test-integration       # Integration tests (requires API keys)
hatch run test-unit-cov         # Unit tests with coverage report
hatch run lint                  # Check linting rules
hatch run check                 # All checks (lint + type + test)
hatch run check-unit            # All checks with unit tests only
```

### Branch Workflow (MANDATORY):
- **ALL development** must use feature branches - NO direct commits to main
- **Branch naming**: `feature/`, `fix/`, `refactor/`, `docs/`, `test/`

### Refactoring Best Practices (PROVEN EFFECTIVE):

**Use IDE Refactoring Tools When Available**:
- **PyCharm rename operations** are significantly more reliable than manual find/replace
- **Automatic import updates** catch edge cases that manual changes miss
- **Git history preservation** better maintained by IDE tools
- **Speed advantage** - PyCharm completed 22-file rename instantly vs manual process

**Incremental Approach for Complex Extractions**:
- **One record at a time** - Extract single class, test, then continue
- **Quality gates between steps** - Run full test suite after each extraction  
- **Type narrowing for MyPy** - Use `isinstance()` assertions for type safety
- **Preserve backward compatibility** - Maintain legacy interfaces during migration
- **Create draft PR early** for continuous CI feedback

**🚨 ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**
- **Error Messages First**: When fixing bugs, address the EXACT error shown
- **MyPy --strict**: ZERO errors allowed in any file
- **Ruff linting**: ZERO violations allowed  
- **Test suite**: ALL tests must pass
- **Coverage**: Must not decrease from current levels
- **User Verification**: Bug fixes require user confirmation before claiming success

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
   - **Reference**: Link to authoritative spec (e.g., PM-CARD-SPEC.md)
   - **Impact**: What functionality is blocked or broken

2. **Defer to Authoritative Docs**: 
   - ✅ "Card generation missing required fields - see PM-CARD-SPEC.md section 3.2"
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

## Development Commands & Testing

### Hatch Environment Management
```bash
# Create environment
hatch env create

# Run tests
hatch run test               # All tests (unit + integration)
hatch run test-unit         # Unit tests only (no live API calls)
hatch run test-integration  # Integration tests (requires API keys)
hatch run test-cov          # Complete coverage measurement (target: >85%)

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
- **User verification**: The user imports the deck into Anki and verifies actual functionality
- **API keys**: Managed via the system keyring using the `api_keyring.py` utility

## Project Architecture

**📋 For detailed architecture information, see the comprehensive design documentation in `docs/`:**
- **`docs/ENG-COMPONENT-INVENTORY.md`** - Complete component inventory and responsibilities
- **`docs/ENG-QUALITY-METRICS.md`** - Current quality metrics and technical debt analysis
- **`docs/ENG-DEVELOPMENT-STANDARDS.md`** - Architectural principles and development standards

### Architecture Overview

For detailed architecture information, see **[docs/ENG-ARCHITECTURE.md](docs/ENG-ARCHITECTURE.md)** which contains:
- Complete system architecture and design patterns
- Data flow pipeline: CSV → Records → MediaEnricher → CardBuilder → AnkiBackend
- Component responsibilities and interactions
- Multi-language architecture roadmap

**Current Status**: Clean Pipeline Architecture with German A1 fully supported. All 7 German word types functional via Records + CardBuilder system.

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

## Project Structure

See `docs/ENG-DEVELOPMENT-GUIDE.md` for complete project structure details.

Key directories:
- `src/langlearn/` - Main application code
- `languages/` - CSV vocabulary files and generated media
- `tests/` - Unit and integration tests  
- `docs/` - Comprehensive documentation

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


### Error Messages Are Sacred
When you see an error like "Field 'DuForm' not found":
1. That IS the problem - fix THAT field name
2. Do NOT fix unit tests first
3. Do NOT refactor code first  
4. Do NOT clean up formatting first
5. Fix the EXACT issue the error describes, THEN handle other concerns

### Additional Communication & Code Standards
- State what you changed and why
- Explain what needs user verification
- Keep responses focused on solving the actual problem
- Do not make value judgements about the code quality unless asked to do so
- Never use meaningless terms like "enterprise grade" or respond to criticism with platitudes
- Ask user for design direction, do not come up with your own ideas of what good is
- Make commit messages modest and relatively short
- Do not add Claude Code attribution to every commit

**Code Standards**:
- Prefer well defined protocols over duck typing and hasattr
- **Protocol Inheritance Required**: All classes implementing protocols MUST explicitly inherit from the protocol class (e.g., `class ConcreteClass(ProtocolClass):`) for PyCharm visibility, type safety, and IDE support
- Use None sparingly; avoid `type | None` parameters unless no alternative
- Never write inline import statements
- Never use mock objects in production code, only test code
- Always use direct imports using `__future__` in Python
- Do not code hacks, defensive coding, or fallbacks
- Write well-typed code with low conditional complexity that fails fast (throws exceptions) when validation fails
- Avoid buzzwords, jargon, and adjectives (especially superlatives), and use precise, factual, accurate descriptions instead in all documentation and all conversation.
- Speak with humility.  Do not brag, exaggerate, or spew non-sense.
- use simple plain accurate language.  Do not talk like a marketing droid. Do not obfuscate facts with jargon.
- STOP USING THE PHRASE CLEAN PIPELINE
- Do not say "Clean Architecture" this is some buzzword you are inventing.