# Project Rules Summary - Anki German Language Deck Generator

## **Python Coding Standards**

### Absolute Requirements (Zero Tolerance)
- **MyPy --strict mode**: 0 errors allowed in any file
- **Ruff linting**: 0 violations permitted
- **Code formatting**: Perfect formatting via `hatch run format`
- **Line length**: Max 88 characters per line
- **Import organization**: PEP 8 compliant (stdlib → third-party → local, with blank lines between groups)
- **Type hints**: Required for all functions, methods, and class attributes

### Testing Requirements
- **All tests must pass**: Currently 813 tests (792 unit + 21 integration)
- **Coverage maintenance**: Must maintain current 73.84%
- **New components**: Minimum 95% test coverage required
- **Mock external dependencies**: Unit tests must mock APIs

## **Development Workflow**

### Micro-Commit Discipline (Mandatory)
**Commit size limits:**
- ✅ **Micro**: 1-2 files, <50 lines (PREFERRED)
- ⚠️ **Small**: 3-5 files, <100 lines (ACCEPTABLE)
- ❌ **Large**: >5 files, >200 lines (PROHIBITED)

### Progressive Quality Gates
1. **Tier 1** (Every 2-3 minutes while coding):
   ```bash
   hatch run type-quick    # Type check current file
   hatch run format-check  # Format check only
   ```

2. **Tier 2** (Before each micro-commit):
   ```bash
   hatch run type      # Full type checking
   hatch run test-unit # Core unit tests
   ```

3. **Tier 3** (Before push, every 30-45 minutes):
   ```bash
   hatch run format   # Apply formatting
   hatch run test-cov # Full test suite with coverage
   ```

### Branch Workflow
- **ALL development** via feature branches (`feature/`, `fix/`, `refactor/`)
- **NO direct commits** to main
- **Push frequency**: Every 3-5 commits OR every 30 minutes
- **Create draft PR early** for CI feedback

### Commit Message Format
```
type(scope): description [impact]
```

**Examples:**
- `fix(pexels): handle empty API key [prevents KeyError]`
- `feat(cards): add verb conjugation templates [+3 card types]`

## **Architecture Principles**

### Clean Pipeline Architecture (Mandatory)
```
CSV → Records → Domain Models → MediaEnricher → Enriched Records → CardBuilder → Cards
```

### Core Design Principles
- **Single Responsibility Principle (SRP)**: Each service has ONE clear responsibility
- **Dependency Inversion**: High-level modules depend on abstractions, not implementations
- **Interface Segregation**: Clients depend only on methods they use
- **Clean separation**: Records (DTOs) vs Services vs Domain Models

### Component Responsibilities
- **Records**: Lightweight Pydantic data transfer objects
- **MediaEnricher**: Audio/image generation with existence checking
- **CardBuilder**: Pure transformation (Records → Formatted Cards)
- **Domain Models**: German-specific validation and business logic

### Critical Rules
- **NEVER bypass** established validation patterns
- **Maintain backward compatibility** with legacy FieldProcessor
- **Ensure extensibility** for multi-language support
- **No hardcoded solutions** - everything must be configurable

## **Johnson's Law (Absolute Truth)**

> **"Any property of software that has not been verified, does not exist."**

**This means:**
- **NEVER claim "fixed"** without user validation
- **Keep debugging code** until user confirms fix works
- **Do NOT declare victory** based on unit tests alone
- **Always request** explicit user verification

## **Root Cause First Protocol**

When encountering errors:
1. **READ THE ERROR MESSAGE** - It tells you EXACTLY what to fix
2. **FIX ONLY THE ROOT CAUSE** - Don't fix peripheral issues first
3. **VERIFY WITH MINIMAL TESTING** - Test only the broken functionality
4. **KEEP DEBUGGING TOOLS** - Never remove logging until user confirms
5. **REQUEST USER VERIFICATION** - Only user can confirm if it works

## **Quality Verification Before ANY Change**

```bash
# These 5 commands MUST all pass - NO EXCEPTIONS:
hatch run type              # 1. ZERO MyPy errors
hatch run ruff check --fix  # 2. ZERO Ruff violations
hatch run format            # 3. Perfect formatting
hatch run test              # 4. ALL tests pass
hatch run test-cov          # 5. Coverage maintained
```

**⚠️ Remember:** A code change is NOT complete until ALL 5 quality gates pass!

---

**Additional Documentation:**
- `docs/ENG-DEVELOPMENT-STANDARDS.md` - Complete development standards
- `docs/ENG-PYTHON-STANDARDS.md` - Detailed Python coding standards
- `docs/ENG-DESIGN-INDEX.md` - Architectural design documentation