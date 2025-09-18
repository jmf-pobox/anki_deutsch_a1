# Development Guide - Standards, Workflow, and Tools

**Document Type**: Comprehensive Development Guide
**Purpose**: Single source of truth for development standards, workflows, and quality requirements
**Audience**: All engineers working on this codebase

---

## Quick Reference

### Essential Commands
```bash
# Quality gates (run after every change)
hatch run type              # MyPy type checking - MUST show 0 errors
hatch run ruff check --fix  # Linting with auto-fix - MUST show 0 violations
hatch run format            # Code formatting
hatch run test              # Run all tests - MUST all pass
hatch run test-cov          # Test with coverage - MUST maintain current levels

# Development commands
hatch run test-unit         # Unit tests only (no API calls)
hatch run test-integration  # Integration tests (requires API keys)
hatch run app              # Run main deck creation
```

### Quality Standards
- **Type Safety**: 0 MyPy errors in strict mode (enforced)
- **Code Quality**: 0 Ruff violations (enforced)
- **Test Coverage**: Maintain or improve current levels
- **All Tests**: Must pass before any commit

---

## Development Workflow

### 🛡️ Purpose: Quality Protection

This workflow protects our critical quality achievements:
- **MyPy --strict compliance**: Zero errors maintained
- **Test suite integrity**: All tests passing
- **Code quality standards**: Zero Ruff violations, maintained coverage
- **Clean Architecture**: Separation of concerns maintained

### 1. Branch-Based Development (MANDATORY)

**All development MUST use feature branches - NO direct commits to main**

#### Branch Creation
```bash
# Feature development
git checkout -b feature/your-feature-name

# Bug fixes
git checkout -b fix/issue-description

# Documentation updates
git checkout -b docs/documentation-update

# Refactoring work
git checkout -b refactor/component-name

# Test improvements
git checkout -b test/test-description
```

#### Local Development Loop
1. **Make changes** on your feature branch
2. **Run quality gates** (mandatory 6-step workflow):
   ```bash
   hatch run type                         # MyPy: ZERO errors
   hatch run ruff check --fix            # Ruff: ZERO violations
   hatch run format                       # Code formatting
   hatch run test                         # ALL tests pass
   hatch run test-cov                     # Coverage maintained
   hatch run type && hatch run test       # Final verification
   ```
3. **Commit only when** all 6 steps pass ✅
4. **Repeat** until feature is complete

#### Commit Guidelines
- **One change per commit**: Each commit should have a single, clear purpose
- **Commit message format**: `type(scope): description [impact]`
- **Examples**:
  - `fix(media): handle missing audio files [prevents FileNotFoundError]`
  - `feat(cards): add verb imperative support [+1 card type]`
  - `refactor(services): extract validation logic [no behavior change]`

### 2. Pull Request Process

#### Creating the PR
```bash
# Push your branch
git push -u origin feature/your-feature-name

# Create PR via GitHub interface or CLI
gh pr create --title "Your feature description" --body-file .github/pull_request_template.md
```

#### PR Requirements
- **Title**: Clear, descriptive summary of changes
- **Template**: Use auto-populated PR template checklist
- **Quality gates**: All CI/CD checks must pass
- **Self-review**: Review your own changes first

#### CI/CD Quality Gates
The following checks run automatically on every PR:

1. **MyPy Type Check**: Must show zero errors
2. **Ruff Linting**: Must show zero violations
3. **Code Formatting**: Must pass formatting check
4. **Unit Test Suite**: All unit tests must pass
5. **Coverage Check**: Must maintain current coverage levels
6. **Final Verification**: Combined MyPy + test check

#### Review Process
- **Self-review**: Verify all quality gates pass
- **Architectural review**: Ensure Clean Architecture compliance
- **Documentation**: Verify docs are updated if needed

### 3. Merge Requirements

**✅ Required for merge:**
- All CI/CD quality gates pass
- PR template checklist completed
- No merge conflicts
- Branch is up to date with main

**❌ Prohibited (will block merge):**
- Any MyPy errors
- Any Ruff violations
- Any test failures
- Coverage decrease
- Missing quality gate checks

### 4. Post-Merge Cleanup
```bash
# After successful merge:
git checkout main
git pull origin main
git branch -d feature/your-feature-name  # Delete local branch
```

### 🚫 Prohibited Actions

**These actions are NEVER allowed:**

1. **Direct commits to main**: All changes must go through feature branches
2. **Bypassing quality gates**: Every PR must pass all CI/CD checks
3. **Force pushing to main**: Protected branch rules prevent this
4. **Merging failing PRs**: No merge allowed with failing quality gates
5. **Incomplete PR templates**: All checklist items must be completed

### 🏗️ Branch Protection Rules

The main branch is protected with these rules:

- **Require pull request reviews** before merging
- **Dismiss stale reviews** when new commits are pushed
- **Require status checks** to pass:
  - MyPy Type Check ✅
  - Ruff Linting ✅
  - Code Formatting ✅
  - Unit Test Suite ✅
  - Coverage Check ✅
  - Final Verification ✅
- **Require branches to be up to date** before merging
- **Include administrators** in restrictions
- **No force pushes** allowed

### 🔄 Workflow Examples

#### Example 1: New Feature
```bash
# Create feature branch
git checkout -b feature/add-verb-conjugation-cards

# Develop and test locally
# ... make changes ...
hatch run type && hatch run ruff check --fix && hatch run format && hatch run test && hatch run test-cov

# Push and create PR
git add -A
git commit -m "Add verb conjugation card generation"
git push -u origin feature/add-verb-conjugation-cards
gh pr create --title "Add verb conjugation card generation"

# After CI passes and review, merge via GitHub
```

#### Example 2: Bug Fix
```bash
# Create fix branch
git checkout -b fix/media-enricher-error-handling

# Fix bug and test
# ... make changes ...
hatch run type && hatch run test

# Push and create PR
git add -A
git commit -m "Fix media enricher error handling for missing files"
git push -u origin fix/media-enricher-error-handling
gh pr create --title "Fix media enricher error handling"

# After CI passes, merge via GitHub
```

### 🚨 Emergency Procedures

**In rare emergencies requiring hotfixes:**

1. **Create hotfix branch**: `git checkout -b hotfix/critical-security-fix`
2. **Minimal changes only**: Fix the specific issue, nothing else
3. **Full quality gates**: Still must pass all 6 steps
4. **Expedited review**: Get immediate review but don't skip quality gates
5. **Post-hotfix analysis**: Review why emergency occurred

**Note**: Even emergencies cannot bypass MyPy/Ruff/Test requirements.

---

## Coding Standards

### Python Standards (PEP 8 Compliance)

#### Import Organization
```python
# Standard library imports
import json
import os
from pathlib import Path

# Third-party imports
import pandas as pd
from pydantic import BaseModel, Field

# Local imports
from langlearn.models import NounRecord
from langlearn.services import CardBuilder
```

#### Type Annotations (MANDATORY)
```python
# All functions must be fully typed
def process_record(record: BaseRecord, options: dict[str, Any]) -> ProcessedData:
    """Process a vocabulary record with given options."""
    # Implementation
    
# Use modern union syntax (Python 3.10+)
def get_value(key: str) -> str | None:
    """Get value or None if not found."""
    return values.get(key)
```

#### Error Handling
```python
# Be specific with exceptions
try:
    record = create_record(data)
except ValidationError as e:
    logger.error(f"Invalid record data: {e}")
    raise RecordCreationError(f"Failed to create record: {e}") from e
except Exception as e:
    logger.exception("Unexpected error in record creation")
    raise
```

### Clean Architecture Principles

#### Single Responsibility Principle (SRP)
Each class/module should have exactly one reason to change:

```python
# GOOD: Single responsibility
class MediaEnricher:
    """Handles media generation and caching."""
    def enrich_record(self, record: BaseRecord) -> dict[str, str]:
        # Only responsible for media generation
        
class CardBuilder:
    """Transforms records into Anki cards."""
    def build_card(self, record: BaseRecord) -> Card:
        # Only responsible for card formatting

# BAD: Multiple responsibilities
class DataProcessor:
    def load_csv(self): ...          # File I/O
    def validate_data(self): ...      # Validation
    def generate_audio(self): ...     # Media generation
    def create_cards(self): ...       # Card creation
```

#### Dependency Injection
```python
# GOOD: Dependencies injected
class CardBuilder:
    def __init__(self, template_service: TemplateService):
        self._template_service = template_service

# BAD: Hard-coded dependencies
class CardBuilder:
    def __init__(self):
        self._template_service = TemplateService()  # Creates own dependency
```

#### Interface Segregation
```python
# GOOD: Focused interfaces
class AudioGenerator(Protocol):
    def generate_audio(self, text: str) -> str: ...

class ImageGenerator(Protocol):
    def generate_image(self, query: str) -> str: ...

# BAD: Fat interface
class MediaGenerator(Protocol):
    def generate_audio(self, text: str) -> str: ...
    def generate_image(self, query: str) -> str: ...
    def generate_video(self, script: str) -> str: ...  # Not all clients need this
```

---

## Infrastructure/Platform/Languages Architecture

**Updated**: 2024-09-18 - New architectural standards

### Overview

The langlearn system follows a three-tier **Infrastructure/Platform/Languages** architecture that provides clear separation of concerns and extensibility:

- **🏗️ Infrastructure Layer** (`langlearn.infrastructure.*`): "You use this" - Stable, concrete implementations
- **🎯 Platform Layer** (`langlearn.core.*`): "You extend this" - Extension points and orchestration
- **🌍 Languages Layer** (`langlearn.languages.*`): "You implement this" - Language-specific implementations

### Architectural Guidelines

#### 🏗️ Infrastructure Layer - "You use this"

**Package**: `langlearn.infrastructure.*`
**Purpose**: Stable implementations that all languages use without modification

```python
# GOOD: Using infrastructure services
from langlearn.infrastructure.services import AudioService, PexelsService
from langlearn.infrastructure.backends import AnkiBackend

# Infrastructure provides concrete implementations
audio_service = AudioService(voice_id="Tatyana", language_code="ru-RU")
backend = AnkiBackend("Russian Deck", media_service)
```

**Infrastructure Layer Rules:**
- ✅ **Closed for modification**: Do not edit infrastructure components for language-specific needs
- ✅ **Language agnostic**: Infrastructure components work with any language
- ✅ **Stable interfaces**: Well-defined contracts that rarely change
- ❌ **No language-specific logic**: Keep all linguistic knowledge in language layer

#### 🎯 Platform Layer - "You extend this"

**Package**: `langlearn.core.*`
**Purpose**: Extension points and orchestration contracts

```python
# GOOD: Extending platform protocols
from langlearn.core.protocols import MediaGenerationCapable, CardProcessorProtocol
from langlearn.core.records import BaseRecord

@dataclass
class SpanishNoun(MediaGenerationCapable):
    """Spanish noun extending platform protocol."""

    def get_combined_audio_text(self) -> str:
        # Spanish-specific audio generation logic
        return f"{self.article} {self.word}. {self.example}"

    def get_image_search_strategy(self, ai_service=None) -> str:
        # Spanish-specific image search logic
        return f"{self.english} Spanish vocabulary"

class SpanishRecord(BaseRecord):
    """Spanish record extending platform base."""
    word: str
    article: str
    gender: str

    @field_validator('gender')
    def validate_spanish_gender(cls, v):
        # Spanish-specific validation
        if v not in ['masculino', 'femenino']:
            raise ValueError(f"Invalid Spanish gender: {v}")
        return v
```

**Platform Layer Rules:**
- ✅ **Open for extension**: Implement protocols and extend base classes
- ✅ **Language-agnostic orchestration**: Platform handles common workflow logic
- ✅ **Protocol compliance**: All language implementations must follow contracts
- ❌ **No concrete implementations**: Platform defines interfaces, not implementations

#### 🌍 Languages Layer - "You implement this"

**Package**: `langlearn.languages.*`
**Purpose**: Language-specific implementations using platform extension points

```python
# GOOD: Language-specific implementations
from langlearn.languages.spanish.models import SpanishNoun
from langlearn.languages.spanish.services import SpanishCardProcessor

class SpanishCardProcessor(CardProcessorProtocol):
    """Spanish-specific card processing."""

    def process_noun(self, noun: SpanishNoun, media_data: dict) -> tuple[list[str], NoteType]:
        # Spanish-specific card formatting
        fields = [
            f"{noun.article} {noun.word}",  # Spanish article handling
            noun.english,
            noun.gender,  # Spanish gender system
            noun.plural,  # Spanish plural rules
            media_data.get('audio', ''),
            media_data.get('image', ''),
        ]
        return fields, self._get_spanish_note_type()
```

**Languages Layer Rules:**
- ✅ **Complete implementation freedom**: Implement any language-specific logic
- ✅ **Protocol compliance**: Must implement all required platform contracts
- ✅ **Linguistic expertise**: Encode all language-specific knowledge here
- ❌ **No infrastructure dependencies**: Use infrastructure through platform layer only

### Package Import Standards

#### Import Hierarchy (MANDATORY)

```python
# CORRECT: Follow architectural layers
from langlearn.infrastructure.services import AudioService  # Infrastructure
from langlearn.core.protocols import MediaGenerationCapable  # Platform
from langlearn.languages.german.models import Noun         # Language

# INCORRECT: Cross-layer violations
from langlearn.infrastructure.services.audio_service import AudioService  # Too specific
from langlearn.languages.german.models import Noun
from langlearn.infrastructure.backends import AnkiBackend  # Skip platform layer
```

#### Layer Dependency Rules

```python
# ✅ ALLOWED: Higher layers can import from lower layers
# Languages → Platform → Infrastructure

# Languages can use Platform
from langlearn.core.protocols import MediaGenerationCapable

# Languages can use Infrastructure (through Platform)
from langlearn.core.deck import DeckBuilderAPI  # Platform orchestrates infrastructure

# Platform can use Infrastructure
from langlearn.infrastructure.services import MediaEnricher

# ❌ FORBIDDEN: Lower layers cannot import from higher layers
# Infrastructure → Platform (FORBIDDEN)
# Infrastructure → Languages (FORBIDDEN)
# Platform → Languages (FORBIDDEN)

# BAD: Infrastructure depending on languages
from langlearn.languages.german.models import Noun  # FORBIDDEN in infrastructure
```

### Adding New Languages

#### Step 1: Create Language Package Structure
```bash
# Create new language directory
mkdir -p src/langlearn/languages/spanish/
mkdir -p src/langlearn/languages/spanish/models/
mkdir -p src/langlearn/languages/spanish/services/
mkdir -p src/langlearn/languages/spanish/records/
```

#### Step 2: Implement Domain Models
```python
# File: src/langlearn/languages/spanish/models/noun.py
from dataclasses import dataclass
from langlearn.core.protocols import MediaGenerationCapable

@dataclass
class SpanishNoun(MediaGenerationCapable):
    word: str
    article: str
    gender: str
    plural: str
    english: str

    def get_combined_audio_text(self) -> str:
        return f"{self.article} {self.word}. {self.english}."

    def get_image_search_strategy(self, ai_service=None) -> str:
        return f"{self.english} Spanish vocabulary"
```

#### Step 3: Create Record Classes
```python
# File: src/langlearn/languages/spanish/records/noun_record.py
from langlearn.core.records import BaseRecord
from pydantic import field_validator

class SpanishNounRecord(BaseRecord):
    word: str
    article: str
    gender: str
    plural: str
    english: str

    @field_validator('gender')
    def validate_spanish_gender(cls, v):
        valid_genders = ['masculino', 'femenino']
        if v not in valid_genders:
            raise ValueError(f"Invalid Spanish gender: {v}")
        return v
```

#### Step 4: Build Language Services
```python
# File: src/langlearn/languages/spanish/services/card_processor.py
from langlearn.core.protocols import CardProcessorProtocol
from langlearn.infrastructure.backends.base import NoteType

class SpanishCardProcessor(CardProcessorProtocol):
    def process_noun(self, model, media_data) -> tuple[list[str], NoteType]:
        # Spanish-specific processing logic
        pass
```

#### Step 5: Register with Platform
```python
# File: src/langlearn/languages/spanish/language.py
from langlearn.core.protocols import TTSConfig

class SpanishLanguage:
    def get_tts_config(self) -> TTSConfig:
        return TTSConfig(
            voice_id="Conchita",
            language_code="es-ES",
            engine="neural"
        )
```

### Architecture Compliance Checks

#### Automated Validation
```bash
# Check import compliance (planned)
hatch run check-architecture

# Verify layer boundaries (planned)
hatch run check-dependencies

# Validate protocol compliance (planned)
hatch run check-protocols
```

#### Manual Code Review Checklist
- ✅ **No circular dependencies** between layers
- ✅ **Protocol compliance** in language implementations
- ✅ **Proper import hierarchy** followed
- ✅ **Single responsibility** maintained in each component
- ✅ **Language-agnostic** infrastructure and platform code

### Migration from Legacy Architecture

**Completed Migration (2024-09-18)**:
- ✅ `langlearn.core.services.*` → `langlearn.infrastructure.services.*`
- ✅ `langlearn.core.backends.*` → `langlearn.infrastructure.backends.*`
- ✅ Platform renamed from `platform` to `core` (Python naming conflict resolution)
- ✅ All 691 tests updated and passing
- ✅ Zero architectural technical debt

**Future Migrations**:
- Managers layer integration with platform orchestration
- Enhanced protocol-based extension system
- Dynamic language discovery and registration

---

## Testing Standards

### Test Coverage Requirements
- **New code**: Minimum 80% coverage
- **Critical paths**: 95%+ coverage required
- **Overall project**: Maintain or improve current coverage levels

### Test Structure
```python
class TestCardBuilder:
    """Test CardBuilder service."""
    
    @pytest.fixture
    def card_builder(self) -> CardBuilder:
        """Create CardBuilder instance for testing."""
        return CardBuilder()
    
    def test_build_card_from_noun_record(self, card_builder: CardBuilder):
        """Test building card from noun record."""
        # Arrange
        record = NounRecord(
            noun="Haus",
            article="das",
            gender="Neutrum",
            plural="Häuser",
            english="house",
            example="Das Haus ist groß."
        )
        
        # Act
        fields, note_type = card_builder.build_card_from_record(record)
        
        # Assert
        assert len(fields) == 9
        assert fields[0] == "Haus"
        assert note_type.name == "German Noun with Media"
    
    def test_handles_missing_data_gracefully(self, card_builder: CardBuilder):
        """Test graceful handling of missing data."""
        # Test edge cases and error conditions
```

### Mocking External Dependencies
```python
@pytest.fixture
def mock_pexels_service(monkeypatch):
    """Mock Pexels service for testing."""
    mock_service = Mock(spec=PexelsService)
    mock_service.download_image.return_value = "path/to/image.jpg"
    monkeypatch.setattr("langlearn.services.pexels_service.PexelsService", mock_service)
    return mock_service
```

---

## Project Structure

### Directory Layout
```
anki_deutsch_a1/
├── src/langlearn/
│   ├── models/          # Domain models and records
│   ├── services/        # Business logic and external APIs
│   ├── backends/        # Anki deck generation
│   ├── templates/       # HTML/CSS card templates
│   └── utils/          # Cross-cutting utilities
├── data/
│   ├── *.csv           # Vocabulary source data
│   ├── audio/          # Generated audio files
│   └── images/         # Downloaded images
├── tests/
│   ├── test_*.py       # Unit tests
│   └── integration/    # Integration tests
└── docs/               # Documentation
```

### Key Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| **Records** | `models/records.py` | Data transfer objects |
| **RecordMapper** | `services/record_mapper.py` | CSV → Record conversion |
| **MediaEnricher** | `services/media_enricher.py` | Audio/image generation |
| **CardBuilder** | `services/card_builder.py` | Record → Card formatting |
| **AnkiBackend** | `backends/anki_backend.py` | .apkg file generation |

---

## API Key Management

### Setting Up API Keys
```bash
# Add keys to system keyring (secure)
python src/langlearn/utils/api_keyring.py add ANTHROPIC_API_KEY your_key
python src/langlearn/utils/api_keyring.py add PEXELS_API_KEY your_key

# AWS credentials (environment variables)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=eu-central-1
```

### Accessing Keys in Code
```python
from langlearn.utils.api_keyring import get_api_key

# Retrieve key from keyring
api_key = get_api_key("PEXELS_API_KEY")
if not api_key:
    raise ValueError("PEXELS_API_KEY not found in keyring")
```

---

## Development Tools

### Hatch Commands

| Command | Purpose |
|---------|---------|
| `hatch run test` | Run all tests |
| `hatch run test-unit` | Unit tests only |
| `hatch run test-integration` | Integration tests |
| `hatch run test-cov` | Tests with coverage |
| `hatch run type` | MyPy type checking |
| `hatch run lint` | Ruff linting |
| `hatch run format` | Code formatting |
| `hatch run app` | Run main application |

### IDE Configuration

#### VS Code
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "python.typeChecking": "strict",
  "editor.formatOnSave": true
}
```

#### PyCharm
- Enable MyPy plugin
- Set Ruff as external tool
- Configure test runner to use pytest

---

## Common Tasks

### Adding a New Word Type

1. **Create Record class** in `models/records.py`
2. **Update RecordMapper** in `services/record_mapper.py`
3. **Add field mapping** in `services/card_builder.py`
4. **Create templates** in `templates/` directory
5. **Write tests** for all components
6. **Update documentation**

### Debugging Failed Tests

```bash
# Run specific test with verbose output
pytest tests/test_card_builder.py::TestCardBuilder::test_specific -vvs

# Run with debugging
pytest tests/test_card_builder.py --pdb

# Check coverage for specific module
hatch run pytest --cov=langlearn.services.card_builder --cov-report=term-missing
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile code execution
profiler = cProfile.Profile()
profiler.enable()

# Your code here
process_vocabulary_items()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 time consumers
```

---

## Troubleshooting

### Common Issues

#### MyPy Errors
```bash
# Check specific file
hatch run mypy src/langlearn/services/card_builder.py

# Ignore unavoidable external library issues
import untyped_library  # type: ignore[import-untyped]
```

#### Test Failures
```bash
# Run with full traceback
pytest --tb=long

# Skip integration tests if no API keys
pytest -m "not live"
```

#### Import Errors
```python
# Ensure proper Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

## Best Practices

### Code Quality
1. **Write tests first** (TDD) when possible
2. **Keep functions small** (<20 lines preferred)
3. **Use descriptive names** for variables and functions
4. **Document complex logic** with inline comments
5. **Fail fast** with early validation

### Performance
1. **Cache expensive operations** (media generation)
2. **Use generators** for large datasets
3. **Batch API calls** when possible
4. **Profile before optimizing**

### Security
1. **Never commit API keys** or credentials
2. **Validate all external input**
3. **Use parameterized queries** for any SQL
4. **Sanitize file paths** before file operations

---

## Training and Adoption

### For New Developers
1. Read this document thoroughly
2. Practice branch workflow on test changes
3. Understand quality gate requirements
4. Know how to interpret CI/CD failures

### Common Issues and Solutions
- **MyPy errors**: Run `hatch run type` locally and fix before pushing
- **Test failures**: Run `hatch run test` locally and ensure all pass
- **Coverage drops**: Add tests for new code to maintain current levels
- **Merge conflicts**: Keep branches up to date with main

## Getting Help

### Documentation
- **System Design**: See `ENG-SYSTEM-DESIGN.md` for architecture
- **Coding Standards**: See `ENG-CODING-STANDARDS.md` for code style requirements
- **CSV Specifications**: See `PM-CSV-SPEC.md` for data format
- **Component Inventory**: See `ENG-COMPONENT-INVENTORY.md` for component details

### Common Questions
- **Q: How do I add a new card type?** A: See "Adding a New Word Type" section above
- **Q: Should I use Clean Pipeline or legacy?** A: Always use Clean Pipeline for new word types
- **Q: What if CI fails?** A: Fix issues locally using the quality gates before pushing again

## Success Metrics

This workflow is successful when:
- **Zero quality regressions**: No degradation of MyPy/Ruff/Test achievements
- **Clean main branch**: Main always passes all quality gates
- **Predictable releases**: All changes thoroughly tested before merge
- **Maintainable codebase**: Quality standards enforced consistently

---

*This guide consolidates all development standards, workflows, and best practices. Keep it bookmarked for daily reference.*