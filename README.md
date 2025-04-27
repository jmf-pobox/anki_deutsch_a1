# Anki Deutsch A1

A specialized Anki deck generator for German language learning, focusing on A1 level vocabulary and grammar.

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
anki_deutsch_a1/
├── data/                  # CSV data files
│   └── backups/           # Automatic backups of enriched files
│   └── audio/             # Supporting audio
│   └── images/            # Supporting images
|
├── src/
│   └── langlearn/
│       ├── models/        # Pydantic models
│       ├── cards/         # Card generators
│       └── services/      # External service integrations
|
├── tests/                 # Test suites
|
└── languages/             # Language-specific documentation
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

3. Configure API keys using the sync-api-key utility, which stores secrets via keyring:
```bash
# For Anthropic API key
python src/langlearn/utils/sync-api-key.py ANTHROPIC_API_KEY your_api_key_here

# For Pexels API key
python src/langlearn/utils/sync-api-key.py PEXELS_API_KEY your_api_key_here
```

4. Configure AWS credentials for audio generation:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_region
```

## Usage

The project is currently in development. Once completed, it will provide:

1. Generation of Anki decks for German A1 vocabulary
2. Audio pronunciation for all words
3. Image associations for concrete nouns and adjectives
4. Example sentences for context
5. Grammar notes and tips
6. Automatic backups of enriched data files

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
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AWS Polly for text-to-speech
- Pexels for image integration
- Anki for the flashcard platform