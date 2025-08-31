# 🎓 Language Learn - Anki Flashcard Generator

**Multi-language flashcard generation system with language-specific grammar intelligence.**

Language Learn creates comprehensive vocabulary decks using advanced Clean Pipeline Architecture. Currently supporting **German A1** as the first implementation, the system is designed for multi-language expansion with language-specific grammar handling, automatic media integration, and enterprise-grade quality standards.

[![CI](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml/badge.svg)](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml)
[![Quality](https://img.shields.io/badge/MyPy-0%20errors-brightgreen)](https://mypy-lang.org/)
[![Tests](https://img.shields.io/badge/Tests-686%20passing-brightgreen)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-73%25+-brightgreen)](https://coverage.readthedocs.io/)

## 🎯 What This Does For You

**Generate language-specific learning decks with production-grade quality:**
- **Language-Specific Intelligence** → Adapts to unique grammar patterns (currently German A1, expanding to Russian, Korean, others)
- **Complete Grammar Coverage** → All word types with language-specific challenges (German: der/die/das articles, verb conjugations, cases)
- **Rich Media Integration** → AWS Polly audio pronunciation, Pexels contextual images
- **Smart Templates** → Clean card design with hint buttons, proper styling, contextual examples
- **Multi-Language Ready** → Clean Pipeline Architecture designed for language expansion
- **Enterprise Quality** → 686 tests, 0 MyPy errors, comprehensive security validation

## 🚀 Quick Start

### 1. Install and Setup
```bash
# Clone the repository
git clone https://github.com/jmf-pobox/anki_deutsch_a1.git
cd anki_deutsch_a1

# Install dependencies using Hatch
pip install hatch
hatch env create
```

### 2. Generate Language Deck (Basic)
```bash
# Generate German A1 deck (current implementation - 1000+ cards)
hatch run app

# Generate sample deck for testing
hatch run run-sample
```

### 3. Generate with Media (Advanced)
Set up API keys for enhanced features:
```bash
# AWS credentials for pronunciation audio
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# Pexels API for contextual images
python scripts/api_keyring.py add PEXELS_API_KEY your_key

# Generate with full media integration
hatch run app --generate-media
```

### 4. Import to Anki
1. Open Anki desktop application
2. Click **File > Import**
3. Select the `.apkg` file from `output/` folder
4. Start studying with intelligent, language-specific flashcards!

## 📚 Current Implementation: German A1 Vocabulary

The system currently includes comprehensive German A1 vocabulary as the first language implementation:

### Word Types Supported:
```
data/
├── nouns.csv           # 200+ German nouns with articles and cases
├── verbs.csv           # 100+ verbs with conjugations and perfect tense
├── adjectives.csv      # Comparative and superlative forms
├── adverbs.csv         # Common German adverbs with examples
├── prepositions.csv    # Case-dependent prepositions
├── phrases.csv         # Essential German phrases
└── negations.csv       # German negation patterns
```

### CSV Format Examples:

**Nouns** (Gender and case-aware):
```csv
noun,article,english,plural,example,related,case_context
Hund,der,dog,Hunde,Der Hund bellt laut,Tier,Nominativ
```

**Verbs** (Complete conjugation support):
```csv
verb,english,present_ich,present_du,present_er,perfect,example
sprechen,to speak,spreche,sprichst,spricht,habe gesprochen,Ich spreche Deutsch
```

## 🎨 Generated Card Types

### 🏠 **Noun Cards** - German Gender Mastery
- **Image + Hint Design:** Visual learning with hidden English translation
- **Article Testing:** "_____ Hund" → "der" (tests gender recall)
- **Context Learning:** "dog" → "der Hund" with example sentences
- **Audio:** Perfect German pronunciation for all forms

### ⚡ **Verb Cards** - Complete Conjugation System  
- **Full Conjugation Audio:** Includes infinitive + all persons + perfect tense
- **Visual Context:** Images based on example sentences
- **Hint System:** Clean design with expandable translations
- **Templates:** Professional styling matching established patterns

### 🎯 **Other Card Types**
- **Adjectives:** Comparative and superlative forms with audio
- **Adverbs:** Contextual usage with pronunciation
- **Prepositions:** Case-dependent forms (Akkusativ/Dativ)
- **Phrases:** Common expressions with natural audio
- **Negations:** German negation patterns and usage

### ✨ **Smart Features**
- **Clean Pipeline Architecture:** Enterprise-grade data processing
- **Media Integration:** Automatic audio/image embedding in .apkg files
- **Security Validated:** Comprehensive filename sanitization
- **Performance Optimized:** Batch processing and intelligent caching
- **German-Specific Logic:** Handles separable verbs, case declensions, gender patterns

## 🏗️ Clean Pipeline Architecture

### Modern Enterprise Architecture
The system uses **Clean Pipeline Architecture** for optimal performance and maintainability:

```
CSV → Records → Domain Models → MediaEnricher → CardBuilder → Anki Backend
```

### Architecture Benefits:
- **Separation of Concerns:** Each component has single responsibility
- **High Testability:** 686 tests with comprehensive coverage
- **Performance Optimized:** Batch processing and intelligent caching
- **Security First:** Comprehensive input validation and sanitization
- **Robust Architecture:** Reliable processing across all word types

### Current Word Type Support:
- ✅ **Modern Architecture:** noun, adjective, adverb, negation, **verb** (5/7 types)
- ✅ **Supported:** preposition, phrase (2/7 types)
- ✅ **Intelligent Processing:** System optimally handles all word types

## ⚙️ Advanced Configuration

### API Services (Optional)
Enhance your decks with professional media:

**AWS Polly (Audio Pronunciation):**
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret  
export AWS_DEFAULT_REGION=us-east-1
```

**Pexels (Contextual Images):**
```bash
python scripts/api_keyring.py add PEXELS_API_KEY your_key
```

## 📊 Quality & Development

### Production-Grade Quality Standards
- ✅ **686 Tests Passing:** 665 unit + 21 integration tests
- ✅ **Zero MyPy Errors:** Strict type checking across 116 source files
- ✅ **73%+ Test Coverage:** Comprehensive edge case and error handling
- ✅ **Zero Linting Violations:** Perfect code quality standards
- ✅ **Security Hardened:** Input validation and sanitization throughout

### Development Commands
```bash
# Quality verification (required for contributions)
hatch run type                 # MyPy type checking (0 errors required)
hatch run test                 # Full test suite (686 tests)
hatch run test-cov             # Coverage analysis (73%+ required)
hatch run format               # Code formatting
hatch run ruff check --fix     # Linting compliance

# Application usage
hatch run app                  # Generate full German A1 deck
hatch run run-sample           # Generate sample deck
hatch run run-adjectives       # Generate adjectives-only deck
```

## 🔄 Roadmap: Multi-Language Vision

### **Phase 1: German Enhancement** ✅ **Current**
- ✅ Complete German A1 implementation (1000+ cards, 7 word types)
- ✅ Clean Pipeline Architecture foundation
- 🔄 Enhanced processing architecture for all word types

### **Phase 2: Multi-Deck Support** 🎯 **Next**
- Multiple deck generation (beginner, intermediate, advanced)
- Topic-based decks (business, travel, academic)
- Custom deck creation workflows

### **Phase 3: Multi-Language Expansion** 🚀 **Future**
- **Russian**: Cyrillic script, case system, aspect pairs
- **Korean**: Hangul, honorifics, complex verb conjugations  
- **Additional Languages**: Spanish, French, Italian, Japanese
- Language-specific grammar intelligence for each

### **Phase 4: Advanced Features**
- Voice recording comparison
- Progress tracking analytics
- Spaced repetition optimization
- Community deck sharing

## 🆘 Getting Help

### Common Solutions

**"No cards generated":** 
- Run `hatch run test` to verify system integrity
- Check CSV file formats match expected structure
- Ensure all 686 tests pass for proper system validation

**"Import failed in Anki":**
- Use Anki desktop application (not AnkiWeb browser version)
- Ensure .apkg file was generated successfully in `output/` folder
- Try `hatch run run-sample` for smaller test deck first

**"Media not working":**
- API keys are optional - cards work without media
- See Advanced Configuration for AWS Polly and Pexels setup
- Use `hatch run app --generate-media` with configured API keys

### Support & Documentation
- 🐛 **Issues:** [GitHub Issues](https://github.com/jmf-pobox/anki_deutsch_a1/issues)
- 📖 **Technical Docs:** `docs/ENG-DESIGN-INDEX.md` for navigation
- 🏗️ **Architecture:** `docs/ENG-DEVELOPMENT-STANDARDS.md` for development standards
- 💡 **Contributing:** Review `CLAUDE.md` and `docs/ENG-PYTHON-STANDARDS.md` for guidelines

## 🎓 Language-Specific Intelligence

### German A1 Implementation (Current)
The system demonstrates language-specific intelligence with German as the first implementation:

**German Grammar Challenges Solved:**
- **Noun Gender System (der/die/das):** Separate cards test article recall vs. meaning
- **Complex Verb System:** Separable verb handling (aufstehen → ich stehe auf), perfect tense
- **Case-Dependent Grammar:** Preposition cards show required cases (mit + Dativ)
- **Context-Aware Learning:** Grammar-specific validation and templates

### Multi-Language Architecture Foundation
The Clean Pipeline Architecture provides a proven foundation for language expansion:

**Designed for Language Diversity:**
- **Russian Readiness:** Case system handling, Cyrillic script support
- **Korean Readiness:** Complex honorific systems, agglutinative grammar patterns  
- **Romance Language Ready:** Verb conjugation complexity, gendered nouns
- **Extensible Framework:** Each language gets custom grammar intelligence

---

## 🏗️ For Developers

### Enterprise-Grade Development Environment
```bash
# Complete development setup
hatch env create
hatch run type          # MyPy strict type checking (0 errors required)
hatch run test          # 686 tests (100% pass rate required)
hatch run test-cov      # Coverage analysis (73%+ maintained)
hatch run format        # Code formatting (PEP 8 compliance)
hatch run ruff check    # Linting (zero violations required)
```

### Clean Pipeline Architecture
- **Modern Design:** Clean separation of concerns with dependency inversion
- **High Testability:** Comprehensive test coverage with mocking and integration tests
- **Type Safety:** MyPy strict mode compliance across entire codebase
- **Multi-Language Ready:** Language-agnostic core with pluggable language modules
- **Production Ready:** Security hardening and performance optimization

### Contributing Guidelines
1. **Read Required Docs:** `CLAUDE.md`, `docs/ENG-PYTHON-STANDARDS.md`, and `docs/ENG-DESIGN-INDEX.md`
2. **Follow Quality Standards:** All 6 quality gates must pass (see CLAUDE.md)
3. **Use Micro-Commits:** Atomic changes with comprehensive testing
4. **Branch Workflow:** Feature branches with PR review process
5. **Architecture Compliance:** Follow Clean Pipeline patterns

### Key Architecture Files
- **Clean Pipeline:** `src/langlearn/services/` (CardBuilder, MediaEnricher, RecordMapper)
- **Language Models:** `src/langlearn/models/` (Currently German, designed for expansion)
- **Records System:** Language-agnostic DTOs for data transport
- **Backend Integration:** `src/langlearn/backends/` (Anki library abstraction)

---

**🏆 Multi-language flashcard generation system with Clean Pipeline Architecture. Currently supporting German A1 with roadmap for Russian, Korean, and other languages.**