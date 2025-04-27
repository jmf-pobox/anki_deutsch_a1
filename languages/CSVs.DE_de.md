# German CSV File Inventory

This document outlines the organization of CSV files for German language learning, based on structural uniformity and grammatical requirements.

## 1. Nouns (Substantive/Nomen)
- **File**: `nouns.csv`
- **Structure**: noun, article, english, plural, example, related
- **Rationale**: All nouns follow the same structure with gender and plural forms

## 2. Verbs (Verben)
- **Regular Verbs**
  - **File**: `regular_verbs.csv`
  - **Structure**: verb, english, present_ich, present_du, present_er, perfect, example
- **Separable Verbs**
  - **File**: `separable_verbs.csv`
  - **Structure**: verb, english, present_ich, present_du, present_er, perfect, example, prefix
- **Irregular Verbs**
  - **File**: `irregular_verbs.csv`
  - **Structure**: verb, english, present_ich, present_du, present_er, perfect, example, notes
- **Rationale**: Different conjugation patterns and special cases require separate files

## 3. Adjectives (Adjektive)
- **File**: `adjectives.csv`
- **Structure**: word, english, example, comparative, superlative
- **Rationale**: All adjectives follow the same pattern for comparison

## 4. Pronouns (Pronomen)
- **Personal Pronouns**
  - **File**: `personal_pronouns.csv`
  - **Structure**: pronoun, english, case, form, example
  - **Rationale**: Each row represents a specific case form of a personal pronoun with an example sentence showing its usage
- **Other Pronouns**
  - **File**: `other_pronouns.csv`
  - **Structure**: pronoun, english, type, gender, case, form, example
  - **Rationale**: Each row represents a specific case and gender form of a possessive pronoun with an example sentence showing its usage

## 5. Prepositions (Präpositionen)
- **File**: `prepositions.csv`
- **Structure**: preposition, english, case, example1, example2
- **Rationale**: All prepositions follow the same pattern with case requirements

## 6. Conjunctions (Konjunktionen)
- **File**: `conjunctions.csv`
- **Structure**: conjunction, english, type, example
- **Rationale**: All conjunctions follow the same basic structure

## 7. Adverbs (Adverbien)
- **File**: `adverbs.csv`
- **Structure**: adverb, english, type, example
- **Rationale**: Adverbs don't decline, so one structure fits all

## 8. Numerals (Numeralien)
- **Cardinal Numbers**
  - **File**: `cardinal_numbers.csv`
  - **Structure**: number, word, english, example
- **Ordinal Numbers**
  - **File**: `ordinal_numbers.csv`
  - **Structure**: number, word, english, example
- **Rationale**: Different formation rules for cardinal and ordinal numbers

## 9. Articles (Artikel)
- **File**: `articles.csv`
- **Structure**: article, type, gender, nominative, accusative, dative, genitive
- **Rationale**: All articles follow the same declension patterns

## 10. Particles (Partikeln)
- **File**: `particles.csv`
- **Structure**: particle, english, type, example
- **Rationale**: All particles follow the same basic structure

## 11. Negation Words (Negationswörter)
- **File**: `negations.csv`
- **Structure**: word, english, type, example
- **Rationale**: All negation words follow the same basic structure

## 12. Interjections (Interjektionen)
- **File**: `interjections.csv`
- **Structure**: word, english, usage, example
- **Rationale**: All interjections follow the same basic structure

## Key Principles
1. Separate files when structural requirements differ significantly
2. Combine categories when they share the same data structure
3. Include all necessary grammatical information in each file
4. Maintain consistency within each file
5. Include examples for context and usage

## Total Files: 15
Each file is organized by structural similarity rather than grammatical category, ensuring consistent data representation and ease of processing.