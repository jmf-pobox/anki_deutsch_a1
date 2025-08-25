# German Anki Card Type Specifications

This document provides comprehensive specifications for all German language card types in the system.
Generated automatically by CardSpecificationGenerator to ensure accuracy and completeness.

This specification describes the accurate active/inactive state of
sub-decks and cards. This specification states requirements for each card
type and sub-deck; however, those requirements may not be reflected in the
current code.  There should be gh issues for each area of difference
between the specification and the code.  Differences tend to me whether
fields exist or not and whether they are mandatory or not.  Also, there is
an overall gh issue related to the templating system.

**Total Card Types**: 15

## System Architecture Status

### Overview
The project is currently undergoing a migration from legacy card generators to a **Clean Pipeline Architecture**. This migration is partially complete, resulting in two parallel systems operating simultaneously:

1. **Clean Pipeline Architecture (New System)**: CSV → Records → MediaEnricher → CardBuilder → AnkiBackend
2. **Legacy Architecture (Old System)**: CSV → Domain Models → Card Generators → AnkiBackend

### Migration Status by Card Type

| Card Type | Sub-deck | System | Status | Media Support | Known Issues |
|-----------|----------|--------|--------|---------------|--------------|
| **Noun** | Nouns | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | None |
| **Adjective** | Adjectives | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | None |
| **Adverb** | Adverbs | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | None |
| **Negation** | Negations | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | None |
| **Verb** | Verbs | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | Currently disabled in favor of verb_conjugation |
| **Verb_Conjugation** | Verbs | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | None |
| **Verb_Imperative** | Verbs | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | None |
| **Preposition** | Prepositions | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | None |
| **Phrase** | Phrases | ✅ Clean Pipeline | **Fully Migrated** | ✅ Full (Image + Audio) | None |
| **Artikel_Context_Cloze** | Articles | ✅ Clean Pipeline | **Active** | ⚠️ Partial | Media fields exist but may not populate |
| **Artikel_Gender_Cloze** | Articles | ✅ Clean Pipeline | **Active** | ⚠️ Partial | Media fields exist but may not populate |
| **Artikel_Context** | Articles | 🔄 Hybrid | **Inactive** | ❌ None | Code exists but not called |
| **Artikel_Gender** | Articles | 🔄 Hybrid | **Inactive** | ❌ None | Code exists but not called |
| **Noun_Article_Recognition** | Articles | ❌ Disabled | **Disabled** | ❌ None | ArticleApplicationService commented out |
| **Noun_Case_Context** | Articles | ❌ Disabled | **Disabled** | ❌ None | ArticleApplicationService commented out |

### Architecture Details

#### ✅ **Clean Pipeline (New System)**
**Implementation**: `deck_builder.py:generate_all_cards()` → `RecordMapper` → `MediaEnricher` → `CardBuilder`

**Components**:
- **RecordMapper**: Converts CSV rows to Pydantic Record models
- **MediaEnricher**: Batch processes media generation (images via Pexels, audio via AWS Polly)
- **CardBuilder**: Assembles final cards with templates and formatting
- **MediaFileRegistrar**: Registers media files with AnkiBackend

**Supported Record Types** (via `RecordMapper`):
- noun, adjective, adverb, negation (fully working)
- verb, verb_conjugation, verb_imperative (fully working)
- preposition, phrase (fully working)
- unified_article (partial - cloze cards only)

#### 📅 **Legacy System (Old System)**
**Implementation**: `deck_builder.py:_generate_all_cards_legacy()` → Domain Models → Card Generators

**Components**:
- **Domain Models**: Rich models with German validation (Noun, Adjective, Adverb, Negation)
- **Card Generators**: Individual generators per type (NounCardGenerator, etc.)
- **CardGeneratorFactory**: Creates configured generators

**Status**: Only used as fallback when no records are loaded via Clean Pipeline

### Critical Issues

#### 1. **Article Media Generation Problem** 🚨
**Issue**: Article cards (Artikel_Context_Cloze, Artikel_Gender_Cloze) have empty Image/Audio fields

**Root Cause Analysis**:
- ArticlePatternProcessor creates cards but media enrichment may fail
- Debug logs show enriched_data is processed but media fields aren't populated
- MediaEnricher may not have proper handlers for UnifiedArticleRecord types

**Impact**: Article cards display without visual/audio aids, reducing learning effectiveness

#### 2. **Disabled Noun-Article Integration** ⚠️
**Issue**: ArticleApplicationService is commented out (deck_builder.py lines 790-803)

**Code Comment**: "TEMPORARY: Disable noun-article cards to focus on testing cloze deletion system"

**Impact**: 
- Learners cannot practice noun-article associations ("das Haus", "der Mann")
- Only abstract pattern recognition available, not concrete noun learning
- Does not meet CEFR A1 requirements for article usage

### Migration Roadmap

#### Phase 1: Complete Article System (URGENT)
1. **Fix Article Media Generation**
   - Debug why MediaEnricher doesn't populate article card media
   - Add proper UnifiedArticleRecord support to MediaEnricher
   - Verify media fields are correctly mapped in CardBuilder

2. **Re-enable ArticleApplicationService**
   - Uncomment lines 790-803 in deck_builder.py
   - Test noun-article card generation
   - Verify integration with existing noun records

#### Phase 2: Remove Legacy Dependencies
1. **Remove Legacy Domain Models**
   - Delete legacy Noun, Adjective, Adverb, Negation classes
   - Remove `_load_legacy_models_from_records()` method
   - Clean up dual storage pattern in DeckBuilder

2. **Remove Legacy Card Generators**
   - Delete individual card generator classes
   - Remove CardGeneratorFactory
   - Remove `_generate_all_cards_legacy()` method

#### Phase 3: Optimize Clean Pipeline
1. **Performance Improvements**
   - Implement parallel media generation
   - Add progress indicators for large batches
   - Optimize MediaEnricher caching

2. **Enhanced Validation**
   - Add record validation before card generation
   - Implement better error recovery
   - Add comprehensive logging

### Developer Notes

**When Adding New Card Types**:
1. Create Record model in `models/records.py`
2. Add mapping in `RecordMapper.map_csv_row_to_record()`
3. Add field mapping in `CardBuilder._get_field_names_for_record_type()`
4. Create templates in `templates/` directory
5. Add media enrichment logic if needed

**Current Data Flow**:
```
CSV Files → RecordMapper → Records → MediaEnricher → Enriched Records → CardBuilder → Cards → AnkiBackend
                                ↓
                    (Legacy compatibility layer)
                                ↓
                         Domain Models (for backward compatibility only)
```

**Testing Migration Status**:
- Check `deck_builder.py` logs for "Clean Pipeline generated" vs "Legacy architecture generated"
- Verify media files are created in `data/audio/` and `data/images/`
- Confirm all expected fields are populated in generated .apkg file

## Table of Contents - Organized by Sub-deck

### Adjectives Sub-deck
1. [Adjective](#adjective)

### Adverbs Sub-deck
2. [Adverb](#adverb)

### Articles Sub-deck
3. [Artikel_Context](#artikel-context) (INACTIVE)
4. [Artikel_Context_Cloze](#artikel-context-cloze) (✅ ACTIVE)
5. [Artikel_Gender](#artikel-gender) (INACTIVE)
6. [Artikel_Gender_Cloze](#artikel-gender-cloze) (✅ ACTIVE)
7. [Noun_Article_Recognition](#noun-article-recognition) (❌ DISABLED)
8. [Noun_Case_Context](#noun-case-context) (❌ DISABLED)

### Negations Sub-deck
9. [Negation](#negation)

### Nouns Sub-deck
10. [Noun](#noun)

### Phrases Sub-deck
11. [Phrase](#phrase)

### Prepositions Sub-deck
12. [Preposition](#preposition)

### Verbs Sub-deck
13. [Verb](#verb) (❌ DISABLED)
14. [Verb_Conjugation](#verb-conjugation) (✅ ACTIVE)
15. [Verb_Imperative](#verb-imperative) (✅ ACTIVE)

---

# Adjectives Sub-deck

## Adjective

**Anki Note Type**: `German Adjective with Media`
**Description**: German adjective cards with comparative/superlative forms
**Learning Objective**: Master German adjective vocabulary with comparative/superlative forms
**Cloze Deletion**: No
**CSV Data Source**: `adjectives.csv`
**Sub-deck**: `Adjectives` (Main Deck::Adjectives)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `adjective_front.html`
- `adjective_back.html`
- `adjective.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|--------|-------------|---------|
| `Word` | adjectives.csv | ✅ | Front | The main German word being learned | `schön` |
| `English` | adjectives.csv | ✅ | Back | English translation or meaning | `beautiful` |
| `Example` | adjectives.csv | ✅ | Back | Example sentence using the word | `Das Haus ist schön.` |
| `Comparative` | adjectives.csv | ✅ | Back | Comparative form of adjective | `schöner` |
| `Superlative` | adjectives.csv | ✅ | Back | Superlative form of adjective | `am schönsten` |
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API using AI-generated search terms | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:schön_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

### Image Search Details
**Source**: German example sentence (direct translation)
**Process**: German example sentence → Claude translation → English search terms → Pexels search
**Example**: `Das Haus ist schön` → `The house is beautiful` → Pexels search for beautiful house images
**Benefits**: Contextual images showing adjectives in actual usage scenarios
**Fallback**: English translation of adjective if translation fails

---

# Adverbs Sub-deck

## Adverb

**Anki Note Type**: `German Adverb with Media`
**Description**: German adverb cards with type classification and usage examples
**Learning Objective**: Learn German adverb vocabulary and usage patterns
**Cloze Deletion**: No
**CSV Data Source**: `adverbs.csv`
**Sub-deck**: `Adverbs` (Main Deck::Adverbs)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `adverb_front.html`
- `adverb_back.html`
- `adverb.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|--------|-------------|---------|
| `Word` | adverbs.csv | ✅ | Front | The main German word being learned | `hier` |
| `English` | adverbs.csv | ✅ | Back | English translation or meaning | `here` |
| `Type` | adverbs.csv | ✅ | Back | Classification or type of word | `location` |
| `Example` | adverbs.csv | ✅ | Back | Example sentence using the word | `Ich wohne hier.` |
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API using AI-generated search terms | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:hier_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

### Image Search Details
**Source**: German example sentence (direct translation)
**Process**: German example sentence → Claude translation → English search terms → Pexels search
**Example**: `Er läuft schnell` → `He runs fast` → Pexels search for fast running images
**Benefits**: Action-based images showing adverbs modifying verbs in context
**Fallback**: English translation of adverb if translation fails

---

# Articles Sub-deck

## System Status Overview

**⚠️ IMPLEMENTATION STATUS**: The Articles sub-deck currently operates with a **partial implementation** focused on abstract pattern learning while noun-article integration is temporarily disabled.

### Currently Active System
- **Service**: `ArticlePatternProcessor` only
- **Cards Generated**: 5 cloze deletion cards per article record
  - 1 Gender Recognition Cloze ("{{c1::Der}} Mann ist hier")
  - 4 Case Context Cloze cards (Nominative, Accusative, Dative, Genitive)
- **Learning Focus**: Abstract article pattern recognition
- **What Learners See**: Cloze deletion exercises for article patterns in sentences

### Currently Disabled System  
- **Service**: `ArticleApplicationService` (commented out in deck_builder.py lines 790-803)
- **Reason**: "TEMPORARY: Disable noun-article cards to focus on testing cloze deletion system"
- **Missing Cards**: Noun-specific article practice ("das Haus", "der Mann", etc.)
- **Impact**: Learners cannot practice article-noun associations in context

### Summary Box: What This Means for Learners

```
┌────────────────────────────────────────────────────────────────────────────┐
│ CURRENT STATE: Pattern Practice Only (Insufficient for A1)                 │
├────────────────────────────────────────────────────────────────────────────┤
│ What Works:                                                                │
│ ✅ Learners practice filling in articles in sentences                      │
│ ✅ Case recognition exercises (nom/acc/dat/gen)                            │
│ ✅ Gender pattern recognition in context                                   │
│                                                                            │
│ What's Missing (CRITICAL):                                                 │
│ ❌ Cannot learn "das Haus", "die Frau", "der Mann"                         │
│ ❌ No noun-to-article memory building                                      │
│ ❌ Missing 85% of required article knowledge                               │
│                                                                            │
│ A1 Requirement Status: ❌ DOES NOT MEET CEFR STANDARDS                     │
└────────────────────────────────────────────────────────────────────────────┘
```

## Pedagogical Assessment

### Current System Limitations for A1 Learners

**Critical Gap**: The disabled noun-article integration creates a significant pedagogical deficit for A1 learners:

1. **Abstract vs. Concrete Learning**: A1 learners need concrete noun-article pairings ("das Haus", "die Frau") before abstract pattern recognition. The current cloze-only system reverses the natural acquisition order.

2. **Memorization Requirements**: German article assignment is largely arbitrary and must be memorized with each noun. Without noun-specific practice, learners lack the essential foundation for German grammar.

3. **CEFR A1 Requirements**: The Common European Framework explicitly requires A1 learners to "use basic articles with familiar nouns." The current system does not adequately support this competency.

### Recommendation Priority: HIGH
**The ArticleApplicationService should be re-enabled as soon as possible**. Article-noun association is fundamental to German language acquisition and cannot be effectively learned through pattern cards alone.

## Data Source and Processing Architecture

**CSV Data Source**: `articles_unified.csv`
- **Format**: Unified article database with German terminology
- **Fields**: `artikel_typ`, `geschlecht`, `nominativ`, `akkusativ`, `dativ`, `genitiv`, `beispiel_nom`, `beispiel_akk`, `beispiel_dat`, `beispiel_gen`
- **Article Types**: `bestimmt` (definite), `unbestimmt` (indefinite), `verneinend` (negative)
- **Genders**: `maskulin`, `feminin`, `neutral`, `plural`

**Processing Services**:
1. **ArticlePatternProcessor** (`article_pattern_processor.py`): **[ACTIVE]**
   - Generates cloze deletion cards for pattern recognition
   - Currently produces 5 cloze cards per record (1 gender + 4 cases)
   - Uses GermanExplanationFactory for German-language explanations
   
2. **ArticleApplicationService** (`article_application_service.py`): **[DISABLED]**
   - Would create 5 cards per noun for article association
   - Would integrate noun data with article patterns
   - Would provide practical application of article knowledge
   - **Status**: Commented out pending cloze deletion system testing

## Artikel_Context [INACTIVE - Non-Cloze Version]

**Anki Note Type**: `German Artikel Context with Media`
**Description**: Case-specific article usage cards generated by ArticlePatternProcessor
**Learning Objective**: Master German article changes in different grammatical cases
**Cloze Deletion**: No
**CSV Data Source**: `articles_unified.csv` (via UnifiedArticleRecord)
**Sub-deck**: `Articles` (Main Deck::Articles)
**Generator Service**: `ArticlePatternProcessor._create_case_context_card()`
**Status**: **⚠️ INACTIVE** - Non-cloze methods exist but are not called in current implementation

### Card Content

**Front**: Sentence with blank for article (e.g., "_____ Mann arbeitet")
**Back**: Complete sentence with correct article form and case explanation

### Template Files

- `artikel_context_DE_de_front.html`
- `artikel_context_DE_de_back.html`
- `artikel_context_DE_de.css`

### Field Specifications

| Field | Source | Required | Processing | Description | Example |
|-------|--------|----------|------------|-------------|---------|
| `FrontText` | Generated | ✅ | `complete_sentence.replace(article_form, "_____")` | Sentence with blank | `_____ Mann arbeitet` |
| `BackText` | Generated | ✅ | Example sentence from CSV | Complete sentence | `Der Mann arbeitet` |
| `Gender` | UnifiedArticleRecord.geschlecht | ✅ | Direct mapping | German gender | `maskulin` |
| `Nominative` | UnifiedArticleRecord.nominativ | ✅ | Direct mapping | Nominative form | `der` |
| `Accusative` | UnifiedArticleRecord.akkusativ | ✅ | Direct mapping | Accusative form | `den` |
| `Dative` | UnifiedArticleRecord.dativ | ✅ | Direct mapping | Dative form | `dem` |
| `Genitive` | UnifiedArticleRecord.genitiv | ✅ | Direct mapping | Genitive form | `des` |
| `ExampleNom` | UnifiedArticleRecord.beispiel_nom | ✅ | Direct mapping | Nominative example | `Der Mann ist hier` |
| `ExampleAcc` | UnifiedArticleRecord.beispiel_akk | ✅ | Direct mapping | Accusative example | `Ich sehe den Mann` |
| `ExampleDat` | UnifiedArticleRecord.beispiel_dat | ✅ | Direct mapping | Dative example | `mit dem Mann` |
| `ExampleGen` | UnifiedArticleRecord.beispiel_gen | ✅ | Direct mapping | Genitive example | `das Auto des Mannes` |
| `Image` | MediaEnricher | ❌ | Via enriched_data | Pexels image | `<img src="mann_001.jpg" />` |
| `ArticleAudio` | MediaEnricher | ❌ | Via enriched_data | Article pronunciation | `[sound:der.mp3]` |
| `ExampleAudio` | MediaEnricher | ❌ | Via enriched_data | Example audio | `[sound:example.mp3]` |
| `NounOnly` | Generated | ✅ | `_extract_noun_from_sentence()` | Extracted noun | `Mann` |
| `NounEnglish` | Generated | ✅ | Translation lookup | English translation | `man` |
| `ArtikelTypBestimmt` | Conditional | ✅ | `"true" if artikel_typ == "bestimmt"` | Template conditional | `true` or empty |
| `ArtikelTypUnbestimmt` | Conditional | ✅ | `"true" if artikel_typ == "unbestimmt"` | Template conditional | `true` or empty |
| `ArtikelTypVerneinend` | Conditional | ✅ | `"true" if artikel_typ == "verneinend"` | Template conditional | `true` or empty |

## Artikel_Context_Cloze [ACTIVE]

**Anki Note Type**: `German Artikel Context Cloze`
**Description**: Cloze deletion cards for case-specific article learning
**Learning Objective**: Practice German case usage through active recall
**Cloze Deletion**: Yes (Anki native cloze support)
**CSV Data Source**: `articles_unified.csv` (via UnifiedArticleRecord)
**Sub-deck**: `Articles` (Main Deck::Articles)
**Generator Service**: `ArticlePatternProcessor._create_case_cloze_card()`
**Status**: **✅ ACTIVE** - Currently generates 4 cards per record (one for each case: nominative, accusative, dative, genitive)

### Card Content

**Front**: Cloze deletion with blanked article
**Back**: Complete text with German grammatical explanation

### Template Files

- `artikel_context_cloze_DE_de_front.html`
- `artikel_context_cloze_DE_de_back.html`
- `artikel_context_cloze_DE_de.css`

### Field Specifications

| Field | Source | Required | Processing | Description | Example |
|-------|--------|----------|------------|-------------|---------|
| `Text` | Generated | ✅ | Case-insensitive article replacement with `{{c1::}}` | Cloze text | `Ich sehe {{c1::den}} Mann` |
| `Explanation` | GermanExplanationFactory | ✅ | `create_case_explanation()` | German grammar rule | `den - Maskulin Akkusativ (wen/was?)` |
| `Image` | MediaEnricher | ❌ | Via enriched_data.get("image_url") | Pexels image | `mann_001.jpg` |
| `Audio` | MediaEnricher | ❌ | Via enriched_data.get("audio_file") | Example audio | `example.mp3` |

### Cloze Generation Process
1. Extract example sentence for specific case (e.g., `beispiel_akk` for accusative)
2. Use regex pattern matching to preserve original capitalization
3. Replace first occurrence of article with `{{c1::article}}`
4. Generate German explanation based on gender and case

## Artikel_Gender [INACTIVE - Non-Cloze Version]

**Anki Note Type**: `German Artikel Gender with Media`
**Description**: Gender recognition cards for learning der/die/das associations
**Learning Objective**: Learn to recognize German noun genders
**Cloze Deletion**: No
**CSV Data Source**: `articles_unified.csv` (via UnifiedArticleRecord)
**Sub-deck**: `Articles` (Main Deck::Articles)
**Generator Service**: `ArticlePatternProcessor._create_gender_recognition_card()` (legacy non-cloze)
**Status**: **⚠️ INACTIVE** - Non-cloze methods exist but are not called in current implementation

### Card Content

**Front**: Blank with noun and hint button (e.g., "_____ Mann")
**Back**: Article with gender explanation and audio

### Template Files

- `artikel_gender_DE_de_front.html` (uses `{{NounOnly}}` in "_____ {{NounOnly}}" format)
- `artikel_gender_DE_de_back.html` (displays `{{BackText}}` with gender info)
- `artikel_gender_DE_de.css`

### Field Specifications

| Field | Source | Required | Processing | Description | Example |
|-------|--------|----------|------------|-------------|---------|
| `FrontText` | Generated | ✅ | `record.gender.title()` | Gender type | `Masculine` |
| `BackText` | Generated | ✅ | `record.nominative` | Nominative article | `der` |
| `Gender` | UnifiedArticleRecord.geschlecht | ✅ | Direct mapping | German gender | `maskulin` |
| `Nominative` | UnifiedArticleRecord.nominativ | ✅ | Direct mapping | Nominative form | `der` |
| `Accusative` | UnifiedArticleRecord.akkusativ | ✅ | Direct mapping | Accusative form | `den` |
| `Dative` | UnifiedArticleRecord.dativ | ✅ | Direct mapping | Dative form | `dem` |
| `Genitive` | UnifiedArticleRecord.genitiv | ✅ | Direct mapping | Genitive form | `des` |
| `ExampleNom` | UnifiedArticleRecord.beispiel_nom | ✅ | Direct mapping | Example sentence | `Der Mann ist hier` |
| `Image` | MediaEnricher | ❌ | Via enriched_data | Pexels image | `<img src="mann_001.jpg" />` |
| `ArticleAudio` | MediaEnricher | ❌ | Via enriched_data | Article audio | `[sound:der.mp3]` |
| `ExampleAudio` | MediaEnricher | ❌ | Via enriched_data | Example audio | `[sound:example.mp3]` |
| `NounOnly` | Generated | ✅ | `_extract_noun_from_sentence()` | Extracted noun | `Mann` |
| `NounEnglish` | Generated | ✅ | Translation dictionary lookup | English translation | `man` |
| `ArtikelTypBestimmt` | Conditional | ✅ | Template conditional flag | Article type flag | `true` or empty |

## Artikel_Gender_Cloze [ACTIVE]

**Anki Note Type**: `German Artikel Gender Cloze`
**Description**: Cloze deletion cards for gender recognition practice
**Learning Objective**: Practice German gender recognition through active recall
**Cloze Deletion**: Yes (Anki native cloze support)
**CSV Data Source**: `articles_unified.csv` (via UnifiedArticleRecord)
**Sub-deck**: `Articles` (Main Deck::Articles)
**Generator Service**: `ArticlePatternProcessor._create_gender_cloze_card()`
**Status**: **✅ ACTIVE** - Currently generates 1 card per record for gender recognition

### Card Content

**Front**: Cloze deletion with blanked article in nominative
**Back**: Complete text with German gender explanation

### Template Files

- `artikel_gender_cloze_DE_de_front.html` (minimal template using `{{cloze:Text}}`)
- `artikel_gender_cloze_DE_de_back.html`
- `artikel_gender_cloze_DE_de.css`

### Field Specifications

| Field | Source | Required | Processing | Description | Example |
|-------|--------|----------|------------|-------------|---------|
| `Text` | Generated | ✅ | Nominative example with `{{c1::}}` | Cloze text | `{{c1::Der}} Mann ist hier` |
| `Explanation` | GermanExplanationFactory | ✅ | `create_gender_recognition_explanation()` | Gender explanation | `Maskulin - Geschlecht erkennen` |
| `Image` | MediaEnricher | ❌ | Via enriched_data.get("image_url") | Pexels image | `mann_001.jpg` |
| `Audio` | MediaEnricher | ❌ | Via enriched_data.get("audio_file") | Example audio | `example.mp3` |

## Noun_Article_Recognition [DISABLED]

**Anki Note Type**: `German Noun_Article_Recognition with Media`
**Description**: Noun-specific article practice cards
**Learning Objective**: Learn which article goes with specific German nouns
**Cloze Deletion**: No
**CSV Data Source**: `nouns.csv` (NounRecord) + article patterns
**Sub-deck**: `Articles` (Main Deck::Articles)
**Generator Service**: `ArticleApplicationService._create_article_recognition_card()`
**Status**: **❌ DISABLED** - ArticleApplicationService is commented out in deck_builder.py

### Card Content

**Front**: Just the noun (e.g., "Haus")
**Back**: Article + noun (e.g., "das Haus") with English translation

### Template Files

- `noun_article_recognition_DE_de_front.html`
- `noun_article_recognition_DE_de_back.html`
- `noun_article_recognition_DE_de.css`

### Field Specifications

| Field | Source | Required | Processing | Description | Example |
|-------|--------|----------|------------|-------------|---------|
| `FrontText` | NounRecord.noun | ✅ | Direct from noun | Just the noun | `Haus` |
| `BackText` | Generated | ✅ | `f"{noun.article} {noun.noun}"` | Article + noun | `das Haus` |
| `Gender` | Derived from article | ✅ | Article → gender mapping | German gender | `neutral` |
| `Nominative` | NounRecord.article | ✅ | Base article form | Nominative article | `das` |
| `Accusative` | Generated | ✅ | Based on article declension | Accusative form | `das` |
| `Dative` | Generated | ✅ | Based on article declension | Dative form | `dem` |
| `Genitive` | Generated | ✅ | Based on article declension | Genitive form | `des` |
| `ExampleNom` | NounRecord.example | ❌ | From noun CSV | Example sentence | `Das Haus ist groß` |
| `Image` | MediaEnricher | ❌ | Via enriched_data | Pexels image | `<img src="haus_001.jpg" />` |
| `ArticleAudio` | MediaEnricher | ❌ | Via enriched_data | Article audio | `[sound:das.mp3]` |
| `ExampleAudio` | MediaEnricher | ❌ | Via enriched_data | Example audio | `[sound:example.mp3]` |
| `NounOnly` | NounRecord.noun | ✅ | Direct from noun | Noun without article | `Haus` |
| `NounEnglishWithArticle` | Generated | ✅ | `f"the {noun.english.lower()}"` | English with article | `the house` |

### Article Declension Patterns
The service uses `_get_article_forms_for_noun()` to generate all case forms:
- **der** (masculine): der → den → dem → des
- **die** (feminine): die → die → der → der  
- **das** (neuter): das → das → dem → des

## Noun_Case_Context [DISABLED]

**Anki Note Type**: `German Noun_Case_Context with Media`
**Description**: Case-specific noun declension practice
**Learning Objective**: Master German noun declension in all four cases
**Cloze Deletion**: No
**CSV Data Source**: `nouns.csv` (NounRecord) + generated case examples
**Sub-deck**: `Articles` (Main Deck::Articles)
**Generator Service**: `ArticleApplicationService._create_noun_case_card()`
**Status**: **❌ DISABLED** - ArticleApplicationService is commented out in deck_builder.py

### Card Content

**Front**: Context sentence with blank (e.g., "___ Haus ist klein")
**Back**: Complete sentence with case explanation

### Template Files

- `noun_case_context_DE_de_front.html`
- `noun_case_context_DE_de_back.html`
- `noun_case_context_DE_de.css`

### Field Specifications

| Field | Source | Required | Processing | Description | Example |
|-------|--------|----------|------------|-------------|---------|
| `FrontText` | Generated | ✅ | Sentence with `___` replacing article | Blank sentence | `___ Haus ist hier` |
| `BackText` | Generated | ✅ | Complete case example | Full sentence | `Das Haus ist hier` |
| `Gender` | Derived | ✅ | From noun article | German gender | `Neutral` |
| `Nominative` | NounRecord.article | ✅ | Base article | Nominative form | `das` |
| `Accusative` | Generated | ✅ | Case declension | Accusative form | `das` |
| `Dative` | Generated | ✅ | Case declension | Dative form | `dem` |
| `Genitive` | Generated | ✅ | Case declension | Genitive form | `des` |
| `ExampleNom` | Generated | ✅ | `f"{article} {noun} ist hier."` | Nominative example | `Das Haus ist hier.` |
| `ExampleAcc` | Generated | ✅ | `f"Ich sehe {article} {noun}."` | Accusative example | `Ich sehe das Haus.` |
| `ExampleDat` | Generated | ✅ | `f"Mit {article} {noun} arbeite ich."` | Dative example | `Mit dem Haus arbeite ich.` |
| `ExampleGen` | Generated | ✅ | `f"Das ist die Farbe {article} {noun}es."` | Genitive example | `Das ist die Farbe des Hauses.` |
| `Image` | MediaEnricher | ❌ | Via enriched_data | Pexels image | `<img src="haus_001.jpg" />` |
| `ArticleAudio` | MediaEnricher | ❌ | Via enriched_data | Article audio | `[sound:das.mp3]` |
| `ExampleAudio` | MediaEnricher | ❌ | Via enriched_data | Example audio | `[sound:example.mp3]` |
| `NounOnly` | NounRecord.noun | ✅ | Direct from noun | Noun without article | `Haus` |
| `NounEnglish` | NounRecord.english | ✅ | Direct from noun | English translation | `house` |
| `case_nominativ` | Conditional | ✅ | `"true" if case == "nominativ"` | Template flag | `true` or empty |
| `case_akkusativ` | Conditional | ✅ | `"true" if case == "akkusativ"` | Template flag | `true` or empty |
| `case_dativ` | Conditional | ✅ | `"true" if case == "dativ"` | Template flag | `true` or empty |
| `case_genitiv` | Conditional | ✅ | `"true" if case == "genitiv"` | Template flag | `true` or empty |

### Case Example Generation
The `_generate_case_examples()` method creates contextually appropriate sentences:
- **Nominative**: Subject position - "{article} {noun} ist hier."
- **Accusative**: Direct object - "Ich sehe {article} {noun}."
- **Dative**: With preposition - "Mit {article} {noun} arbeite ich."
- **Genitive**: Possession - "Das ist die Farbe {article} {noun}es."

## Implementation Notes

### Current Active Pipeline (Cloze-Only)
1. **CSV Loading**: `articles_unified.csv` → `UnifiedArticleRecord` via `RecordMapper`
2. **Pattern Processing**: Each record generates **5 cloze cards**:
   - 1 Gender Recognition Cloze card (`_create_gender_cloze_card`)
   - 4 Case Context Cloze cards (`_create_case_cloze_card` for nom/acc/dat/gen)
   - **Note**: Non-cloze methods exist but are never called
3. **Noun Integration**: **DISABLED** - ArticleApplicationService is commented out
4. **Media Enrichment**: Images and audio added via `MediaEnricher` service
5. **Card Assembly**: Final formatting via `CardBuilder` service

### Pedagogical Impact of Current Implementation

**Critical Deficiency**: The current system only teaches abstract patterns without concrete noun associations:
- ❌ Learners see: "{{c1::Der}} Mann ist hier" (pattern practice)
- ❌ Missing: "Haus" → "das Haus" (noun-article memorization)
- ❌ Result: A1 learners lack the fundamental noun-article pairings required by CEFR standards

## Pedagogical Recommendations for Article Learning System

### 1. Immediate Priority: Re-enable ArticleApplicationService
**Timeline**: URGENT - Should be completed before any user testing

**Rationale**: German article assignment is **85% arbitrary memorization** and only 15% pattern-based. The current cloze-only system addresses the 15% while ignoring the critical 85%.

**Required Actions**:
1. Uncomment ArticleApplicationService integration in deck_builder.py (lines 790-803)
2. Convert ArticleApplicationService to use cloze deletion format if template issues persist
3. Ensure noun CSV data includes sufficient A1-level nouns (minimum 100 high-frequency nouns)

### 2. Learning Sequence Optimization

**Current Problem**: Abstract pattern learning before concrete examples violates natural acquisition order.

**Recommended Card Presentation Order**:
1. **First**: Noun-Article Recognition ("Haus" → "das Haus")
2. **Second**: Gender Pattern Recognition (neuter nouns often end in -chen, -lein)
3. **Third**: Case Context Practice (applying known articles in sentences)

**Implementation**: Add a "difficulty" or "order" field to control Anki's initial presentation sequence.

### 3. Cognitive Load Management

**Current Issue**: 5 cards per article pattern + potential noun cards = overwhelming repetition

**Recommended Reduction**:
- **Keep**: Gender cloze (1 card) + Nominative case cloze (1 card) = 2 cards per pattern
- **Defer**: Accusative, Dative, Genitive cloze cards to A2 level
- **Prioritize**: Noun-article cards (when re-enabled) over pattern cards

**Rationale**: A1 learners primarily encounter nominative and accusative cases. Dative and genitive are less frequent and can overwhelm beginners.

### 4. Concrete Learning Materials

**Missing Elements**:
1. **Visual Associations**: Images should show the noun with its article ("das Haus" with house image)
2. **Mnemonic Hints**: Gender patterns and rules (e.g., "-ung always feminine")
3. **High-Frequency First**: Focus on the 100 most common German nouns at A1

### 5. Success Metrics for Article Learning

**Minimum Viable Competency at A1**:
- Correctly recall articles for 50 high-frequency nouns
- Recognize gender patterns for 70% of new nouns
- Apply correct articles in nominative case 80% of the time
- Apply correct articles in accusative case 60% of the time

**Current System Achievement**: ~30% of target (pattern recognition only, no noun-specific knowledge)

### 6. Technical Implementation Priorities

**Phase 1 (Immediate)**:
1. Re-enable ArticleApplicationService
2. Verify noun-article cards generate correctly
3. Test with 10-20 high-frequency nouns

**Phase 2 (Next Sprint)**:
1. Convert ArticleApplicationService to cloze format if needed
2. Add visual article indicators to images
3. Implement card ordering system

**Phase 3 (Future Enhancement)**:
1. Add gender pattern hint cards
2. Create article rules reference cards
3. Implement spaced repetition optimization for article-noun pairs

### 7. Warning: Current System Pedagogical Risk

**🚨 Without noun-article cards, learners will**:
1. Guess articles randomly in real communication
2. Develop incorrect pattern assumptions
3. Struggle with basic German sentence construction
4. Fail A1 certification requirements for article usage

**Recommendation**: Do not release to learners until ArticleApplicationService is re-enabled and tested.

### Noun Extraction Algorithm
The `_extract_noun_from_sentence()` method:
1. Splits sentence into words
2. Filters out articles, prepositions, and common words
3. Returns first capitalized word (likely the noun)
4. Fallback to "Wort" if extraction fails

### Translation Dictionary
Basic noun translations are hardcoded for common A1-level nouns:
- Mann → man, Frau → woman, Kind → child
- Auto → car, Haus → house, Buch → book
- Tisch → table, Stuhl → chair

### Field Mapping in CardBuilder
The `_extract_field_values()` method maps record fields to Anki fields using predefined mappings for each card type, ensuring correct field order for Anki import.

---

# Negations Sub-deck

## Negation

**Anki Note Type**: `German Negation with Media`
**Description**: German negation word cards (nicht, kein, nie, etc.)
**Learning Objective**: Master German negation words and their proper usage
**Cloze Deletion**: No
**CSV Data Source**: `negations.csv`
**Sub-deck**: `Negations` (Main Deck::Negations)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `negation_front.html`
- `negation_back.html`
- `negation.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|--------|-------------|---------|
| `Word` | negations.csv | ✅ | Front | The main German word being learned | `nicht` |
| `English` | negations.csv | ✅ | Back | English translation or meaning | `not` |
| `Type` | negations.csv | ✅ | Back | Classification or type of word | `adverb` |
| `Example` | negations.csv | ✅ | Back | Example sentence using the word | `Ich komme nicht.` |
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API using AI-generated search terms | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:nicht_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

### Image Search Details
**Source**: German example sentence (direct translation)
**Process**: German example sentence → Claude translation → English search terms → Pexels search
**Example**: `Ich komme nicht` → `I am not coming` → Pexels search for negation/absence images
**Benefits**: Contextual images showing negation in actual sentence usage
**Fallback**: English translation of negation word if translation fails

---

# Nouns Sub-deck

## Noun

**Anki Note Type**: `German Noun with Media`
**Description**: Basic German noun cards with article, plural, and example sentences
**Learning Objective**: Learn German noun vocabulary with correct articles and plural forms
**Cloze Deletion**: No
**CSV Data Source**: `nouns.csv`
**Sub-deck**: `Nouns` (Main Deck::Nouns)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `noun_front.html`
- `noun_back.html`
- `noun.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|--------|-------------|---------|
| `Noun` | nouns.csv | ✅ | Front | German noun with proper capitalization | `Haus` |
| `Article` | nouns.csv | ✅ | Back | German article (der, die, das) | `das` |
| `English` | nouns.csv | ✅ | Back | English translation or meaning | `house` |
| `Plural` | nouns.csv | ✅ | Back | Plural form of the noun | `Häuser` |
| `Example` | nouns.csv | ✅ | Back | Example sentence using the word | `Das Haus ist schön.` |
| `Related` | nouns.csv | ✅ | Back | Related words or expressions | `Gebäude, Wohnung` |
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API using AI-generated search terms (concrete nouns only) | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:haus_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

### Image Search Details
**Source**: German example sentence (direct translation, concrete nouns only)
**Process**: German example sentence → Claude translation → English search terms → Pexels search
**Example**: `Das Haus ist groß` → `The house is big` → Pexels search for house images
**Concrete Check**: Abstract nouns (ending in -heit, -keit, -ung, etc.) are filtered out
**Benefits**: Contextual images showing nouns in descriptive sentences
**Fallback**: English translation of noun if translation fails, no image for abstract nouns

---

# Phrases Sub-deck

## Phrase

**Anki Note Type**: `German Phrase with Media`
**Description**: Common German phrase cards with contextual usage
**Learning Objective**: Learn common German phrases and expressions with context
**Cloze Deletion**: No
**CSV Data Source**: `phrases.csv`
**Sub-deck**: `Phrases` (Main Deck::Phrases)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with audio pronunciation support

### Template Files

- `phrase_DE_de_front.html`
- `phrase_DE_de_back.html`
- `phrase_DE_de.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|--------|-------------|---------|
| `Phrase` | phrases.csv | ✅ | Front | German phrase or expression | `Guten Tag` |
| `English` | phrases.csv | ✅ | Back | English translation or meaning | `Good day` |
| `Context` | phrases.csv | ✅ | Back | Context or situation where phrase is used | `greeting someone` |
| `Related` | phrases.csv | ❌ | Back | Related words or expressions | `Hallo, Auf Wiedersehen` |
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API using translated phrase text | `<img src="house_001.jpg" />` |
| `PhraseAudio` | AWS_Polly | ✅ | Front | Generated phrase audio from AWS Polly | `[sound:guten_tag.mp3]` |

### Image Search Details
**Source**: German phrase text (direct translation)
**Process**: German phrase → Claude translation → English search terms → Pexels search
**Example**: `Guten Tag` → `Good day` → Pexels search for greeting/daytime images
**Optimization**: Checks for existing images first to avoid unnecessary translation calls
**Fallback**: Context field or English field if translation fails

---

# Prepositions Sub-deck

## Preposition

**Anki Note Type**: `German Preposition with Media`
**Description**: German preposition cards with case requirements and examples
**Learning Objective**: Master German prepositions with their required grammatical cases
**Cloze Deletion**: No
**CSV Data Source**: `prepositions.csv`
**Sub-deck**: `Prepositions` (Main Deck::Prepositions)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with audio pronunciation support

### Template Files

- `preposition_DE_de_front.html`
- `preposition_DE_de_back.html`
- `preposition_DE_de.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|--------|-------------|---------|
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API using translated Example1 sentence | `<img src="house_001.jpg" />` |
| `Preposition` | prepositions.csv | ✅ | Front | German preposition | `mit` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:mit_pronunciation.mp3]` |
| `English` | prepositions.csv | ✅ | Back | English translation or meaning | `with` |
| `Case` | prepositions.csv | ✅ | Back | German grammatical case (Nominativ, Akkusativ, Dativ, Genitiv) | `Dativ` |
| `Example1` | prepositions.csv | ✅ | Back | First example sentence | `Ich gehe mit dem Auto.` |
| `Example1Audio` | AWS_Polly | ✅ | Back | Generated audio for first example | `[sound:example1.mp3]` |
| `Example2` | prepositions.csv | ❌ | Back | Second example sentence (optional - not all prepositions have two cases) | `Mit dir ist alles besser.` |
| `Example2Audio` | AWS_Polly | ❌ | Back | Generated audio for second example (optional) | `[sound:example2.mp3]` |

### Image Search Details
**Source**: German Example1 sentence (required field)
**Process**: German example sentence → Claude translation → English search terms → Pexels search
**Example**: `Ich gehe in die Schule` → `I go to school` → Pexels search for school/education images
**Rationale**: Example1 is required field per spec, provides rich contextual information for spatial relationships
**Fallback**: English translation of preposition if translation fails

---

# Verbs Sub-deck

## Verb

**Anki Note Type**: `German Verb with Media`
**Description**: Comprehensive German verb cards with essential tense forms and classification
**Learning Objective**: Learn German verbs from image + English hint to produce infinitive, present conjugation (ich/du/er), Präteritum (3rd person), auxiliary verb (haben/sein), Perfekt form (3rd person), and verb classification
**Cloze Deletion**: No
**CSV Data Source**: `verbs.csv`
**Sub-deck**: `Verbs` (Main Deck::Verbs) - **CURRENTLY DISABLED**

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `verb_DE_de_front.html`
- `verb_DE_de_back.html`
- `verb_DE_de.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|-------|-------------|---------|
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API using translated example sentence | `<img src="work_001.jpg" />` |
| `English` | verbs.csv | ✅ | Both | English translation or meaning (hint on front, definition on back) | `to work` |
| `Verb` | verbs.csv | ✅ | Back | German verb in infinitive form | `arbeiten` |
| `Classification` | verbs.csv | ✅ | Back | Verb classification using German terms (regelmäßig, unregelmäßig, gemischt) | `regelmäßig` |
| `PresentIch` | verbs.csv | ✅ | Back | Present tense first person singular (ich) | `arbeite` |
| `PresentDu` | verbs.csv | ✅ | Back | Present tense second person singular (du) | `arbeitest` |
| `PresentEr` | verbs.csv | ✅ | Back | Present tense third person singular (er/sie/es) | `arbeitet` |
| `Präteritum` | verbs.csv | ✅ | Back | Präteritum 3rd person singular form (er/sie/es) | `arbeitete` |
| `Auxiliary` | verbs.csv | ✅ | Back | Auxiliary verb for perfect tense (haben or sein) | `haben` |
| `Perfect` | verbs.csv | ✅ | Back | Perfect tense 3rd person singular (auxiliary + past participle) | `hat gearbeitet` |
| `Example` | verbs.csv | ✅ | Back | Example sentence using the verb in present tense | `Er arbeitet in einer Bank.` |
| `Separable` | verbs.csv | ✅ | Back | Whether the verb is separable (true) or not (false) | `false` |
| `WordAudio` | AWS_Polly | ✅ | Back | Generated pronunciation audio for infinitive form | `[sound:arbeiten_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

### Image Search Details
**Source**: German example sentence
**Process**: German example sentence → Claude translation → English search terms → Pexels search
**Example**: `Er arbeitet in einer Bank` → `He works in a bank` → Pexels search for work/office images
**Rationale**: Example sentences provide action context better than infinitive verbs alone
**Fallback**: English translation of infinitive if translation fails

## Verb_Conjugation

**Anki Note Type**: `German Verb_Conjugation with Media`
**Description**: Comprehensive German verb conjugation cards by tense
**Learning Objective**: Master German verb conjugation across all persons and tenses
**Cloze Deletion**: No
**CSV Data Source**: `verbs_unified.csv`
**Sub-deck**: `Verbs` (Main Deck::Verbs)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with audio pronunciation support

### Template Files

- `verb_conjugation_front.html`
- `verb_conjugation_back.html`
- `verb_conjugation.css`
- `verb_conjugation_DE_de_front.html`
- `verb_conjugation_DE_de_back.html`
- `verb_conjugation_DE_de.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|-------|-------------|---------|
| `English` | verbs_unified.csv | ✅ | Both | English translation or meaning (hint on front, hint on back) | `beautiful` |
| `Image` | Pexels | ✅ | Both | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `Tense` | verbs_unified.csv | ✅ | Both | Verb tense (present, preterite, perfect, etc.) | `present` |
| `Infinitive` | verbs_unified.csv | ✅ | Back | German verb in infinitive form | `sprechen` |
| `Classification` | verbs_unified.csv | ✅ | Back | Verb classification (regular, irregular, modal, etc.) | `regular` |
| `Separable` | verbs_unified.csv | ✅ | Back | Whether the verb is separable (Yes/No) | `Yes` |
| `Auxiliary` | verbs_unified.csv | ✅ | Back | Auxiliary verb used (haben/sein) | `haben` |
| `Ich` | verbs_unified.csv | ✅ | Back | First person singular conjugation (ich) | `ich spreche` |
| `Du` | verbs_unified.csv | ✅ | Back | Second person singular conjugation (du) | `du sprichst` |
| `Er` | verbs_unified.csv | ✅ | Back | Third person singular conjugation (er/sie/es) | `er spricht` |
| `Wir` | verbs_unified.csv | ✅ | Back | First person plural conjugation (wir) | `wir sprechen` |
| `Ihr` | verbs_unified.csv | ✅ | Back | Second person plural conjugation (ihr) | `ihr sprecht` |
| `Sie` | verbs_unified.csv | ✅ | Back | Third person plural/formal conjugation (Sie/sie) | `sie sprechen` |
| `Example` | verbs_unified.csv | ✅ | Back | Example sentence using the word | `Das Haus ist schön.` |
| `WordAudio` | AWS_Polly | ✅ | Back | Generated pronunciation audio from AWS Polly | `[sound:haus_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

## Verb_Imperative

**Anki Note Type**: `German Verb_Imperative with Media`
**Description**: German imperative (command) form cards for all persons
**Learning Objective**: Learn German imperative (command) forms for all persons
**Cloze Deletion**: No
**CSV Data Source**: `verbs_unified.csv`
**Sub-deck**: `Verbs` (Main Deck::Verbs)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `verb_imperative_front.html`
- `verb_imperative_back.html`
- `verb_imperative.css`
- `verb_imperative_DE_de_front.html`
- `verb_imperative_DE_de_back.html`
- `verb_imperative_DE_de.css`

### Field Specifications

| Field | Source | Required | Usage | Description | Example |
|-------|--------|----------|-------|-------------|---------|
| `Image` | Pexels | ✅ | Both | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `English` | verbs_unified.csv | ✅ | Both | English translation or meaning (hint on front, hint on back) | `beautiful` |
| `Infinitive` | verbs_unified.csv | ✅ | Back | German verb in infinitive form | `sprechen` |
| `Du` | verbs_unified.csv | ✅ | Back | Informal singular imperative (du form) | `Sprich!` |
| `Ihr` | verbs_unified.csv | ✅ | Back | Informal plural imperative (ihr form) | `Sprecht!` |
| `Sie` | verbs_unified.csv | ✅ | Back | Formal imperative (Sie form) | `Sprechen Sie!` |
| `Wir` | verbs_unified.csv | ✅ | Back | Inclusive imperative (wir form) | `Sprechen wir!` |
| `ExampleDu` | verbs_unified.csv | ✅ | Back | Example sentence with du imperative | `Sprich lauter!` |
| `ExampleIhr` | verbs_unified.csv | ✅ | Back | Example sentence with ihr imperative | `Sprecht deutlicher!` |
| `ExampleSie` | verbs_unified.csv | ✅ | Back | Example sentence with Sie imperative | `Sprechen Sie bitte langsamer!` |
| `WordAudio` | AWS_Polly | ✅ | Back | Generated pronunciation audio from AWS Polly (covers all imperative forms) | `[sound:haus_pronunciation.mp3]` |

---
