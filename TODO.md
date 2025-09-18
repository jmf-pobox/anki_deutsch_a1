# Project TODO

Last updated: 2025-01-18

## 🚨 ACTIVE PRIORITIES


### **PRIORITY 1: DeckBuilder API Redesign** 🔴 **CRITICAL**

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

### **PRIORITY 2: Replace Pydantic with Dataclasses** 🟠 **HIGH PRIORITY**

**Problem**: Pydantic creates metaclass conflicts preventing protocol inheritance, adds complexity with minimal benefit (67 files coupled, only 5 test validation).

**Solution**: Replace with dataclasses + explicit validation

**3 Phases (~16 hours)**:
1. **Create Dataclass BaseRecord** (4h)
2. **Migrate All Record Classes** (8h) - Convert 22 record files across 3 languages
3. **Update Dependent Services** (4h) - Remove Pydantic dependency

**Benefits**: Eliminates metaclass conflicts, reduces complexity, enables clean protocol inheritance

---

### **PRIORITY 3: Protocol Inheritance Audit** 🟡 **MEDIUM PRIORITY**

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
- ✅ **DeckBuilder 100% language-agnostic** - zero hardcoded services
- ✅ Multi-language architecture foundation complete

**Pending Work**:
- ⚠️ API design needs observable phases and read access
- ⚠️ Pydantic prevents clean protocol inheritance

---

## 📚 COMPLETED WORK

### **Recently Completed**
- ✅ **DeckBuilder Language-Agnostic Architecture** - 100% complete, zero hardcoded services
- ✅ **Korean Language Implementation** - Complete package with particles, counters, typography
- ✅ **AnkiBackend Language-Agnostic Refactoring** - 83% code reduction (240→37 lines)
- ✅ **Multi-Language Architecture Foundation** - Protocol system, registry, template resolution
- ✅ **Documentation Consolidation** - Streamlined technical specs

### **Major Milestones**
- ✅ German Record System (13 classes) + Template Migration (54 files)
- ✅ MediaGenerationCapable Protocol Migration
- ✅ Legacy Code Removal + Quality Standards Achievement