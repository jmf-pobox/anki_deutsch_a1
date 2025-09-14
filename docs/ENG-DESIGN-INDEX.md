# Documentation Index

Comprehensive documentation for the **Anki German Language Deck Generator** - a production-ready flashcard generation system using Clean Pipeline Architecture.

**Current Status**:  
- **Quality**: 813 tests passing (792 unit + 21 integration)  
- **Coverage**: 24.79% overall  
- **Type Safety**: 0 MyPy errors in strict mode  
- **Architecture**: Clean Pipeline with single responsibility design

---

## Quick Start for Developers

### Essential Reading Order
1. **[ENG-DEVELOPMENT-GUIDE.md](./ENG-DEVELOPMENT-GUIDE.md)** - Complete development standards and workflow
2. **[ENG-SYSTEM-DESIGN.md](./ENG-SYSTEM-DESIGN.md)** - How CSV becomes Anki cards (the pipeline)
3. **[ENG-ARCHITECTURE.md](./ENG-ARCHITECTURE.md)** - High-level system architecture

### Finding Information
- **How to develop?** → [ENG-DEVELOPMENT-GUIDE.md](./ENG-DEVELOPMENT-GUIDE.md)
- **How does it work?** → [ENG-SYSTEM-DESIGN.md](./ENG-SYSTEM-DESIGN.md)  
- **What are the components?** → [ENG-COMPONENT-INVENTORY.md](./ENG-COMPONENT-INVENTORY.md)
- **Current metrics?** → Run `hatch run test-cov` for live data
- **Data formats?** → [PROD-CSV-SPEC.md](PM-CSV-SPEC.md)

---

## Core Documentation

### [ENG-DEVELOPMENT-GUIDE.md](./ENG-DEVELOPMENT-GUIDE.md)
**Purpose**: Single source of truth for all development activities  
**Audience**: All engineers  
**Content**:
- Development workflow and quality gates
- Coding standards and best practices
- Testing requirements and patterns
- Common tasks and troubleshooting
- Tool configuration and usage

---

### [ENG-SYSTEM-DESIGN.md](./ENG-SYSTEM-DESIGN.md)
**Purpose**: Explain the complete CSV → Anki card pipeline  
**Audience**: Engineers implementing features  
**Content**:
- Step-by-step data transformation pipeline
- Single Responsibility Principle implementation
- Adding new card types guide
- Component interactions and data flow

---

### [ENG-ARCHITECTURE.md](./ENG-ARCHITECTURE.md)
**Purpose**: High-level system architecture overview  
**Audience**: Architects, Senior Engineers  
**Content**:
- System layers and responsibilities
- Architectural patterns and decisions
- Quality attributes and technology stack
- Future architecture and extension points

---

### [ENG-COMPONENT-INVENTORY.md](./ENG-COMPONENT-INVENTORY.md)
**Purpose**: Detailed inventory of all system components  
**Audience**: All engineers  
**Content**:
- Component responsibilities (SRP analysis)
- Package structure and organization
- Design patterns implemented
- Architecture quality assessment

---

## Data Specifications

### [PROD-CSV-SPEC.md](PM-CSV-SPEC.md)
**Purpose**: CSV format specifications for vocabulary data  
**Content**: Column definitions, validation rules, encoding standards

### [DATA-DICTIONARY.md](ENG-DATA-DICTIONARY.md)
**Purpose**: Authoritative field definitions for all card types  
**Content**: Field names, types, validation rules, examples

### [PROD-CARD-SPEC.md](PM-CARD-SPEC.md)
**Purpose**: Anki card type specifications  
**Content**: Card templates, field mappings, styling guidelines

---

## Technical Standards

### [ENG-EXCEPTIONS.md](./ENG-EXCEPTIONS.md)
**Purpose**: Mandatory exception handling standards  
**Audience**: All engineers  
**Content**:
- Fail-fast principles aligned with Johnson's Law
- Custom exception hierarchy and categories
- Service availability patterns
- Migration guidelines for eliminating fallback anti-patterns

### [ENG-TECHNICAL-DEBT-AUDIT.md](./ENG-TECHNICAL-DEBT-AUDIT.md)
**Purpose**: Comprehensive technical debt analysis  
**Content**: Identified anti-patterns, fallback logic, remediation priority

---

## Legacy Documentation

**Note**: The following documents are maintained for reference but may contain outdated information. Always defer to the core documentation above for current standards.

- **ENG-QUALITY-METRICS.md** - Historical quality metrics (use `hatch run test-cov` for current data)
- **ENG-DEVELOPMENT-STANDARDS.md** - Superseded by ENG-DEVELOPMENT-GUIDE.md
- **ENG-BRANCH-WORKFLOW.md** - Integrated into ENG-DEVELOPMENT-GUIDE.md
- **ENG-TYPE-SAFETY.md** - Type safety standards (reference only)
- **ENG-PYTHON-STANDARDS.md** - General Python standards (reference only)

## How to Generate Current Metrics

```bash
# Test coverage
hatch run test-cov
# View HTML report: open htmlcov/index.html

# Type checking status
hatch run type

# Linting status
hatch run ruff check

# Test count
hatch run test --co -q | grep "test" | wc -l
```

## Quality Standards

### Mandatory Quality Gates
- **MyPy**: 0 errors required (strict mode)
- **Ruff**: 0 violations required
- **Tests**: All must pass
- **Coverage**: Must not decrease from current level

### Target Metrics
- **New code coverage**: 80% minimum
- **Critical path coverage**: 95% minimum
- **Overall coverage**: Maintain or improve current 24.79%