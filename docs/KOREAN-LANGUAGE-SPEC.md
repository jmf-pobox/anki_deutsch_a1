# Korean Language - Complete Specification

## Overview

**Language**: Korean (한국어)
**Implementation Status**: Minimal - Basic noun vocabulary with particle system
**Total Card Types**: 1
**Total CSV Files**: 1
**Total Vocabulary**: 5 words

> **Particle-Focused Implementation**: Korean serves as a demonstration of how agglutinative languages with complex particle systems can be supported. Korean's unique features include particle phonological rules, counter/classifier system, and Hangul script typography.

## System Architecture

**Data Flow**: CSV → KoreanNounRecord (dataclass) → KoreanNoun (Domain Model) → MediaEnricher → CardBuilder → AnkiBackend → .apkg

**Key Features**:
- Hangul script support with proper typography
- Korean particle system (은/는, 이/가, 을/를) with phonological rules
- Counter/classifier system (개, 명, 마리, 채, 권)
- Final consonant (jongseong) detection for particle selection
- AWS Polly Korean TTS (Seoyeon voice)
- Unicode filename support for Hangul media files

---

# CSV Format Specification

## Directory Structure

Korean CSV files are organized by deck:
```
languages/korean/
└── default/         # Minimal content (1 CSV file)
```

## Korean Grammar Requirements

### 1. Korean-Specific Features
- **Particle System**: Subject (이/가), topic (은/는), object (을/를) particles
- **Phonological Rules**: Particle selection based on final consonant presence
- **Counter System**: Semantic classifiers for different object types
- **Agglutinative Structure**: Particles attach to nouns based on sound patterns

### 2. Korean Data Types
- **string_hangul**: Korean text in Hangul script (UTF-8)
- **romanization**: Revised Romanization of Korean
- **semantic_category**: person, animal, object, place, food, etc.
- **counter_korean**: Korean counters/classifiers (개, 명, 마리, 채, 권, etc.)

### 3. Technical Standards
- **Encoding**: UTF-8 (required for Hangul characters)
- **Script**: Hangul alphabet support (U+AC00-U+D7AF)
- **Phonology**: Final consonant detection for particle rules
- **Header Language**: English column names, Korean content

---

# Data Dictionary - Korean Language Fields

## Korean-Specific Field Types

### Korean Grammar Field Types
- **string_hangul**: Korean text in Hangul script with full Unicode support
- **romanization_korean**: Revised Romanization standard
- **semantic_category**: Semantic classification for counter selection
- **counter_korean**: Korean counter/classifier system
- **honorific_form**: Honorific alternatives where applicable

### Korean Grammar Constraints
- **Particle Rules**: 은/는 (final consonant/vowel), 이/가 (final consonant/vowel), 을/를 (final consonant/vowel)
- **Counter Appropriateness**: Counters must match semantic categories
- **Hangul Script**: All Korean content must be in Hangul, not romanization
- **Example Completeness**: Examples should demonstrate particle usage

## CSV File: nouns.csv

**Korean Grammar Focus**: Particle generation, counter system, semantic categorization

### CSV File: `languages/korean/default/nouns.csv`

| Field | Type | Required | Korean Rules | Example |
|-------|------|----------|--------------|---------|
| `hangul` | string_hangul | ✅ | Hangul script only | `학생` |
| `romanization` | romanization_korean | ✅ | Revised Romanization standard | `haksaeng` |
| `english` | string | ✅ | English translation | `student` |
| `primary_counter` | counter_korean | ✅ | Appropriate counter for category | `명` |
| `semantic_category` | semantic_category | ✅ | Semantic classification | `person` |
| `example` | string_hangul | ✅ | Complete Korean sentence with particles | `학생이 공부합니다` |
| `example_english` | string | ✅ | English translation | `The student studies` |
| `honorific_form` | string_hangul | ❌ | Honorific form if exists | `댁` (for 집) |
| `usage_notes` | string | ❌ | Additional usage information | (empty) |

---

# Card Type Specifications

## Card Type: Korean Noun

**Anki Note Type**: `Korean Noun with Media`
**Description**: Basic Korean noun cards with particle system and counters
**Learning Objective**: Learn Korean noun vocabulary with particles and counters
**Sub-deck**: `Nouns` (Main Deck::Nouns)

### Card Content

**Front**: English translation with image
**Back**: Korean noun with particles, romanization, counter, and example

### Field Specifications

| Field | Source | Description | Example |
|-------|--------|-------------|---------|
| `Hangul` | nouns.csv | Korean word in Hangul | `학생` |
| `Romanization` | nouns.csv | Revised Romanization | `haksaeng` |
| `English` | nouns.csv | English translation | `student` |
| `TopicParticle` | Generated | Topic particle (은/는) | `학생은` |
| `SubjectParticle` | Generated | Subject particle (이/가) | `학생이` |
| `ObjectParticle` | Generated | Object particle (을/를) | `학생을` |
| `Counter` | nouns.csv | Primary counter | `명` |
| `Example` | nouns.csv | Example sentence | `학생이 공부합니다` |
| `Image` | Pexels | Generated contextual image | `<img src="학생.jpg" />` |
| `WordAudio` | AWS_Polly | Korean pronunciation (Seoyeon voice) | `[sound:학생.mp3]` |
| `ExampleAudio` | AWS_Polly | Example sentence audio | `[sound:example.mp3]` |

## Language-Specific Features

### Korean Particle System
- **Topic Particle**: 은/는 (phonological rules: final consonant → 은, vowel → 는)
- **Subject Particle**: 이/가 (phonological rules: final consonant → 이, vowel → 가)
- **Object Particle**: 을/를 (phonological rules: final consonant → 을, vowel → 를)

### Counter/Classifier System
- **개**: General counter for objects
- **명**: Counter for people
- **마리**: Counter for animals
- **채**: Counter for buildings/houses
- **권**: Counter for books/volumes

### Hangul Typography
- **Fonts**: 'Noto Sans CJK KR', 'Malgun Gothic', '맑은 고딕'
- **Character Support**: Full Unicode Hangul block (U+AC00-U+D7AF)
- **Final Consonant Detection**: Automatic particle selection based on jongseong

### Audio Generation
- **Voice**: Seoyeon (ko-KR, female)
- **Engine**: AWS Polly Standard
- **Format**: MP3 with hash-based filenames

### Image Generation
- **Source**: Pexels API with translated search terms
- **Process**: Korean example → Claude translation → English search
- **Filename**: Hangul-based with .jpg extension (Unicode support)

## Implementation Status

**✅ Completed**:
- KoreanLanguage protocol implementation
- KoreanNounRecord dataclass model with particle generation
- KoreanNoun domain model with MediaGenerationCapable
- Korean-specific card builder and templates
- Hangul filename support in MediaFileRegistrar
- Unicode filename validation for Korean script
- Language registry integration
- NamingService architecture for consistent naming

**📋 Current Vocabulary**:
1. 학생 (student) - person, counter: 명
2. 사과 (apple) - food, counter: 개
3. 고양이 (cat) - animal, counter: 마리
4. 집 (house) - place, counter: 채, honorific: 댁
5. 책 (book) - object, counter: 권

**🔄 Future Expansion Opportunities**:
- Verb conjugation system (polite vs casual forms)
- Honorific system expansion
- Additional counters and particles
- Complex sentence patterns
- Hanja (Chinese character) integration