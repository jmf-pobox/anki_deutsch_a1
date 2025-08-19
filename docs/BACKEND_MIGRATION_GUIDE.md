# Backend Migration Guide

## Overview

The German A1 Anki Deck Generator supports two backend options for creating Anki decks:

- **AnkiBackend** (Production Default): Uses the official Anki library
- **GenanKiBackend** (Fallback): Uses the third-party genanki library

As of the Priority 2.3 Backend Consolidation phase, **AnkiBackend is now the production default**.

## Migration Status

✅ **COMPLETED - AnkiBackend is Production Default**
- Main application (`src/langlearn/main.py`) now uses AnkiBackend
- Examples (`examples/german_deck_builder_demo.py`) updated to AnkiBackend
- GermanDeckBuilder default remains "anki" for new instances
- Comprehensive testing validates 100% feature parity

## Backend Comparison Summary

| Feature | GenanKi | AnkiBackend | Winner |
|---------|---------|-------------|--------|
| **Performance** | 127K notes/sec | 1.8K notes/sec | GenanKi (70x faster) |
| **Memory Usage** | 0.06 MB | 9.02 MB | GenanKi (150x less) |
| **Feature Parity** | ✅ 100% | ✅ 100% | Tie |
| **Reliability** | ✅ 100% | ✅ 100% | Tie |
| **Strategic Value** | ❌ Third-party | ✅ Official Anki | AnkiBackend |
| **Future-Proof** | ❌ Limited | ✅ Full ecosystem | AnkiBackend |
| **Maintenance** | ⚠️ Community | ✅ Anki team | AnkiBackend |

**Recommendation**: AnkiBackend for production use due to strategic advantages.

## How to Switch Backends

### Option 1: Environment Variable (Recommended)
```bash
# Use AnkiBackend (production default)
export ANKI_BACKEND_TYPE="anki"
python src/langlearn/main.py

# Use GenanKi (fallback)
export ANKI_BACKEND_TYPE="genanki" 
python src/langlearn/main.py
```

### Option 2: Code Modification
Edit `src/langlearn/main.py` and change the backend_type parameter:

```python
# Use AnkiBackend (current default)
with GermanDeckBuilder(
    deck_name=deck_name,
    backend_type="anki",  # Production default
    enable_media_generation=True,
) as builder:

# Use GenanKi (fallback option)
with GermanDeckBuilder(
    deck_name=deck_name,
    backend_type="genanki",  # Fallback option
    enable_media_generation=True,
) as builder:
```

### Option 3: Programmatic Usage
```python
from langlearn.german_deck_builder import GermanDeckBuilder

# AnkiBackend (production)
with GermanDeckBuilder("My Deck", backend_type="anki") as builder:
    builder.load_data_from_directory("data/")
    builder.generate_all_cards()
    builder.export_deck("output/deck.apkg")

# GenanKi (fallback)
with GermanDeckBuilder("My Deck", backend_type="genanki") as builder:
    builder.load_data_from_directory("data/")
    builder.generate_all_cards()
    builder.export_deck("output/deck.apkg")
```

## Testing Backend Switch

Verify the backend switch works correctly:

```bash
# Test AnkiBackend
hatch run app
# Should show: "🚀 Initialized anki backend"

# Test specific backend
hatch run test-unit tests/test_german_deck_builder.py -k "backend" -v
# Should pass all 3 backend selection tests
```

## Rollback Instructions

If issues arise with AnkiBackend, rollback is immediate:

1. **Immediate Rollback**: Edit `src/langlearn/main.py` line 42:
   ```python
   backend_type="genanki",  # Rollback to GenanKi
   ```

2. **Environment Variable Rollback**:
   ```bash
   export ANKI_BACKEND_TYPE="genanki"
   ```

3. **Verify Rollback**:
   ```bash
   hatch run app
   # Should show: "🚀 Initialized genanki backend"
   ```

## Migration Timeline

- **Phase 1**: ✅ COMPLETE - AnkiBackend as production default
- **Phase 2**: Monitor production stability (1-4 weeks)
- **Phase 3**: Remove GenanKi dependency after stable period (1-2 months)

## Support and Troubleshooting

### Known Issues
- AnkiBackend uses more memory (9MB vs 0.06MB) - acceptable for production
- AnkiBackend is slower (1.8K vs 127K notes/sec) - still adequate for real-world usage

### Performance Benchmarks
Both backends successfully handle the full German A1 dataset:
- **963 total vocabulary entries** across all CSV files
- **Both achieve 100% success rate** in stress testing
- **Perfect feature parity** - identical .apkg outputs

### Getting Help
- Check `tests/test_german_deck_builder.py` for backend usage examples
- Review `examples/german_deck_builder_demo.py` for implementation patterns
- See comprehensive backend comparison results in project analysis

## Validation

This migration is backed by comprehensive analysis:
- ✅ 600 tests passing with both backends
- ✅ 100% feature parity validation
- ✅ Production workload testing with full German A1 dataset
- ✅ Performance benchmarking and reliability assessment
- ✅ Strategic analysis favoring official Anki library

The migration to AnkiBackend as production default provides future-proof architecture while maintaining full backward compatibility.