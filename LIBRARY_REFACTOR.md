# Anki Library Refactor Analysis

## Current Setup (genanki)
- Using `genanki>=0.13.0` as our deck creation library
- Third-party library providing basic Anki deck creation functionality
- Simpler but more limited in scope

## Official Anki Library (ankitects/anki)
The official library from Anki's repository offers significantly more functionality:

### Core Features
- Full access to Anki's internal data structures and database
- Native support for all Anki features including:
  - Card templates and styling
  - Media handling
  - Scheduling algorithms
  - Note types and fields
  - Deck management
  - Tag system
  - Statistics and progress tracking

### Advanced Capabilities
- Direct database access for complex operations
- Native support for Anki's scheduling system
- Built-in support for Anki's media handling
- Access to Anki's internal state and configuration
- Support for Anki's add-on system
- Better integration with Anki's UI and features

### Key Modules
- `collection.py` - Core collection management
- `cards.py` - Card creation and management
- `notes.py` - Note type handling
- `decks.py` - Deck management
- `scheduler.py` - Spaced repetition algorithms
- `media.py` - Media file handling
- `sync.py` - Synchronization support

## Advantages of Switching
- More robust and feature-complete
- Better maintained and updated
- Direct access to Anki's internal systems
- Better support for advanced features
- Native support for Anki's scheduling system
- Better integration with Anki's ecosystem

## Considerations
- More complex API to learn
- Requires more careful handling of Anki's internal state
- May require more setup and configuration
- Need to handle database operations more carefully

## Recommendation
Given our project's goals of creating sophisticated language learning decks with:
- Custom card templates
- Audio integration
- Image associations
- Complex scheduling needs
- Multiple card types

The official Anki library would provide:
1. Better control over card generation
2. More robust media handling
3. Native support for Anki's scheduling system
4. Better integration with Anki's ecosystem
5. More future-proof solution

## Next Steps
When ready to proceed with the migration, we should:
1. Create a detailed migration plan
2. Implement the migration in phases
3. Test thoroughly at each phase
4. Maintain backward compatibility during transition 