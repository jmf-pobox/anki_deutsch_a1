# German Language - Complete Specification

## Overview

**Language**: German (Deutsch)
**Implementation Status**: Complete - Full A1 grammar coverage
**Total Card Types**: 15
**Total CSV Files**: 15
**Total Vocabulary**: 500+ words across all word types

> **Complete Implementation**: German is the primary language implementation with comprehensive grammar coverage, including cases, genders, verb conjugations, article declensions, and all major word types required for A1-level German learning.

## System Architecture

**Data Flow**: CSV → GermanRecords (dataclass) → GermanDomainModels → MediaEnricher → CardBuilder → AnkiBackend → .apkg

**Key Features**:
- Complete German case system (Nominativ, Akkusativ, Dativ, Genitiv)
- Gender system (maskulin, feminin, neutral) with article declensions
- Verb conjugation system (regular, irregular, separable verbs)
- German-specific linguistic features (umlauts, ß, compound words)
- AWS Polly German TTS (Marlene voice)
- Comprehensive template system with 54 German-specific templates

---

# CSV Format Specification

## Directory Structure

German CSV files are organized by deck:
```
languages/german/
├── default/          # Complete A1 content (15 CSV files)
├── a1.1/            # A1.1 level content (11 CSV files)
├── a1/              # A1 level content (10 CSV files)
└── business/        # Business vocabulary (1 CSV file)
```

## Core Principles for German CSVs

### 1. German Grammar Requirements
- **Case Fields**: German nouns require Nominativ, Akkusativ, Dativ, Genitiv forms
- **Gender Fields**: Articles must specify maskulin, feminin, neutral, plural
- **Verb Conjugation**: ich/du/er/wir/ihr/sie forms required for present tense
- **Article Declensions**: Definite, indefinite, and negative articles by case

### 2. German-Specific Data Types
- **string_german**: German text supporting ä, ö, ü, ß characters
- **article_type**: bestimmt, unbestimmt, verneinend
- **gender_type**: maskulin, feminin, neutral, plural
- **case_type**: Nominativ, Akkusativ, Dativ, Genitiv
- **verb_classification**: regelmäßig, unregelmäßig, gemischt

### 3. Technical Standards
- **Encoding**: UTF-8 (required for German special characters)
- **Delimiter**: Comma (`,`)
- **Quote Character**: Double quote (`"`) for fields containing commas
- **Header Language**: English column names, German content

---

# Data Dictionary - German Language Fields

## German-Specific Field Types

### Common German Field Types
- **string_german**: German text with ä, ö, ü, ß support
- **gender_german**: maskulin, feminin, neutral, plural
- **case_german**: Nominativ, Akkusativ, Dativ, Genitiv
- **article_german**: der, die, das (definite); ein, eine (indefinite); kein, keine (negative)
- **verb_class_german**: regelmäßig, unregelmäßig, gemischt

### German Grammar Constraints
- **German Nouns**: Must be capitalized (Haus, not haus)
- **Articles**: Must be der, die, or das for definite articles
- **Cases**: Must use German case names (not English equivalents)
- **Verb Forms**: Must follow German conjugation patterns
- **Examples**: Must be complete, grammatically correct German sentences

## CSV Files and Fields

### 1. Nouns (nouns.csv)
**German Grammar Focus**: Articles, plurals, examples

| Field | Type | Required | German Rules | Example |
|-------|------|----------|--------------|---------|
| `noun` | string_german | ✅ | Must be capitalized | `Haus` |
| `article` | article_german | ✅ | der, die, or das only | `das` |
| `english` | string | ✅ | English translation | `house` |
| `plural` | string_german | ✅ | German plural form | `Häuser` |
| `example` | string_german | ✅ | Complete German sentence | `Das Haus ist schön.` |
| `related` | string_german | ❌ | Comma-separated German words | `Gebäude, Wohnung` |

### 2. Articles Unified (articles_unified.csv)
**German Grammar Focus**: Case declensions, gender patterns

| Field | Type | Required | German Rules | Example |
|-------|------|----------|--------------|---------|
| `artikel_typ` | string | ✅ | bestimmt, unbestimmt, verneinend | `bestimmt` |
| `geschlecht` | gender_german | ✅ | maskulin, feminin, neutral, plural | `maskulin` |
| `nominativ` | article_german | ✅ | German article in nominative | `der` |
| `akkusativ` | article_german | ✅ | German article in accusative | `den` |
| `dativ` | article_german | ✅ | German article in dative | `dem` |
| `genitiv` | article_german | ✅ | German article in genitive | `des` |
| `beispiel_nom` | string_german | ❌ | Complete German sentence | `Der Mann ist hier` |
| `beispiel_akk` | string_german | ❌ | Complete German sentence | `Ich sehe den Mann` |
| `beispiel_dat` | string_german | ❌ | Complete German sentence | `mit dem Mann` |
| `beispiel_gen` | string_german | ❌ | Complete German sentence | `das Auto des Mannes` |

### 3. Verbs (verbs.csv)
**German Grammar Focus**: Conjugations, auxiliary verbs, separable verbs

| Field | Type | Required | German Rules | Example |
|-------|------|----------|--------------|---------|
| `verb` | string_german | ✅ | German infinitive | `arbeiten` |
| `english` | string | ✅ | Starts with "to" | `to work` |
| `classification` | verb_class_german | ✅ | regelmäßig, unregelmäßig, gemischt | `regelmäßig` |
| `present_ich` | string_german | ✅ | ich conjugation | `arbeite` |
| `present_du` | string_german | ✅ | du conjugation | `arbeitest` |
| `present_er` | string_german | ✅ | er/sie/es conjugation | `arbeitet` |
| `präteritum` | string_german | ✅ | Simple past 3rd person | `arbeitete` |
| `auxiliary` | string_german | ✅ | haben or sein | `haben` |
| `perfect` | string_german | ✅ | Perfect tense 3rd person | `hat gearbeitet` |
| `example` | string_german | ❌ | Complete German sentence | `Er arbeitet in einer Bank.` |
| `separable` | boolean | ✅ | true or false | `false` |

### 4. Verbs Unified (verbs_unified.csv)
**German Grammar Focus**: Complete conjugation paradigms by tense

| Field | Type | Required | German Rules | Example |
|-------|------|----------|--------------|---------|
| `infinitive` | string_german | ✅ | German infinitive | `sprechen` |
| `english` | string | ✅ | English translation | `to speak` |
| `classification` | verb_class_german | ✅ | regelmäßig, unregelmäßig, gemischt | `unregelmäßig` |
| `separable` | boolean | ✅ | true or false | `false` |
| `auxiliary` | string_german | ✅ | haben or sein | `haben` |
| `tense` | string | ✅ | present, preterite, perfect, future | `present` |
| `ich` | string_german | ❌ | ich conjugation | `spreche` |
| `du` | string_german | ❌ | du conjugation | `sprichst` |
| `er` | string_german | ❌ | er/sie/es conjugation | `spricht` |
| `wir` | string_german | ❌ | wir conjugation | `sprechen` |
| `ihr` | string_german | ❌ | ihr conjugation | `sprecht` |
| `sie` | string_german | ❌ | sie/Sie conjugation | `sprechen` |
| `example` | string_german | ❌ | Complete German sentence | `Ich spreche Deutsch.` |

### 5. Adjectives (adjectives.csv)
**German Grammar Focus**: Comparative, superlative forms

| Field | Type | Required | German Rules | Example |
|-------|------|----------|--------------|---------|
| `word` | string_german | ✅ | Base form, lowercase | `schön` |
| `english` | string | ✅ | English translation | `beautiful` |
| `example` | string_german | ❌ | Complete German sentence | `Das Haus ist schön.` |
| `comparative` | string_german | ❌ | Usually ends in -er | `schöner` |
| `superlative` | string_german | ❌ | Typically am + -sten | `am schönsten` |

### 6. Prepositions (prepositions.csv)
**German Grammar Focus**: Case requirements

| Field | Type | Required | German Rules | Example |
|-------|------|----------|--------------|---------|
| `preposition` | string_german | ✅ | German preposition | `mit` |
| `english` | string | ✅ | English translation | `with` |
| `case` | string | ✅ | German case requirements | `Dativ` |
| `example1` | string_german | ❌ | Complete German sentence | `Ich gehe mit dem Auto.` |
| `example2` | string_german | ❌ | Second example if applicable | `Mit dir ist alles besser.` |

### 7. Additional Word Types
Similar pattern for: adverbs.csv, negations.csv, phrases.csv, personal_pronouns.csv, other_pronouns.csv, conjunctions.csv, interjections.csv, cardinal_numbers.csv, ordinal_numbers.csv

---

# Card Type Specifications

## System Architecture

**Current Architecture**: CSV → Records (dataclass models) → Domain Models (dataclass + MediaGenerationCapable) → MediaEnricher → CardBuilder → AnkiBackend → .apkg

### Implementation Status by Card Type

| Card Type | Sub-deck | Status | Media Support | German Features |
|-----------|----------|--------|---------------|-----------------|
| **Noun** | Nouns | ✅ Active | ✅ Full | Article + plural + cases |
| **Adjective** | Adjectives | ✅ Active | ✅ Full | Comparative/superlative |
| **Adverb** | Adverbs | ✅ Active | ✅ Full | Type classification |
| **Verb** | Verbs | ⚠️ Available | ✅ Full | Conjugations + auxiliary |
| **Verb_Conjugation** | Verbs | ✅ Active | ✅ Full | Multi-tense paradigms |
| **Verb_Imperative** | Verbs | ✅ Active | ✅ Full | Command forms |
| **Preposition** | Prepositions | ✅ Active | ✅ Full | Case requirements |
| **Phrase** | Phrases | ✅ Active | ✅ Full | Context usage |
| **Negation** | Negations | ✅ Active | ✅ Full | Negation patterns |
| **Article Cards** | Articles | ✅ Active | ⚠️ Partial | Cloze deletion + cases |

## German-Specific Card Features

### Noun Cards
- **Front**: English translation + image
- **Back**: German noun with der/die/das + plural form
- **German Features**: Article gender learning, plural irregularities
- **Media**: Contextual images from German example sentences

### Verb Cards
- **Front**: English infinitive + action image
- **Back**: German infinitive + present conjugations (ich/du/er) + classification
- **German Features**: Regular vs irregular patterns, separable verb handling
- **Media**: Action images from German example sentences

### Article Cards (Cloze System)
- **Front**: German sentence with blanked article
- **Back**: Complete sentence + case explanation
- **German Features**: Case recognition practice, gender association
- **Learning Focus**: Der/die/das selection in context

### Adjective Cards
- **Front**: English + descriptive image
- **Back**: German adjective + comparative/superlative forms
- **German Features**: Declension patterns (basic level)
- **Media**: Images showing adjective qualities

## Template System

**German Template Directory**: `src/langlearn/languages/german/templates/`
**Total Templates**: 54 German-specific templates
**Naming Convention**: `{card_type}_{language_code}_{region_code}_{front|back}.html`

### Template Categories
- **Card Templates**: HTML templates for front/back of cards
- **CSS Stylesheets**: German-specific typography and styling
- **Field Mapping**: Template fields match Anki NoteType fields exactly

### German Typography Features
- **Font Support**: German characters (ä, ö, ü, ß) properly rendered
- **Case Highlighting**: Color coding for different grammatical cases
- **Gender Indicators**: Visual cues for der/die/das articles

---

# Implementation Status

## ✅ Completed German Features

**Grammar Coverage**:
- ✅ Complete case system (4 cases × 3 genders + plural)
- ✅ Verb conjugation system (regular, irregular, separable)
- ✅ Article declension system (definite, indefinite, negative)
- ✅ German-specific phonology (AWS Polly Marlene voice)

**Technical Implementation**:
- ✅ 13 German record classes with dataclass validation
- ✅ German domain models with MediaGenerationCapable protocol
- ✅ German-specific card builder and template system
- ✅ MediaEnricher with German linguistic intelligence
- ✅ Complete integration with multi-language architecture

**Data Quality**:
- ✅ 15 CSV files with 500+ German vocabulary items
- ✅ All fields validated against German grammar rules
- ✅ Examples are complete, grammatically correct sentences
- ✅ UTF-8 encoding with proper special character support

## 📋 Current German Vocabulary

**Complete Coverage**:
- **Nouns**: 100+ with articles, plurals, examples
- **Verbs**: 50+ with full conjugation paradigms
- **Adjectives**: 30+ with comparative/superlative forms
- **Articles**: Complete declension patterns for all types
- **Prepositions**: Case requirements and example sentences
- **Other**: Adverbs, negations, phrases, pronouns, conjunctions, numbers

## 🔄 Future Enhancement Opportunities

**Advanced German Grammar**:
- Subjunctive mood (Konjunktiv I/II)
- Advanced verb aspects and modal verbs
- Complex sentence patterns with subordinate clauses
- Regional variations and dialect support

**Extended Vocabulary**:
- B1/B2 level vocabulary expansion
- Technical and professional terminology
- Cultural context and idiomatic expressions
- Audio variations with different German accents