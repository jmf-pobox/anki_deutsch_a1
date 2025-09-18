# Project TODO

Last updated: 2025-01-18

## 🚨 ACTIVE PRIORITIES

### **PRIORITY 1: Replace Pydantic with Dataclasses** 🟠 **HIGH PRIORITY**

**Problem**: Pydantic creates metaclass conflicts preventing protocol inheritance, adds complexity with minimal benefit (67 files coupled, only 5 test validation).

**Solution**: Replace with dataclasses + explicit validation

**3 Phases (~16 hours)**:
1. **Create Dataclass BaseRecord** (4h)
2. **Migrate All Record Classes** (8h) - Convert 22 record files across 3 languages
3. **Update Dependent Services** (4h) - Remove Pydantic dependency

**Benefits**: Eliminates metaclass conflicts, reduces complexity, enables clean protocol inheritance

---

### **PRIORITY 2: Protocol Inheritance Audit** 🟡 **MEDIUM PRIORITY**

**Problem**: Many concrete classes implement protocols but don't explicitly inherit, breaking PyCharm visibility.

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
- ✅ Multi-language architecture foundation complete
- ✅ **DeckBuilder Observable API** - 5-phase pipeline with structured data access
- ✅ **Infrastructure/Platform/Languages Architecture** - Clean 3-tier package structure complete
- ✅ **Test Coverage**: 73.45% with comprehensive unit and integration test suite

**Pending Work**:
- ⚠️ Pydantic prevents clean protocol inheritance
- ⚠️ Protocol inheritance audit needed for PyCharm visibility

---

## 📚 COMPLETED WORK

### **Recently Completed**
- ✅ **Infrastructure/Platform/Languages Migration** - Complete 3-tier architecture with clean boundaries
- ✅ **Test Coverage Improvement** - From ~70% to 73.45% with comprehensive test additions
- ✅ **DeckBuilder API Redesign** - Observable 5-phase pipeline with read APIs
- ✅ **Package Refactoring** - langlearn/core/deck/ structure with file logging
- ✅ **Multi-Language Architecture** - Protocol system, registry, template resolution