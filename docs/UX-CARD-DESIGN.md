# UX Card Design - Language Learn Multi-Language Flashcard Generator

## Executive Summary

**Status**: Production-ready template system with German A1 implementation  
**Last Updated**: 2025-08-21  
**Architecture**: HTML/CSS template system with responsive and accessible design  
**Integration**: Clean Pipeline Architecture with CardBuilder service

## Table of Contents

1. [Requirements](#requirements)
2. [Style Guidelines](#style-guidelines)
3. [Implementation Overview](#implementation-overview)
4. [Template Architecture](#template-architecture)
5. [Field Mapping System](#field-mapping-system)
6. [Media Integration](#media-integration)
7. [Language-Specific Features](#language-specific-features)
8. [Design Patterns](#design-patterns)
9. [Future Enhancements](#future-enhancements)

## Requirements

### Functional Requirements

#### Core Features
- **Multi-language Support**: Template system must support any language with proper RTL/LTR handling
- **Word Type Coverage**: Templates for all grammatical categories (nouns, verbs, adjectives, etc.)
- **Media Integration**: Seamless embedding of audio and images
- **Progressive Disclosure**: Hint system for gradual learning
- **Responsive Design**: Optimal display on mobile and desktop devices

#### Learning Experience
- **Active Recall**: Front side prompts memory retrieval without giving away answers
- **Context-Based Learning**: Example sentences provide usage context
- **Multi-sensory Input**: Visual (images), auditory (audio), and textual learning
- **Grammar Focus**: Language-specific grammatical features highlighted
- **Difficulty Progression**: Hints available for struggling learners

### Non-Functional Requirements

#### Performance
- **Fast Loading**: Minimal CSS and JavaScript for quick card rendering
- **Efficient Caching**: Template caching via TemplateService
- **Lazy Media Loading**: Images and audio load only when needed

#### Accessibility
- **Screen Reader Support**: Semantic HTML structure
- **Keyboard Navigation**: All interactive elements keyboard-accessible
- **High Contrast**: Support for dark mode and high contrast themes
- **Font Scaling**: Responsive typography for readability

#### Maintainability
- **Template Separation**: HTML, CSS, and content clearly separated
- **Naming Conventions**: Consistent file naming (e.g., `{word_type}_front.html`)
- **Modular CSS**: Reusable style classes across templates
- **Version Control**: Template changes tracked with meaningful commits

## Style Guidelines

### Visual Design Principles

#### 1. Clarity First
```css
/* Primary content stands out */
.german {
    font-size: 28px;
    font-weight: bold;
    color: #2c5aa0;  /* German blue */
}

/* Secondary information is subtle */
.part-of-speech {
    font-size: 16px;
    color: #666;
    font-style: italic;
}
```

#### 2. Visual Hierarchy
- **Level 1**: Target word/phrase (largest, boldest)
- **Level 2**: English translation or prompt (medium, highlighted)
- **Level 3**: Example sentences (smaller, styled differently)
- **Level 4**: Metadata (smallest, subtle styling)

#### 3. Color Scheme
```css
/* Primary Colors */
--primary-blue: #2c5aa0;      /* German language association */
--success-green: #4CAF50;     /* Hints and positive actions */
--background-light: #f8f9fa;  /* Card background */
--text-primary: #333;          /* Main text */
--text-secondary: #666;        /* Supporting text */

/* Semantic Colors */
--hint-bg: #e8f4fd;           /* Light blue for hints */
--example-bg: #f0f4f8;        /* Subtle background for examples */
--border-accent: #2c5aa0;     /* Accent borders */
```

#### 4. Typography
```css
/* Font Stack */
font-family: Arial, sans-serif;  /* Universal readability */

/* Size Scale */
--font-xl: 28px;   /* Primary word */
--font-lg: 24px;   /* English prompts */
--font-md: 18px;   /* Hints */
--font-base: 16px; /* Examples, metadata */
--font-sm: 14px;   /* Additional info */
--font-xs: 12px;   /* Audio indicators */
```

### Component Design Standards

#### Card Container
```css
.card {
    font-family: Arial, sans-serif;
    text-align: center;
    background-color: #f8f9fa;
    padding: 20px;
    color: #333;
}
```

#### Interactive Elements
```css
.hint-button {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    font-size: 16px;
    border-radius: 25px;  /* Rounded for friendliness */
    cursor: pointer;
    transition: background-color 0.3s;
}

.hint-button:hover {
    background: #45a049;  /* Darker on hover */
}
```

#### Media Components
```css
.image-container img {
    max-width: 250px;
    max-height: 170px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.inline-audio {
    font-size: 12px;
    background: #f1f3f4;
    padding: 4px 8px;
    border-radius: 12px;
    cursor: pointer;
}
```

### Responsive Design

#### Mobile Optimization
```css
@media (max-width: 768px) {
    .card { padding: 15px; }
    .german { font-size: 24px; }
    .english-prompt { font-size: 20px; }
    img { max-width: 200px; max-height: 140px; }
    
    /* Stack audio controls vertically on mobile */
    .word-with-audio, .example-with-audio {
        flex-direction: column;
        gap: 8px;
    }
}
```

#### Dark Mode Support
```css
@media (prefers-color-scheme: dark) {
    .card {
        background-color: #2d3748;
        color: #e2e8f0;
    }
    
    .noun-forms {
        background: #4a5568;
        border-color: #63b3ed;
    }
}
```

## Implementation Overview

### Template Service Architecture

```python
class TemplateService:
    """Manages Anki card templates with external file loading and caching."""
    
    def __init__(self, template_dir: Path):
        self._template_dir = template_dir
        self._cache: dict[str, CardTemplate] = {}
    
    def get_template(self, card_type: str) -> CardTemplate:
        """Get template with caching for performance."""
        if card_type not in self._cache:
            self._cache[card_type] = self._load_template(card_type)
        return self._cache[card_type]
```

### CardBuilder Integration

```python
class CardBuilder:
    """Builds formatted cards from enriched records using templates."""
    
    def build_card_from_record(
        self, 
        record: BaseRecord, 
        enriched_data: dict[str, Any] | None = None
    ) -> tuple[list[str], NoteType]:
        # 1. Get record type
        record_type = self._get_record_type_from_instance(record)
        
        # 2. Load template
        template = self._template_service.get_template(record_type)
        
        # 3. Create note type with fields
        note_type = self._create_note_type_for_record(record_type, template)
        
        # 4. Extract field values
        field_values = self._extract_field_values(record_type, card_data, note_type)
        
        return field_values, note_type
```

### File Organization

```
src/langlearn/templates/
├── Clean Pipeline Templates (Modern)
│   ├── noun_front.html
│   ├── noun_back.html
│   ├── noun.css
│   ├── adjective_front.html
│   ├── adjective_back.html
│   ├── adjective.css
│   ├── adverb_front.html
│   ├── adverb_back.html
│   ├── adverb.css
│   └── negation_*.{html,css}
│
├── Verb Templates (Complex)
│   ├── verb_conjugation_front.html
│   ├── verb_conjugation_back.html
│   ├── verb_conjugation.css
│   ├── verb_imperative_front.html
│   ├── verb_imperative_back.html
│   └── verb_imperative.css
│
└── Legacy Templates (Language-specific)
    ├── phrase_DE_de_*.{html,css}
    ├── preposition_DE_de_*.{html,css}
    └── verb_DE_de_*.{html,css}
```

## Template Architecture

### Template Components

#### 1. Front Template (Question Side)
```html
<!-- Standard Structure -->
{{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}

<div class="part-of-speech">{{PartOfSpeech}}</div>

<div class="hint-container">
    <button class="hint-button" onclick="showHint()">💡 Hint</button>
    <div id="hint-content" class="hint-content hidden">{{English}}</div>
</div>

<script>
function showHint() {
    var hint = document.getElementById('hint-content');
    var button = document.querySelector('.hint-button');
    hint.classList.remove('hidden');
    button.style.display = 'none';
}
</script>
```

#### 2. Back Template (Answer Side)
```html
<!-- Word with Audio -->
<div class="word-with-audio">
    <span class="german">{{Word}}</span>
    {{#WordAudio}}<span class="inline-audio">🔊 {{WordAudio}}</span>{{/WordAudio}}
</div>

<!-- Grammar Information -->
<div class="grammar-info">
    <!-- Word-type specific fields -->
</div>

<!-- Example with Audio -->
<div class="example-with-audio">
    <span class="example-sentence">{{Example}}</span>
    {{#ExampleAudio}}<span class="inline-audio">🔊 {{ExampleAudio}}</span>{{/ExampleAudio}}
</div>
```

#### 3. CSS Template
```css
/* Base styles applied to all cards */
.card { /* ... */ }

/* Component-specific styles */
.german { /* ... */ }
.example-sentence { /* ... */ }

/* Word-type specific styles */
.noun-forms { /* ... */ }
.verb-conjugation { /* ... */ }

/* Responsive and theme support */
@media (max-width: 768px) { /* ... */ }
@media (prefers-color-scheme: dark) { /* ... */ }
```

### Template Variables

#### Standard Fields (All Templates)
- `{{Word}}` or `{{Noun}}/{{Verb}}` - Target vocabulary
- `{{English}}` - English translation
- `{{Example}}` - Example sentence
- `{{Image}}` - Visual representation
- `{{WordAudio}}` - Pronunciation audio
- `{{ExampleAudio}}` - Example sentence audio

#### Word-Type Specific Fields

**Nouns**:
- `{{Article}}` - der/die/das
- `{{Plural}}` - Plural form
- `{{Related}}` - Related words

**Adjectives**:
- `{{Comparative}}` - Comparative form
- `{{Superlative}}` - Superlative form

**Verbs**:
- `{{Classification}}` - Regular/irregular
- `{{Separable}}` - Separable verb indicator
- `{{Auxiliary}}` - haben/sein
- `{{Tense}}` - Tense being practiced
- `{{Ich}}, {{Du}}, {{Er}}...` - Conjugated forms

## Field Mapping System

### Record to Field Mapping

```python
field_mappings = {
    "noun": [
        "Noun", "Article", "English", "Plural", 
        "Example", "Related", "Image", "WordAudio", "ExampleAudio"
    ],
    "adjective": [
        "Word", "English", "Example", "Comparative", 
        "Superlative", "Image", "WordAudio", "ExampleAudio"
    ],
    "verb_conjugation": [
        "Infinitive", "English", "Classification", "Separable",
        "Auxiliary", "Tense", "Ich", "Du", "Er", "Wir", "Ihr", 
        "Sie", "Example", "Image", "WordAudio", "ExampleAudio"
    ]
}
```

### Field Value Extraction

```python
def _extract_field_values(self, record_type: str, card_data: dict, note_type: NoteType):
    """Maps record data to Anki field values."""
    field_mapping = self._get_field_mapping(record_type)
    field_values = []
    
    for field_name in note_type.fields:
        # Convert field name to record attribute
        attr_name = self._field_to_attribute(field_name)
        
        # Get value with fallback to empty string
        value = card_data.get(attr_name, "")
        
        # Format media fields
        if "Audio" in field_name or "Image" in field_name:
            value = self._format_media_field(value)
        
        field_values.append(value)
    
    return field_values
```

## Media Integration

### Image Integration

#### Template Markup
```html
{{#Image}}
<div class="image-container">
    {{Image}}  <!-- Anki replaces with <img> tag -->
</div>
{{/Image}}
```

#### CSS Styling
```css
.image-container {
    margin: 10px 0;
}

img {
    max-width: 250px;
    max-height: 170px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

### Audio Integration

#### Inline Audio Controls
```html
{{#WordAudio}}
<span class="inline-audio">🔊 {{WordAudio}}</span>
{{/WordAudio}}
```

#### Audio Styling
```css
.inline-audio {
    font-size: 12px;
    color: #666;
    background: #f1f3f4;
    padding: 4px 8px;
    border-radius: 12px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.inline-audio:hover {
    background: #e8f0fe;
    border-color: #2c5aa0;
}
```

### Media Enrichment Pipeline

```python
# Media enrichment flow
CSV Data → RecordMapper → MediaEnricher → CardBuilder → Anki Backend

# MediaEnricher responsibilities:
1. Check for existing media files
2. Generate missing audio via AWS Polly
3. Search and download images via Pexels
4. Return media file paths for embedding
```

## Language-Specific Features

### German Language Templates

#### Noun Gender Visualization
```html
<div class="noun-forms">
    <div class="word-with-audio">
        <span class="german">{{Article}} {{Noun}}</span>
        <!-- Article color-coded by gender -->
    </div>
    <div class="plural-form">
        <strong>Plural:</strong> {{Plural}}
    </div>
</div>
```

#### Verb Conjugation Grid
```html
<div class="conjugation-grid">
    <div class="conjugation-row">
        <span class="pronoun">ich</span>
        <span class="conjugated-form">{{Ich}}</span>
    </div>
    <!-- Repeated for all pronouns -->
</div>
```

#### Case-Dependent Prepositions
```html
<div class="preposition-info">
    <div class="case-requirement">
        <strong>Case:</strong> {{Case}}
    </div>
    <div class="examples">
        {{Example1}} / {{Example2}}
    </div>
</div>
```

### Multi-Language Considerations

#### RTL Language Support
```css
/* Future Arabic/Hebrew support */
[dir="rtl"] .card {
    direction: rtl;
    text-align: right;
}

[dir="rtl"] .word-with-audio {
    flex-direction: row-reverse;
}
```

#### Character Set Support
```css
/* CJK language support */
.card.cjk {
    font-family: "Noto Sans CJK", "Microsoft YaHei", sans-serif;
    line-height: 1.6;  /* Better spacing for complex characters */
}
```

#### Language-Specific Naming
```
# Template naming convention for future languages
{word_type}_{language_code}_{country_code}_front.html
verb_FR_fr_front.html  # French verb
noun_JA_jp_front.html   # Japanese noun
```

## Design Patterns

### Progressive Disclosure Pattern

```javascript
// Hint system reveals information gradually
function showHint() {
    // 1. Hide button after click (one-time reveal)
    button.style.display = 'none';
    
    // 2. Show hint content with animation
    hint.classList.remove('hidden');
    
    // 3. Track hint usage for spaced repetition algorithm
    // (Future enhancement)
}
```

### Conditional Rendering Pattern

```html
<!-- Only show element if field has content -->
{{#Related}}
<div class="related-words">
    <strong>Related:</strong> {{Related}}
</div>
{{/Related}}
```

### Component Composition Pattern

```css
/* Base component */
.info-box {
    padding: 10px;
    background: #f0f4f8;
    border-radius: 5px;
}

/* Specialized variants */
.noun-forms {
    @extend .info-box;
    border: 2px solid #2c5aa0;
}

.verb-conjugation {
    @extend .info-box;
    display: grid;
    grid-template-columns: 1fr 2fr;
}
```

### Responsive Container Pattern

```css
/* Container queries for component-level responsiveness */
.conjugation-grid {
    container-type: inline-size;
}

@container (max-width: 400px) {
    .conjugation-grid {
        grid-template-columns: 1fr;  /* Stack on small screens */
    }
}
```

## Future Enhancements

### Planned Features

#### 1. Interactive Elements
- **Input Fields**: Type answer before revealing
- **Drag-and-Drop**: Match words with translations
- **Audio Recording**: Compare pronunciation with native speaker

#### 2. Advanced Styling
- **Theme System**: User-selectable color themes
- **Animation**: Subtle transitions for better UX
- **Gamification**: Progress bars and achievement badges

#### 3. Multi-Language Templates
- **Template Inheritance**: Base templates for all languages
- **Language Packs**: Downloadable template sets
- **Cultural Customization**: Region-specific imagery and examples

#### 4. Accessibility Improvements
- **ARIA Labels**: Enhanced screen reader support
- **Keyboard Shortcuts**: Quick navigation between cards
- **High Contrast Mode**: Beyond basic dark mode

#### 5. Learning Analytics
- **Hint Usage Tracking**: Identify struggling areas
- **Time-on-Card Metrics**: Measure difficulty
- **Visual Progress Indicators**: Show mastery level

### Template Extension Points

```python
class TemplateService:
    def register_custom_template(self, word_type: str, template: CardTemplate):
        """Allow plugins to register custom templates."""
        pass
    
    def apply_theme(self, theme_name: str):
        """Apply user-selected theme to all templates."""
        pass
    
    def get_template_with_variant(self, card_type: str, variant: str):
        """Support template variants (e.g., 'simple', 'detailed')."""
        pass
```

### Community Templates

```yaml
# Future template manifest format
name: "Visual German Nouns"
version: "1.0.0"
language: "de_DE"
word_types: ["noun"]
features:
  - large_images
  - gender_colors
  - etymology_hints
files:
  - noun_visual_front.html
  - noun_visual_back.html
  - noun_visual.css
```

## Best Practices

### Template Development

1. **Start Simple**: Basic HTML structure first, enhance progressively
2. **Test on Devices**: Verify on both mobile and desktop Anki
3. **Validate Accessibility**: Use screen readers to test
4. **Optimize Performance**: Minimize CSS and JavaScript
5. **Document Fields**: Clear documentation of required fields

### CSS Guidelines

1. **Use CSS Variables**: For consistent theming
2. **Mobile-First**: Design for mobile, enhance for desktop
3. **Avoid !important**: Use specificity properly
4. **Semantic Classes**: Name by purpose, not appearance
5. **Comment Complex Styles**: Explain non-obvious styling choices

### JavaScript Guidelines

1. **Minimal JavaScript**: Only for essential interactivity
2. **No External Dependencies**: Anki doesn't support external libraries
3. **Defensive Coding**: Check for element existence
4. **Event Delegation**: For dynamically added elements
5. **Performance**: Avoid expensive operations

### Testing Templates

```python
# Test template rendering
def test_noun_template():
    template = template_service.get_template("noun")
    assert "{{Article}}" in template.front_html
    assert "{{Plural}}" in template.back_html
    assert ".noun-forms" in template.css

# Test field mapping
def test_noun_field_mapping():
    fields = card_builder._get_field_names_for_record_type("noun")
    assert "Article" in fields
    assert "Plural" in fields
    assert len(fields) == 9
```

## Conclusion

The Language Learn template system provides a robust, extensible foundation for multi-language flashcard generation. With its focus on clean architecture, responsive design, and language-specific features, it delivers an optimal learning experience while maintaining code quality and extensibility for future enhancements.

The current German A1 implementation serves as a reference for adding new languages, demonstrating best practices in template design, media integration, and user experience optimization. The system's modular architecture ensures that new languages and card types can be added without disrupting existing functionality.