# 🎓 Language Learning Flashcard Generator

**Multi-language Anki deck generator with intelligent language-specific features**

Create personalized vocabulary flashcards that understand the unique grammar challenges of your target language. Perfect for language learners and teachers who want effective, scientifically-designed study materials.

[![Languages](https://img.shields.io/badge/languages-German%20%7C%20Korean%20%7C%20Russian-brightgreen)](https://github.com/jmf-pobox/langlearn-anki)
[![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![CI](https://github.com/jmf-pobox/langlearn-anki/actions/workflows/ci.yml/badge.svg)](https://github.com/jmf-pobox/langlearn-anki/actions/workflows/ci.yml)
[![Last Commit](https://img.shields.io/github/last-commit/jmf-pobox/langlearn-anki)](https://github.com/jmf-pobox/langlearn-anki)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/jmf-pobox/langlearn-anki/blob/main/LICENSE)

---

## 🎯 Why This Tool Exists

**The Problem**: Most Anki decks are generic and don't address the specific challenges of learning different languages. Learning German articles (der/die/das) requires different strategies than Korean particles (은/는/이/가) or Russian cases.

**The Solution**: This generator creates flashcards that adapt to each language's unique grammar patterns, helping you learn more efficiently and effectively.

**Built for [Anki](https://github.com/ankitects/anki)**: Creates `.apkg` files compatible with the powerful Anki spaced repetition system.

**Inspiration**: Based on principles from *Fluent Forever* by Gabriel Wyner, emphasizing image-based learning and spaced repetition optimization.

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone and set up
git clone https://github.com/jmf-pobox/langlearn-anki.git
cd langlearn-anki
pip install hatch
hatch env create
```

### 2. Generate Your First Deck
```bash
# German (comprehensive A1-B1 vocabulary)
hatch run app --language german --deck default

# Russian (basic vocabulary with case system)
hatch run app --language russian --deck default

# Korean (basic vocabulary with particle system)
hatch run app --language korean --deck default
```

### 3. Import to Anki
1. Open Anki desktop application
2. **File > Import**
3. Select your `.apkg` file from the `output/` folder
4. Start studying!

---

## 🌍 Supported Languages

### 🇩🇪 **German** - Complete Implementation
- **Levels**: A1.1 (Beginner) → A1 (Elementary) → A2/B1 (Intermediate) + Business German
- **Grammar Features**: Der/die/das articles, 4-case system, verb conjugations, separable verbs
- **Vocabulary**: 1000+ words across all major word types
- **Special Focus**: Gender recognition, case usage, irregular plurals

```bash
# Available German decks
hatch run app --language german --deck a1.1     # Absolute beginner
hatch run app --language german --deck a1       # Elementary
hatch run app --language german --deck default  # Intermediate (most comprehensive)
hatch run app --language german --deck business # Professional vocabulary
```

### 🇷🇺 **Russian** - Basic Implementation
- **Level**: Basic vocabulary (5 essential nouns)
- **Grammar Features**: 6-case declensions, animacy distinctions, Cyrillic script
- **Focus**: Demonstrates different case system from German

```bash
hatch run app --language russian --deck default
```

### 🇰🇷 **Korean** - Basic Implementation
- **Level**: Basic vocabulary (5 essential nouns)
- **Grammar Features**: Particle system (은/는, 이/가, 을/를), counter/classifiers, Hangul typography
- **Focus**: Agglutinative language patterns, phonological rules

```bash
hatch run app --language korean --deck default
```

---

## 🎴 What Makes These Cards Special

### **Language-Specific Design**
Each language gets cards designed for its unique challenges:

**German Cards**: Focus on gender/article recognition
- Front: Image + "house" (English hint)
- Back: "das Haus" + plural "Häuser" + example sentence

**Korean Cards**: Focus on particle selection
- Front: Image + "student" (English hint)
- Back: "학생" + particles (학생이/학생은/학생을) + counter information

**Russian Cards**: Focus on case declensions
- Front: Image + "house" (English hint)
- Back: "дом" + all 6 case forms + animacy information

### **Rich Media Integration**
- **🔊 Audio**: Native pronunciation using AWS Polly (German: Marlene, Russian: Tatyana, Korean: Seoyeon)
- **🖼️ Images**: Contextual photos from Pexels based on example sentences
- **💡 Hint System**: Clean design with expandable translations

### **Proven Learning Techniques**
- **Visual Learning**: Images before text to build natural associations
- **Contextual Examples**: Real sentences, not isolated words
- **Graduated Difficulty**: Cards reveal information progressively

---

## 📚 For Language Teachers

### **Classroom Integration**
- **Customizable Vocabulary**: Edit CSV files to match your curriculum
- **CEFR-Aligned**: German decks follow established proficiency levels
- **Consistent Quality**: All cards follow the same professional design standards

### **Curriculum Support**
```bash
# Create custom vocabulary lists
# Edit files in: languages/{language}/{deck}/
# Example: languages/german/business/nouns.csv
```

**File Structure Example**:
```
languages/german/a1/
├── nouns.csv          # Nouns with articles and plurals
├── verbs.csv          # Conjugations and perfect tense
├── adjectives.csv     # Comparative/superlative forms
├── prepositions.csv   # Case requirements
└── phrases.csv        # Common expressions
```

---

## ⚙️ Advanced Features (Optional)

### **Enhanced Audio & Images**
Set up API keys for professional-quality media:

```bash
# German/Russian/Korean pronunciation (AWS Polly)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# Contextual images (Pexels)
python scripts/api_keyring.py add PEXELS_API_KEY your_key

# Test setup
hatch run test-env
```

### **Custom Output**
```bash
# Specify output filename
hatch run app --language german --deck a1 --output "My_German_A1_Deck.apkg"

# Check available options
hatch run app --help
```

---

## 🔧 Troubleshooting

### **Common Issues**

**❌ "No cards generated"**
- Verify CSV files exist in `languages/{language}/{deck}/`
- Run `hatch run test` to check system integrity

**❌ "Anki import failed"**
- Use Anki desktop (not AnkiWeb browser)
- Check that `.apkg` file exists in `output/` folder
- Try a smaller test deck: `hatch run app --language korean`

**❌ "No audio/images"**
- Media is optional - cards work without it
- Check API key setup in Advanced Features section
- Cards will still have text content and work perfectly

### **Getting Help**
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/jmf-pobox/langlearn-anki/issues)
- 💬 **Questions**: Create a GitHub issue with the "question" label
- 📖 **Documentation**: See developer docs in `docs/` folder

## 🙏 Credits

This project builds upon the excellent work of:

- **[Anki](https://github.com/ankitects/anki)** by Damien Elmes - The powerful spaced repetition system that makes effective learning possible
- **[Fluent Forever](https://fluent-forever.com/)** by Gabriel Wyner - Language learning methodology emphasizing image-based memory and spaced repetition

---

## 🔮 Future Languages

**Priority Languages**:
- **Hebrew**: Right-to-left script, verb binyanim system, vowel pointing
- **Bosnian/Croatian/Serbian (BCS)**: Case declensions, aspect pairs, Cyrillic/Latin scripts

**Additional Planned Languages**:
- **Spanish**: Gendered nouns, subjunctive mood, ser vs estar
- **French**: Nasal vowels, liaison rules, irregular verbs
- **Japanese**: Hiragana/Katakana/Kanji, honorific system, particles

Each language will get cards specifically designed for its unique learning challenges.

---

## 🏗️ For Developers

**Quick Developer Setup**:
```bash
hatch run test      # Verify everything works
hatch run type      # Type checking (must pass)
hatch run format    # Code formatting
```

**📋 Developer Documentation**:
- **Getting Started**: `docs/ENG-DESIGN-INDEX.md`
- **Architecture**: `docs/ENG-DEVELOPMENT-STANDARDS.md`
- **Standards**: `CLAUDE.md` and `docs/ENG-PYTHON-STANDARDS.md`
- **Language Specs**: `docs/GERMAN-LANGUAGE-SPEC.md`, `docs/RUSSIAN-LANGUAGE-SPEC.md`, `docs/KOREAN-LANGUAGE-SPEC.md`

**🤝 Contributing**: All contributions welcome! Please read `CLAUDE.md` for development workflow and quality standards.

---

*Built with ❤️ for language learners and teachers worldwide*