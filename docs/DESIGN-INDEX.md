# Design Documentation Index

This directory contains design documentation for Language Learn - An Anki Card Generator. The application generates Anki decks with vocabulary, grammar patterns, and integrated media for multiple languages and proficiency levels.

**Status**: Production Ready ✅  
**Test Coverage**: 73.84% with 401 tests (562 unit + 24 integration)

---

## 🚀 **Quick Start Guide**

### **New Developer Setup**
1. **Start here**: [DESIGN-STATE.md](./DESIGN-STATE.md) - Current implementation status
2. **Development standards**: [DESIGN-GUIDANCE.md](./DESIGN-GUIDANCE.md) - Coding standards and workflow
3. **Component reference**: [DESIGN-SRP.md](./DESIGN-SRP.md) - System components overview

### **Need Something Specific?**
- 🎯 **Implementation status?** → [DESIGN-STATE.md](./DESIGN-STATE.md)
- 🔧 **Development workflow?** → [DESIGN-GUIDANCE.md](./DESIGN-GUIDANCE.md)  
- 🔍 **Component overview?** → [DESIGN-SRP.md](./DESIGN-SRP.md)
- 📊 **Quality metrics?** → Run `hatch run test-cov` for coverage report
- 🏗️ **System design?** → [DESIGN.md](./DESIGN.md)

---

## 📋 **Document Descriptions**

### **[DESIGN-SRP.md](./DESIGN-SRP.md)** - System Components
**Target Audience**: All Engineers  
**Purpose**: Overview of system components and their responsibilities  
**When to Use**: 
- Understanding application architecture
- Finding the right component for a task
- Onboarding to the codebase
- Component integration reference

**Content**:
- Application data flow (CSV → Models → Services → Anki cards)
- Component responsibilities
- Multi-language processing pipeline
- Media integration details

---

### **[DESIGN-STATE.md](./DESIGN-STATE.md)** - Current Status  
**Target Audience**: Technical Leadership, Senior Engineers  
**Purpose**: Implementation status and quality metrics  
**When to Use**:
- Understanding current application state
- Reviewing code quality metrics
- Planning future enhancements
- Technical assessment reference

**Content**:
- Clean Pipeline Architecture migration completion status (5 phases complete)
- Quality metrics: 586 tests, 81.70% coverage, 0 linting errors
- Performance improvements and optimizations
- Dual architecture support (Clean Pipeline + Legacy fallback)

---

### **[DESIGN-GUIDANCE.md](./DESIGN-GUIDANCE.md)** - Development Standards
**Target Audience**: All Engineers (Daily Reference)  
**Purpose**: Clean Pipeline Architecture development practices and standards  
**When to Use**:
- Implementing Clean Pipeline components
- Following separation of concerns principles
- Writing tests for Clean Architecture
- Maintaining backward compatibility

**Content**:
- Clean Pipeline Architecture principles and patterns
- Service layer design standards
- Testing strategies for Clean Architecture
- Legacy integration guidelines

---

### **[DESIGN.md](./DESIGN.md)** - Architecture Overview
**Target Audience**: Architects, Senior Engineers  
**Purpose**: Clean Pipeline Architecture design and implementation details  
**When to Use**:
- Understanding overall architecture flow
- Learning Clean Architecture implementation
- Designing new components
- Architecture review and evaluation

**Content**:
- Complete Clean Pipeline flow documentation
- CardBuilder service architecture
- MediaEnricher integration patterns
- Dual architecture support strategy

---

## 🎯 **Clean Pipeline Architecture Status**

### **Current Implementation**:
- ✅ **Phase 1**: Record system (NounRecord, AdjectiveRecord, AdverbRecord, NegationRecord)
- ✅ **Phase 2**: RecordMapper service for CSV → Records conversion
- ✅ **Phase 3**: MediaEnricher integration with existence checking
- ✅ **Phase 4**: CardBuilder service with 97.83% test coverage
- ✅ **Phase 5**: Documentation and quality verification complete

### **Architecture Support**:
- ✅ **Clean Pipeline**: noun, adjective, adverb, negation (4/7 word types)
- ✅ **Legacy Fallback**: verb, preposition, phrase (3/7 word types)
- ✅ **Automatic Delegation**: AnkiBackend seamlessly chooses architecture

---

## 📊 **Quality Metrics**

| **Metric** | **Current** | **Status** |
|------------|-------------|------------|
| **Total Tests** | 586 tests | ✅ All Passing |
| **Coverage** | 81.70% | ✅ Excellent |
| **CardBuilder Coverage** | 97.83% | ✅ Outstanding |
| **Linting** | 0 errors | ✅ Clean |
| **Architecture Quality** | Clean Pipeline + Backward Compatible | ✅ Enterprise-grade |

---

## 🔧 **Document Update Status**

All documentation has been updated to reflect the completed Clean Pipeline Architecture:

| **Document** | **Status** | **Last Updated** |
|--------------|------------|------------------|
| **DESIGN-INDEX.md** | ✅ Current | Clean Pipeline Migration |
| **DESIGN-STATE.md** | ✅ Updated | Current metrics and status |
| **DESIGN-GUIDANCE.md** | ✅ Updated | Clean Architecture practices |
| **DESIGN-SRP.md** | ✅ Updated | Component responsibilities |

---

## 💡 **Contributing to Clean Pipeline Architecture**

### **Development Standards**:
- ✅ **Single Responsibility**: Each service has one clear purpose
- ✅ **Separation of Concerns**: German logic separate from infrastructure
- ✅ **Test Coverage**: Comprehensive tests for all components
- ✅ **Backward Compatibility**: Graceful fallback to legacy systems

### **Quality Gates**:
- All tests must pass (586 tests)
- Coverage must not decrease (currently 81.70%)
- Linting must be clean (0 errors)
- Clean Architecture principles must be followed

---

*Last Updated: Clean Pipeline Architecture Migration Complete | Architecture: Enterprise Clean Pipeline with Legacy Compatibility*