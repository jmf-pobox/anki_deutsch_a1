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
hatch run test-cov          # Test with coverage - MUST maintain 24%+

# Development commands
hatch run test-unit         # Unit tests only (no API calls)
hatch run test-integration  # Integration tests (requires API keys)
hatch run app              # Run main deck creation
```

### Current Quality Metrics
- **Tests**: 792 unit + 21 integration = 813 total tests passing
- **Coverage**: 24.79% overall (target: maintain or improve)
- **MyPy**: 0 errors in strict mode across 133 source files
- **Linting**: 0 Ruff violations

---

## Development Workflow

### 1. Branch-Based Development (MANDATORY)

**All development MUST use feature branches - NO direct commits to main**

#### Branch Creation
```bash
# Feature development
git checkout -b feature/your-feature-name

# Bug fixes
git checkout -b fix/issue-description

# Refactoring
git checkout -b refactor/component-name
```

#### Commit Guidelines
- **One change per commit**: Each commit should have a single, clear purpose
- **Commit message format**: `type(scope): description [impact]`
- **Examples**:
  - `fix(media): handle missing audio files [prevents FileNotFoundError]`
  - `feat(cards): add verb imperative support [+1 card type]`
  - `refactor(services): extract validation logic [no behavior change]`

### 2. Quality Gates (MANDATORY)

**Run these commands after EVERY code change:**

```bash
# The "Big 5" - All must pass before committing
hatch run type              # 1. Type checking (0 errors required)
hatch run ruff check --fix  # 2. Linting (0 violations required)
hatch run format            # 3. Code formatting
hatch run test              # 4. All tests must pass
hatch run test-cov          # 5. Coverage must not decrease
```

### 3. Pull Request Process

1. **Push your branch**: `git push -u origin feature/your-feature-name`
2. **Create PR**: Use GitHub interface or `gh pr create`
3. **Ensure CI passes**: All automated checks must succeed
4. **Self-review**: Check your changes against standards
5. **Merge**: Only after all checks pass

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

## Testing Standards

### Test Coverage Requirements
- **New code**: Minimum 80% coverage
- **Critical paths**: 95%+ coverage required
- **Overall project**: Maintain or improve current 24.79%

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

## Getting Help

### Documentation
- **System Design**: See `ENG-SYSTEM-DESIGN.md` for architecture
- **CSV Specifications**: See `PROD-CSV-SPEC.md` for data format
- **Component Inventory**: See `ENG-COMPONENT-INVENTORY.md` for component details

### Common Questions
- **Q: How do I add a new card type?** A: See "Adding a New Word Type" section above
- **Q: Why is coverage low in some areas?** A: Focus on critical paths first, legacy code second
- **Q: Should I use Clean Pipeline or legacy?** A: Always use Clean Pipeline for new word types

---

*This guide consolidates all development standards, workflows, and best practices. Keep it bookmarked for daily reference.*