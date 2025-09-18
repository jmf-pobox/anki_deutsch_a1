# Project TODO

Last updated: 2025-01-18

## 🚨 ACTIVE PRIORITIES

### **PRIORITY 1: Package Structure Refactoring** 🔴 **CRITICAL**

**Problem**: Current `core/` concept is too broad and unclear. The `langlearn/core/deck/` package (application orchestration) doesn't belong in infrastructure.

**Solution**: Restructure around open-closed extensibility principles:
```
src/langlearn/
├── infrastructure/          # CLOSED - Pure technical services
│   ├── services/           # External APIs (AWS, Pexels, Anthropic)
│   ├── backends/           # Anki integration
│   └── storage/            # File/media management
├── platform/               # OPEN - Extension points & orchestration
│   ├── deck/               # DeckBuilderAPI (moved from core)
│   ├── pipeline/           # Data transformation pipeline
│   ├── records/            # Base record system
│   └── protocols/          # Extension interfaces
└── languages/              # EXTENSIONS - Language implementations
```

**Benefits**: Clear mental model (Infrastructure you use, Platform you extend, Languages you implement), self-documenting extension intent, eliminates confusion about where DeckBuilderAPI belongs.

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

**Pending Work**:
- ⚠️ Package structure needs open-closed clarity
- ⚠️ Pydantic prevents clean protocol inheritance

---

## 📚 COMPLETED WORK

### **Recently Completed**
- ✅ **DeckBuilder API Redesign** - Observable 5-phase pipeline with read APIs
- ✅ **Package Refactoring** - langlearn/core/deck/ structure with file logging
- ✅ **Multi-Language Architecture** - Protocol system, registry, template resolution