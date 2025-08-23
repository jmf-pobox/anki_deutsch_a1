# Article Card Redesign: Cloze Deletion Implementation

## Current Problems

### Template-Field Mismatch Issues
- Templates reference fields (`{{NounOnly}}`, `{{NounEnglish}}`) that don't exist in note types
- Complex field mapping pipeline between ArticlePatternProcessor → CardBuilder → TemplateService → AnkiBackend
- Cards render blank because templates can't find expected fields
- Brittle multi-template system requiring separate HTML/CSS files for each card type

### Architecture Complexity
- **5 cards per article record**: 1 gender recognition + 4 case context cards
- **2 separate template files per card type**: `artikel_gender_DE_de_*.html` and `artikel_context_DE_de_*.html`
- **Complex field mapping**: 22+ fields in CardBuilder mappings for article templates
- **Error-prone template syntax**: Mustache tag mismatches causing card generation failures
- **Dual card systems**: ArticlePatternProcessor (pure article cards) + ArticleApplicationService (noun-article integration)

## Solution: Migrate to Anki Cloze Deletion Cards

### Core Concept
Replace the current 5-template system with **2 simple Cloze Deletion note types**:

1. **Article Gender Recognition Cloze**: Test gender recall with German explanations
   - Text: `"{{c1::Der}} Mann ist hier"`
   - Card shows: `"_____ Mann ist hier"`
   - Answer: `"**Der** Mann ist hier"`
   - Explanation: `"Maskulin - Nominativ (wer/was?)"`
   
2. **Article Case Context Cloze**: Test case-specific article usage with German case explanations
   - Text: `"Ich sehe {{c1::den}} Mann"`
   - Card shows: `"Ich sehe _____ Mann"`
   - Answer: `"Ich sehe **den** Mann"`
   - Explanation: `"Maskulin - Akkusativ (wen/was? direktes Objekt)"`

### Benefits
- **Eliminates field mapping complexity**: Only needs single "Text" field + optional extras
- **Removes template-field mismatches**: No more missing `{{NounOnly}}` field issues
- **Native Anki feature**: More reliable than custom template system
- **Automatic card generation**: Anki handles cloze → multiple cards conversion
- **Simpler testing**: Single field to populate vs 22+ field mappings
- **German-immersive learning**: Explanations in German reinforce language acquisition

### German Explanation System

#### Case Explanations (in German)
- **Nominativ**: "wer/was? - Subjekt des Satzes"
- **Akkusativ**: "wen/was? - direktes Objekt"  
- **Dativ**: "wem? - indirektes Objekt"
- **Genitiv**: "wessen? - Besitz und bestimmte Präpositionen"

#### Gender + Case Combinations
- **Maskulin Nominativ**: "der - Maskulin Nominativ (wer/was?)"
- **Maskulin Akkusativ**: "den - Maskulin Akkusativ (wen/was? direktes Objekt)"
- **Maskulin Dativ**: "dem - Maskulin Dativ (wem? indirektes Objekt)"
- **Maskulin Genitiv**: "des - Maskulin Genitiv (wessen? Besitz)"

#### Article Type Explanations
- **Bestimmter Artikel**: "der/die/das - bestimmter Artikel"
- **Unbestimmter Artikel**: "ein/eine - unbestimmter Artikel" 
- **Verneinender Artikel**: "kein/keine - verneinender Artikel"

## Implementation Design

### Affected Files

#### Core Logic Changes
- `src/langlearn/services/article_pattern_processor.py` - **MAJOR REWRITE**
  - Replace `_create_gender_recognition_card()` and `_create_case_context_card()`
  - Add `_create_gender_cloze_card()` and `_create_case_cloze_card()`
  - Generate cloze syntax directly instead of template field population

#### Template System Simplification  
- `src/langlearn/templates/` - **REMOVE 6 FILES**
  - Delete: `artikel_gender_DE_de_front.html`, `artikel_gender_DE_de_back.html`, `artikel_gender_DE_de.css`
  - Delete: `artikel_context_DE_de_front.html`, `artikel_context_DE_de_back.html`, `artikel_context_DE_de.css`

#### Field Mapping Cleanup
- `src/langlearn/services/card_builder.py` - **SIMPLIFY**
  - Replace 22-field `artikel_gender` mapping with 3-field cloze mapping: `["Text", "Image", "Audio"]`
  - Replace 22-field `artikel_context` mapping with 3-field cloze mapping: `["Text", "Image", "Audio"]`

#### Backend Configuration
- `src/langlearn/backends/anki_backend.py` - **UPDATE MAPPINGS**
  - Update note type mappings to support cloze card types
  - Add cloze deletion note type support

### Implementation Steps

#### Phase 1: Create New Cloze Generators
1. **Add cloze generation methods to ArticlePatternProcessor**:
   ```python
   def _create_gender_cloze_card(self, record, enriched_data):
       """Generate: '{{c1::Der}} Mann ist hier' for gender recognition"""
       
   def _create_case_cloze_card(self, record, case, enriched_data):  
       """Generate: 'Ich sehe {{c1::den}} Mann' for case context"""
   ```

2. **Update main processing methods**:
   - `_generate_cards_for_record()`: Call new cloze methods instead of template methods
   - Maintain 5 cards per record (1 gender + 4 case contexts)

#### Phase 2: Update CardBuilder Integration
1. **Add cloze note type support**:
   - `artikel_gender_cloze` field mapping: `["Text", "Image", "Audio"]` 
   - `artikel_context_cloze` field mapping: `["Text", "Image", "Audio"]`

2. **Update template service**:
   - Add cloze note type creation (uses Anki's built-in cloze template)
   - Remove custom template file loading for article cards

#### Phase 3: Backend Integration
1. **Update AnkiBackend mappings**:
   ```python
   "German Artikel Gender Cloze": "artikel_gender_cloze",
   "German Artikel Context Cloze": "artikel_context_cloze",
   ```

2. **Test cloze card generation**: Verify Anki properly creates multiple cards from cloze text

#### Phase 4: Cleanup
1. **Remove obsolete template files**: 6 artikel template files
2. **Remove complex field mappings**: 44+ field definitions for old article templates  
3. **Update tests**: Modify article card tests to expect cloze format

### Data Examples

#### Current (Broken) Approach:
```python
# ArticlePatternProcessor generates:
card_data = {
    "FrontText": "_____ Haus", 
    "BackText": "das Haus",
    "NounOnly": "Haus",        # ← Field doesn't exist in note type
    "NounEnglish": "house",    # ← Field doesn't exist in note type
    "Gender": "neutral",
    # ... 18 more fields
}
```

#### New Cloze Approach:
```python
# ArticlePatternProcessor generates:
card_data = {
    "Text": "{{c1::Das}} Haus ist groß",  # ← Single field, native Anki feature
    "Explanation": "Neutrum - Nominativ (wer/was? Subjekt)",  # ← German explanation
    "Image": "haus.jpg",
    "Audio": "[sound:das_haus.mp3]"
}
# Anki automatically creates card: "_____ Haus ist groß" → "Das Haus ist groß"
# With explanation: "Neutrum - Nominativ (wer/was? Subjekt)"
```

## Risk Assessment

### Low Risk Changes
- **Cloze deletion is native Anki**: Well-tested, reliable feature
- **Simpler data flow**: Fewer points of failure than current template system  
- **Backward compatibility**: Can implement alongside existing system, migrate gradually

### Medium Risk Changes  
- **ArticlePatternProcessor rewrite**: Core logic changes, needs thorough testing
- **Field mapping changes**: Must ensure CardBuilder correctly handles cloze fields

### Validation Plan
1. **Unit tests**: Test cloze text generation for all article types and cases
2. **Integration tests**: Verify Anki creates correct number of cards from cloze text
3. **Manual testing**: Import generated deck and verify card behavior in Anki

## Success Metrics
- **Zero template-field mismatch errors**: No more blank cards
- **Reduced complexity**: 6 template files → 0, 44+ field mappings → 6  
- **Maintained functionality**: Still generates 5 cards per article record
- **Improved reliability**: Native Anki cloze system vs custom template system

## Scope Boundaries
- **IN SCOPE**: ArticlePatternProcessor (pure article cards)
- **OUT OF SCOPE**: ArticleApplicationService (noun-article integration cards) - keep existing system
- **COMPATIBILITY**: Existing noun, verb, adjective cards unchanged