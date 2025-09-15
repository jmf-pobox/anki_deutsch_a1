# Production CSV Specification

This document defines the canonical CSV format specifications for the Anki German Language Deck Generator project. All CSV files must conform to these standards to ensure consistency, maintainability, and extensibility to future languages and multiple decks per language.

## Directory Structure

CSV files are organized by language and deck:
```
languages/
├── german/
│   ├── default/          # Complete A1 content (15 CSV files)
│   ├── a1.1/             # A1.1 level content (11 CSV files)
│   ├── a1/               # A1 level content (10 CSV files)
│   └── business/         # Business vocabulary (1 CSV file)
├── russian/
│   └── basic/           # Sample structure
└── korean/
    └── hanja/           # Sample structure
```

**File Locations**: All CSV files are located at `languages/{language}/{deck}/filename.csv`

Important DRY note: Field-level column definitions and constraints are maintained authoritatively in ENG-DATA-DICTIONARY.md. Any detailed column tables in this file are informational and may be trimmed; if discrepancies exist, ENG-DATA-DICTIONARY.md is the source of truth.

## Core Principles

### 1. Language Separation
- **Target Language**: German text appears in language-neutral column names (e.g., `word`, `noun`, `verb`)
- **Non-Target Language**: English translations must be in columns explicitly named or prefixed with the language code
  - Use `english` for English translations
  - Use `english_example` for English example sentences
  - Use `english_context` for English contextual information
  - Future languages will follow pattern: `spanish`, `spanish_example`, etc.

### 2. Consistency
- All similar fields across different word types use identical naming
- Column order must be consistent within each word type
- Data types and validation rules apply uniformly

### 3. Extensibility
- Design supports future addition of new languages
- Column naming allows for multi-language support
- Structure accommodates additional grammatical features

## Technical Standards

### File Format
- **Encoding**: UTF-8 (required for German special characters: ä, ö, ü, ß)
- **Delimiter**: Comma (`,`)
- **Quote Character**: Double quote (`"`) for fields containing commas
- **Line Endings**: Unix-style (`\n`) preferred, Windows (`\r\n`) acceptable
- **Header Row**: Required, must be first line
- **Empty Fields**: Represented as empty string between delimiters

### Data Validation Rules
- **Required Fields**: Must not be empty or whitespace-only
- **Optional Fields**: May be empty but must maintain column position
- **Text Fields**: Trimmed of leading/trailing whitespace
- **German Text**: Must support Unicode characters
- **Examples**: Should be complete sentences with proper punctuation

## Word Type Specifications

Authoritative field-level definitions and constraints are maintained in ENG-DATA-DICTIONARY.md. This section provides a high-level overview with links to the corresponding dictionary sections to avoid duplication.

- Nouns (nouns.csv)
  - Purpose: German nouns with articles, plural forms, and examples
  - See ENG-DATA-DICTIONARY.md → "Nouns (nouns.csv)"

- Adjectives (adjectives.csv)
  - Purpose: Adjectives with comparative/superlative forms
  - See ENG-DATA-DICTIONARY.md → "Adjectives (adjectives.csv)"

- Verbs - Simple Format (verbs.csv)
  - Purpose: Basic verb conjugations for common verbs
  - See ENG-DATA-DICTIONARY.md → "Verbs (verbs.csv)"

- Verbs - Unified Format (verbs_unified.csv)
  - Purpose: Multi-tense conjugation records
  - See ENG-DATA-DICTIONARY.md → "Verbs Unified (verbs_unified.csv)"

### 5. Adverbs (adverbs.csv)

**Purpose**: German adverbs categorized by type

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| word | Yes | string | German adverb | hier |
| english | Yes | string | English translation | here |
| type | Yes | string | Adverb category | location |
| example | No | string | Example sentence | Ich wohne hier. |

**Validation**:
- `type` common values: location, time, manner, frequency, degree

### 6. Negations (negations.csv)

**Purpose**: German negation words and patterns

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| word | Yes | string | German negation word | nicht |
| english | Yes | string | English translation | not |
| type | Yes | string | Negation type | general |
| example | No | string | Example sentence | Ich verstehe das nicht. |

**Validation**:
- `type` values: general, article, verb, adjective

### 7. Prepositions (prepositions.csv)

**Purpose**: German prepositions with case requirements

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| preposition | Yes | string | German preposition | in |
| english | Yes | string | English translation | in |
| case | Yes | string | Required case(s) | Accusative/Dative |
| example1 | No | string | First example | Ich gehe in die Schule. |
| example2 | No | string | Second example | Ich bin in der Schule. |

**Validation**:
- `case` values: Nominative, Accusative, Dative, Genitive, or combinations

### 8. Phrases (phrases.csv)

**Purpose**: Common German phrases and expressions

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| phrase | Yes | string | German phrase | Guten Morgen! |
| english | Yes | string | English translation | Good morning! |
| context | No | string | Usage context | Morning greeting |
| related | No | string | Related phrases | Guten Tag! Guten Abend! |

### 9. Cardinal Numbers (cardinal_numbers.csv)

**Purpose**: German cardinal numbers (counting numbers)

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| number | Yes | integer | Numeric value | 2 |
| word | Yes | string | German word | zwei |
| english | Yes | string | English translation | two |
| example | No | string | Example sentence | Es gibt zwei Äpfel auf dem Tisch. |

### 10. Ordinal Numbers (ordinal_numbers.csv)

**Purpose**: German ordinal numbers with declensions

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| number | Yes | string | Ordinal notation | 1st |
| word | Yes | string | German word | erste |
| english | Yes | string | English translation | first |
| case | Yes | string | Grammatical case | Nominativ |
| gender | Yes | string | Gender | masculine |
| example | No | string | Example sentence | Das ist der erste Tag in Deutschland. |

**Validation**:
- `case` values: Nominativ, Akkusativ, Dativ, Genitiv
- `gender` values: masculine, feminine, neuter, plural

### 11. Conjunctions (conjunctions.csv)

**Purpose**: German conjunctions for sentence connection

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| word | Yes | string | German conjunction | und |
| english | Yes | string | English translation | and |
| type | Yes | string | Conjunction type | coordinating |
| example | No | string | Example sentence | Ich lese ein Buch und sie schaut fern. |

**Validation**:
- `type` values: coordinating, subordinating, correlative

### 12. Interjections (interjections.csv)

**Purpose**: German interjections and exclamations

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| word | Yes | string | German interjection | Ach |
| english | Yes | string | English translation | oh |
| usage | Yes | string | Usage context | expression of surprise or realization |
| example | No | string | Example sentence | Ach, jetzt verstehe ich! |

### 13. Personal Pronouns (personal_pronouns.csv)

**Purpose**: German personal pronouns with case forms

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| pronoun | Yes | string | Base pronoun | ich |
| english | Yes | string | English translation | I |
| case | Yes | string | Grammatical case | nominative |
| form | Yes | string | Case-specific form | ich |
| example | No | string | Example sentence | Ich gehe nach Hause. |

**Validation**:
- `case` values: nominative, accusative, dative, genitive

### 14. Other Pronouns (other_pronouns.csv)

**Purpose**: Possessive, demonstrative, and other pronoun types

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| pronoun | Yes | string | Base pronoun | mein |
| english | Yes | string | English translation | my |
| type | Yes | string | Pronoun type | possessive |
| gender | Yes | string | Gender agreement | Masculine |
| case | Yes | string | Grammatical case | nominative |
| form | Yes | string | Declined form | mein |
| example | No | string | Example sentence | Das ist mein Bruder. |

**Validation**:
- `type` values: possessive, demonstrative, reflexive, relative, interrogative
- `gender` values: Masculine, Feminine, Neuter, Plural

### 15. Articles Unified (articles_unified.csv)

**Purpose**: German article declensions across all cases and genders

**⚠️ SPECIFICATION VIOLATION**: This CSV file currently uses German headers (artikel_typ, geschlecht, beispiel_nom, etc.) which violates the English header principle stated in Core Principles section. This should be corrected to use English headers (article_type, gender, example_nom, etc.).

**Columns**:
| Column | Required | Type | Description | Example |
|--------|----------|------|-------------|---------|
| artikel_typ | Yes | string | Article type | bestimmt |
| geschlecht | Yes | string | Gender/Number | maskulin |
| nominativ | Yes | string | Nominative case form | der |
| akkusativ | Yes | string | Accusative case form | den |
| dativ | Yes | string | Dative case form | dem |
| genitiv | Yes | string | Genitive case form | des |
| beispiel_nom | No | string | Nominative example | Der Mann ist hier |
| beispiel_akk | No | string | Accusative example | Ich sehe den Mann |
| beispiel_dat | No | string | Dative example | mit dem Mann |
| beispiel_gen | No | string | Genitive example | das Auto des Mannes |

**Validation**:
- `artikel_typ` values: bestimmt (definite), unbestimmt (indefinite), verneinend (negative)
- `geschlecht` values: maskulin, feminin, neutral, plural
- All case forms must be valid German articles
- Examples should demonstrate proper case usage

## Guidelines

### Adding New Languages
1. Create language directory: `languages/{language}/`
2. Add default deck directory: `languages/{language}/default/`
3. Copy/adapt CSV files from `languages/german/default/` template
4. Add translation columns with language prefix: `spanish`, `french`, etc.
5. Add example columns: `spanish_example`, `french_example`
6. Maintain all existing German and English columns
7. Update RecordMapper to handle new language columns

### Adding New Decks
1. Create deck directory: `languages/{language}/{deck}/`
2. Copy relevant CSV files from `languages/{language}/default/`
3. Modify content for specific deck purpose (business, beginner, etc.)
4. Ensure all CSV files maintain same format/column structure
5. Test with: `hatch run app --language {language} --deck {deck}`

## Quality Checklist

Before committing CSV changes:

- [ ] UTF-8 encoding verified
- [ ] Header row present and correct
- [ ] Required fields non-empty
- [ ] German nouns capitalized
- [ ] Articles are der/die/das only
- [ ] English text in `english` columns only
- [ ] Examples are complete sentences
- [ ] No trailing/leading whitespace
- [ ] Commas in text are quoted
- [ ] Special characters (ä,ö,ü,ß) display correctly

