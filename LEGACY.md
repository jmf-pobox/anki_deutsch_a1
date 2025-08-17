# LEGACY.md

This document tracks legacy code that can be safely removed in future releases as the project has migrated from genanki to the official Anki library with integrated media generation.

## Migration Status

**Current Phase**: Phase 1 Complete - Backend abstraction implemented with full media integration
**Next Phase**: Phase 2 - Full migration to official Anki library only
**Cleanup Phase**: Phase 3 - Remove all legacy code documented below

---

## Legacy Components Ready for Removal

### 1. genanki Library and Related Code

**Status**: ⚠️ LEGACY - Can be removed in Phase 3
**Reason**: Replaced by official Anki library backend

#### Files to Remove:
- `src/langlearn/genanki.pyi` - Type stubs for genanki library
- Any imports of `genanki` throughout the codebase

#### Dependencies to Remove:
```toml
# From pyproject.toml dependencies section:
"genanki>=0.13.0",  # Keep temporarily during migration
```

**Replaced By**: `AnkiBackend` using official `anki>=25.07` library

---

### 2. Separate Media Enrichment Scripts

**Status**: ⚠️ LEGACY - Can be removed in Phase 3
**Reason**: Media generation now integrated directly into AnkiBackend during deck creation

#### Files to Remove:
- `src/langlearn/scripts/enrich_audio.py`
- `src/langlearn/scripts/enrich_images.py`
- `src/langlearn/utils/audio_enricher.py`
- `src/langlearn/utils/image_enricher.py`
- `tests/integration/test_audio_enricher.py` 
- `tests/integration/test_image_enricher.py`

#### Hatch Scripts to Remove:
```toml
# From pyproject.toml [tool.hatch.envs.default.scripts]:
encode-audio = "python -m langlearn.scripts.encode_audio {args}"
```

**Replaced By**: Integrated media generation in `AnkiBackend._process_fields_with_media()` method

**Key Difference**: 
- **Legacy**: Manual CSV enrichment with path updates → deck generation
- **Current**: Automatic media generation during deck creation (no CSV path updates needed)

---

### 3. Legacy AnkiDeckGenerator Class

**Status**: ⚠️ LEGACY - Can be removed in Phase 3
**Reason**: Functionality absorbed into AnkiBackend

#### Files to Remove:
- `src/langlearn/generator.py` (if it still exists)
- Any references to `AnkiDeckGenerator` class

**Replaced By**: `AnkiBackend` class provides all deck generation functionality

---

### 4. CSV Path Dependency

**Status**: ⚠️ LEGACY APPROACH - Current system ignores these paths
**Reason**: Dynamic media generation eliminates need for CSV path tracking

#### Current CSV Format (Legacy):
```csv
word,english,example,comparative,superlative,word_audio,example_audio,image_path
groß,big/tall,Er ist sehr groß.,größer,am größten,data/audio/038c4ba71c55ea4d817d37062b489fb7.mp3,data/audio/e76845f1114e958ebd2c9c38d422fb9e.mp3,data/images/groß.jpg
```

#### Future CSV Format:
```csv
word,english,example,comparative,superlative
groß,big/tall,Er ist sehr groß.,größer,am größten
```

**Replaced By**: Dynamic media generation using algorithmic file naming:
- Audio: MD5 hash of text content
- Images: Descriptive naming (word.jpg)

---

### 5. Backup and Restore Utilities for CSV

**Status**: ⚠️ LEGACY - Can be removed in Phase 3
**Reason**: No longer needed since CSV files are not modified during deck generation

#### Code to Remove:
- CSV backup functionality in enrichment scripts
- Any CSV restoration utilities
- References to `data/backups/` directory

**Replaced By**: Source CSV files remain unchanged; media generated on-demand

---

### 6. genanki Backend Implementation

**Status**: ⚠️ LEGACY - Can be removed in Phase 3

#### Files to Remove:
- `src/langlearn/backends/genanki_backend.py`
- Any tests specifically for genanki backend functionality

**Replaced By**: `src/langlearn/backends/anki_backend.py` provides all functionality

---

## Migration Benefits Achieved

### ✅ Integrated Media Generation
- **Before**: Separate enrichment scripts → CSV updates → deck generation
- **After**: Single-step deck creation with automatic media generation

### ✅ Improved File Management
- **Before**: CSV path tracking, backup/restore complexity
- **After**: Algorithmic file naming, no CSV modification needed

### ✅ Enhanced Media Features
- **Before**: Basic audio/image support
- **After**: Combined adjective forms audio, proper Anki sound references, image optimization

### ✅ Better Error Handling
- **Before**: Failed enrichment could corrupt CSV files
- **After**: Graceful error handling, no data corruption risk

### ✅ Official Anki Library Benefits
- **Before**: Limited genanki functionality
- **After**: Full Anki collection management, better compatibility

---

## Removal Timeline

### Phase 2 (Next): Complete Migration
- Remove all genanki dependencies
- Implement remaining official Anki library features
- Complete test coverage for AnkiBackend only

### Phase 3 (Cleanup): Legacy Removal
- Remove all files listed in this document
- Update documentation to reflect new architecture
- Clean up dependencies and build configuration

---

## Important Notes

### ⚠️ Do Not Remove Until Phase 3
The legacy code should remain until Phase 2 is complete to ensure:
- Backup functionality during transition
- Ability to compare old vs new implementations
- Fallback options if issues are discovered

### 🔍 Testing Strategy
Before legacy removal:
- Ensure all functionality is replicated in AnkiBackend
- Verify media generation produces identical results
- Test deck compatibility with Anki desktop/mobile

### 📁 Data Migration
- Existing media files in `data/audio/` and `data/images/` remain compatible
- CSV files can be simplified but current format still works
- No user data loss during legacy removal

---

## Code Quality Impact

Legacy removal will:
- **Reduce codebase size** by ~30%
- **Eliminate dependency conflicts** between genanki and official Anki library
- **Simplify testing** by removing dual backend complexity
- **Improve maintainability** with single, modern implementation
- **Enable advanced features** only available in official Anki library