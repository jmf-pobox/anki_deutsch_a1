# Design Documentation Index

This directory contains comprehensive design documentation for the German A1 vocabulary learning application. Each document serves a specific purpose and audience in the development lifecycle.

---

## 🚀 **Quick Start Guide**

### **New to the Project?**
1. **Start here**: [DESIGN-SRP.md](./DESIGN-SRP.md) - Complete system inventory and component responsibilities
2. **Then read**: [DESIGN-STATE.md](./DESIGN-STATE.md) - Current reality and quality assessment
3. **Finally**: [DESIGN-GUIDANCE.md](./DESIGN-GUIDANCE.md) - Development standards and practices

### **Need Something Specific?**
- 🏗️ **Planning major changes?** → [DESIGN-STATE.md](./DESIGN-STATE.md)
- 📝 **Daily development work?** → [DESIGN-GUIDANCE.md](./DESIGN-GUIDANCE.md)
- 🔍 **Looking up a component?** → [DESIGN-SRP.md](./DESIGN-SRP.md)
- 📚 **Understanding design history?** → [DESIGN.md](./DESIGN.md)
- 📊 **Current test coverage?** → Run `hatch run test-cov` and view `htmlcov/index.html`
- 🔧 **Type safety and MyPy standards?** → [CODE-TYPING.md](./CODE-TYPING.md)

---

## 📋 **Document Descriptions**

### **[DESIGN-SRP.md](./DESIGN-SRP.md)** - System Reference
**Target Audience**: All Engineers  
**Purpose**: Comprehensive inventory of packages, modules, and classes  
**When to Use**: 
- Understanding component responsibilities
- Finding the right class for a task
- Onboarding new team members
- Code review reference

**Content**:
- Complete package hierarchy analysis
- Single Responsibility Principle assessment
- Class-by-class responsibility matrix
- Architecture quality evaluation

---

### **[DESIGN-STATE.md](./DESIGN-STATE.md)** - Reality Assessment  
**Target Audience**: Technical Leadership, Senior Engineers  
**Purpose**: Critical analysis of current quality and technical debt  
**When to Use**:
- Planning technical investment priorities
- Understanding blockers for multi-language support
- Making architectural decisions
- Setting realistic implementation timelines

**Content**:
- Measured code quality metrics (363 MyPy errors, 113 linting violations)
- Multi-language readiness assessment (2/10 rating)
- Technical debt prioritization matrix
- Realistic implementation phases with timelines

---

### **[DESIGN-GUIDANCE.md](./DESIGN-GUIDANCE.md)** - Development Standards
**Target Audience**: All Engineers (Daily Reference)  
**Purpose**: Prescriptive guidance for development practices and architectural decisions  
**When to Use**:
- Before making design decisions
- During code review
- Setting up development environment
- Establishing quality gates

**Content**:
- Mandatory architectural principles (SRP, Clean Architecture, Multi-Language)
- Package architecture standards
- Import and testing requirements
- Anti-patterns and prohibited practices
- Experience-level specific guidance

---

### **[DESIGN.md](./DESIGN.md)** - Historical Context
**Target Audience**: Architects, Senior Engineers  
**Purpose**: Documents original intended architecture and design patterns  
**When to Use**:
- Understanding design evolution
- Learning from original architectural intentions
- Comparing current state to intended design
- Historical context for major decisions

**Content**:
- Original architectural principles analysis
- Intended design patterns (Strategy, Template Method, DDD)
- Service-oriented architecture documentation
- Abstract base class designs

---

## 🎯 **Document Relationships**

```
DESIGN.md           DESIGN-SRP.md
(What was           (What exists
 intended)           currently)
     ↓                   ↓
DESIGN-STATE.md ←→ DESIGN-GUIDANCE.md
(Current reality    (How to develop
 & problems)         going forward)
```

### **Cross-Document Navigation**:
- **DESIGN.md** ↔️ **DESIGN-STATE.md**: Compare intentions vs reality
- **DESIGN-SRP.md** ↔️ **DESIGN-GUIDANCE.md**: Current structure + development standards  
- **DESIGN-STATE.md** ↔️ **DESIGN-GUIDANCE.md**: Problems identified + solutions prescribed

---

## 📊 **Document Update Frequency**

| **Document** | **Update Frequency** | **Triggers** | **Owner** |
|--------------|---------------------|--------------|-----------|
| **DESIGN.md** | Rarely | Major architectural decisions | Principal Engineer |
| **DESIGN-SRP.md** | Medium | Package restructuring, new components | Senior Engineers |
| **DESIGN-GUIDANCE.md** | Medium | New standards, policy changes | Principal Engineer |
| **DESIGN-STATE.md** | High | Quality metrics, technical debt analysis | Technical Leadership |

---

## 🔧 **Maintenance Guidelines**

### **For Document Authors**:
- **Keep cross-references updated** when moving or renaming content
- **Maintain consistent terminology** across all documents
- **Update metrics in DESIGN-STATE.md** with actual measured data
- **Reflect reality, not aspirations** in all assessments

### **For Reviewers**:
- **Check document accuracy** against actual codebase
- **Verify cross-references** still work after changes
- **Ensure unique content** - avoid duplication between documents
- **Validate quality metrics** with actual tool output

---

## 🏗️ **Architecture Decision Records**

For major architectural decisions not covered in these design documents, see:
- `MIGRATION_PLAN.md` - Backend migration strategy
- `ANKI_API_TESTPLAN.md` - Testing strategy for new backend
- `SRP.md` - Single Responsibility Principle inventory (if different from DESIGN-SRP.md)

---

## 💡 **Contributing to Design Documentation**

### **Before Making Changes**:
1. **Read the relevant document completely**
2. **Check current implementation** to ensure accuracy
3. **Measure actual metrics** rather than estimating
4. **Consider impact on other documents**

### **Quality Standards**:
- ✅ **Factual**: All claims backed by measurable evidence
- ✅ **Current**: Information reflects actual codebase state  
- ✅ **Actionable**: Recommendations include specific steps
- ✅ **Realistic**: Timelines and assessments are achievable

### **Review Process**:
- **DESIGN-STATE.md** changes require Principal Engineer approval
- **DESIGN-GUIDANCE.md** changes require architecture team review
- **Cross-document changes** need validation of all affected documents

---

## 📞 **Questions and Clarifications**

**Architecture Questions**: Consult Principal Engineer  
**Implementation Questions**: Start with DESIGN-GUIDANCE.md, escalate to Senior Engineers  
**Component Questions**: Reference DESIGN-SRP.md, ask component owners  
**Quality Questions**: Check DESIGN-STATE.md metrics, discuss with Technical Leadership

---

*Last Updated: [Current Date] | Maintained by: Principal Engineer*