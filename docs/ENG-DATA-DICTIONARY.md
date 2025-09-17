# German Language - Data Dictionary

## Version 1.2 - German Language Learning System

This document provides a comprehensive field-by-field description of all data elements across all CSV files in the **German Language Learning System**. Each field includes data type, constraints, validation rules, and examples.

> **Language Scope**: This data dictionary is specific to the German language implementation only.
> Other languages (Russian, Korean) have separate, minimal data structures documented in their respective language packages.

## General Data Standards

### Common Field Types
- **string**: Text field supporting Unicode (UTF-8) characters including German special characters (ä, ö, ü, ß)
- **integer**: Whole numbers (no decimals)
- **boolean**: true/false values

### Common Constraints
- **Required**: Field must contain non-empty value
- **Optional**: Field may be empty but column must exist
- **Unique**: Values must be unique within the file
- **Capitalized**: German nouns and proper names must start with capital letter

## Field Definitions by CSV File

### 1. Articles Unified (articles_unified.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| artikel_typ | string | Yes | English/German | Type of German article | Must be: bestimmt, unbestimmt, verneinend | bestimmt |
| geschlecht | string | Yes | English/German | Gender or plurality | Must be: maskulin, feminin, neutral, plural | maskulin |
| nominativ | string | Yes | German | Nominative case form | Valid German article | der |
| akkusativ | string | Yes | German | Accusative case form | Valid German article | den |
| dativ | string | Yes | German | Dative case form | Valid German article | dem |
| genitiv | string | Yes | German | Genitive case form | Valid German article | des |
| beispiel_nom | string | No | German | Nominative case example | Complete German sentence | Der Mann ist hier |
| beispiel_akk | string | No | German | Accusative case example | Complete German sentence | Ich sehe den Mann |
| beispiel_dat | string | No | German | Dative case example | Complete German sentence | mit dem Mann |
| beispiel_gen | string | No | German | Genitive case example | Complete German sentence | das Auto des Mannes |

### 2. Nouns (nouns.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| noun | string | Yes | German | German noun | Must be capitalized | Haus |
| article | string | Yes | German | Definite article | Must be: der, die, das | das |
| english | string | Yes | English | English translation | Non-empty string | house |
| plural | string | No | German | Plural form | Should differ from singular | Häuser |
| example | string | No | German | Example sentence | Complete German sentence | Mein Haus ist sehr klein. |
| related | string | No | German | Related words | Comma-separated list | die Wohnung, das Zimmer |

### 3. Adjectives (adjectives.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| word | string | Yes | German | German adjective | Base form, typically lowercase | groß |
| english | string | Yes | English | English translation | Non-empty string | big/tall |
| example | string | No | German | Example sentence | Complete German sentence | Er ist sehr groß. |
| comparative | string | No | German | Comparative form | Usually ends in -er | größer |
| superlative | string | No | German | Superlative form | Typically starts with "am", ends in -sten/-ten | am größten |

### 4. Adverbs (adverbs.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| word | string | Yes | German | German adverb | Lowercase unless proper adverb | hier |
| english | string | Yes | English | English translation | Non-empty string | here |
| type | string | Yes | English | Adverb category | Common values: location, time, manner, frequency, degree | location |
| example | string | No | German | Example sentence | Complete German sentence | Ich wohne hier. |

### 5. Verbs (verbs.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| verb | string | Yes | German | Infinitive form | German verb infinitive | sein |
| english | string | Yes | English | English translation | Starts with "to" | to be |
| classification | string | Yes | English/German | Verb regularity type | Must be: regelmäßig, unregelmäßig, gemischt | unregelmäßig |
| present_ich | string | Yes | German | Present tense ich conjugation | German conjugated form | bin |
| present_du | string | Yes | German | Present tense du conjugation | German conjugated form | bist |
| present_er | string | Yes | German | Present tense er/sie/es conjugation | German conjugated form | ist |
| präteritum | string | Yes | German | Simple past tense 3rd person singular | German past tense form | war |
| auxiliary | string | Yes | German | Auxiliary verb for perfect tense | Must be: haben or sein | sein |
| perfect | string | Yes | German | Perfect tense 3rd person singular | German perfect form with past participle | ist gewesen |
| example | string | No | German | Example sentence | Complete German sentence | Ich bin zu Hause. |
| separable | boolean | Yes | English | Is separable verb | true or false | false |

### 6. Verbs Unified (verbs_unified.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| infinitive | string | Yes | German | Infinitive form | German verb infinitive | abfahren |
| english | string | Yes | English | English translation | Starts with "to" | to depart |
| classification | string | Yes | English/German | Verb regularity type | Must be: regelmäßig, unregelmäßig, gemischt | unregelmäßig |
| separable | boolean | Yes | English | Is separable verb | true or false | true |
| auxiliary | string | Yes | German | Auxiliary verb | Must be: haben or sein | sein |
| tense | string | Yes | English | Tense name | Values: present, preterite, perfect, future | present |
| ich | string | No | German | ich conjugation | May be empty for imperatives | fahre ab |
| du | string | No | German | du conjugation | May be empty for imperatives | fährst ab |
| er | string | No | German | er/sie/es conjugation | May be empty for imperatives | fährt ab |
| wir | string | No | German | wir conjugation | May be empty for imperatives | fahren ab |
| ihr | string | No | German | ihr conjugation | May be empty for imperatives | fahrt ab |
| sie | string | No | German | sie/Sie conjugation | May be empty for imperatives | fahren ab |
| example | string | No | German | Example sentence | Complete German sentence | Der Bus fährt ab. |

### 7. Negations (negations.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| word | string | Yes | German | German negation word | Lowercase unless proper | nicht |
| english | string | Yes | English | English translation | Non-empty string | not |
| type | string | Yes | English | Negation type | Values: general, article, verb, adjective | general |
| example | string | No | German | Example sentence | Complete German sentence | Ich verstehe das nicht. |

### 8. Prepositions (prepositions.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| preposition | string | Yes | German | German preposition | Lowercase | in |
| english | string | Yes | English | English translation | Non-empty string | in |
| case | string | Yes | English/German | Required grammatical case(s) | German case names or combinations | Accusative/Dative |
| example1 | string | No | German | First example | Complete German sentence | Ich gehe in die Schule. |
| example2 | string | No | German | Second example | Complete German sentence | Ich bin in der Schule. |

### 9. Phrases (phrases.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| phrase | string | Yes | German | German phrase | Complete phrase with punctuation | Guten Morgen! |
| english | string | Yes | English | English translation | Non-empty string | Good morning! |
| context | string | No | English | Usage context | Descriptive context | Morning greeting |
| related | string | No | German | Related phrases | Comma-separated list | Guten Tag! Guten Abend! |

### 10. Cardinal Numbers (cardinal_numbers.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| number | integer | Yes | Numeric | Numeric value | Positive integer, unique | 1 |
| word | string | Yes | German | German number word | German spelling of number | eins |
| english | string | Yes | English | English translation | English spelling of number | one |
| example | string | No | German | Example sentence | Complete German sentence | Ich habe nur einen Euro. |

### 11. Ordinal Numbers (ordinal_numbers.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| number | string | Yes | English | Ordinal notation | Format: 1st, 2nd, 3rd, etc. | 1st |
| word | string | Yes | German | German ordinal word | Declined form | erste |
| english | string | Yes | English | English translation | English ordinal | first |
| case | string | Yes | English/German | Grammatical case | Must be: Nominativ, Akkusativ, Dativ, Genitiv | Nominativ |
| gender | string | Yes | English | Gender agreement | Must be: masculine, feminine, neuter, plural | masculine |
| example | string | No | German | Example sentence | Complete German sentence | Das ist der erste Tag in Deutschland. |

### 12. Conjunctions (conjunctions.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| word | string | Yes | German | German conjunction | Lowercase | und |
| english | string | Yes | English | English translation | Non-empty string | and |
| type | string | Yes | English | Conjunction type | Values: coordinating, subordinating, correlative | coordinating |
| example | string | No | German | Example sentence | Complete German sentence | Ich lese ein Buch und sie schaut fern. |

### 13. Interjections (interjections.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| word | string | Yes | German | German interjection | May be capitalized | Ach |
| english | string | Yes | English | English translation | Non-empty string | oh |
| usage | string | Yes | English | Usage context | Descriptive explanation | expression of surprise or realization |
| example | string | No | German | Example sentence | Complete German sentence | Ach, jetzt verstehe ich! |

### 14. Personal Pronouns (personal_pronouns.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| pronoun | string | Yes | German | Base pronoun | German pronoun | ich |
| english | string | Yes | English | English translation | Non-empty string | I |
| case | string | Yes | English | Grammatical case | Must be: nominative, accusative, dative, genitive | nominative |
| form | string | Yes | German | Case-specific form | Declined pronoun form | ich |
| example | string | No | German | Example sentence | Complete German sentence | Ich gehe nach Hause. |

### 15. Other Pronouns (other_pronouns.csv)

| Field | Type | Required | Language | Description | Validation Rules | Examples |
|-------|------|----------|----------|-------------|------------------|----------|
| pronoun | string | Yes | German | Base pronoun | German pronoun | mein |
| english | string | Yes | English | English translation | Non-empty string | my |
| type | string | Yes | English | Pronoun type | Values: possessive, demonstrative, reflexive, relative, interrogative | possessive |
| gender | string | Yes | English | Gender agreement | Must be: Masculine, Feminine, Neuter, Plural | Masculine |
| case | string | Yes | English | Grammatical case | Must be: nominative, accusative, dative, genitive | nominative |
| form | string | Yes | German | Declined form | Fully declined pronoun form | mein |
| example | string | No | German | Example sentence | Complete German sentence | Das ist mein Bruder. |

## Data Quality Standards

### Required Field Rules
- **Required fields** must contain non-empty values
- **Text fields** are trimmed of leading/trailing whitespace
- **Examples** should be complete, grammatically correct German sentences
- **German text** must properly use special characters (ä, ö, ü, ß)

### Validation Constraints
- **German nouns** must be capitalized (noun, word field in nouns.csv)
- **Articles** must be der, die, or das only
- **Cases** must use proper German case names
- **Verb classifications** must follow specified values
- **Boolean fields** accept true/false values only

### Data Consistency Rules
- **Column naming** follows language separation principle
- **English translations** use 'english' column naming
- **Example sentences** use 'example' column naming
- **UTF-8 encoding** required for all files
- **Comma delimited** format with quoted fields containing commas

## Change Management

### Adding New Fields
1. Update this data dictionary with new field specifications
2. Add validation rules and examples
3. Update PM-CSV-SPEC.md with structural changes
4. Verify existing data compatibility

### Modifying Existing Fields
1. Document backward compatibility impact
2. Update validation rules in this dictionary
3. Update related specification documents
4. Test data migration if needed

## Column Naming Consistency Analysis

### Current Naming Inconsistencies

The project has several functionally equivalent columns with inconsistent naming across CSV files, and one major violation of the English header principle. The following analysis identifies standardization opportunities:

#### Primary German Word Column (Major Inconsistency)
**Current inconsistent naming for single words:**
- `word` - used in 8 files (conjunctions, interjections, adverbs, negations, adjectives, cardinal_numbers, ordinal_numbers)
- `noun` - used in nouns.csv  
- `verb` - used in verbs.csv
- `preposition` - used in prepositions.csv
- `pronoun` - used in pronoun files
- `infinitive` - used in verbs_unified.csv

**Semantic distinctions to preserve:**
- `phrase` - used in phrases.csv (multi-word expressions, correctly distinct from single words)
- `number` - used in cardinal_numbers.csv (numeric values, not linguistic words)

**Issue:** Single-word entries use different column names but should be standardized, while preserving meaningful semantic distinctions.

#### Language Naming Convention Violations (CRITICAL ISSUE)
**articles_unified.csv violations:**
- ❌ **CURRENT STATE**: Uses German column names: `artikel_typ`, `geschlecht`, `beispiel_nom`, `beispiel_akk`, `beispiel_dat`, `beispiel_gen`
- ✅ **REQUIRED**: Should follow English naming convention for headers
- **Impact**: This file violates the core principle that CSV headers must be in English while data is in target language

### Recommended Standardization Mapping

#### High Priority - Single Word Column Standardization
```
From                    To          File(s)
────────────────────────────────────────────────────────────
noun                 -> word        nouns.csv
verb                 -> word        verbs.csv
preposition          -> word        prepositions.csv
pronoun              -> word        personal_pronouns.csv, other_pronouns.csv
infinitive           -> word        verbs_unified.csv
```

#### Preserve Semantic Distinctions (Keep As Is)
```
Current Name            Reason to Keep
─────────────────────────────────────────────────────────────────
phrase                  Multi-word expressions, semantically different from single words
number                  Represents numeric values, not linguistic words
```

#### High Priority - articles_unified.csv Column Renaming
```
From                    To                File
─────────────────────────────────────────────────────────────────
artikel_typ          -> article_type    articles_unified.csv
geschlecht           -> gender          articles_unified.csv
beispiel_nom         -> example_nom     articles_unified.csv
beispiel_akk         -> example_acc     articles_unified.csv
beispiel_dat         -> example_dat     articles_unified.csv
beispiel_gen         -> example_gen     articles_unified.csv
```

#### Medium Priority - Example Column Standardization
```
From                    To                    File
─────────────────────────────────────────────────────────────
example1             -> example_primary     prepositions.csv
example2             -> example_secondary   prepositions.csv
```

### Language Content Specifications

All field definitions above have been updated to include the expected language for content:

#### German Content (Target Language)
- **Single word columns**: `word`, `noun`, etc. - Contains single German words
- **Multi-word columns**: `phrase` - Contains German multi-word expressions  
- **Conjugation columns**: `ich`, `du`, `er`, `wir`, `ihr`, `sie` - German grammatical persons
- **Case forms**: `nominativ`, `akkusativ`, `dativ`, `genitiv` - German article forms  
- **German grammatical forms**: `plural`, `comparative`, `superlative` - German language forms
- **Example sentences**: All `example*` columns - Complete German sentences

#### English Content
- **Translation column**: `english` - English translations only
- **Future expansion**: Any `english_*` prefixed columns - English content

#### Metadata (English Names, Mixed Content)
- **Classification fields**: `type`, `classification`, `usage`, `context` - English descriptive text
- **Grammatical metadata**: `case`, `gender`, `tense` - English or German values acceptable
- **Boolean flags**: `separable`, `required` - English true/false

### Implementation Recommendations

#### Phase 1: Critical Standardization
1. **Standardize single-word columns** to `word` (preserving semantic distinctions for phrases and numbers)
2. **Rename articles_unified.csv columns** to follow English naming convention  
3. **Update DATA-DICTIONARY.md** with standardized specifications

#### Phase 2: Code Integration
1. **Update RecordMapper** to handle standardized column names
2. **Update Pydantic models** for renamed columns
3. **Create migration scripts** for smooth transition

#### Benefits of Standardization
- **Consistency**: Uniform column naming reduces cognitive load
- **Maintainability**: Easier to work across multiple CSV files
- **Extensibility**: Clear patterns for adding new languages
- **Language Clarity**: Explicit separation of German content from English metadata

#### Risk Mitigation
- **Backup all CSV files** before implementing changes
- **Update all dependent code** (RecordMapper, Pydantic models, tests)  
- **Run comprehensive test suite** to verify compatibility
- **Implement changes incrementally** with validation at each step

## Version History

- **1.2** (2025-01-14): Updated for current German default deck accuracy
  - Verified all 15 CSV files in languages/german/default/ match documentation
  - Added missing präteritum field to verbs.csv documentation
  - Highlighted critical articles_unified.csv header violation
  - Confirmed English headers vs German data principle compliance
  - Total CSV files documented: 15

- **1.0** (2025-08-23): Initial comprehensive data dictionary
  - Documented all 14 CSV file structures
  - Defined field types, constraints, and validation rules
  - Established data quality standards
  - Created change management procedures
  - Added column naming consistency analysis and standardization recommendations
  - Added language content specifications for all fields