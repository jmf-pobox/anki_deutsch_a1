# Project TODO

Last updated: 2025-01-17

## 🚨 ACTIVE PRIORITIES

### **PRIORITY 1: Complete DeckBuilder Language-Agnostic Design** 🟠 **HIGH PRIORITY**

**Problem**: DeckBuilder hardcodes `StandardMediaEnricher` for all languages (lines 153-159), preventing language-specific media enrichment strategies.

**Status**: 95% complete - only MediaEnricher delegation remaining

**Solution**: Add language-specific media enricher creation to Language protocol.

**Remaining Work (~4 hours)**:
1. **Add MediaEnricher method to Language protocol** (1h)
2. **Update language implementations** (2h) - German, Russian, Korean return appropriate enrichers
3. **Replace hardcoded StandardMediaEnricher in DeckBuilder** (1h) - Use language delegation

**Quality Gates**: No hardcoded services in DeckBuilder, all tests pass, all languages work

---

### **PRIORITY 2: DeckBuilder API Redesign** 🔴 **CRITICAL**

**Problem**: DeckBuilder is "a process wrapped in a class" with a 167-line monolithic `generate_all_cards` method that hides intermediate state and provides no read APIs.

**Solution**: Observable Phase-Based API with 5 clear phases:
- `INITIALIZED → DATA_LOADED → MEDIA_ENRICHED → CARDS_BUILT → DECK_EXPORTED`

**Key Features**:
- **Read APIs**: `get_loaded_data()`, `get_enriched_data()`, `preview_card()`
- **Progress tracking**: Observable progress within and between phases
- **Composable operations**: Run phases independently or partially
- **Backward compatibility**: Legacy interface preserved

**3 Phases (~16 hours)**:
1. **Parallel Implementation** (8h) - New DeckBuilderAPI class
2. **Migration Path** (4h) - Backward compatibility adapter
3. **Update Usage Patterns** (4h) - Migrate to new API patterns

---

### **PRIORITY 3: Replace Pydantic with Dataclasses** 🟠 **HIGH PRIORITY**

**Problem**: Pydantic creates metaclass conflicts preventing protocol inheritance, adds complexity with minimal benefit (67 files coupled, only 5 test validation).

**Solution**: Replace with dataclasses + explicit validation

**3 Phases (~16 hours)**:
1. **Create Dataclass BaseRecord** (4h)
2. **Migrate All Record Classes** (8h) - Convert 22 record files across 3 languages
3. **Update Dependent Services** (4h) - Remove Pydantic dependency

**Benefits**: Eliminates metaclass conflicts, reduces complexity, enables clean protocol inheritance

---

### **PRIORITY 4: Protocol Inheritance Audit** 🟡 **MEDIUM PRIORITY**

**Problem**: Many concrete classes implement protocols but don't explicitly inherit, breaking PyCharm visibility.

**Status**: ✅ CardProcessor classes fixed, others pending

**Remaining Protocols**:
- **LanguageDomainModel**: 18 domain model files across languages
- **ImageQueryGenerationProtocol**: Domain models with search terms
- **ImageSearchProtocol**: PexelsService
- **MediaEnricherProtocol**: StandardMediaEnricher
- **MediaGenerationCapable**: All 18 domain model classes

---

## 🎯 CURRENT STATUS

**Working State**:
- ✅ Three languages implemented: German (full), Russian (minimal), Korean (minimal)
- ✅ All tests passing, MyPy strict mode clean
- ✅ AnkiBackend fully language-agnostic
- ✅ Multi-language architecture foundation complete

**Pending Work**:
- ⚠️ DeckBuilder hardcodes StandardMediaEnricher (final 5% of language-agnostic design)
- ⚠️ API design needs observable phases and read access
- ⚠️ Pydantic prevents clean protocol inheritance

---

## 📚 COMPLETED WORK

### **Recently Completed**
- ✅ **Korean Language Implementation** - Complete package with particles, counters, typography
- ✅ **AnkiBackend Language-Agnostic Refactoring** - 83% code reduction (240→37 lines)
- ✅ **Multi-Language Architecture Foundation** - Protocol system, registry, template resolution
- ✅ **Documentation Consolidation** - Streamlined technical specs

### **Major Milestones**
- ✅ German Record System (13 classes) + Template Migration (54 files)
- ✅ MediaGenerationCapable Protocol Migration
- ✅ Legacy Code Removal + Quality Standards Achievement