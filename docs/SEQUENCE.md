# German A1 Deck Generator - Execution Sequence

This sequence diagram shows the complete flow when `main.py` is executed to generate a German A1 vocabulary Anki deck.

```
User    main.py   GermanDeckBuilder   GenanKiBackend   CSVService   MediaService   AudioService   TemplateService   DeckManager
 |         |              |                 |             |             |             |               |              |
 |-------->|              |                 |             |             |             |               |              |
 |      python main.py    |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |----.         |                 |             |             |             |               |              |
 |         |    | Setup   |                 |             |             |             |               |              |
 |         |    | logging |                 |             |             |             |               |              |
 |         |    | & paths |                 |             |             |             |               |              |
 |         |<---'         |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |------------->|                 |             |             |             |               |              |
 |         |  __init__(   |                 |             |             |             |               |              |
 |         | deck_name,   |                 |             |             |             |               |              |
 |         | backend_type,|                 |             |             |             |               |              |
 |         | enable_media)|                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |----.            |             |             |             |               |              |
 |         |              |    | Initialize |             |             |             |               |              |
 |         |              |    | Services   |             |             |             |               |              |
 |         |              |<---'            |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |------------------------------>|             |             |               |              |
 |         |              |              CSVService()     |             |             |               |              |
 |         |              |<------------------------------|             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |---------------------------------------------------------->|               |              |
 |         |              |                       TemplateService(template_dir)      |               |              |
 |         |              |<----------------------------------------------------------|               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |------------------------------------------>|             |               |              |
 |         |              |              MediaService()              |             |               |              |
 |         |              |                 |             |---------->|             |               |              |
 |         |              |                 |          AudioService() |             |               |              |
 |         |              |                 |             |<----------|             |               |              |
 |         |              |<------------------------------------------|             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |---------------->|             |             |             |               |              |
 |         |              |  GenanKiBackend |             |             |             |               |              |
 |         |              |<----------------|             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |---------------------------------------------------------->|               |------------->|
 |         |              |                    DeckManager & MediaManager            |               |  __init__()  |
 |         |              |<----------------------------------------------------------|               |<-------------|
 |         |              |                 |             |             |             |               |              |
 |         |<-------------|                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |------------->|                 |             |             |             |               |              |
 |         | load_data_   |                 |             |             |             |               |              |
 |         | from_        |                 |             |             |             |               |              |
 |         | directory()  |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |-------------------------------->|             |             |               |              |
 |         |              |        load_nouns_from_csv() |             |             |               |              |
 |         |              |<--------------------------------|             |             |               |              |
 |         |              |          List[Noun]           |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |-------------------------------->|             |             |               |              |
 |         |              |    load_adjectives_from_csv() |             |             |               |              |
 |         |              |<--------------------------------|             |             |               |              |
 |         |              |        List[Adjective]        |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |         [Similar for adverbs, negations]    |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |<-------------|                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |------------->|                 |             |             |             |               |              |
 |         |get_statistics|                 |             |             |             |               |              |
 |         |<-------------|                 |             |             |             |               |              |
 |         |{loaded_data} |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |----.         |                 |             |             |             |               |              |
 |         |    | Display |                 |             |             |             |               |              |
 |         |    | loaded  |                 |             |             |             |               |              |
 |         |    | stats   |                 |             |             |             |               |              |
 |         |<---'         |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |------------->|                 |             |             |             |               |              |
 |         |generate_all_ |                 |             |             |             |               |              |
 |         |cards(True)   |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |----.            |             |             |             |               |              |
 |         |              |    |generate_   |             |             |             |               |              |
 |         |              |    |noun_cards()|             |             |             |               |              |
 |         |              |<---'            |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |---------------------------------------------------------->|               |              |
 |         |              |                    get_noun_note_type()                  |               |              |
 |         |              |<----------------------------------------------------------|               |              |
 |         |              |                       NoteType                           |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |---------------------------------------------------------->|               |------------->|
 |         |              |                    create_note_type()                    |               | create_note_ |
 |         |              |                 |             |             |             |               | type()       |
 |         |              |                 |<------------|             |             |               |<-------------|
 |         |              |                 | note_type_id|             |             |               |              |
 |         |              |<----------------------------------------------------------|               |              |
 |         |              |                   note_type_id                           |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |             [For each noun]  |             |             |               |              |
 |         |              |----.            |             |             |             |               |              |
 |         |              |    | Get        |             |             |             |               |              |  
 |         |              |    | combined   |             |             |             |               |              |
 |         |              |    | audio text |             |             |             |               |              |
 |         |              |<---'            |             |             |             |               |              |
 |         |              | "die Katze,     |             |             |             |               |              |
 |         |              |  die Katzen"    |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |------------------------------------------>|             |               |              |
 |         |              |           generate_and_add_audio()        |             |               |              |
 |         |              |                 |             |---------->|             |               |              |
 |         |              |                 |             | generate_ |             |               |              |
 |         |              |                 |             | audio()   |             |               |              |
 |         |              |                 |             |<----------|             |               |              |
 |         |              |                 |             | audio_path|             |               |              |
 |         |              |<------------------------------------------|             |               |              |
 |         |              |                MediaFile                  |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |         [Similar for example audio & images]           |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |---------------------------------------------------------->|               |------------->|
 |         |              |                      add_note()                         |               | add_note()   |
 |         |              |                 |             |             |             |               |<-------------|
 |         |              |                 |<------------|             |             |               | note_id      |
 |         |              |<----------------------------------------------------------|               |              |
 |         |              |                     note_id                              |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |            [Repeat for adjectives, adverbs, negations]  |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |<-------------|                 |             |             |             |               |              |
 |         |{card_counts} |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |----.         |                 |             |             |             |               |              |
 |         |    | Display |                 |             |             |             |               |              |
 |         |    | card    |                 |             |             |             |               |              |
 |         |    | stats   |                 |             |             |             |               |              |
 |         |<---'         |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |------------->|                 |             |             |             |               |              |
 |         | export_deck()|                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |---------------------------------------------------------->|               |------------->|
 |         |              |                     export_deck()                       |               | export_deck()|
 |         |              |                 |             |             |             |               |              |
 |         |              |                 |----.        |             |             |               |              |
 |         |              |                 |    | Create |             |             |               |              |
 |         |              |                 |    | temp   |             |             |               |              |
 |         |              |                 |    | dir &  |             |             |               |              |
 |         |              |                 |    | copy   |             |             |               |              |
 |         |              |                 |    | media  |             |             |               |              |
 |         |              |                 |<---'        |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |              |                 |----.        |             |             |               |              |
 |         |              |                 |    | Create |             |             |               |              |
 |         |              |                 |    | .apkg  |             |             |               |              |
 |         |              |                 |    | zip    |             |             |               |              |
 |         |              |                 |<---'        |             |             |               |              |
 |         |              |                 |<------------|             |             |               |              |
 |         |              |<----------------------------------------------------------|               |              |
 |         |<-------------|                 |             |             |             |               |              |
 |         |   Success    |                 |             |             |             |               |              |
 |         |              |                 |             |             |             |               |              |
 |         |----.         |                 |             |             |             |               |              |
 |         |    | Display |                 |             |             |             |               |              |
 |         |    | success |                 |             |             |             |               |              |
 |         |    | message |                 |             |             |             |               |              |
 |         |<---'         |                 |             |             |             |               |              |
```

## Key Components

### Main Application Flow
1. **Initialization**: Main.py sets up paths, logging, and validates data directory
2. **Builder Creation**: GermanDeckBuilder initializes all required services and backends
3. **Data Loading**: CSV files are parsed into typed Python models (Noun, Adjective, etc.)
4. **Card Generation**: Each word type generates cards with media (audio + images)
5. **Deck Export**: Final .apkg file is created with embedded media

### Service Architecture
- **CSVService**: Loads and validates vocabulary data from CSV files
- **GermanLanguageService**: Handles German-specific logic (combined audio forms, categorization)
- **TemplateService**: Manages HTML/CSS templates for different card types
- **MediaService**: Coordinates audio and image generation
- **AudioService**: AWS Polly integration for pronunciation audio
- **PexelsService**: Image search and download from Pexels API
- **Backend**: genanki integration for .apkg generation

### Media Generation Process
1. **Audio**: Combined word forms (e.g., "die Katze, die Katzen") + example sentences
2. **Images**: Contextual image search based on English translations
3. **Caching**: Existing files are reused, missing files are generated
4. **Integration**: All media files are embedded into the final .apkg

### German Language Features
- **Noun Audio**: Article + singular, article + plural forms
- **Adjective Audio**: Normal, comparative, superlative forms  
- **Context-Aware Images**: German cultural context for better learning
- **Subdecks**: Organized by part of speech (Nouns, Adjectives, etc.)

The entire process is designed to be robust, with comprehensive error handling and progress reporting throughout the execution.