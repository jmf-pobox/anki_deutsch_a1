# Exception Handling Standards

**Document Version**: 1.0  
**Date**: 2025-09-06  
**Status**: AUTHORITATIVE  
**Scope**: All Python code in the Anki German Language Deck Generator project

---

## 🎯 Executive Summary

This document establishes mandatory exception handling standards for the project, eliminating anti-patterns identified in our technical debt audit while maintaining system reliability. These standards enforce fail-fast principles, specific error types, and proper logging patterns aligned with Johnson's Law: "Any property of software that has not been verified, does not exist."

**Core Mandate**: Silent failures are prohibited. Every exception must be either handled explicitly with proper logging or allowed to propagate for upstream handling.

---

## 📋 Table of Contents

1. [Core Principles](#core-principles)
2. [Exception Categories](#exception-categories)
3. [Custom Exception Hierarchy](#custom-exception-hierarchy)
4. [Implementation Patterns](#implementation-patterns)
5. [Anti-Patterns to Eliminate](#anti-patterns-to-eliminate)
6. [Service Availability Pattern](#service-availability-pattern)
7. [Migration Guidelines](#migration-guidelines)
8. [Testing Requirements](#testing-requirements)
9. [Integration with Project Standards](#integration-with-project-standards)

---

## Core Principles

### 1. Fail-Fast Principle (MANDATORY)

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

### 2. Specific Exception Types (MANDATORY)

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

### 3. Explicit Error Contracts (MANDATORY)

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

### 4. Proper Logging for Visibility (MANDATORY)

All exception handling must include appropriate logging:

```python
# ✅ REQUIRED: Logged exception handling
try:
    service = AudioService()
except ValueError as e:
    logger.info(f"AudioService not available: {e}")  # INFO for expected
    return None
except ImportError as e:
    logger.warning(f"AudioService dependencies missing: {e}")  # WARNING for missing deps
    return None
```

---

## Exception Categories

### 1. Configuration Errors

**When**: Missing or invalid configuration (API keys, credentials, settings)  
**Type**: `ValueError` or custom `ConfigurationError`  
**Handling**: Log at INFO level (expected), allow service degradation

```python
class ConfigurationError(ValueError):
    """Raised when service configuration is invalid or missing."""
    pass

# Usage
if not api_key:
    raise ConfigurationError("ANTHROPIC_API_KEY not found in environment")
```

### 2. External Service Failures

**When**: API calls fail, network issues, rate limits  
**Type**: Custom service-specific exceptions  
**Handling**: Log at WARNING level, propagate or handle based on criticality

```python
class ServiceError(Exception):
    """Base class for all service-related errors."""
    pass

class ServiceUnavailableError(ServiceError):
    """Raised when an external service is unavailable."""
    pass

class RateLimitError(ServiceError):
    """Raised when API rate limit is exceeded."""
    pass

class MediaGenerationError(ServiceError):
    """Raised when media (audio/image) generation fails."""
    pass
```

### 3. Domain Validation Errors

**When**: German language rules violated, invalid linguistic data  
**Type**: Custom domain exceptions  
**Handling**: Log at ERROR level, always propagate

```python
class DomainError(Exception):
    """Base class for domain-specific errors."""
    pass

class GrammarValidationError(DomainError):
    """Raised when German grammar rules are violated."""
    pass

class ArticlePatternError(DomainError):
    """Raised when article pattern doesn't match German rules."""
    pass

class ConjugationError(DomainError):
    """Raised when verb conjugation fails."""
    pass
```

### 4. Data Processing Errors

**When**: CSV parsing fails, data transformation errors  
**Type**: `ValueError` for format issues, custom for processing  
**Handling**: Log at ERROR level, fail fast

```python
class DataProcessingError(Exception):
    """Base class for data processing errors."""
    pass

class CSVParsingError(DataProcessingError):
    """Raised when CSV data cannot be parsed."""
    pass

class RecordValidationError(DataProcessingError):
    """Raised when a record fails Pydantic validation."""
    pass
```

### 5. Import/Dependency Errors

**When**: Optional dependencies missing  
**Type**: `ImportError`  
**Handling**: Log at WARNING level, degrade gracefully ONLY for optional features

```python
try:
    from anthropic import Anthropic
except ImportError as e:
    logger.warning(f"Anthropic package not installed: {e}")
    # Only acceptable for truly optional features
    raise ImportError("anthropic package required for AI features") from e
```

---

## Custom Exception Hierarchy

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

class RateLimitError(ServiceError):
    """API rate limit exceeded."""
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

class ConjugationError(DomainError):
    """Verb conjugation failed."""
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

# Card Generation Exceptions
class CardGenerationError(LangLearnError):
    """Card generation failed."""
    pass

class TemplateError(CardGenerationError):
    """Template processing failed."""
    pass

class FieldMappingError(CardGenerationError):
    """Field mapping failed."""
    pass
```

---

## Implementation Patterns

### Pattern 1: Service Availability (CORRECT)

Based on the fixed ServiceContainer pattern:

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

**Key Points**:
- Specific exception types (`ValueError`, `ImportError`)
- Appropriate logging levels (INFO for expected, WARNING for dependencies)
- Returns None ONLY for optional services
- Clear documentation of return contract

### Pattern 2: Required Service Initialization (CORRECT)

When a service is required, not optional:

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

### Pattern 3: Domain Model Processing (CORRECT)

Remove fallback logic, let errors propagate:

```python
def generate_image_search_terms(self) -> str:
    """Generate search terms for image lookup.
    
    Raises:
        ServiceUnavailableError: If AI service is not available
        MediaGenerationError: If search term generation fails
    """
    ai_service = get_anthropic_service()
    if not ai_service:
        raise ServiceUnavailableError("AI service required for image search terms")
    
    # No try/except - let service exceptions propagate
    context = self._build_search_context()
    result = ai_service.generate_image_query(context)
    
    if not result or not result.strip():
        raise MediaGenerationError(f"Empty search terms for noun: {self.noun}")
    
    return result.strip()
```

### Pattern 4: Batch Processing with Error Collection (CORRECT)

When processing multiple items, collect errors for reporting:

```python
def process_records(self, records: list[NounRecord]) -> tuple[list[EnrichedNounRecord], list[ProcessingError]]:
    """Process multiple records, collecting errors.
    
    Returns:
        Tuple of (successful_records, errors)
    """
    successful = []
    errors = []
    
    for record in records:
        try:
            enriched = self.enrich_record(record)
            successful.append(enriched)
        except RecordValidationError as e:
            errors.append(ProcessingError(record=record, error=e))
            logger.error(f"Validation failed for {record.noun}: {e}")
        except ServiceError as e:
            errors.append(ProcessingError(record=record, error=e))
            logger.warning(f"Service error for {record.noun}: {e}")
            # Continue processing other records
    
    return successful, errors
```

---

## Anti-Patterns to Eliminate

### Anti-Pattern 1: Silent Fallback (PROHIBITED)

**Current Code** (40+ instances identified):
```python
# ❌ PROHIBITED - From models/noun.py:269-274
try:
    result = ai_service.generate_context()
except Exception as e:
    logger.warning(f"AI generation failed: {e}")
    pass  # Silent failure
return self.english  # Fallback masks the error
```

**Required Fix**:
```python
# ✅ REQUIRED - Fail fast
result = ai_service.generate_context()  # Let exception propagate
return result
```

### Anti-Pattern 2: Generic Exception Catching (PROHIBITED)

**Current Code** (25+ instances identified):
```python
# ❌ PROHIBITED - Generic catch-all
try:
    service = AnthropicService()
except Exception:
    return None
```

**Required Fix**:
```python
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

### Anti-Pattern 3: Duck Typing Fallbacks (PROHIBITED)

**Current Code** (15+ instances identified):
```python
# ❌ PROHIBITED - hasattr chains with fallback
if hasattr(model, "noun"):
    return model.noun
elif hasattr(model, "verb"):
    return model.verb
else:
    return "default"  # Hidden fallback
```

**Required Fix**:
```python
# ✅ REQUIRED - Explicit type handling
match model:
    case Noun():
        return model.noun
    case Verb():
        return model.verb
    case _:
        raise ValueError(f"Unsupported model type: {type(model).__name__}")
```

### Anti-Pattern 4: Empty Except Blocks (PROHIBITED)

**Current Code**:
```python
# ❌ PROHIBITED - Silent swallowing
try:
    process_data()
except:
    pass
```

**Required Fix**:
```python
# ✅ REQUIRED - Explicit handling
try:
    process_data()
except DataProcessingError as e:
    logger.error(f"Data processing failed: {e}")
    raise  # Re-raise after logging
```

---

## Service Availability Pattern

Based on the successful ServiceContainer fix, use this pattern for optional services:

### Principles

1. **Optional Services**: Return None with proper logging
2. **Required Services**: Raise exceptions immediately
3. **Service Contracts**: Document availability in return types

### Implementation Template

```python
class ServiceProvider:
    """Provider for optional services."""
    
    def get_optional_service(self) -> OptionalService | None:
        """Get optional service if available.
        
        Returns:
            Service instance or None if not configured/available
        """
        try:
            return OptionalService()
        except ValueError as e:
            logger.info(f"Optional service not configured: {e}")
            return None
        except ImportError as e:
            logger.warning(f"Optional service dependencies missing: {e}")
            return None
    
    def get_required_service(self) -> RequiredService:
        """Get required service.
        
        Raises:
            ConfigurationError: If service cannot be configured
            ImportError: If dependencies are missing
        """
        try:
            return RequiredService()
        except ValueError as e:
            raise ConfigurationError(f"Required service misconfigured: {e}") from e
        except ImportError as e:
            raise ImportError(f"Required dependencies missing: {e}") from e
```

### Usage Pattern

```python
# For optional services
audio_service = get_audio_service()
if audio_service:
    audio_path = audio_service.generate_audio(text)
else:
    audio_path = None  # Graceful degradation

# For required services
try:
    translation_service = get_translation_service()
    translation = translation_service.translate(text)
except ServiceUnavailableError:
    # Cannot continue without translation
    raise
```

---

## Migration Guidelines

### Phase 1: Create Exception Module (Immediate)

1. Create `src/langlearn/exceptions.py` with custom exception hierarchy
2. Run type checking: `hatch run type`
3. Commit: `fix(exceptions): create custom exception hierarchy [foundation]`

### Phase 2: Fix Critical Paths (This Sprint)

Target the 40+ fallback instances in priority order:

#### 2.1 Domain Models (HIGH PRIORITY)
**Files**: `models/noun.py`, `models/verb.py`, `models/phrase.py`, etc.

```bash
# For each model file:
1. Remove try/except blocks around AI service calls
2. Let exceptions propagate
3. Update docstrings with Raises: sections
4. Run: hatch run type && hatch run test-unit
5. Commit: fix(models/noun): remove silent fallback [fail-fast]
```

#### 2.2 Media Enricher (HIGH PRIORITY)
**File**: `services/media_enricher.py`

```bash
1. Replace hasattr chains with match/case
2. Add explicit ValueError for unsupported types
3. Run: hatch run type && hatch run test-unit
4. Commit: fix(media): replace duck typing with type dispatch [type-safety]
```

#### 2.3 Backend Processing (MEDIUM PRIORITY)
**File**: `backends/anki_backend.py`

```bash
1. Replace media fallbacks with explicit handling
2. Add proper logging for each failure mode
3. Run: hatch run type && hatch run test-unit
4. Commit: fix(backend): remove media type fallbacks [explicit-errors]
```

### Phase 3: Standardize Service Patterns (Next Sprint)

1. Update all service initialization to follow ServiceContainer pattern
2. Add proper exception types for each service
3. Document service availability contracts

### Validation Checklist

Before committing each change:

```bash
# Micro-commit validation (2-3 minutes)
☐ Removed all generic Exception catches
☐ Removed all silent fallbacks
☐ Added specific exception types
☐ Added proper logging
☐ Updated docstrings with Raises: sections
☐ hatch run type (MUST PASS)
☐ hatch run test-unit (MUST PASS)
```

---

## Testing Requirements

### 1. Exception Path Testing (MANDATORY)

Every exception path must have a test:

```python
def test_noun_generation_handles_service_failure():
    """Test that service failures propagate correctly."""
    noun = Noun(noun="Haus", english="house", plural="Häuser", article="das")
    
    with patch('langlearn.services.get_anthropic_service', return_value=None):
        with pytest.raises(ServiceUnavailableError):
            noun.generate_image_search_terms()
```

### 2. Service Availability Testing

```python
def test_service_container_handles_missing_config():
    """Test graceful handling of missing configuration."""
    with patch.dict(os.environ, {}, clear=True):
        container = ServiceContainer()
        
        # Optional service returns None
        assert container.get_audio_service() is None
        
        # Verify proper logging
        assert "AudioService not available" in caplog.text
```

### 3. Error Message Testing

```python
def test_configuration_error_message():
    """Test that error messages are informative."""
    with pytest.raises(ConfigurationError) as exc_info:
        service = RequiredService(api_key=None)
    
    assert "API key" in str(exc_info.value)
    assert "required" in str(exc_info.value).lower()
```

### 4. Coverage Requirements

- All exception paths must be covered
- Use `# pragma: no cover` ONLY for truly unreachable code
- Maintain or improve current 73.84% coverage

---

## Integration with Project Standards

### 1. Type Safety Integration

Exception handling must maintain type safety:

```python
from typing import Never

def process_or_fail(data: str) -> ProcessedData | Never:
    """Process data or raise exception.
    
    Returns:
        ProcessedData if successful
        
    Raises:
        DataProcessingError: Always if processing fails
    """
    if not validate(data):
        raise DataProcessingError(f"Invalid data: {data}")
    return ProcessedData(data)
```

### 2. Micro-Commit Workflow

Each exception fix should be a micro-commit:

```bash
# One fallback removal = one commit
git add src/langlearn/models/noun.py
git commit -m "fix(noun): remove AI fallback for image terms [fail-fast]"

# Run quality gates before push
hatch run type
hatch run test-unit
```

### 3. Logging Standards

Follow logging level guidelines:

- **DEBUG**: Detailed diagnostic information (not in production)
- **INFO**: Expected conditions (missing optional services)
- **WARNING**: Unexpected but recoverable (missing dependencies)
- **ERROR**: Error conditions that should be investigated
- **CRITICAL**: System-wide failures requiring immediate attention

### 4. Documentation Requirements

Every function that can raise exceptions must document them:

```python
def enrich_noun(self, noun: NounRecord) -> EnrichedNounRecord:
    """Enrich a noun record with media and context.
    
    Args:
        noun: The noun record to enrich
        
    Returns:
        Enriched noun record with media paths
        
    Raises:
        ValidationError: If noun record is invalid
        ServiceUnavailableError: If required service is down
        MediaGenerationError: If media generation fails
    """
```

---

## Success Metrics

After implementing these standards:

1. **Zero silent failures**: No `except: pass` or fallback returns
2. **Zero generic catches**: No bare `except:` or `except Exception:`
3. **100% exception documentation**: All Raises: sections complete
4. **Improved debugging**: Clear error messages and stack traces
5. **Maintained coverage**: ≥73.84% test coverage

---

## Enforcement

These standards are **MANDATORY** and enforced through:

1. **Code Review**: All PRs must comply with these standards
2. **Automated Checks**: Type checking and linting detect violations
3. **Test Requirements**: Exception paths must be tested
4. **Documentation Review**: Raises: sections required

**Remember Johnson's Law**: Any error handling that has not been verified, does not exist. Test all exception paths explicitly.

---

## References

- `CLAUDE.md`: Core development principles and Johnson's Law
- `ENG-TECHNICAL-DEBT-AUDIT.md`: Identified anti-patterns to eliminate
- `ENG-DEVELOPMENT-STANDARDS.md`: Overall development standards
- ServiceContainer fix (commit 30b598c): Example implementation

---

## Revision History

- v1.0 (2025-09-06): Initial standards based on technical debt audit and ServiceContainer fix