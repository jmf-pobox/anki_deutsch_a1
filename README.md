# 🎓 Language Learn, an Anki Flashcard Generator

**Multi-language flashcard generation system that adapts to specific language grammar patterns.**

This project generates customized language learning Anki decks. One issue 
this system addresses is that many existing Anki decks do not reflect the 
specific challenges of the target language.  For example, memorizing 
German and irregular verb conjugations are two challenges. The grammar of 
the target language affects the best Anki deck design. This Anki deck 
generator seeks to address that challenge.  The primary user of this 
system is intended to be the language learner. A secondary user of the 
system is intended to be foreign language teachers. This system is 
inspired by Fluent Forever, a book by Gabriel Wyner.

[![CI](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml/badge.svg)](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/langlearn.svg)](https://pypi.org/project/langlearn/)
<a href="https://pypi.org/project/langlearn"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/langlearn?color=blue"></a>
[![License](https://img.shields.io/github/license/jmf-pobox/anki_deutsch_a1.svg)](https://github.com/jmf-pobox/anki_deutsch_a1/blob/main/LICENSE)

## 🎯 What This Does For You

**Generate language-specific learning decks with the following features:**
- **Language-Specific Adaptation** → Handles unique grammar patterns (currently German, expanding to Russian, Korean, others)
- **Complete Grammar Coverage** → All word types with language-specific challenges (German: der/die/das articles, verb conjugations, cases)
- **Rich Media Integration** → AWS Polly audio pronunciation, Pexels contextual images
- **Card Templates** → Clean design with hint buttons, proper styling, contextual examples
- **Test Coverage & Quality Tools** → Comprehensive test suite, 0 MyPy strict mode errors

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

### 2. Generate German Decks
```bash
# Generate default German deck (A2/B1 level - 1000+ cards)
hatch run app

# Generate specific German decks by level
hatch run app -- --language german --deck a1.1    # Beginner (A1.1)
hatch run app -- --language german --deck a1      # Elementary (A1)
hatch run app -- --language german --deck default # Intermediate (A2/B1)
hatch run app -- --language german --deck business # Business German

# Custom output file
hatch run app -- --language german --deck a1 --output my-german-a1.apkg
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

# Test your API key setup (tests both Anthropic and Pexels APIs)
hatch run test-env
```

### 4. Import to Anki
1. Open Anki desktop application
2. Click **File > Import**
3. Select the `.apkg` file from `output/` folder
4. Start studying with intelligent, language-specific flashcards!

## 📚 Current Implementation: German Vocabulary Decks

The system includes comprehensive German decks organized by CEFR levels:

- **A1.1 (Beginner)**: Basic vocabulary for absolute beginners
- **A1 (Elementary)**: Complete A1 level vocabulary  
- **Default (A2/B1)**: Intermediate vocabulary for advanced learners
- **Business**: German business and professional vocabulary 

### Available German Decks:

```bash
# Check what decks are available
hatch run app -- --help

# List available German decks
hatch run app -- --language german --deck nonexistent
# (Will show available deck options)
```

**Deck Structure** - Each deck contains:
```
languages/german/{deck}/
├── nouns.csv           # German nouns with articles and cases
├── verbs.csv           # Verbs with conjugations and perfect tense
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
- **Templates:** Consistent styling matching established patterns

### 🎯 **Other Card Types**
- **Adjectives:** Comparative and superlative forms with audio
- **Adverbs:** Contextual usage with pronunciation
- **Prepositions:** Case-dependent forms (Akkusativ/Dativ)
- **Phrases:** Common expressions with natural audio
- **Negations:** German negation patterns and usage

### ✨ **System Features**
- **Clean Pipeline:** CSV → Records → MediaEnricher → CardBuilder → AnkiBackend data flow
- **Media Integration:** Automatic audio/image embedding in .apkg files
- **Filename Sanitization:** Comprehensive validation for safe file operations
- **Batch Processing:** Efficient handling and caching of media files
- **German-Specific Logic:** Handles separable verbs, case declensions, gender patterns

## 🏗️ System Architecture

### Architecture

The system turns CSV data into Anki cards using the following flow:

```
CSV → RecordMapper → Records → MediaEnricher → Domain Models → Enriched Records → CardBuilder → AnkiBackend
```

### Architecture Components:
- **Records**: Pydantic data transport objects with validation
- **Domain Models**: Objects with German language business logic methods  
- **MediaEnricher**: Converts Records → Domain Models, calls business logic, returns enriched Records
- **CardBuilder**: Transforms enriched Records into formatted card templates
- **AnkiBackend**: Uses enriched Records for card creation, falls back to ModelFactory when needed

### Current Word Type Support:
- ✅ **Full Support:** All 7 German word types (noun, adjective, adverb, negation, verb, preposition, phrase)
- ✅ **Dual System:** Records for validation + Domain Models for business logic
- ✅ **Media Generation:** German-specific audio and image processing

## ⚙️ Advanced Configuration

### API Services (Optional)
Enhance your decks with audio and images:

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

### Quality Standards
- ✅ **Test Coverage:** Edge case and error handling tests included (run `hatch run test-cov` for current metrics)
- ✅ **Zero MyPy Errors:** Strict type checking across all source files
- ✅ **Zero Linting Violations:** Ruff and black compliance

### Development Commands
```bash
# Quality verification (required for contributions)
hatch run type                 # MyPy type checking (0 errors required)
hatch run test                 # Full test suite
hatch run test-cov             # Coverage analysis (see current metrics)
hatch run format               # Code formatting
hatch run ruff check --fix     # Linting compliance

# Application usage
hatch run app                  # Generate default German deck (A2/B1)
hatch run app -- --deck a1.1  # Generate A1.1 beginner deck  
hatch run app -- --deck a1    # Generate A1 elementary deck
hatch run app -- --deck business # Generate business German deck
```

## 🔄 Roadmap: Multi-Language Vision

### **Phase 1: Multi-Language Expansion** 🚀 **Future**
- **Russian**: Cyrillic script, case system, aspect pairs
- **Korean**: Hangul, honorifics, complex verb conjugations  
- **Additional Languages**: Spanish, French, Italian, Japanese
- Language-specific grammar intelligence for each

### **Phase 2: Advanced Features**
- Voice recording comparison
- Progress tracking analytics
- Spaced repetition optimization
- Community deck sharing

## 🆘 Getting Help

### Common Solutions

**"No cards generated":**
- Run `hatch run test` to verify system integrity
- Check CSV file formats match expected structure
- Ensure all tests pass for proper system validation

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

## 🏗️ For Developers

### Development Environment
```bash
# Complete development setup
hatch env create
hatch run type          # MyPy strict type checking (0 errors required)
hatch run test          # All tests (unit + integration)
hatch run test-unit     # Unit tests only (100% pass rate required)
hatch run test-cov      # Coverage analysis (current metrics maintained)
hatch run format        # Code formatting (PEP 8 compliance)
hatch run lint          # Linting (zero violations required)
hatch run check         # Complete quality verification
```

### Contributing Guidelines
1. **Read Required Docs:** `CLAUDE.md`, `docs/ENG-PYTHON-STANDARDS.md`, and `docs/ENG-DESIGN-INDEX.md`
2. **Follow Quality Standards:** All 6 quality gates must pass (see CLAUDE.md)
3. **Use Micro-Commits:** Atomic changes with comprehensive testing
4. **Branch Workflow:** Feature branches with PR review process
5. **Architecture Compliance:** Follow clean pipeline architecture patterns

### Key Architecture Files
- **Services:** `src/langlearn/services/` (CardBuilder, MediaEnricher, RecordMapper)
- **Models:** `src/langlearn/models/` (Records + Domain Models for German processing)
- **Records System:** Pydantic objects for data validation and transport
- **Domain Models:** Objects with German language business logic methods
- **Backend Integration:** `src/langlearn/backends/` (Anki library abstraction)
