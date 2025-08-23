# German Anki Card Type Specifications

This document provides comprehensive specifications for all German language card types in the system.
Generated automatically by CardSpecificationGenerator to ensure accuracy and completeness.

**Total Card Types**: 15

## Table of Contents

1. [Noun](#noun)
2. [Adjective](#adjective)
3. [Adverb](#adverb)
4. [Negation](#negation)
5. [Verb](#verb)
6. [Verb_Conjugation](#verb-conjugation)
7. [Verb_Imperative](#verb-imperative)
8. [Phrase](#phrase)
9. [Preposition](#preposition)
10. [Artikel_Gender](#artikel-gender)
11. [Artikel_Context](#artikel-context)
12. [Artikel_Gender_Cloze](#artikel-gender-cloze)
13. [Artikel_Context_Cloze](#artikel-context-cloze)
14. [Noun_Article_Recognition](#noun-article-recognition)
15. [Noun_Case_Context](#noun-case-context)

---

## Noun

**Anki Note Type**: `German Noun with Media`
**Description**: Basic German noun cards with article, plural, and example sentences
**Learning Objective**: Learn German noun vocabulary with correct articles and plural forms
**Cloze Deletion**: No
**CSV Data Source**: `nouns.csv`

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

## Adjective

**Anki Note Type**: `German Adjective with Media`
**Description**: German adjective cards with comparative/superlative forms
**Learning Objective**: Master German adjective vocabulary with comparative/superlative forms
**Cloze Deletion**: No
**CSV Data Source**: `adjectives.csv`

### Card Content

**Front**: Question with optional hint button
**Back**: Answer with grammar forms and examples

### Template Files

- `adjective_front.html`
- `adjective_back.html`
- `adjective.css`
- `adjective_DE_de_front.html`
- `adjective_DE_de_back.html`
- `adjective_DE_de.css`

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

## Adverb

**Anki Note Type**: `German Adverb with Media`
**Description**: German adverb cards with type classification and usage examples
**Learning Objective**: Learn German adverb vocabulary and usage patterns
**Cloze Deletion**: No
**CSV Data Source**: `adverbs.csv`

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

## Negation

**Anki Note Type**: `German Negation with Media`
**Description**: German negation word cards (nicht, kein, nie, etc.)
**Learning Objective**: Master German negation words and their proper usage
**Cloze Deletion**: No
**CSV Data Source**: `negations.csv`

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

## Verb

**Anki Note Type**: `German Verb with Media`
**Description**: Basic German verb cards with present tense conjugation
**Learning Objective**: Learn German verb vocabulary with basic present tense conjugation
**Cloze Deletion**: No
**CSV Data Source**: `verbs.csv`

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
| `English` | verbs.csv | ✅ | Both | English translation or meaning (hint on front, hint on back) | `to work` |
| `Image` | Pexels | ✅ | Both | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `Example` | verbs.csv | ✅ | Back | Example sentence using the word | `Er arbeitet in einer Bank.` |
| `ExampleAudio` | AWS_Polly | ✅ | Back | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |
| `Perfect` | verbs.csv | ✅ | Back | Perfect tense form (haben/sein + past participle) | `hat gearbeitet` |
| `PresentDu` | verbs.csv | ✅ | Back | Present tense second person (du) | `arbeitest` |
| `PresentEr` | verbs.csv | ✅ | Back | Present tense third person (er/sie/es) | `arbeitet` |
| `PresentIch` | verbs.csv | ✅ | Back | Present tense first person (ich) | `arbeite` |
| `Verb` | verbs.csv | ✅ | Back | German verb in infinitive form | `arbeiten` |
| `WordAudio` | AWS_Polly | ✅ | Back | Generated pronunciation audio from AWS Polly | `[sound:arbeiten_pronunciation.mp3]` |


---

## Verb_Conjugation

**Anki Note Type**: `German Verb_Conjugation with Media`
**Description**: Comprehensive German verb conjugation cards by tense
**Learning Objective**: Master German verb conjugation across all persons and tenses
**Cloze Deletion**: No
**CSV Data Source**: `verbs_unified.csv`

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


---

## Verb_Imperative

**Anki Note Type**: `German Verb_Imperative with Media`
**Description**: German imperative (command) form cards for all persons
**Learning Objective**: Learn German imperative (command) forms for all persons
**Cloze Deletion**: No
**CSV Data Source**: `verbs_unified.csv`

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
| `Meaning` | verbs_unified.csv | ✅ | Back | English meaning of the word | `to work` |
| `Classification` | verbs_unified.csv | ✅ | Back | Verb classification (regular, irregular, modal, etc.) | `regular` |
| `Separable` | verbs_unified.csv | ✅ | Back | Whether the verb is separable (Yes/No) | `Yes` |
| `DuForm` | verbs_unified.csv | ✅ | Back | Imperative form for 'du' | `sprich!` |
| `IhrForm` | verbs_unified.csv | ✅ | Back | Imperative form for 'ihr' | `sprecht!` |
| `SieForm` | verbs_unified.csv | ✅ | Back | Imperative form for 'Sie' | `sprechen Sie!` |
| `WirForm` | verbs_unified.csv | ✅ | Back | Imperative form for 'wir' | `sprechen wir!` |
| `ExampleDu` | verbs_unified.csv | ✅ | Back | Example sentence with du imperative | `Sprich lauter!` |
| `ExampleIhr` | verbs_unified.csv | ✅ | Back | Example sentence with ihr imperative | `Sprecht deutlicher!` |
| `ExampleSie` | verbs_unified.csv | ✅ | Back | Example sentence with Sie imperative | `Sprechen Sie bitte langsamer!` |
| `WordAudio` | AWS_Polly | ✅ | Back | Generated pronunciation audio from AWS Polly (covers all imperative forms) | `[sound:haus_pronunciation.mp3]` |


---

## Phrase

**Anki Note Type**: `German Phrase with Media`
**Description**: Common German phrase cards with contextual usage
**Learning Objective**: Learn common German phrases and expressions with context
**Cloze Deletion**: No
**CSV Data Source**: `phrases.csv`

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

## Preposition

**Anki Note Type**: `German Preposition with Media`
**Description**: German preposition cards with case requirements and examples
**Learning Objective**: Master German prepositions with their required grammatical cases
**Cloze Deletion**: No
**CSV Data Source**: `prepositions.csv`

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
 `Example2` | prepositions.csv | ❌ | Back | Second example sentence (optional - not all prepositions have two cases) | `Mit dir ist alles besser.` |
| `Example2Audio` | AWS_Polly | ❌ | Back | Generated audio for second example (optional) | `[sound:example2.mp3]` |
|

---

## Artikel_Gender

**Anki Note Type**: `German Artikel Gender with Media`
**Description**: German article gender recognition cards (der/die/das)
**Learning Objective**: Learn to recognize German noun genders (der/die/das)
**Cloze Deletion**: No
**CSV Data Source**: `articles_unified.csv`

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
| `ArtikelTypBestimmt` | Generated | ❌ | Conditional field for definite articles | `true` |
| `ArtikelTypUnbestimmt` | Generated | ❌ | Conditional field for indefinite articles | `` |
| `ArtikelTypVerneinend` | Generated | ❌ | Conditional field for negative articles | `` |
| `NounOnly` | Generated | ❌ | Extracted noun without article | `Haus` |
| `NounEnglish` | Generated | ❌ | English translation of extracted noun | `house` |


---

## Artikel_Context

**Anki Note Type**: `German Artikel Context with Media`
**Description**: German article case usage cards (nom/acc/dat/gen)
**Learning Objective**: Master German article changes in different grammatical cases
**Cloze Deletion**: No
**CSV Data Source**: `articles_unified.csv`

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
| `Case` | articles_unified.csv | ❌ | German grammatical case (Nominativ, Akkusativ, Dativ, Genitiv) | `Akkusativ` |
| `CaseRule` | Generated | ❌ | Generated case rule explanation | `Maskulin Akkusativ = den` |
| `ArticleForm` | articles_unified.csv | ❌ | Specific article form for this case | `dem` |
| `CaseUsage` | Generated | ❌ | Generated case usage explanation | `the direct object` |
| `Nominative` | articles_unified.csv | ❌ | Nominative case article form | `das` |
| `Accusative` | articles_unified.csv | ❌ | Accusative case article form | `das` |
| `Dative` | articles_unified.csv | ❌ | Dative case article form | `dem` |
| `Genitive` | articles_unified.csv | ❌ | Genitive case article form | `des` |
| `CaseNominative` | Generated | ❌ | Conditional highlighting for nominative case | `true` |
| `CaseAccusative` | Generated | ❌ | Conditional highlighting for accusative case | `` |
| `CaseDative` | Generated | ❌ | Conditional highlighting for dative case | `` |
| `CaseGenitive` | Generated | ❌ | Conditional highlighting for genitive case | `` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `ExampleAudio` | AWS_Polly | ❌ | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |
| `ArtikelTypBestimmt` | Generated | ❌ | Conditional field for definite articles | `true` |
| `ArtikelTypUnbestimmt` | Generated | ❌ | Conditional field for indefinite articles | `` |
| `ArtikelTypVerneinend` | Generated | ❌ | Conditional field for negative articles | `` |
| `NounOnly` | Generated | ❌ | Extracted noun without article | `Haus` |
| `NounEnglish` | Generated | ❌ | English translation of extracted noun | `house` |


---

## Artikel_Gender_Cloze

**Anki Note Type**: `German Artikel Gender Cloze`
**Description**: Cloze deletion cards for German gender recognition
**Learning Objective**: Practice German gender recognition through cloze deletion
**Cloze Deletion**: Yes
**CSV Data Source**: `articles_unified.csv`

### Card Content

**Front**: Cloze deletion question with blanked text
**Back**: Cloze deletion answer with revealed text

### Template Files

- `artikel_gender_cloze_DE_de_front.html`
- `artikel_gender_cloze_DE_de_back.html`
- `artikel_gender_cloze_DE_de.css`

### Field Specifications

| Field | Source | Required | Description | Example |
|-------|--------|----------|-------------|---------|
| `Text` | Generated | ❌ | Generated cloze deletion text | `Das {{c1::Haus}} ist groß.` |
| `Explanation` | Generated | ❌ | Generated German grammar explanation | `Neutrum - Geschlecht erkennen` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `Audio` | AWS_Polly | ❌ | Field for audio | `example_audio` |


---

## Artikel_Context_Cloze

**Anki Note Type**: `German Artikel Context Cloze`
**Description**: Cloze deletion cards for German case usage
**Learning Objective**: Practice German case usage through cloze deletion
**Cloze Deletion**: Yes
**CSV Data Source**: `articles_unified.csv`

### Card Content

**Front**: Cloze deletion question with blanked text
**Back**: Cloze deletion answer with revealed text

### Template Files

- `artikel_context_cloze_DE_de_front.html`
- `artikel_context_cloze_DE_de_back.html`
- `artikel_context_cloze_DE_de.css`

### Field Specifications

| Field | Source | Required | Description | Example |
|-------|--------|----------|-------------|---------|
| `Text` | Generated | ❌ | Generated cloze deletion text | `Das {{c1::Haus}} ist groß.` |
| `Explanation` | Generated | ❌ | Generated German grammar explanation | `Neutrum - Geschlecht erkennen` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `Audio` | AWS_Polly | ❌ | Field for audio | `example_audio` |


---

## Noun_Article_Recognition

**Anki Note Type**: `German Noun_Article_Recognition with Media`
**Description**: Practice cards for learning noun-article pairs
**Learning Objective**: Learn which article goes with each German noun
**Cloze Deletion**: No
**CSV Data Source**: `nouns.csv + articles_unified.csv`

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
| `Noun` | nouns.csv + articles_unified.csv | ❌ | German noun with proper capitalization | `Haus` |
| `Article` | nouns.csv + articles_unified.csv | ❌ | German article (der, die, das) | `das` |
| `English` | nouns.csv + articles_unified.csv | ❌ | English translation or meaning | `beautiful` |
| `Plural` | nouns.csv + articles_unified.csv | ❌ | Plural form of the noun | `Häuser` |
| `Example` | nouns.csv + articles_unified.csv | ❌ | Example sentence using the word | `Das Haus ist schön.` |
| `Related` | nouns.csv + articles_unified.csv | ❌ | Related words or expressions | `Hallo, Auf Wiedersehen` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ❌ | Generated pronunciation audio from AWS Polly | `[sound:haus_pronunciation.mp3]` |
| `NounOnly` | Generated | ❌ | Extracted noun without article | `Haus` |
| `NounEnglishWithArticle` | Generated | ❌ | English translation including article | `the house` |


---

## Noun_Case_Context

**Anki Note Type**: `German Noun_Case_Context with Media`
**Description**: Practice cards for noun declension in different cases
**Learning Objective**: Master German noun declension in different cases
**Cloze Deletion**: No
**CSV Data Source**: `nouns.csv + articles_unified.csv`

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
| `Noun` | nouns.csv + articles_unified.csv | ❌ | German noun with proper capitalization | `Haus` |
| `Article` | nouns.csv + articles_unified.csv | ❌ | German article (der, die, das) | `das` |
| `Case` | nouns.csv + articles_unified.csv | ❌ | German grammatical case (Nominativ, Akkusativ, Dativ, Genitiv) | `Akkusativ` |
| `CaseRule` | Generated | ❌ | Generated case rule explanation | `Maskulin Akkusativ = den` |
| `ArticleForm` | nouns.csv + articles_unified.csv | ❌ | Specific article form for this case | `dem` |
| `CaseUsage` | Generated | ❌ | Generated case usage explanation | `the direct object` |
| `English` | nouns.csv + articles_unified.csv | ❌ | English translation or meaning | `beautiful` |
| `Plural` | nouns.csv + articles_unified.csv | ❌ | Plural form of the noun | `Häuser` |
| `CaseNominativ` | Generated | ❌ | Conditional highlighting for Nominativ | `true` |
| `CaseAkkusativ` | Generated | ❌ | Conditional highlighting for Akkusativ | `` |
| `CaseDativ` | Generated | ❌ | Conditional highlighting for Dativ | `` |
| `CaseGenitiv` | Generated | ❌ | Conditional highlighting for Genitiv | `` |
| `Image` | Pexels | ❌ | Generated image from Pexels API | `<img src="house_001.jpg" />` |
| `WordAudio` | AWS_Polly | ❌ | Generated pronunciation audio from AWS Polly | `[sound:haus_pronunciation.mp3]` |
| `ExampleAudio` | AWS_Polly | ❌ | Generated example sentence audio from AWS Polly | `[sound:example_sentence.mp3]` |


---
