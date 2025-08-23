# Production CSV Specification

## Version 1.0 - German Language Learning System

This document defines the canonical CSV format specifications for the Anki German Language Deck Generator project. All CSV files must conform to these standards to ensure consistency, maintainability, and extensibility to future languages.

Important DRY note: Field-level column definitions and constraints are maintained authoritatively in DATA-DICTIONARY.md. Any detailed column tables in this file are informational and may be trimmed; if discrepancies exist, DATA-DICTIONARY.md is the source of truth.

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

Authoritative field-level definitions and constraints are maintained in DATA-DICTIONARY.md. This section provides a high-level overview with links to the corresponding dictionary sections to avoid duplication.

- Nouns (nouns.csv)
  - Purpose: German nouns with articles, plural forms, and examples
  - See DATA-DICTIONARY.md → "Nouns (nouns.csv)"

- Adjectives (adjectives.csv)
  - Purpose: Adjectives with comparative/superlative forms
  - See DATA-DICTIONARY.md → "Adjectives (adjectives.csv)"

- Verbs - Simple Format (verbs.csv)
  - Purpose: Basic verb conjugations for common verbs
  - See DATA-DICTIONARY.md → "Verbs (verbs.csv)"

- Verbs - Unified Format (verbs_unified.csv)
  - Purpose: Multi-tense conjugation records
  - See DATA-DICTIONARY.md → "Verbs Unified (verbs_unified.csv)"
| du | No | string | du conjugation | fährst ab |
| er | No | string | er/sie/es conjugation | fährt ab |
| wir | No | string | wir conjugation | fahren ab |
| ihr | No | string | ihr conjugation | fahrt ab |
| sie | No | string | sie/Sie conjugation | fahren ab |
| example | No | string | Example sentence | Der Bus fährt ab. |

**Validation**:
- `classification` must be one of: regelmäßig, unregelmäßig, gemischt
- `auxiliary` must be: haben or sein
- `tense` values: present, preterite, perfect, future
- Multiple rows per verb (one per tense)

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

## Legacy CSV Files (Deprecated)

The following CSV files are maintained for backward compatibility but should not be used for new development:

- **regular_verbs.csv**: Replaced by verbs_unified.csv
- **irregular_verbs.csv**: Replaced by verbs_unified.csv
- **separable_verbs.csv**: Replaced by verbs_unified.csv

These files follow the same structure as verbs.csv but with additional type-specific columns.

## Migration Guidelines

### Adding New Languages
1. Add translation columns with language prefix: `spanish`, `french`, etc.
2. Add example columns: `spanish_example`, `french_example`
3. Maintain all existing German and English columns
4. Update RecordMapper to handle new language columns

### Converting Legacy Data
1. Use verbs_unified.csv for all verb data
2. Migrate type-specific verb CSVs to unified format
3. Ensure `english` column naming (not `meaning`)
4. Validate all required fields are present

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

## Version History

- **1.0** (2024-01): Initial specification
  - Standardized column naming conventions
  - Established english/target language separation
  - Defined validation rules for all word types
  - Marked legacy files as deprecated