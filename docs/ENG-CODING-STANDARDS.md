# Python Coding Standards

**Document Version**: 1.0
**Date**: 2025-09-14
**Status**: AUTHORITATIVE
**Scope**: All Python code in the Anki German Language Deck Generator project

---

## 🎯 Executive Summary

This document establishes comprehensive coding standards for Python development in the Anki German Language Deck Generator project. These standards cover general Python practices, exception handling, and type safety requirements to ensure maintainable, robust, and error-free code.

**Core Principles**:
- **Fail-fast with proper exceptions** - No silent failures or fallback logic
- **100% type safety** - Zero MyPy errors in strict mode
- **Modern Python patterns** - Leverage Python 3.10+ features
- **Comprehensive testing** - All code paths must be tested

---

## 📋 Table of Contents

1. [General Python Standards](#general-python-standards)
2. [Exception Handling Standards](#exception-handling-standards)
3. [Type Safety Standards](#type-safety-standards)
4. [Development Workflow](#development-workflow)
5. [Quality Gates](#quality-gates)

---

## General Python Standards

### Project Structure Guidelines

Recommended src-layout structure for Python projects:
```
project/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── main.py
│       ├── api/         # For web/API projects
│       ├── core/        # Core functionality
│       ├── db/          # Database related code
│       ├── models/      # Data models
│       └── schemas/     # Data validation schemas
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── pyproject.toml
├── README.md
└── .gitignore
```

### Core Development Tools

- **Ruff** (for linting and formatting)
- **MyPy** (for static type checking, use --strict)
- **Pytest** (for testing)
- **Hatch** (for project management)
- **Docker** (for containerization when needed)

### Python Coding Preferences

#### 1. Object-Oriented Programming Principles

**Single Responsibility Principle (SRP)**:
```python
# ✅ CORRECT: Separate responsibilities
class UserCreator:
    def create_user(self) -> None: ...

class EmailService:
    def send_email(self) -> None: ...

class PasswordValidator:
    def validate_password(self) -> None: ...

# ❌ INCORRECT: Class doing too much
class UserManager:
    def create_user(self) -> None: ...
    def send_email(self) -> None: ...
    def validate_password(self) -> None: ...
```

**Open/Closed Principle (OCP)**:
```python
# ✅ CORRECT: Extending through inheritance
class PaymentProcessor:
    def process_payment(self) -> None: ...

class CreditCardProcessor(PaymentProcessor):
    def process_payment(self) -> None: ...

class PayPalProcessor(PaymentProcessor):
    def process_payment(self) -> None: ...

# ❌ INCORRECT: Modifying existing class
class PaymentProcessor:
    def process_payment(self, payment_type: str) -> None:
        if payment_type == "credit":
            # process credit
        elif payment_type == "paypal":
            # process paypal
```

#### 2. Design Patterns (When Appropriate)

**Factory Pattern for object creation**:
```python
class PaymentMethodFactory:
    @staticmethod
    def create_payment_method(method_type: str) -> PaymentMethod:
        match method_type:
            case "credit": return CreditCardPayment()
            case "paypal": return PayPalPayment()
            case _: raise ValueError(f"Unknown payment method: {method_type}")
```

**Strategy Pattern for algorithms**:
```python
class SortStrategy(Protocol):
    def sort(self, data: list[int]) -> list[int]: ...

class QuickSort:
    def sort(self, data: list[int]) -> list[int]: ...

class MergeSort:
    def sort(self, data: list[int]) -> list[int]: ...
```

#### 3. Pythonic Data Structures and Idioms

**Use appropriate data structures**:
```python
# Sets for unique items
unique_items: set[str] = {"apple", "banana", "apple"}

# Dicts for key-value pairs
user_preferences: dict[str, Any] = {
    "theme": "dark",
    "notifications": True
}

# Lists for ordered collections
items: list[str] = ["first", "second", "third"]
```

**Leverage Python's built-in types**:
```python
# Use Enum for constants
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

# Use NamedTuple for simple data
class Point(NamedTuple):
    x: float
    y: float
```

#### 4. Modern Python Features

**Data Classes for simple objects**:
```python
@dataclass(slots=True)
class User:
    name: str
    email: str
    age: int
    is_active: bool = True
```

**Type Annotations and Generics**:
```python
def process_items[T](items: list[T]) -> list[T]:
    return [item for item in items if item is not None]
```

**Context Managers**:
```python
@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        release_resource(resource)
```

#### 5. Functional Programming in Python

**List Comprehensions**:
```python
squares = [x**2 for x in range(10) if x % 2 == 0]
```

**Generator Expressions**:
```python
large_squares = (x**2 for x in range(1000000) if x % 2 == 0)
```

**Lambda Functions (sparingly)**:
```python
# ✅ CORRECT: Simple operations
square = lambda x: x**2

# ❌ INCORRECT: Complex logic
process_data = lambda x: (x**2 if x > 0 else 0) + (x if x < 10 else 10)
```

---

## Exception Handling Standards

### Core Principles

#### 1. Fail-Fast Principle (MANDATORY)

**Johnson's Law Applied**: Unverified functionality does not exist. Therefore:
- Errors must propagate immediately to reveal problems
- Silent failures that mask issues are prohibited
- Fallback logic that hides errors is forbidden

```python
# ❌ PROHIBITED: Silent fallback
try:
    result = ai_service.generate_context(text)
except Exception:
    return self.english  # Silent failure - hides real problem

# ✅ REQUIRED: Fail-fast
result = ai_service.generate_context(text)  # Let exception propagate
return result
```

#### 2. Specific Exception Types (MANDATORY)

Generic `Exception` catching prevents proper error diagnosis and handling:

```python
# ❌ PROHIBITED: Generic exception
except Exception as e:
    logger.error(f"Something went wrong: {e}")
    return None

# ✅ REQUIRED: Specific exceptions
except ValueError as e:
    logger.error(f"Invalid configuration: {e}")
    raise ConfigurationError(f"Service configuration invalid: {e}") from e
except ImportError as e:
    logger.warning(f"Optional dependency missing: {e}")
    return None  # Only when service is truly optional
```

#### 3. Explicit Error Contracts (MANDATORY)

Every function must declare its error conditions:

```python
def process_noun(self, noun: NounRecord) -> EnrichedNounRecord:
    """Process a noun record with enrichment.

    Raises:
        ValidationError: If noun record fails validation
        ServiceUnavailableError: If required enrichment service is down
        MediaGenerationError: If audio/image generation fails
    """
```

### Custom Exception Hierarchy

Create a dedicated exceptions module at `src/langlearn/exceptions.py`:

```python
"""Custom exceptions for the Anki German Language Deck Generator."""

# Base Exceptions
class LangLearnError(Exception):
    """Base exception for all project-specific errors."""
    pass

# Configuration Exceptions
class ConfigurationError(LangLearnError, ValueError):
    """Configuration is invalid or missing."""
    pass

# Service Exceptions
class ServiceError(LangLearnError):
    """Base for service-related errors."""
    pass

class ServiceUnavailableError(ServiceError):
    """External service is unavailable."""
    pass

class MediaGenerationError(ServiceError):
    """Media generation failed."""
    pass

# Domain Exceptions
class DomainError(LangLearnError):
    """Base for domain logic errors."""
    pass

class GrammarValidationError(DomainError):
    """German grammar validation failed."""
    pass

class ArticlePatternError(DomainError):
    """Article pattern validation failed."""
    pass

# Data Processing Exceptions
class DataProcessingError(LangLearnError):
    """Base for data processing errors."""
    pass

class CSVParsingError(DataProcessingError):
    """CSV parsing failed."""
    pass

class RecordValidationError(DataProcessingError):
    """Record validation failed."""
    pass
```

### Implementation Patterns

#### Pattern 1: Service Availability (CORRECT)

```python
def get_audio_service(self) -> AudioService | None:
    """Get the shared AudioService instance.

    Returns:
        AudioService instance or None if AWS credentials are missing
    """
    if self._audio_service is None:
        try:
            from langlearn.services.audio import AudioService
            self._audio_service = AudioService()
        except ValueError as e:
            # Expected: Missing configuration
            logger.info(f"AudioService not available: {e}")
            return None
        except ImportError as e:
            # Expected: Missing dependencies
            logger.warning(f"AudioService dependencies missing: {e}")
            return None
    return self._audio_service
```

#### Pattern 2: Required Service Initialization (CORRECT)

```python
def __init__(self):
    """Initialize the enrichment service.

    Raises:
        ConfigurationError: If required API keys are missing
        ImportError: If required dependencies are missing
    """
    try:
        self.audio_service = AudioService()
    except ValueError as e:
        raise ConfigurationError(f"Audio service configuration failed: {e}") from e
    except ImportError as e:
        raise ImportError(f"Audio service dependencies required: {e}") from e
```

### Anti-Patterns to Eliminate

#### Anti-Pattern 1: Silent Fallback (PROHIBITED)

```python
# ❌ PROHIBITED - Silent fallback
try:
    result = ai_service.generate_context()
except Exception as e:
    logger.warning(f"AI generation failed: {e}")
    pass  # Silent failure
return self.english  # Fallback masks the error

# ✅ REQUIRED - Fail fast
result = ai_service.generate_context()  # Let exception propagate
return result
```

#### Anti-Pattern 2: Generic Exception Catching (PROHIBITED)

```python
# ❌ PROHIBITED - Generic catch-all
try:
    service = AnthropicService()
except Exception:
    return None

# ✅ REQUIRED - Specific exceptions
try:
    service = AnthropicService()
except ValueError as e:
    logger.info(f"Service configuration missing: {e}")
    return None  # Only if service is optional
except ImportError as e:
    logger.warning(f"Service package not installed: {e}")
    return None  # Only if service is optional
```

---

## Type Safety Standards

### Universal Typing Requirements

#### All Functions Must Be Typed

```python
# ✅ CORRECT: Complete type annotations
def process_word(word: str, language: str = "de") -> ProcessedWord:
    """Process a word for German language learning."""
    return ProcessedWord(word=word, language=language)

# ❌ INCORRECT: Missing annotations
def process_word(word, language="de"):
    return ProcessedWord(word=word, language=language)
```

#### Explicit Return Types Required

```python
# ✅ CORRECT: Even for simple returns
def get_word_count() -> int:
    return len(self.words)

def log_message(msg: str) -> None:
    print(msg)

# ❌ INCORRECT: Implicit returns
def get_word_count():
    return len(self.words)
```

#### Generic Types Must Be Specified

```python
# ✅ CORRECT: Specific generic types
words: list[str] = []
word_counts: dict[str, int] = {}
optional_word: str | None = None

# ❌ INCORRECT: Bare generic types
words = []
word_counts = {}
```

### MyPy Configuration

```toml
[tool.mypy]
python_version = "3.10"
strict = true                    # Maximum type checking
warn_return_any = true          # Flag Any returns
warn_unused_configs = true      # Clean configuration
disallow_untyped_defs = true    # All functions must be typed
disallow_incomplete_defs = true # Complete type annotations required
check_untyped_defs = true       # Check existing untyped code
disallow_untyped_decorators = true
no_implicit_optional = true    # Explicit Optional[T] required
warn_redundant_casts = true
warn_unused_ignores = true      # Clean up unused ignores
warn_no_return = true
warn_unreachable = true
```

### Handling External Dependencies

#### Well-Typed Libraries (Use Directly)
- `requests` - Has official stubs
- `pydantic` - Native type support
- `pathlib` - Built-in typing

#### Libraries with Type Stubs (Install Stubs)
```bash
# Add to pyproject.toml dependencies
mypy-boto3-polly = ">=1.0.0"      # AWS Polly stubs
pandas-stubs = ">=2.2.0"          # Pandas stubs
types-requests = ">=2.31.0"       # Requests stubs
```

#### Untyped Dependencies (Explicit Handling)
```python
# ✅ CORRECT: Type boundary with cast and validation
from typing import cast
import some_untyped_lib  # type: ignore[import-untyped]

def process_external_data(data: str) -> ProcessedData:
    """Process data using untyped library with type boundary."""
    # Use untyped library
    raw_result = some_untyped_lib.process(data)  # type: ignore[no-untyped-call]

    # Cast and validate at boundary
    typed_result = cast(dict[str, Any], raw_result)

    # Immediate validation
    if not isinstance(typed_result, dict):
        raise TypeError(f"Expected dict, got {type(typed_result)}")

    # Convert to typed domain object
    return ProcessedData(**typed_result)
```

### Type Suppression Standards

#### Allowed Suppressions (With Justification)
```python
# ✅ ACCEPTABLE: Import-level suppressions for untyped libraries
import boto3  # type: ignore[import-untyped]  # AWS SDK lacks official stubs
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

# ✅ ACCEPTABLE: API boundary suppressions with validation
response = self.client.synthesize_speech(**params)  # type: ignore[no-untyped-call]
if not hasattr(response, 'AudioStream'):
    raise ValueError("Invalid response format")
```

#### Forbidden Suppressions
```python
# ❌ FORBIDDEN: Broad suppressions
result = some_function()  # type: ignore  # Too broad

# ❌ FORBIDDEN: Suppressions in business logic
def calculate_score(word: str):  # type: ignore[no-untyped-def]
    return len(word) * 2

# ❌ FORBIDDEN: Any types without justification
def process_data(data: Any) -> Any:  # Should be more specific
    return data
```

---

## Development Workflow

### Project Management with Hatch

Always use `pyproject.toml` for project configuration and Hatch for:
- Virtual environment management
- Build system
- Development scripts
- Dependency management

Common Hatch commands:
```bash
hatch run test          # Run tests
hatch run lint          # Run linting
hatch run type          # Run type checking
hatch run format        # Format code
hatch run dev           # Start development server (if applicable)
```

### Testing Strategy

- **Unit tests**: Mock external dependencies, run with `hatch run test-unit`
- **Integration tests**: Require live API keys, marked with `@pytest.mark.live`
- **Coverage testing**: Use `hatch run test-cov` for complete measurement (target: >85%)
- **Property-based testing**: For complex logic validation
- **Type checking in CI/CD**: Mandatory zero-error requirement

For external services, create both:
1. Unit tests based on mocks using Monkeypatch
2. Integration tests that run against external services requiring valid API keys
3. Credentials stored in and accessed via keyring package

### Import Standards for PyCharm Refactoring Support

#### Core Principles

**CRITICAL**: Import patterns must support PyCharm's automatic refactoring capabilities. Poor import patterns prevent PyCharm from correctly tracking dependencies during moves/renames.

#### 1. Consistent Import Patterns (MANDATORY)

**✅ PREFERRED**: Direct, specific imports enable PyCharm tracking:
```python
# Direct class import - PyCharm can track and refactor automatically
from langlearn.core.services.audio_service import AudioService
from langlearn.core.services.ai_service import AnthropicService

# Usage
audio_service = AudioService()
```

**❌ AVOID**: Mixed import patterns confuse PyCharm refactoring:
```python
# Multiple ways to import same class - PyCharm struggles with refactoring
from langlearn.services.audio import AudioService      # Direct
from langlearn.services import AudioService           # Through __init__.py
import langlearn.services.audio                       # Module import
```

#### 2. TYPE_CHECKING Pattern for Complex Dependencies (MANDATORY)

Use TYPE_CHECKING for services with complex dependency chains:

```python
from typing import TYPE_CHECKING

# Always import the actual class/service you need
from langlearn.core.services.ai_service import AnthropicService

if TYPE_CHECKING:
    # Only import complex dependencies here
    from langlearn.services.audio import AudioService
    from langlearn.services.pexels_service import PexelsService

class ServiceContainer:
    _audio_service: "AudioService | None" = None
    _pexels_service: "PexelsService | None" = None
    _anthropic_service: AnthropicService | None = None  # Direct import used
```

#### 3. Service Container Pattern for High-Usage Services (PREFERRED)

For services used in 15+ locations, use service container pattern:

```python
# ✅ GOOD: Service container abstracts direct imports
from langlearn.core.services import get_audio_service

class MediaEnricher:
    def __init__(self):
        self.audio_service = get_audio_service()

# This makes refactoring easier - only service_container.py imports AudioService directly
```

#### 4. Package __init__.py Export Standards (RESTRICTIVE)

**MINIMIZE** exports in `__init__.py` to reduce refactoring complexity:

```python
# ✅ PREFERRED: Minimal exports, functions over classes
"""Services module for langlearn."""

# Export functions that abstract dependencies
from .service_container import (
    get_audio_service,
    get_anthropic_service,
    reset_services,
)

__all__ = [
    "get_audio_service",
    "get_anthropic_service",
    "reset_services",
]
```

**❌ AVOID**: Large class exports create refactoring complexity:
```python
# Avoid exporting many classes - makes moves hard
from .audio import AudioService
from .pexels_service import PexelsService
from .ai_service import AnthropicService
# ... 15+ class exports
```

#### 5. Import Organization (PEP 8 + Refactoring Support)

```python
# Standard library imports
import os
import logging
from pathlib import Path
from typing import TYPE_CHECKING

# Related third party imports
import pytest
from pydantic import BaseModel

# Local application imports (most specific first)
from langlearn.core.services.audio_service import AudioService
from langlearn.core.services.ai_service import AnthropicService

# TYPE_CHECKING imports last
if TYPE_CHECKING:
    from langlearn.services.pexels_service import PexelsService
```

#### 6. Refactoring-Safe Patterns

**Pattern A - Service Factory Functions** (Best for PyCharm):
```python
# src/langlearn/core/services/__init__.py
from .service_container import get_audio_service, get_ai_service

# Usage throughout codebase
from langlearn.core.services import get_audio_service
audio_service = get_audio_service()
```

**Pattern B - Direct Import with Consistent Path** (Good for PyCharm):
```python
# Always use the same import path
from langlearn.core.services.audio_service import AudioService

# Never mix with:
# from langlearn.core.services import AudioService  # Different path
```

**Pattern C - Dependency Injection** (Best for testing + refactoring):
```python
class MediaEnricher:
    def __init__(self, audio_service: AudioService):
        self.audio_service = audio_service

# Factory handles the import complexity
def create_media_enricher() -> MediaEnricher:
    return MediaEnricher(get_audio_service())
```

#### 7. Anti-Patterns That Break PyCharm Refactoring

**❌ Mixed Import Patterns**:
```python
# File A uses direct import
from langlearn.services.audio import AudioService

# File B uses package import
from langlearn.services import AudioService

# PyCharm can't track all references during refactoring
```

**❌ Dynamic Imports**:
```python
# PyCharm cannot track dynamic imports
module = importlib.import_module("langlearn.services.audio")
AudioService = getattr(module, "AudioService")
```

**❌ Circular Dependencies**:
```python
# services/audio.py
from langlearn.services.media_service import MediaService

# services/media_service.py
from langlearn.services.audio import AudioService
# PyCharm struggles with circular reference tracking
```

#### 8. Testing Import Patterns

Test files should use the same import patterns as production:

```python
# test_audio_service.py
# ✅ Same import pattern as production code
from langlearn.core.services.audio_service import AudioService

# ❌ Don't use different import patterns in tests
# from langlearn.services.audio import AudioService  # Different path than production
```

#### 9. Migration-Safe Import Updates

When moving services, update imports in order of dependency:

1. **Move the service file**: `git mv src/langlearn/services/audio.py src/langlearn/core/services/audio_service.py`
2. **Update direct imports first**: Files that import the class directly
3. **Update package exports**: Update `__init__.py` files
4. **Update service container**: Update dependency injection patterns
5. **Run quality gates**: Ensure PyCharm can track all references

#### 10. PyCharm Configuration Support

Configure PyCharm to support this pattern:

**Settings → Editor → Code Style → Python → Imports**:
- ✅ "Sort imports" enabled
- ✅ "From import style: Always use from imports for relative imports"
- ✅ "Structure order: stdlib, third-party, project"

**Settings → Tools → Python Integrated Tools**:
- ✅ Default test runner: pytest
- ✅ Docstring format: Google

This ensures PyCharm's refactoring and auto-import features work optimally with our standards.

---

## Quality Gates

### Mandatory Checks (Before Every Commit)

```bash
# All commands must pass with exit code 0
hatch run type                     # Zero MyPy errors (ABSOLUTE REQUIREMENT)
hatch run ruff check --fix       # Zero Ruff violations (ABSOLUTE REQUIREMENT)
hatch run format                  # Perfect formatting (ABSOLUTE REQUIREMENT)
hatch run test                    # All tests pass (ABSOLUTE REQUIREMENT)
hatch run test-cov                # Coverage maintained (ABSOLUTE REQUIREMENT)
```

### Success Metrics

- **Type Safety**: 0 MyPy errors (enforced)
- **Code Quality**: 0 Ruff violations
- **Test Coverage**: ≥85% maintained
- **Exception Handling**: Zero silent failures
- **Documentation**: All functions with Raises: sections

### CI/CD Integration

```yaml
# GitHub Actions Configuration
- name: Type Check
  run: hatch run type
  # Must return exit code 0 (no errors)

- name: Code Quality
  run: hatch run ruff check

- name: Tests
  run: hatch run test-cov
```

### Enforcement

These standards are **MANDATORY** and enforced through:

1. **Code Review**: All PRs must comply with these standards
2. **Automated Checks**: Type checking and linting detect violations
3. **Test Requirements**: Exception paths must be tested
4. **Documentation Review**: Raises: sections required

**Remember Johnson's Law**: Any error handling that has not been verified, does not exist. Test all exception paths explicitly.

---

## Environment Configuration

### Development Environment
- Python 3.11+ preferred
- VS Code with Python extensions or PyCharm Professional
- Virtual environment management via Hatch
- Docker for containerization when needed

### Debugging Best Practices

#### Test-Driven Development
1. ALWAYS run tests BEFORE making any code changes to verify current state
2. ALWAYS run tests AFTER making code changes to verify the fix
3. NEVER assume a fix worked without running tests
4. When tests fail:
   - Add debug output BEFORE modifying the code
   - Understand the exact failure case through debug output
   - Only then make code changes
   - Verify with tests again

#### Debugging Process
1. First step is ALWAYS to gather information:
   - Add print/debug statements
   - Log variable values
   - Log control flow
   - Understand exact state when failure occurs
2. Only after understanding the issue:
   - Form hypothesis about the problem
   - Make minimal changes to test hypothesis
   - Verify with tests
3. Document learnings in comments if relevant

### Common Mistakes to Avoid
1. Making changes without running tests first
2. Assuming a fix worked without verification
3. Making multiple changes before testing
4. Not adding debug output when tests fail
5. Not understanding the failure case before attempting fixes
6. Exceeding 88 characters per line (Ruff guideline)
7. Using inline import statements
8. Using mock objects in production code (only in tests)

---

## References

### Standards Documentation
- **PEP 8**: Style Guide for Python Code
- **PEP 484**: Type Hints
- **PEP 526**: Variable Annotations
- **PEP 585**: Type Hinting Generics (Python 3.9+)
- **PEP 604**: Union Types (Python 3.10+)

### Tools and Integration
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Hatch Documentation](https://hatch.pypa.io/)

### Project-Specific References
- `CLAUDE.md`: Core development principles and Johnson's Law
- `docs/ENG-TECHNICAL-DEBT.md`: Current technical debt status
- `docs/ENG-SYSTEM-DESIGN.md`: Architecture and system design

---

## Revision History

- v1.0 (2025-09-14): Initial consolidated standards combining exception handling, Python practices, and type safety requirements

---

**This document establishes comprehensive coding standards that balance uncompromising quality requirements with practical engineering needs, ensuring maintainable, robust, and error-free Python code.**