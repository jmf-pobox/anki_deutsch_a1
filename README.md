# 🎓 Language Learn - German Anki Deck Generator

**Production-ready system for generating intelligent German A1 flashcards with Clean Pipeline Architecture.**

Language Learn creates comprehensive German vocabulary decks using advanced Clean Pipeline Architecture. The system generates over 1,000 cards from 7 different word types, with automatic media integration, proper German grammar handling, and enterprise-grade quality standards.

[![CI](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml/badge.svg)](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml)
[![Quality](https://img.shields.io/badge/MyPy-0%20errors-brightgreen)](https://mypy-lang.org/)
[![Tests](https://img.shields.io/badge/Tests-686%20passing-brightgreen)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-73%25+-brightgreen)](https://coverage.readthedocs.io/)

## 🎯 What This Does For You

**Generate comprehensive German learning decks with production-grade quality:**
- **Complete Word Type Coverage** → Nouns, verbs, adjectives, adverbs, prepositions, phrases, negations
- **German Grammar Mastery** → Article recall (der/die/das), verb conjugations with perfect tense, case-dependent prepositions  
- **Rich Media Integration** → AWS Polly audio pronunciation, Pexels contextual images
- **Smart Templates** → Clean card design with hint buttons, proper styling, contextual examples
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

### 2. Generate German A1 Deck (Basic)
```bash
# Generate deck with included German vocabulary (500+ words)
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
python src/langlearn/utils/api_keyring.py add PEXELS_API_KEY your_key

# Generate with full media integration
hatch run app --generate-media
```

### 4. Import to Anki
1. Open Anki desktop application
2. Click **File > Import**
3. Select the `.apkg` file from `output/` folder
4. Start studying your German vocabulary with 1,000+ intelligent flashcards!

## 📚 Included German A1 Vocabulary

The system includes comprehensive German A1 vocabulary across 7 word types:

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
- **Backward Compatible:** Seamless fallback for legacy components

### Word Type Implementation Status:
- ✅ **Clean Pipeline:** noun, adjective, adverb, negation, **verb** (5/7 types)
- ✅ **Legacy Fallback:** preposition, phrase (2/7 types)
- ✅ **Automatic Delegation:** System chooses optimal architecture per type

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
python src/langlearn/utils/api_keyring.py add PEXELS_API_KEY your_key
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

## 🔄 Future Roadmap

### Planned Enhancements:
- **Complete Clean Pipeline Migration:** Move remaining 2/7 word types to modern architecture
- **Multi-Language Foundation:** Language-agnostic architecture for Spanish, French, Italian support  
- **Advanced Features:** Multi-deck generation, voice recording comparison, progress analytics
- **Performance Optimization:** Enhanced batch processing and caching strategies

## 🆘 Getting Help

### Common Solutions

**"No cards generated":** 
- Run `hatch run test` to verify system integrity
- Check CSV file formats match expected structure
- Verify all 686 tests pass before troubleshooting

**"Import failed in Anki":**
- Use Anki desktop application (not AnkiWeb browser version)
- Ensure .apkg file was generated successfully in `output/` folder
- Try `hatch run run-sample` for smaller test deck first

**"Media not working":**
- API keys are optional - cards work without media
- See Advanced Configuration for AWS Polly and Pexels setup
- Use `hatch run app --generate-media` only after API setup

### Support & Documentation
- 🐛 **Issues:** [GitHub Issues](https://github.com/jmf-pobox/anki_deutsch_a1/issues)
- 📖 **Technical Docs:** `docs/DESIGN-INDEX.md` for navigation
- 🏗️ **Architecture:** `docs/DESIGN-GUIDANCE.md` for development standards
- 💡 **Contributing:** Review `CLAUDE.md` and `AI.md` for guidelines

## 🎓 German Language Specialization

### Why German A1 Focus?
This system was specifically designed to handle German's unique challenges:

**Noun Gender System (der/die/das):**
- Separate cards test article recall vs. meaning
- Visual memory reinforcement with contextual images
- Audio pronunciation includes articles with nouns

**Complex Verb System:**
- Separable verb handling (aufstehen → ich stehe auf)
- Perfect tense audio (habe gesprochen, bin gekommen)
- Complete conjugation patterns with pronunciation

**Case-Dependent Grammar:**
- Preposition cards show required cases (mit + Dativ)
- Context-aware example sentences
- Grammar-specific validation and templates

The Clean Pipeline Architecture provides a foundation for extending this German-specific expertise to other languages with similar complexity.

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
- **German Expertise:** Language-specific validation and processing logic
- **Production Ready:** Security hardening and performance optimization

### Contributing Guidelines
1. **Read Required Docs:** `CLAUDE.md`, `AI.md`, and `docs/DESIGN-INDEX.md`
2. **Follow Quality Standards:** All 6 quality gates must pass (see CLAUDE.md)
3. **Use Micro-Commits:** Atomic changes with comprehensive testing
4. **Branch Workflow:** Feature branches with PR review process
5. **Architecture Compliance:** Follow Clean Pipeline patterns

### Key Architecture Files
- **Clean Pipeline:** `src/langlearn/services/` (CardBuilder, MediaEnricher, RecordMapper)
- **Domain Models:** `src/langlearn/models/` (German-specific validation)
- **Records System:** Lightweight DTOs for data transport
- **Backend Integration:** `src/langlearn/backends/` (Anki library abstraction)

---

**🏆 Production-ready German A1 flashcard generation system with enterprise-grade architecture and comprehensive German language support.**