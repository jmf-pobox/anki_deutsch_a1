"""Custom exceptions for the Anki German Language Deck Generator.

This module defines the exception hierarchy for the project, following
the standards defined in docs/ENG-EXCEPTIONS.md.

Exception Categories:
    - Configuration: Missing or invalid configuration
    - Service: External service failures
    - Domain: German language rule violations
    - Data Processing: CSV and record processing errors
    - Card Generation: Template and field mapping errors

All exceptions inherit from LangLearnError for easy catching of
project-specific errors while maintaining specific error types
for proper handling.
"""

# Base Exceptions


class LangLearnError(Exception):
    """Base exception for all project-specific errors.

    This is the root of the exception hierarchy, allowing
    catch-all handling of project errors when needed while
    maintaining specific exception types for proper handling.
    """

    pass


# Configuration Exceptions


class ConfigurationError(LangLearnError, ValueError):
    """Configuration is invalid or missing.

    Raised when:
        - API keys are missing from environment
        - Configuration files are malformed
        - Required settings are not provided

    This inherits from ValueError to maintain compatibility
    with existing code that catches ValueError for config issues.
    """

    pass


# Service Exceptions


class ServiceError(LangLearnError):
    """Base class for service-related errors.

    All external service failures should use this hierarchy
    to distinguish service issues from other error types.
    """

    pass


class ServiceUnavailableError(ServiceError):
    """External service is unavailable.

    Raised when:
        - Service connection fails
        - Service returns error status
        - Service dependency is missing
    """

    pass


class RateLimitError(ServiceError):
    """API rate limit exceeded.

    Raised when:
        - API returns 429 status
        - Rate limit headers indicate exhaustion
        - Throttling is required
    """

    pass


class MediaGenerationError(ServiceError):
    """Media generation failed.

    Raised when:
        - Audio generation fails (AWS Polly)
        - Image search/download fails (Pexels)
        - AI-generated content fails (Anthropic)
    """

    pass


# Domain Exceptions


class DomainError(LangLearnError):
    """Base class for domain logic errors.

    German language-specific validation and processing
    errors should use this hierarchy.
    """

    pass


class GrammarValidationError(DomainError):
    """German grammar validation failed.

    Raised when:
        - Article doesn't match noun gender
        - Case declension is incorrect
        - Plural form doesn't follow patterns
    """

    pass


class ArticlePatternError(DomainError):
    """Article pattern validation failed.

    Raised when:
        - Article pattern doesn't match German rules
        - Gender detection fails
        - Case requirements are violated
    """

    pass


class ConjugationError(DomainError):
    """Verb conjugation failed.

    Raised when:
        - Irregular verb pattern not found
        - Separable verb handling fails
        - Tense formation is incorrect
    """

    pass


# Data Processing Exceptions


class DataProcessingError(LangLearnError):
    """Base class for data processing errors.

    CSV parsing, record validation, and data transformation
    errors should use this hierarchy.
    """

    pass


class CSVParsingError(DataProcessingError):
    """CSV parsing failed.

    Raised when:
        - CSV file is malformed
        - Required columns are missing
        - Data types don't match expectations
    """

    pass


class RecordValidationError(DataProcessingError):
    """Record validation failed.

    Raised when:
        - Pydantic validation fails
        - Required fields are missing
        - Field values don't meet constraints
    """

    pass


# Card Generation Exceptions


class CardGenerationError(LangLearnError):
    """Card generation failed.

    Base class for all card generation errors.
    """

    pass


class TemplateError(CardGenerationError):
    """Template processing failed.

    Raised when:
        - Template file not found
        - Template syntax is invalid
        - Template variables are missing
    """

    pass


class FieldMappingError(CardGenerationError):
    """Field mapping failed.

    Raised when:
        - Required fields are missing
        - Field types don't match
        - Mapping configuration is invalid
    """

    pass


# Processing Result Container


class ProcessingError:
    """Container for errors during batch processing.

    Used when processing multiple records to collect
    errors without stopping the entire batch.

    Attributes:
        record: The record that failed processing
        error: The exception that occurred
        context: Optional additional context
    """

    def __init__(self, record: object, error: Exception, context: str | None = None):
        """Initialize a processing error container.

        Args:
            record: The record that failed
            error: The exception that occurred
            context: Optional additional context
        """
        self.record = record
        self.error = error
        self.context = context

    def __str__(self) -> str:
        """String representation of the error."""
        base = f"Processing failed for {self.record}: {self.error}"
        if self.context:
            base += f" ({self.context})"
        return base

    def __repr__(self) -> str:
        """Developer representation of the error."""
        return (
            f"ProcessingError(record={self.record!r}, "
            f"error={self.error!r}, context={self.context!r})"
        )
