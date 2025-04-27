# Language Learn Anki Deck Generator (langlearn-anki-deck-generator)

## Project Introduction

This Python application is designed to generate Anki decks for language learning. The motivation for the project is to create decks that reflect grammatical nuances of the target language while preserving the popular Anki user interface to the content.

Currently, German is the only target language, but Korean and other languages are planned.  The intent is to make the code base modular enough to support multiple languages, while still being customized for the grammar of each language.  

An early difficulty in acquiring German is to cope with the lack of systematic rules related to the gender of nouns.  In many languages, the word ending conveys gender or at least strongly hints at gender. While there are some heuristics in German, the reality is that the learner has to be able to recall / memorize the gender.  Most decks with German include the article (der/das/die), but they do not test the learner specifically for recalling the article.  The pedagagocial method in Anki (spaced, repeition, progressive recall) is designed to help learners memorize material, but most decks for German treat the article plus noun as a phrase (das Buch), rather than prompting for the article (___ Buch?).  This is only one such nuance in German.  Others include separable verbs, cases for prepositions, and many other must be memorized elements.

This Python application should be able to generate Anki decks for any level (A1, A2, ... C2) as the data is separate from the system.  The system is intended to create customized page layouts for different types of words.  The raw worklists are enriched with images and audio assets.  The goal is to use very little English in the cards themselves but rather point to pictures as prompts, present fill in the blank statements, to present listening comprehension questions, or to engage in dialog even.

## General Documentation

This system is built for Anki as a front-end. Card templates tell Anki which fields should appear on the front and back of your card, and control which cards will be generated when certain fields have text in them. By adjusting your card templates, you can alter the design and styling of many of your cards at once.  Anki supports HTML, CSS, some JavaScript, MathJax, and LaTeX. Media is also supported (audio, video). In general, cards are treated as webpages.

* https://docs.ankiweb.net/templates/intro.html - Anki template system

## Project Status

The project is currently in an intermediary phase with the following components completed:

### Completed Components
- ✅ All CSV data files with initial A1-level content
- ✅ Comprehensive model classes with validation:
  - Nouns, Verbs (Regular, Separable, Irregular)
  - Adjectives, Prepositions, Phrases
  - Pronouns (Personal, Possessive, Other)
  - Conjunctions, Adverbs, Negations, Interjections
  - Numbers (Cardinal, Ordinal)
- ✅ AWS Polly integration for audio pronunciation
- ✅ Pexels integration for image association with automatic backup functionality
- ✅ CSV service for data management
- ✅ Comprehensive test suites for all models and services

### In Progress
- 🔄 Card generators for each word type
- 🔄 Deck generation functionality
- 🔄 Additional validation rules

### Future Development
- 📋 Audio pronunciation for all word types
- 📋 CLI interface for deck management
- 📋 Support for multiple languages
- 📋 Spaced repetition algorithm
- 📋 Web interface for practice
- 📋 Progress tracking and statistics
- 📋 Export to Anki format
- 📋 CI/CD pipeline
- 📋 User and developer documentation

## Project Structure

```
langlearn-anki-deck-generator/
├── data/                  # Language data in CSV files
│   └── audio/             # Supporting audio enrichments
│   └── images/            # Supporting image enrichments
│   └── backups/           # Backups of CVS files made during enrichment
|
├── src/
│   └── langlearn/
│       ├── models/        # Pydantic models representing parts of speech and language acquisition units
│       ├── cards/         # Card generators for each part of Pydantic model, depends upon models
│       └── services/      # Service interfaces to external endpoints (AWS, Pexels, Filesystem, etc.)
│       └── utils/         # Utilities that are used to generate and enrich content, manage API keys, etc.
│       └── scripts/       # Scripts that are used to generate content, rely upon utils
│       └── examples/      # Standalone example showing the genanki interface and deck creation
|
├── tests/                 # Test suites
│       └── integration/   # Tests that call live APIs and/or external dependencies (e.g., filesystem, keyring)
|
└── languages/             # Language-specific documentation covering grammar and required data files
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/anki-deutsch-a1.git
cd anki-deutsch-a1
```

2. Install dependencies using Hatch:
```bash
hatch env create
```

3. Configure API keys using the api_keyring utility, which stores secrets via keyring:
```bash
# For Anthropic API key
python src/langlearn/utils/api_keyring.py add ANTHROPIC_API_KEY your_api_key_here

# For Pexels API key
python src/langlearn/utils/api_keyring.py add PEXELS_API_KEY your_api_key_here

# To view a stored API key
python src/langlearn/utils/api_keyring.py view ANTHROPIC_API_KEY
```

4. Configure AWS credentials for audio generation:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_region
```

## Usage

The project is currently in development. 

The intended use involves a user of the application deciding their target language, using LLMs to build wordlists for each part of speech and each supported content type (e.g., dialog), followed by enrichment with speech sourced from AWS Polly (or a similar service), and images sourced from Pexels, finally resulting in a custom programmatically generated Anki deck.

Once completed, it will provide:

1. Generation of Anki decks based on target language data
2. Audio for all words
3. Image associations for concrete nouns and adjectives
4. Example sentences for context
5. Unique card templates in Anki for different parts of speech
5. Additional card templates (listening comprehension, dialog)

## Development

### Running Tests
```bash
python -m pytest tests/ -v
```

### Adding New Words
1. Add entries to the appropriate CSV file in `data/`
2. Run tests to ensure validation passes
3. Generate new cards using the card generators

### Contributing
1. Fork the repository
2. Create a feature branch for a new language or feature
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AWS Polly for text-to-speech
- Pexels for image integration
- Anki for the flashcard platform