# Russian Language - Complete Specification

## Overview

**Language**: Russian (Русский)
**Implementation Status**: Minimal - Basic noun vocabulary
**Total Card Types**: 1
**Total CSV Files**: 1
**Total Vocabulary**: 5 words

> **Minimal Implementation**: Russian serves as a proof-of-concept for the multi-language architecture, demonstrating how different grammatical systems can be supported. Russian's unique features include 6-case declensions, animacy distinctions, and Cyrillic script support.

## System Architecture

**Data Flow**: CSV → RussianNounRecord (Pydantic) → RussianNoun (Domain Model) → MediaEnricher → CardBuilder → AnkiBackend → .apkg

**Key Features**:
- Cyrillic script support with UTF-8 encoding
- Russian case declension system (6 cases vs German's 4)
- Animacy distinction (animate vs inanimate nouns)
- AWS Polly Russian TTS (Tatyana voice)
- Unicode filename support for Cyrillic media files

---

# CSV Format Specification

## Directory Structure

Russian CSV files are organized by deck:
```
languages/russian/
└── default/         # Minimal content (1 CSV file)
```

## Russian Grammar Requirements

### 1. Russian-Specific Features
- **6-Case System**: Nominative, Genitive, Dative, Accusative, Instrumental, Prepositional
- **Animacy**: Animate vs inanimate affects accusative case formation
- **Gender System**: Masculine, feminine, neuter (similar to German but different endings)
- **Soft/Hard Consonants**: Affects declension patterns

### 2. Russian Data Types
- **string_cyrillic**: Russian text in Cyrillic script (UTF-8)
- **gender_russian**: masculine, feminine, neuter
- **animacy_russian**: animate, inanimate
- **case_russian**: nominative, genitive, dative, accusative, instrumental, prepositional

### 3. Technical Standards
- **Encoding**: UTF-8 (required for Cyrillic characters)
- **Script**: Cyrillic alphabet support
- **Header Language**: English column names, Russian content

---

# Data Dictionary - Russian Language Fields

## Russian-Specific Field Types

### Russian Grammar Field Types
- **string_cyrillic**: Russian text with full Cyrillic support
- **gender_russian**: masculine, feminine, neuter
- **animacy_russian**: animate (живой), inanimate (неживой)
- **case_forms**: All 6 Russian cases in singular and plural

### Russian Grammar Constraints
- **Case Completeness**: All 6 cases required for complete declension
- **Animacy Rules**: Animate masculine nouns have genitive = accusative
- **Gender Patterns**: Endings must follow Russian gender patterns
- **Cyrillic Script**: All Russian content must be in Cyrillic, not Latin transliteration

## CSV File: nouns.csv

**Russian Grammar Focus**: 6-case declensions, animacy, gender patterns

| Field | Type | Required | Russian Rules | Example |
|-------|------|----------|--------------|---------|
| `noun` | string_cyrillic | ✅ | Cyrillic script only | `дом` |
| `english` | string | ✅ | English translation | `house` |
| `gender` | gender_russian | ✅ | masculine, feminine, neuter | `masculine` |
| `genitive` | string_cyrillic | ✅ | Genitive singular form | `дома` |
| `example` | string_cyrillic | ✅ | Complete Russian sentence | `Это мой дом` |
| `related` | string_cyrillic | ❌ | Related Russian words | `домик` |
| `animacy` | animacy_russian | ✅ | animate or inanimate | `inanimate` |
| `instrumental` | string_cyrillic | ✅ | Instrumental singular | `домом` |
| `prepositional` | string_cyrillic | ✅ | Prepositional singular | `доме` |
| `dative` | string_cyrillic | ✅ | Dative singular | `дому` |
| `plural_nominative` | string_cyrillic | ✅ | Plural nominative | `дома` |
| `plural_genitive` | string_cyrillic | ✅ | Plural genitive | `домов` |

---

# Card Type Specifications

## Card Type: Russian Noun

**Anki Note Type**: `Russian Noun with Media`
**Description**: Basic Russian noun cards with case declensions
**Learning Objective**: Learn Russian noun vocabulary with case system
**Sub-deck**: `Nouns` (Main Deck::Nouns)

### Card Content

**Front**: English translation with image
**Back**: Russian noun with example sentence and audio

### Field Specifications

| Field | Source | Description | Example |
|-------|--------|-------------|---------|
| `Noun` | nouns.csv | Russian noun in Cyrillic | `дом` |
| `English` | nouns.csv | English translation | `house` |
| `Gender` | nouns.csv | Grammatical gender | `masculine` |
| `Genitive` | nouns.csv | Genitive case form | `дома` |
| `Example` | nouns.csv | Example sentence | `Это мой дом` |
| `Related` | nouns.csv | Related words | `домик` |
| `Image` | Pexels | Generated contextual image | `<img src="house.jpg" />` |
| `WordAudio` | AWS_Polly | Russian pronunciation (Tatyana voice) | `[sound:дом.mp3]` |
| `ExampleAudio` | AWS_Polly | Example sentence audio | `[sound:example.mp3]` |

## Language-Specific Features

### Russian Case System
- **6 Cases**: Nominative, Genitive, Dative, Accusative, Instrumental, Prepositional
- **Animacy**: Distinguishes animate vs inanimate for accusative case
- **Gender**: Masculine, feminine, neuter affect declension patterns

### Audio Generation
- **Voice**: Tatyana (ru-RU, female)
- **Engine**: AWS Polly Standard
- **Format**: MP3 with hash-based filenames

### Image Generation
- **Source**: Pexels API with translated search terms
- **Process**: Russian example → Claude translation → English search
- **Filename**: English-based with .jpg extension

## Implementation Status

**✅ Completed**:
- RussianLanguage protocol implementation
- RussianNounRecord Pydantic model
- RussianNoun domain model with MediaGenerationCapable
- Russian-specific card builder and templates
- Cyrillic filename support in MediaFileRegistrar
- Language registry integration

**📋 Current Vocabulary**:
1. дом (house) - masculine, inanimate
2. кот (cat) - masculine, animate
3. мама (mother) - feminine, animate
4. вода (water) - feminine, inanimate
5. окно (window) - neuter, inanimate

**🔄 Future Expansion Opportunities**:
- Additional vocabulary sets (verbs, adjectives)
- More complex grammatical features
- Advanced case usage patterns
- Aspect system for verbs