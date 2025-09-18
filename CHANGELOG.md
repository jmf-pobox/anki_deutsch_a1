# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-18

### Added
- **Multi-language architecture**: Support for German, Korean, and Russian language learning decks
- **Korean language support**: Complete implementation with noun records, grammar service, and card templates
- **Russian language support**: Complete implementation with noun records, grammar service, and card templates
- **Language registry system**: Centralized management for multiple languages
- **Protocol inheritance**: Explicit protocol inheritance throughout domain models for improved IDE support
- **3-tier architecture**: Clean Infrastructure/Core/Languages structure
- **Enhanced test coverage**: Comprehensive tests for all language implementations

### Changed
- **BREAKING**: Migrated all record classes from Pydantic BaseModel to Python dataclasses
- **BREAKING**: Updated validation patterns from Pydantic validators to validate() methods
- **Updated architecture**: Reorganized codebase into clean 3-tier structure
- **Enhanced IDE support**: Added explicit protocol inheritance for better type visibility
- **Improved performance**: Dataclasses are lighter weight than Pydantic models

### Removed
- **Pydantic dependency**: Completely removed from project dependencies
- **Legacy validation patterns**: Eliminated Pydantic Field() patterns throughout codebase

### Technical
- All 726 unit tests passing
- MyPy strict mode: 0 errors across 171 source files
- Test coverage: 73.45%
- 233 files changed: 13,161 insertions, 4,986 deletions

## [0.1.0] - 2024-XX-XX

### Added
- **German language support**: Complete Anki deck generation for German A1 level
- **Multi-word type support**: Nouns, verbs, adjectives, articles, and more
- **Media enrichment**: Automatic audio and image generation
- **CSV-based vocabulary**: Structured data input for vocabulary management
- **Anki integration**: Direct .apkg file generation
- **API integrations**: Anthropic for content generation, Pexels for images, AWS Polly for audio

### Technical
- Initial project architecture
- Comprehensive test suite
- Type-safe codebase with MyPy
- Modern Python development practices

---

## Changelog Guidelines

This changelog follows these principles:

### Categories
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
- **Technical** for infrastructure/architecture changes

### Versioning
- **Major version** (X.0.0): Breaking changes or major new features
- **Minor version** (0.X.0): New features, backwards compatible
- **Patch version** (0.0.X): Bug fixes, backwards compatible

### Breaking Changes
Changes that require user action are marked with **BREAKING** and explained clearly.