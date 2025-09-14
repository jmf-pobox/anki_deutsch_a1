# Production CSV File Inventory

This document provides a complete inventory of all CSV files in the German Language Learning System and their current status.

## CSV File Status Categories

- **✅ ACTIVE**: Currently used in production, properly integrated
- **🔧 UNINTEGRATED**: Valid data but not yet integrated into the system

## Multi-Deck Architecture

**Directory Structure**: `languages/{language}/{deck}/` organization
- **Primary Location**: `languages/german/default/` (complete A1 content)
- **Additional Decks**: `languages/german/business/`, `languages/german/beginner/`
- **Sample Structures**: `languages/russian/basic/`, `languages/korean/hanja/`

**CSV File Distribution**:
- **languages/german/default/**: 15 CSV files (complete word type coverage)
- **languages/german/business/**: 1 CSV file (nouns.csv with business vocabulary)
- **languages/german/beginner/**: 1 CSV file (nouns.csv with beginner vocabulary)

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

## Unintegrated CSV Files (Available but Not Processed)

### 🔧 Numbers (Located in languages/german/default/)

| File | Status | Rows | Purpose | Integration Needed |
|------|--------|------|---------|-------------------|
| cardinal_numbers.csv | 🔧 UNINTEGRATED | ~30 | Counting numbers 1-100 | Create CardinalNumberRecord + RecordMapper support |
| ordinal_numbers.csv | 🔧 UNINTEGRATED | ~20 | First, second, third, etc. | Create OrdinalNumberRecord + RecordMapper support |

### 🔧 Grammar Components (Located in languages/german/default/)

| File | Status | Rows | Purpose | Integration Needed |
|------|--------|------|---------|-------------------|
| conjunctions.csv | 🔧 UNINTEGRATED | ~20 | und, aber, oder, etc. | Create ConjunctionRecord + RecordMapper support |
| interjections.csv | 🔧 UNINTEGRATED | ~15 | Ach, Oh, Na ja, etc. | Create InterjectionRecord + RecordMapper support |

### 🔧 Pronouns (Located in languages/german/default/)

| File | Status | Rows | Purpose | Integration Needed |
|------|--------|------|---------|-------------------|
| personal_pronouns.csv | 🔧 UNINTEGRATED | ~40 | ich, du, er, sie, etc. | Create PersonalPronounRecord + RecordMapper support |
| other_pronouns.csv | 🔧 UNINTEGRATED | ~60 | Possessive, demonstrative | Create PronounRecord + RecordMapper support |


## Integration Priority Recommendations

### High Priority (Core Learning Components)
1. **personal_pronouns.csv** - Essential for basic German
2. **cardinal_numbers.csv** - Fundamental vocabulary
3. **conjunctions.csv** - Needed for sentence construction

### Medium Priority (Enhanced Learning)
4. **ordinal_numbers.csv** - Dates and ordering
5. **other_pronouns.csv** - Possessives and demonstratives

### Low Priority (Advanced Features)
6. **interjections.csv** - Conversational fluency

## File Summary

| Category | Files | Total Rows (est.) | Status |
|----------|-------|------------------|--------|
| Active Integrated | 9 | ~1200 | ✅ Production ready |
| Unintegrated | 6 | ~200 | 🔧 Awaiting integration |

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
    "verbs_unified.csv": "verb_conjugation",
    "articles_unified.csv": "unified_article",
    # Unintegrated files available in languages/german/default/:
    # "cardinal_numbers.csv": needs record type
    # "ordinal_numbers.csv": needs record type  
    # "conjunctions.csv": needs record type
    # "interjections.csv": needs record type
    # "personal_pronouns.csv": needs record type
    # "other_pronouns.csv": needs record type
}
```

**Usage Examples**:
```bash
# Generate default German A1 deck
hatch run app

# Generate business vocabulary deck
hatch run app --language german --deck business

# Generate beginner deck
hatch run app --language german --deck beginner
```

## Recommendations

### For New Development
1. Use only ACTIVE CSV files
2. Follow PROD-CSV-SPEC.md for any modifications
3. Maintain english column naming convention

### For Quality Assurance
1. Run validation against PROD-CSV-SPEC.md
2. Verify all example sentences are complete
3. Ensure UTF-8 encoding for special characters