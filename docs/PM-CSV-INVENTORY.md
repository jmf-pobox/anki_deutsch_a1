# Production CSV File Inventory

This document provides a complete inventory of all CSV files in the German Language Learning System and their current status.

## CSV File Status Categories

- **✅ ACTIVE**: Currently used in production, properly integrated
- **🔧 UNINTEGRATED**: Valid data but not yet integrated into the system

## Multi-Deck Architecture

**Directory Structure**: `languages/{language}/{deck}/` organization
- **Primary Location**: `languages/german/default/` (complete vocabulary with all unintegrated files)
- **German Decks**: `languages/german/a1.1/`, `languages/german/a1/`, `languages/german/business/`
- **Sample Structures**: `languages/russian/basic/`

**CSV File Distribution**:
- **languages/german/default/**: 15 CSV files (complete word type coverage + unintegrated)
- **languages/german/a1.1/**: 11 CSV files (beginner level subset)
- **languages/german/a1/**: 10 CSV files (elementary level subset)
- **languages/german/business/**: 1 CSV file (business nouns only)

## Active CSV Files (Currently Integrated)

### ✅ Core Word Types (Multi-Deck Distributed)

| File | Status | Record Type | Primary Location | Integration | Notes |
|------|--------|-------------|------------------|-------------|-------|
| nouns.csv | ✅ ACTIVE | noun | languages/german/default/ | Clean Pipeline | Articles, plurals, examples - distributed across decks |
| adjectives.csv | ✅ ACTIVE | adjective | languages/german/default/ | Clean Pipeline | Comparative/superlative forms |
| adverbs.csv | ✅ ACTIVE | adverb | languages/german/default/ | Clean Pipeline | Location, time, manner types |
| negations.csv | ✅ ACTIVE | negation | languages/german/default/ | Clean Pipeline | Negation patterns |
| prepositions.csv | ✅ ACTIVE | preposition | languages/german/default/ | Clean Pipeline | Case requirements |
| phrases.csv | ✅ ACTIVE | phrase | languages/german/default/ | Clean Pipeline | Common expressions |
| verbs.csv | ✅ ACTIVE | verb | languages/german/default/ | Clean Pipeline | Single-tense conjugations with separable info |
| verbs_unified.csv | ✅ ACTIVE | verb_conjugation | languages/german/default/ | Clean Pipeline | Multi-tense conjugations |
| articles_unified.csv | ✅ ACTIVE | unified_article | languages/german/default/ | Clean Pipeline | Article declensions (cloze cards only) |

### Integration Status:
- **Clean Pipeline Architecture**: All word types use Clean Pipeline with RecordMapper → MediaEnricher → CardBuilder

## Integrated Across Multiple Decks

### ✅ Numbers (Distributed Across a1.1, a1, default)

| File | Status | Decks | Purpose | Integration Status |
|------|--------|-------|---------|-------------------|
| cardinal_numbers.csv | ✅ ACTIVE | a1.1, a1, default | Counting numbers 1-100 | Integrated in all beginner decks |

### ✅ Pronouns (Distributed Across a1.1, a1, default)

| File | Status | Decks | Purpose | Integration Status |
|------|--------|-------|---------|-------------------|
| personal_pronouns.csv | ✅ ACTIVE | a1.1, a1, default | ich, du, er, sie, etc. | Integrated in all beginner decks |

## Unintegrated CSV Files (Available but Not Processed)

### 🔧 Grammar Components (Located in languages/german/default/ only)

| File | Status | Rows | Purpose | Integration Needed |
|------|--------|------|---------|-------------------|
| conjunctions.csv | 🔧 UNINTEGRATED | ~20 | und, aber, oder, etc. | Create ConjunctionRecord + RecordMapper support |
| interjections.csv | 🔧 UNINTEGRATED | ~15 | Ach, Oh, Na ja, etc. | Create InterjectionRecord + RecordMapper support |
| ordinal_numbers.csv | 🔧 UNINTEGRATED | ~20 | First, second, third, etc. | Create OrdinalNumberRecord + RecordMapper support |
| other_pronouns.csv | 🔧 UNINTEGRATED | ~60 | Possessive, demonstrative | Create PronounRecord + RecordMapper support |


## Integration Priority Recommendations

### High Priority (Core Learning Components)
1. **conjunctions.csv** - Needed for sentence construction
2. **ordinal_numbers.csv** - Essential for dates and ordering

### Medium Priority (Enhanced Learning)
3. **other_pronouns.csv** - Possessives and demonstratives

### Low Priority (Advanced Features)
4. **interjections.csv** - Conversational fluency

## File Summary

| Category | Files | Total Rows (est.) | Status |
|----------|-------|------------------|--------|
| Active Integrated | 11 | ~1400 | ✅ Production ready |
| Unintegrated | 4 | ~135 | 🔧 Awaiting integration |

## System Configuration

### Multi-Deck Architecture Implementation

**Main Application**: `src/langlearn/main.py`
- **CLI Parameters**: `--language german --deck default` (default values, case-insensitive input)
- **Data Path Resolution**: `languages/{language}/{deck}/` (normalized to lowercase)
- **Output Naming**: `LangLearn_{Language}_{deck}.apkg` (language is capitalized in filename)

**DeckBuilder Configuration**: `src/langlearn/deck_builder.py`
- **Path Construction**: `project_root / "languages" / language / deck_type`
- **Media Path Setup**: Each deck has isolated `audio/` and `images/` subdirectories
- **MediaFileRegistrar**: Configured with deck-specific media paths

**Current RecordMapper CSV mapping**:
```python
csv_files = {
    "nouns.csv": "noun",
    "adjectives.csv": "adjective",
    "adverbs.csv": "adverb",
    "negations.csv": "negation",
    "prepositions.csv": "preposition",
    "phrases.csv": "phrase",
    "verbs.csv": "verb",
    "verbs_unified.csv": "verb_conjugation",  # Available in default only
    "articles_unified.csv": "unified_article",
    "cardinal_numbers.csv": "cardinal_number",  # Active in a1.1, a1, default
    "personal_pronouns.csv": "personal_pronoun",  # Active in a1.1, a1, default
    # Unintegrated files available in languages/german/default/ only:
    # "ordinal_numbers.csv": needs record type
    # "conjunctions.csv": needs record type
    # "interjections.csv": needs record type
    # "other_pronouns.csv": needs record type
}
```

**Usage Examples**:
```bash
# Generate default German deck (A2/B1 level)
hatch run app

# Generate A1.1 beginner deck
hatch run app --language german --deck a1.1

# Generate A1 elementary deck
hatch run app --language german --deck a1

# Generate business vocabulary deck
hatch run app --language german --deck business
```

## Recommendations

### For New Development
1. Use only ACTIVE CSV files
2. Follow PM-CSV-SPEC.md for any modifications
3. Maintain english column naming convention

### For Quality Assurance
1. Run validation against PM-CSV-SPEC.md
2. Verify all example sentences are complete
3. Ensure UTF-8 encoding for special characters