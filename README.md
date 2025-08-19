# 🎓 Language Learn - An Anki Card Generator

A language learning application that generates customized Anki decks with vocabulary, grammar patterns, and multimedia content. Supports multiple languages and proficiency levels with specialized handling for language-specific grammatical features.

## 📊 Project Status

[![CI](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml/badge.svg)](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-401%20Passing-brightgreen)](#testing)
[![Coverage](https://img.shields.io/badge/Coverage-73.84%25-yellow)](#testing)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-MyPy%20%7C%20Ruff-success)](#quality)
[![Platform](https://img.shields.io/badge/Platform-Anki-blue)](#usage)
[![Languages](https://img.shields.io/badge/Languages-Multi--Language-orange)](#language-features)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

### 🚀 Current State

| **Aspect** | **Status** | **Details** |
|------------|------------|-------------|
| **Build Status** | ![CI](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml/badge.svg) | Automated testing on every push |
| **Code Quality** | ✅ **Excellent** | 100% MyPy compliance, zero linting violations |
| **Test Coverage** | 📊 **73.84%** | 401 comprehensive tests (562 unit + 24 integration) |
| **Output Format** | 🟢 **Anki Decks** | .apkg files ready for import |
| **Documentation** | 📖 **Comprehensive** | Complete design docs in `docs/` directory |

### 📈 Quality Metrics
- **Static Analysis**: MyPy strict mode with zero errors
- **Linting**: Ruff compliance with comprehensive rule set  
- **Test Suite**: 401 tests covering core functionality
- **Architecture**: Clean Pipeline Architecture with service layer separation

### Core Functionality ✅
- **Deck Generation**: Creates Anki decks (.apkg files) with vocabulary and grammar patterns
- **Multi-Language Support**: Extensible architecture supporting multiple languages and proficiency levels
- **Media Integration**: AWS Polly audio generation and Pexels image integration for enhanced learning
- **Grammar-Aware Processing**: Specialized handling for language-specific grammatical features
- **Code Quality**: 100% MyPy strict mode compliance, comprehensive linting, enterprise-grade standards

## 📚 Documentation

This project includes comprehensive design documentation in the `docs/` directory:

### 🎯 **Primary Documentation**

#### **[docs/DESIGN-INDEX.md](docs/DESIGN-INDEX.md)** - Documentation Navigator
**Start here** for navigation of all design documents. Provides:
- Quick start guide for new developers
- Document descriptions and use cases
- Cross-reference guide between documents
- Maintenance guidelines and update procedures

### 🏗️ **Architecture Documentation**

#### **[docs/DESIGN-SRP.md](docs/DESIGN-SRP.md)** - System Component Inventory
Complete codebase inventory organized by Single Responsibility Principle:
- Package hierarchy with responsibility matrix
- Class-by-class functionality breakdown
- Component relationship mapping
- Code organization reference

#### **[docs/DESIGN-STATE.md](docs/DESIGN-STATE.md)** - Current Quality Assessment
Critical analysis of current codebase state:
- Measured code quality metrics
- Technical debt assessment
- Multi-language readiness evaluation
- Implementation priority matrix

#### **[docs/DESIGN-GUIDANCE.md](docs/DESIGN-GUIDANCE.md)** - Development Standards
Prescriptive guidance for development work:
- Architectural principles and patterns
- Code quality requirements and gates
- Import structure and testing standards
- Anti-patterns and prohibited practices

#### **[docs/DESIGN.md](docs/DESIGN.md)** - Original Architecture Analysis
Historical context and intended design patterns:
- Original architectural intentions
- Intended design patterns analysis
- Clean architecture principles documentation
- Abstract base class designs

### 🔄 **Migration Documentation**

#### **[docs/MIGRATION_PLAN.md](docs/ANKI_MIGRATION_PLAN.md)** - Backend Migration Status
Current status of genanki to official Anki library migration:
- Phase-by-phase migration progress
- Current implementation status
- Risk assessment and mitigation strategies
- Timeline and success criteria

#### **[docs/LIBRARY_REFACTOR.md](docs/ANKI_LIBRARY_REFACTOR.md)** - Integration Architecture
Technical achievements in backend integration:
- Dual backend architecture implementation
- Interface consistency and switching capability
- Performance characteristics and testing status
- Benefits realized and future considerations

#### **[docs/LEGACY.md](docs/LEGACY.md)** - Component Evolution
Analysis of components for potential refactoring:
- Current backend architecture assessment
- Future consolidation scenarios
- Decision framework and evaluation criteria
- Maintenance recommendations

### 🧪 **Testing Documentation**

#### **[docs/ANKI_API_TESTPLAN.md](docs/ANKI_API_TESTPLAN.md)** - Comprehensive Test Strategy
Detailed testing plan for official Anki backend validation:
- Phase-by-phase test coverage plan
- German language integration testing
- Performance and error recovery testing
- Success criteria and deliverables

## 🌍 Language Features

### Grammar-Aware Card Generation
- **Noun Cards**: Article recall, gender, and plural forms (language-specific)
- **Verb Cards**: Conjugation patterns with irregular verb detection
- **Adjective Cards**: Comparison forms and declension patterns
- **Preposition Cards**: Case requirements and usage contexts
- **Phrase Cards**: Common expressions with contextual examples

### Language Learning Optimizations
- **Grammar Validation**: Language-specific grammatical rule enforcement
- **Pattern Recognition**: Specialized handling for irregular forms and exceptions
- **Contextual Learning**: Example sentences demonstrating proper usage
- **Audio Integration**: Native pronunciation using AWS Polly (multiple language voices)
- **Visual Learning**: Contextual images from Pexels API for vocabulary retention

### Current Language Support
- **German**: Full A1-level vocabulary with gender, case, and conjugation support
- **Extensible Architecture**: Ready for additional languages and proficiency levels

## 🏗️ Project Structure

```
language-learn/
├── 📊 data/                    # Language vocabulary data (CSV format)
│   ├── nouns.csv              # Nouns with language-specific attributes
│   ├── adjectives.csv         # Adjectives with comparison forms
│   ├── verbs.csv              # Regular and irregular verbs
│   ├── adverbs.csv            # Adverbs with usage examples
│   └── negations.csv          # Negation words and phrases
│
├── 🏗️ src/langlearn/
│   ├── 🎯 backends/            # Anki integration layer
│   ├── 📝 models/              # Pydantic language models (extensible)
│   ├── 🔌 services/            # External API integrations (AWS, Pexels, CSV)
│   ├── 🛠️ utils/               # API key management and utilities
│   ├── 🎨 templates/           # HTML/CSS templates for card designs
│   ├── main.py                 # Main application entry point
│   └── deck_builder.py         # Primary deck orchestrator
│
├── 🧪 tests/                   # 263 comprehensive unit tests
├── 📦 output/                  # Generated Anki decks (.apkg files)
├── 🌍 languages/               # Language-specific grammar documentation
├── 📋 examples/                # Usage demonstrations
└── 📖 docs/                    # Comprehensive design documentation
```

## 🚀 Installation & Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd language-learn
```

2. **Install dependencies using Hatch:**
```bash
hatch env create
```

3. **Configure API keys (optional for media generation):**
```bash
# Store API keys securely using keyring
python src/langlearn/utils/api_keyring.py add PEXELS_API_KEY your_pexels_key

# Configure AWS credentials for German audio
export AWS_ACCESS_KEY_ID=your_aws_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret
export AWS_DEFAULT_REGION=us-east-1
```

4. **Verify installation:**
```bash
# Run comprehensive test suite
hatch run test-unit

# Test deck generation  
PYTHONPATH=src python src/langlearn/main.py
```

## 💻 Usage

### Basic Deck Generation
```bash
# Create language learning deck
python src/langlearn/main.py
```

This generates a complete language learning Anki deck with:
- Multiple vocabulary types (nouns, verbs, adjectives, adverbs, negations)
- Language-specific grammar validation
- Optional media integration (audio/images)
- Export to `.apkg` format ready for Anki import

### Usage Example
```python
from langlearn.deck_builder import DeckBuilder

# Create language learning deck
with DeckBuilder(
    deck_name="My Language Deck",
    enable_media_generation=True
) as builder:
    builder.load_data_from_directory("data/")
    builder.generate_all_cards(generate_media=True)
    builder.export_deck("output/language_deck.apkg")
```

## 🧪 Development & Testing

### CI/CD Pipeline
The project uses GitHub Actions for automated testing and quality assurance:

| **Trigger** | **Jobs** | **Status** |
|-------------|----------|------------|
| **Push/PR** | Lint, Type Check, Unit Tests (Python 3.10-3.12) | ![CI](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml/badge.svg) |
| **PR to Main** | Integration Tests (with API keys) | Automated on PRs |
| **Manual** | Full test suite with coverage reporting | On-demand workflow |

### Running Tests Locally
```bash
# All unit tests (offline, no API calls)
hatch run test-unit           # 562 unit tests

# Integration tests (requires API keys)  
hatch run test-integration    # 24 integration tests

# Full test suite with coverage
hatch run test-cov           # All 586 tests + coverage report

# Code quality checks
hatch run format     # Code formatting (Ruff)
hatch run lint       # Linting (Ruff)
hatch run type       # Type checking (MyPy strict)
hatch run check      # All quality checks + tests
```

### Development Workflow
Following the mandatory development workflow from `CLAUDE.md`:
1. **Run unit tests**: `hatch run test-unit`
2. **Fix linting**: `hatch run ruff check --fix`
3. **Format code**: `hatch run format`
4. **Verify tests still pass**: `hatch run test-unit`

### Quality Gates
- ✅ **All tests must pass** (586 tests total)
- ✅ **Coverage must not decrease** (currently 73.84%, target 85%+)
- ✅ **Zero linting violations** (Ruff compliance required)
- ✅ **Zero type errors** (MyPy strict mode required)
- ✅ **Integration tests pass** (on PRs to main branch)

## 🔧 Architecture

### Key Design Principles
- **Multi-Language Architecture**: Extensible framework supporting multiple languages and proficiency levels
- **Grammar-Aware Processing**: Specialized handling for language-specific grammatical patterns
- **Media-Rich Learning**: Optional audio pronunciation and visual learning aids
- **Type Safety**: Full MyPy compliance with comprehensive type hints
- **Clean Pipeline**: CSV data → Domain models → Enriched content → Anki cards
- **Testability**: Comprehensive unit test coverage with mocked dependencies

### Upcoming MVP Architecture (Planned)
The codebase is planned for evolution to a clean **MVP (Model-View-Presenter)** architecture:

- **Models**: Domain objects with validation (`Noun`, `Adjective`, etc.)
- **Views**: HTML/CSS templates for Anki cards (`noun_front.html`, etc.)
- **Presenters**: Card generators handling data binding between models and views
- **Orchestrator**: Slimmed-down `GermanDeckBuilder` focusing only on coordination

**Benefits**: 90% reduction in code duplication, easy grammar extensibility, cleaner separation of concerns.

See **`docs/MVP_REINTEGRATION_PLAN.md`** for detailed implementation roadmap.

## 🤝 Contributing

### Development Setup
1. Read `docs/DESIGN-INDEX.md` for documentation navigation
2. Review `docs/DESIGN-GUIDANCE.md` for development standards
3. Check `docs/DESIGN-STATE.md` for current technical debt
4. Follow quality gates and testing requirements

### Areas for Contribution
- **Language Content**: Add vocabulary data for new languages and proficiency levels
- **Templates**: Enhance HTML/CSS card designs for different languages
- **Language Models**: Implement grammar validation for additional languages
- **Testing**: Improve test coverage and add integration scenarios
- **Documentation**: Update and maintain design documentation

## 📊 Technical Specifications

- **Python**: 3.11+ required
- **Dependencies**: genanki, anki, pydantic, boto3, requests
- **Testing**: pytest with 263 unit tests
- **Type Checking**: mypy strict mode compliance
- **Package Management**: Hatch for development environment

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🎯 Project Goals

Language Learn aims to:
1. **Simplify Language Learning**: Generate comprehensive, grammar-aware flashcards for multiple languages
2. **Enable Multi-Language Support**: Extensible architecture supporting various languages and proficiency levels  
3. **Ensure Quality**: Maintain high code quality with comprehensive testing
4. **Provide Rich Media**: Integrate audio pronunciation and visual learning aids
5. **Support Scalability**: Clean architecture for adding new languages, features, and card types

**Current Status**: Production-ready application with German A1 support, designed for multi-language expansion.