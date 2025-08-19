# 🎓 Language Learn - Smart Flashcard Generator

**Create personalized Anki flashcards that adapt to your target language's unique grammar challenges.**

Language Learn automatically generates intelligent flashcards designed for the specific grammar patterns and learning challenges of your target language. Instead of generic vocabulary cards, you get cards that understand noun genders, verb conjugations, and other language-specific features that make learning more effective.

[![CI](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml/badge.svg)](https://github.com/jmf-pobox/anki_deutsch_a1/actions/workflows/ci.yml)

## 🎯 What This Does For You

**Transform simple vocabulary lists into smart learning experiences:**
- **German nouns** → Cards that test article recall (der/die/das) separately from meaning
- **Verb conjugations** → Cards that practice irregular patterns and separable verbs  
- **Adjective forms** → Cards covering comparative and superlative forms
- **Pronunciation** → Audio files for proper pronunciation practice
- **Visual memory** → Images to reinforce vocabulary retention

## 🚀 Quick Start

### 1. Get Your Vocabulary Data Ready
Create CSV files with your target language vocabulary. The software currently includes German vocabulary, but you can use any language by providing your own CSV files:

```
data/
├── nouns.csv        # Your nouns with language-specific info
├── adjectives.csv   # Adjectives with comparison forms  
├── verbs.csv        # Verbs with conjugation patterns
├── adverbs.csv      # Adverbs and examples
└── phrases.csv      # Common phrases and expressions
```

### 2. Install the Software
```bash
# Clone the repository
git clone <repository-url>
cd language-learn

# Install dependencies
pip install hatch
hatch env create
```

### 3. Generate Your Flashcard Deck
```bash
# Basic deck generation (no audio/images)
python src/langlearn/main.py

# Advanced: With audio and images (requires API keys)
python src/langlearn/main.py --with-media
```

### 4. Import to Anki
1. Open Anki on your computer
2. Click "Import" 
3. Select the generated `.apkg` file from the `output/` folder
4. Start studying your personalized cards!

## 📝 Using Your Own Vocabulary

The software works with any vocabulary in CSV format. Here's how to create cards for your target language:

### Basic CSV Format Example (nouns.csv):
```csv
noun,article,english,plural,example,related
Hund,der,dog,Hunde,Der Hund bellt laut,Tier
Katze,die,cat,Katzen,Die Katze schläft,Tier  
Auto,das,car,Autos,Das Auto ist schnell,Fahrzeug
```

### Run with Your Data:
```bash
# Point to your data directory
python src/langlearn/main.py --data-dir /path/to/your/csv/files

# Specify output location  
python src/langlearn/main.py --output output/my_deck.apkg
```

## 🎨 Card Types Generated

### 🏠 **Noun Cards** (for languages with genders)
- **Front:** "dog" → **Back:** "der Hund" (tests article + word together)
- **Front:** "_____ Hund" → **Back:** "der" (tests article recall specifically)  
- **Front:** "Hund → Plural" → **Back:** "Hunde" (tests plural forms)

### ⚡ **Verb Cards** (for conjugated languages)
- **Front:** "to speak (ich)" → **Back:** "ich spreche" (tests conjugation)
- **Front:** "speak up (separable)" → **Back:** "ich stehe auf" (tests separable verbs)

### 🎯 **Smart Features**
- **Grammar-aware:** Cards adapt to your target language's specific challenges
- **Audio pronunciation:** Hear correct pronunciation (with API keys configured)
- **Visual learning:** Images help with vocabulary retention
- **Example sentences:** Learn words in context, not isolation

## ⚙️ Configuration

### Basic Usage (No Setup Required)
The software works out of the box with the included German vocabulary data.

### Enhanced Features (Optional Setup)
For audio and images, configure these services:

#### Audio Pronunciation (AWS Polly)
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret  
export AWS_DEFAULT_REGION=us-east-1
```

#### Visual Learning (Pexels Images)
```bash
python src/langlearn/utils/api_keyring.py add PEXELS_API_KEY your_key
```

## 🗂️ Organizing Your Deck

The software automatically organizes cards into logical subdecks:
```
My German Deck
├── Nouns
├── Verbs  
├── Adjectives
├── Adverbs
└── Phrases
```

You can customize the main deck name:
```bash
python src/langlearn/main.py --deck-name "My French A1 Vocabulary"
```

## 🔄 Planned Features

**Coming Soon:**
- **Multi-deck support:** Generate separate decks for different topics
- **Multi-language support:** Built-in support for Spanish, French, Italian, etc.
- **Voice recording:** Record yourself to compare with native pronunciation
- **Quiz modes:** Multiple choice for articles, verb forms, etc.
- **Progress tracking:** See which grammar patterns you've mastered

## 🆘 Getting Help

### Common Issues

**"No cards generated":** 
- Check that your CSV files are in the correct format
- Verify the data directory path is correct

**"Import failed in Anki":**
- Make sure you're using Anki desktop (not AnkiWeb)
- Try importing a smaller test deck first

**"Audio/images not working":**
- This feature requires API keys (see Configuration section)
- Cards will still work without media - only text will be shown

### Support
- 📧 **Issues:** [Report problems here](https://github.com/jmf-pobox/anki_deutsch_a1/issues)
- 📖 **Documentation:** See `docs/` folder for technical details
- 💬 **Discussions:** Ask questions in GitHub Discussions

## 🎓 Example: German Learning

The included German dataset demonstrates how Language Learn adapts to German's specific challenges:

**German Challenge:** *Noun genders (der/die/das) are arbitrary and must be memorized*
**Language Learn Solution:** *Separate cards test article recall vs. word meaning*

**German Challenge:** *Separable verbs work differently than English phrasal verbs*  
**Language Learn Solution:** *Cards specifically practice separable verb patterns*

**German Challenge:** *Adjective endings change based on case, gender, and definiteness*
**Language Learn Solution:** *Cards show adjectives in various contexts and declensions*

This same adaptive approach will extend to other languages as multi-language support is added.

---

## 🏗️ For Developers

<details>
<summary>Click to view technical details</summary>

### Development Setup
```bash
hatch env create
hatch run test        # Run tests
hatch run lint        # Check code quality  
```

### Architecture
- **Clean Pipeline:** CSV → Domain Models → Cards → Anki Deck
- **Language Agnostic:** Core engine supports any language with proper CSV data
- **Quality:** 401 tests, MyPy strict mode, comprehensive linting

### Contributing
1. Check `docs/DESIGN-INDEX.md` for navigation
2. Review `docs/DESIGN-GUIDANCE.md` for standards  
3. Add vocabulary data for new languages
4. Enhance card templates for different grammar patterns

</details>

---

**Transform your vocabulary lists into intelligent flashcards that understand your target language's unique challenges.**