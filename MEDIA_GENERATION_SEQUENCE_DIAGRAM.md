# MediaGenerationCapable Protocol - Sequence Diagram

## BEFORE: Broken Protocol Implementation ❌

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐    ┌─────────────────┐
│ DeckBuilder │    │ MediaEnricher   │    │ Phrase      │    │ AnthropicService│
└─────┬───────┘    └─────┬───────────┘    └─────┬───────┘    └─────┬───────────┘
      │                  │                      │                  │
      │ enrich_record()  │                      │                  │
      ├─────────────────►│                      │                  │
      │                  │                      │                  │
      │                  │ _enrich_phrase_record_clean()           │
      │                  ├─────────────────────┐│                  │
      │                  │                     ││                  │
      │                  │ get_anthropic_service()                 │
      │                  │◄────────────────────┘│                  │
      │                  │                      │                  │
      │                  │ get_image_search_strategy(svc)          │
      │                  ├─────────────────────►│                  │
      │                  │                      │                  │
      │                  │    strategy()        │                  │
      │                  │◄─────────────────────┤                  │
      │                  │                      │                  │
      │                  │                      │ _build_search_context()
      │                  │                      ├─────────────────┐│
      │                  │                      │  returns STRING ││
      │                  │                      │◄────────────────┘│
      │                  │                      │                  │
      │                  │                      │ generate_pexels_query(context_string)
      │                  │                      ├─────────────────►│
      │                  │                      │                  │
      │                  │                      │                  │ ❌ ERROR!
      │                  │                      │                  │ context_string.word
      │                  │                      │                  │ 'str' has no 'word'
      │                  │                      │                  │
      │                  │                      │ ❌ EXCEPTION     │
      │                  │                      │◄─────────────────┤
      │                  │                      │                  │
      │                  │ ❌ WARNING logged    │                  │
      │                  │◄─────────────────────┤                  │
      │                  │                      │                  │
      │ ❌ Fallback used │                      │                  │
      │◄─────────────────┤                      │                  │
```

## AFTER: Fixed Protocol Implementation ✅

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐
│ DeckBuilder │    │ MediaEnricher   │    │ Phrase      │    │PhraseAdapter│    │ AnthropicService│
└─────┬───────┘    └─────┬───────────┘    └─────┬───────┘    └─────┬───────┘    └─────┬───────────┘
      │                  │                      │                  │                  │
      │ __init__(anthropic_service)              │                  │                  │
      ├─────────────────►│                      │                  │                  │
      │                  │ self._anthropic_service = svc            │                  │
      │                  ├─────────────────────┐│                  │                  │
      │                  │                     ││                  │                  │
      │                  │◄────────────────────┘│                  │                  │
      │                  │                      │                  │                  │
      │ enrich_record()  │                      │                  │                  │
      ├─────────────────►│                      │                  │                  │
      │                  │                      │                  │                  │
      │                  │ _enrich_phrase_record_clean()           │                  │
      │                  ├─────────────────────┐│                  │                  │
      │                  │                     ││                  │                  │
      │                  │ get_image_search_strategy(self._anthropic_service)         │
      │                  ├─────────────────────►│                  │                  │
      │                  │                      │                  │                  │
      │                  │    strategy()        │                  │                  │
      │                  │◄─────────────────────┤                  │                  │
      │                  │                      │                  │                  │
      │                  │                      │ PhraseAdapter(self)                 │
      │                  │                      ├─────────────────►│                  │
      │                  │                      │                  │ .word = phrase   │
      │                  │                      │                  │ .english = english│
      │                  │                      │                  │ .example = context│
      │                  │                      │                  │                  │
      │                  │                      │ generate_pexels_query(adapter)     │
      │                  │                      ├─────────────────────────────────────►│
      │                  │                      │                  │                  │
      │                  │                      │                  │ ✅ SUCCESS!     │
      │                  │                      │                  │ adapter.word     │
      │                  │                      │                  │ adapter.english  │
      │                  │                      │                  │ adapter.example  │
      │                  │                      │                  │                  │
      │                  │                      │ ✅ English search terms           │
      │                  │                      │◄─────────────────────────────────────┤
      │                  │                      │                  │                  │
      │                  │ ✅ Search terms     │                  │                  │
      │                  │◄─────────────────────┤                  │                  │
      │                  │                      │                  │                  │
      │                  │ _get_or_generate_image(terms)           │                  │
      │                  ├─────────────────────┐│                  │                  │
      │                  │                     ││                  │                  │
      │                  │◄────────────────────┘│                  │                  │
      │                  │                      │                  │                  │
      │ ✅ Enriched record                      │                  │                  │
      │◄─────────────────┤                      │                  │                  │
```

## Architecture Components

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           CLEAN PIPELINE ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────────────────────────┐  │
│  │ CSV Records │───►│ MediaEnricher   │───►│ Enriched Records with Media         │  │
│  └─────────────┘    └─────────────────┘    └─────────────────────────────────────┘  │
│                              │                                                      │
│                              │ MediaGenerationCapable Protocol                     │
│                              ▼                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN MODELS (SMART)                                   │   │
│  │                                                                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │
│  │  │    Noun     │  │  Adjective  │  │    Verb     │  │      Phrase         │  │   │
│  │  │             │  │             │  │             │  │                     │  │   │
│  │  │ .word       │  │ .word       │  │ .verb       │  │ .phrase             │  │   │
│  │  │ .english    │  │ .english    │  │ .english    │  │ .english            │  │   │
│  │  │ .example    │  │ .example    │  │ .example    │  │ .context            │  │   │
│  │  │             │  │             │  │             │  │                     │  │   │
│  │  │ German      │  │ German      │  │ German      │  │ German              │  │   │
│  │  │ Grammar     │  │ Grammar     │  │ Conjugation │  │ Pragmatics          │  │   │
│  │  │ Rules       │  │ Rules       │  │ Rules       │  │ Rules               │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                              │                                                      │
│                              │ get_image_search_strategy()                          │
│                              ▼                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    EXTERNAL SERVICES (DUMB)                                │   │
│  │                                                                             │   │
│  │  ┌─────────────────┐                      ┌─────────────────┐              │   │
│  │  │ AnthropicService│                      │  PexelsService  │              │   │
│  │  │                 │                      │                 │              │   │
│  │  │ generate_pexels_│ ────────────────────►│ search_photos() │              │   │
│  │  │ query()         │  English search terms│                 │              │   │
│  │  │                 │                      │                 │              │   │
│  │  │ Expects:        │                      │ Returns:        │              │   │
│  │  │ .word           │                      │ Image URLs      │              │   │
│  │  │ .english        │                      │                 │              │   │
│  │  │ .example        │                      │                 │              │   │
│  │  └─────────────────┘                      └─────────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Key Fixes Applied

### 1. Interface Adapter Pattern
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Phrase Model    │    │ PhraseAdapter   │    │ AnthropicService│
│                 │    │                 │    │                 │
│ .phrase         │───►│ .word           │───►│ expects .word   │
│ .english        │───►│ .english        │───►│ expects .english│
│ .context        │───►│ .example        │───►│ expects .example│
│ .related        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Dependency Injection Fix
```
❌ OLD: get_anthropic_service()  (dynamic lookup)
✅ NEW: self._anthropic_service  (injected dependency)
```

### 3. Method Standardization  
```
❌ OLD: self.generate_image()         (inconsistent)
✅ NEW: self._get_or_generate_image()  (standard pattern)
```

## Error Elimination Results

```
BEFORE (❌ Broken):
│ WARNING - AI generation failed for 'Nun...': 'str' object has no attribute 'word'
│ WARNING - AI generation failed for 'Ja, also...': 'str' object has no attribute 'word'
│ [75+ similar errors for all phrase records]

AFTER (✅ Fixed):
│ [No 'str' object has no attribute 'word' errors]
│ ✅ Phrase enrichment working correctly
│ ✅ AI-generated English search terms
│ ✅ MediaGenerationCapable protocol functional
```

## Protocol Success Flow

```
1. CSV Record     ──► 2. Domain Model    ──► 3. Search Strategy ──► 4. AI Service
   {"phrase":...}     Phrase(phrase=...)     get_image_search...     generate_pexels...
                                                     │
8. Enriched       ◄── 7. Image Generated ◄── 6. Pexels API    ◄── 5. English Terms
   {"image":...}       <img src="...">        download_image()       "business meeting"
```

**Result**: Complete elimination of phrase MediaGenerationCapable protocol errors! ✅