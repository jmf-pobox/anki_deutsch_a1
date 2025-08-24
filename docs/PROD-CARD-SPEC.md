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

## Table of Contents - Organized by Sub-deck

### Adjectives Sub-deck
1. [Adjective](#adjective)

### Adverbs Sub-deck
2. [Adverb](#adverb)

### Unified_articles Sub-deck
3. [Artikel_Context](#artikel-context)
4. [Artikel_Context_Cloze](#artikel-context-cloze)
5. [Artikel_Gender](#artikel-gender)
6. [Artikel_Gender_Cloze](#artikel-gender-cloze)
7. [Noun_Article_Recognition](#noun-article-recognition)
8. [Noun_Case_Context](#noun-case-context)

### Negations Sub-deck
9. [Negation](#negation)

### Nouns Sub-deck
10. [Noun](#noun)

### Phrases Sub-deck
11. [Phrase](#phrase)

### Prepositions Sub-deck
12. [Preposition](#preposition)

### Verbs Sub-deck
13. [Verb](#verb) (DISABLED)
14. [Verb_Conjugation](#verb-conjugation)
15. [Verb_Imperative](#verb-imperative)

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
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:schön_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

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
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:hier_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

---

# Unified_articles Sub-deck

## Artikel_Context

**Anki Note Type**: `German Artikel Context with Media`
**Description**: German article case usage cards (nom/acc/dat/gen)
**Learning Objective**: Master German article changes in different grammatical cases
**Cloze Deletion**: No
**CSV Data Source**: `articles_unified.csv`
**Sub-deck**: `Unified_articles` (Main Deck::Unified_articles)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `artikel_context_DE_de_front.html`
- `artikel_context_DE_de_back.html`
- `artikel_context_DE_de.css`

### Field Specifications

| Field | Source | Required | Description | Example |
|-------|--------|----------|-------------|---------|
| `FrontText` | Generated | ❌ | Generated text for card front | `What is the German word for 'beautiful'?` |
| `BackText` | Generated | ❌ | Generated text for card back | `schön` |
| `Gender` | articles_unified.csv | ❌ | German grammatical gender (masculine, feminine, neuter) | `neutrum` |
| `Nominative` | articles_unified.csv | ❌ | Nominative case article form | `das` |
| `Accusative` | articles_unified.csv | ❌ | Accusative case article form | `das` |
| `Dative` | articles_unified.csv | ❌ | Dative case article form | `dem` |
| `Genitive` | articles_unified.csv | ❌ | Genitive case article form | `des` |
| `ExampleNom` | articles_unified.csv | ❌ | Example sentence in nominative case | `Der Mann arbeitet hier.` |
| `ExampleAcc` | articles_unified.csv | ❌ | Example sentence in accusative case | `Ich sehe den Mann.` |
| `ExampleDat` | articles_unified.csv | ❌ | Example sentence in dative case | `Ich gebe dem Mann das Buch.` |
| `ExampleGen` | articles_unified.csv | ❌ | Example sentence in genitive case | `Das ist das Haus des Mannes.` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `ArticleAudio` | AWS_Polly | ❌ | Generated audio for article pronunciation | `[sound:das_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ❌ | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |
| `NounOnly` | Generated | ❌ | Extracted noun without article | `Haus` |
| `NounEnglish` | Generated | ❌ | English translation of extracted noun | `house` |

## Artikel_Context_Cloze

**Anki Note Type**: `German Artikel Context Cloze`
**Description**: Cloze deletion cards for German case usage
**Learning Objective**: Practice German case usage through cloze deletion
**Cloze Deletion**: Yes
**CSV Data Source**: `articles_unified.csv`
**Sub-deck**: `Unified_articles` (Main Deck::Unified_articles)

### Card Content

**Front**: Cloze deletion question with blanked text
**Back**: Answer with complete text and explanation

### Template Files

- `artikel_context_cloze_DE_de_front.html`
- `artikel_context_cloze_DE_de_back.html`
- `artikel_context_cloze_DE_de.css`

### Field Specifications

| Field | Source | Required | Description | Example |
|-------|--------|----------|-------------|---------|
| `Text` | Generated | ❌ | Cloze deletion text with {{c1::}} tags | `Ich sehe {{c1::den}} Mann` |
| `Explanation` | Generated | ❌ | Explanation of the grammatical rule | `Akkusativ - direktes Objekt` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `Audio` | AWS_Polly | ❌ | Field for audio | `example_audio` |

## Artikel_Gender

**Anki Note Type**: `German Artikel Gender with Media`
**Description**: German article gender recognition cards (der/die/das)
**Learning Objective**: Learn to recognize German noun genders (der/die/das)
**Cloze Deletion**: No
**CSV Data Source**: `articles_unified.csv`
**Sub-deck**: `Unified_articles` (Main Deck::Unified_articles)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `artikel_gender_DE_de_front.html`
- `artikel_gender_DE_de_back.html`
- `artikel_gender_DE_de.css`

### Field Specifications

| Field | Source | Required | Description | Example |
|-------|--------|----------|-------------|---------|
| `FrontText` | Generated | ❌ | Generated text for card front | `What is the German word for 'beautiful'?` |
| `BackText` | Generated | ❌ | Generated text for card back | `schön` |
| `Gender` | articles_unified.csv | ❌ | German grammatical gender (masculine, feminine, neuter) | `neutrum` |
| `Nominative` | articles_unified.csv | ❌ | Nominative case article form | `das` |
| `Accusative` | articles_unified.csv | ❌ | Accusative case article form | `das` |
| `Dative` | articles_unified.csv | ❌ | Dative case article form | `dem` |
| `Genitive` | articles_unified.csv | ❌ | Genitive case article form | `des` |
| `ExampleNom` | articles_unified.csv | ❌ | Example sentence in nominative case | `Der Mann arbeitet hier.` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `ArticleAudio` | AWS_Polly | ❌ | Generated audio for article pronunciation | `[sound:das_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ❌ | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |
| `NounOnly` | Generated | ❌ | Extracted noun without article | `Haus` |
| `NounEnglish` | Generated | ❌ | English translation of extracted noun | `house` |

## Artikel_Gender_Cloze

**Anki Note Type**: `German Artikel Gender Cloze`
**Description**: Cloze deletion cards for German gender recognition
**Learning Objective**: Practice German gender recognition through cloze deletion
**Cloze Deletion**: Yes
**CSV Data Source**: `articles_unified.csv`
**Sub-deck**: `Unified_articles` (Main Deck::Unified_articles)

### Card Content

**Front**: Cloze deletion question with blanked text
**Back**: Answer with complete text and explanation

### Template Files

- `artikel_gender_cloze_DE_de_front.html`
- `artikel_gender_cloze_DE_de_back.html`
- `artikel_gender_cloze_DE_de.css`

### Field Specifications

| Field | Source | Required | Description | Example |
|-------|--------|----------|-------------|---------|
| `Text` | Generated | ❌ | Cloze deletion text with {{c1::}} tags | `{{c1::Der}} Mann arbeitet hier` |
| `Explanation` | Generated | ❌ | Explanation of the grammatical rule | `Maskulin - Geschlecht erkennen` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `Audio` | AWS_Polly | ❌ | Field for audio | `example_audio` |

## Noun_Article_Recognition

**Anki Note Type**: `German Noun_Article_Recognition with Media`
**Description**: Practice cards for learning noun-article pairs
**Learning Objective**: Learn which article goes with each German noun
**Cloze Deletion**: No
**CSV Data Source**: `nouns.csv + articles_unified.csv`
**Sub-deck**: `Unified_articles` (Main Deck::Unified_articles)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `noun_article_recognition_DE_de_front.html`
- `noun_article_recognition_DE_de_back.html`
- `noun_article_recognition_DE_de.css`

### Field Specifications

| Field | Source | Required | Description | Example |
|-------|--------|----------|-------------|---------|
| `FrontText` | Generated | ❌ | Generated text for card front | `What is the German word for 'beautiful'?` |
| `BackText` | Generated | ❌ | Generated text for card back | `schön` |
| `Gender` | articles_unified.csv | ❌ | German grammatical gender (masculine, feminine, neuter) | `neutrum` |
| `Nominative` | articles_unified.csv | ❌ | Nominative case article form | `das` |
| `Accusative` | articles_unified.csv | ❌ | Accusative case article form | `das` |
| `Dative` | articles_unified.csv | ❌ | Dative case article form | `dem` |
| `Genitive` | articles_unified.csv | ❌ | Genitive case article form | `des` |
| `ExampleNom` | articles_unified.csv | ❌ | Example sentence in nominative case | `Der Mann arbeitet hier.` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `ArticleAudio` | AWS_Polly | ❌ | Generated audio for article pronunciation | `[sound:das_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ❌ | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |
| `NounOnly` | Generated | ❌ | Extracted noun without article | `Haus` |
| `NounEnglishWithArticle` | Generated | ❌ | English translation including article | `the house` |

## Noun_Case_Context

**Anki Note Type**: `German Noun_Case_Context with Media`
**Description**: Practice cards for noun declension in different cases
**Learning Objective**: Master German noun declension in different cases
**Cloze Deletion**: No
**CSV Data Source**: `nouns.csv + articles_unified.csv`
**Sub-deck**: `Unified_articles` (Main Deck::Unified_articles)

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `noun_case_context_DE_de_front.html`
- `noun_case_context_DE_de_back.html`
- `noun_case_context_DE_de.css`

### Field Specifications

| Field | Source | Required | Description | Example |
|-------|--------|----------|-------------|---------|
| `FrontText` | Generated | ❌ | Generated text for card front | `What is the German word for 'beautiful'?` |
| `BackText` | Generated | ❌ | Generated text for card back | `schön` |
| `Gender` | articles_unified.csv | ❌ | German grammatical gender (masculine, feminine, neuter) | `neutrum` |
| `Nominative` | articles_unified.csv | ❌ | Nominative case article form | `das` |
| `Accusative` | articles_unified.csv | ❌ | Accusative case article form | `das` |
| `Dative` | articles_unified.csv | ❌ | Dative case article form | `dem` |
| `Genitive` | articles_unified.csv | ❌ | Genitive case article form | `des` |
| `ExampleNom` | articles_unified.csv | ❌ | Example sentence in nominative case | `Der Mann arbeitet hier.` |
| `ExampleAcc` | articles_unified.csv | ❌ | Example sentence in accusative case | `Ich sehe den Mann.` |
| `ExampleDat` | articles_unified.csv | ❌ | Example sentence in dative case | `Ich gebe dem Mann das Buch.` |
| `ExampleGen` | articles_unified.csv | ❌ | Example sentence in genitive case | `Das ist das Haus des Mannes.` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `ArticleAudio` | AWS_Polly | ❌ | Generated audio for article pronunciation | `[sound:das_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ❌ | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |
| `NounOnly` | Generated | ❌ | Extracted noun without article | `Haus` |
| `NounEnglish` | Generated | ❌ | English translation of extracted noun | `house` |

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
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:nicht_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

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
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:haus_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |

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
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `PhraseAudio` | AWS_Polly | ✅ | Front | Generated phrase audio from AWS Polly | `[sound:guten_tag.mp3]` |

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
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `Preposition` | prepositions.csv | ✅ | Front | German preposition | `mit` |
| `WordAudio` | AWS_Polly | ✅ | Front | Generated pronunciation audio from AWS Polly | `[sound:mit_pronunciation.mp3]` |
| `English` | prepositions.csv | ✅ | Back | English translation or meaning | `with` |
| `Case` | prepositions.csv | ✅ | Back | German grammatical case (Nominativ, Akkusativ, Dativ, Genitiv) | `Dativ` |
| `Example1` | prepositions.csv | ✅ | Back | First example sentence | `Ich gehe mit dem Auto.` |
| `Example1Audio` | AWS_Polly | ✅ | Back | Generated audio for first example | `[sound:example1.mp3]` |
| `Example2` | prepositions.csv | ❌ | Back | Second example sentence (optional - not all prepositions have two cases) | `Mit dir ist alles besser.` |
| `Example2Audio` | AWS_Polly | ❌ | Back | Generated audio for second example (optional) | `[sound:example2.mp3]` |

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
| `Image` | Pexels | ✅ | Front | Generated image from Pexels API representing the verb action | `<img src="work_001.jpg" />` |
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
