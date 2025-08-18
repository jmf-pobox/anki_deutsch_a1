# LEGACY.md - Deprecation Status

This document tracks legacy components that have been removed or deprecated during the clean architecture and backend migration initiatives.

## Migration Status: COMPLETE

**Current Phase**: Production consolidation complete  
**Production Backend**: AnkiBackend (official Anki library)  
**Fallback Backend**: GenanKi (planned removal in 1-2 months)  
**Legacy Cleanup**: 273 lines of legacy code removed

---

## ✅ Completed Removals

### Legacy Field Processing (Removed in Phase 5)
- **Removed**: 273 lines of legacy infrastructure field processing methods
- **Replaced with**: Domain model FieldProcessor pattern
- **Status**: ✅ Complete - Clean architecture implementation

### Backend Migration Status  
- **Production Backend**: ✅ AnkiBackend (official Anki library)
- **Legacy Backend**: ⚠️ GenanKi (fallback, planned deprecation)
- **Migration Guide**: ✅ Complete (`docs/BACKEND_MIGRATION_GUIDE.md`)
- **Rollback Capability**: ✅ Available (one-line configuration change)

### Libraries Currently in Use
```toml
# From pyproject.toml dependencies:
"genanki>=0.13.0",     # Active production backend
"anki>=25.07",         # Available backend option
```

**Current Recommendation**: Maintain both libraries for flexibility and risk mitigation.

---

## Components Under Review

### 1. Dual Backend Maintenance

**Status**: ✅ CURRENT APPROACH - Maintain both
**Reason**: Provides flexibility and fallback options

#### Current Files:
- `src/langlearn/backends/genanki_backend.py` - Production backend
- `src/langlearn/backends/anki_backend.py` - Alternative backend
- `src/langlearn/backends/base.py` - Shared interface

**Future Consideration**: If official Anki backend proves superior after extensive testing, could consider genanki backend deprecation.

**Decision Criteria**:
- Performance comparison results
- Feature parity validation
- Production stability testing
- Community feedback and preferences

---

### 2. Type Stub Files

**Status**: ✅ KEEP - Still needed
**Location**: `src/langlearn/genanki.pyi`

**Reason**: Provides type safety for genanki library usage while it remains active backend.

**Future**: Remove only if genanki backend is deprecated.

---

### 3. Configuration Complexity

**Status**: ⚠️ MONITOR - Acceptable current complexity

#### Current Approach:
- Backend selection via `backend_type` parameter
- Automatic backend instantiation based on configuration
- Error handling for unsupported backend types

**Benefit**: Flexibility for different use cases and testing
**Cost**: Additional configuration complexity

**Review Criteria**: If one backend clearly emerges as preferred, could simplify configuration.

---

## Migration Benefits Achieved

### ✅ Flexible Backend Architecture
- **Before**: Single backend dependency (genanki)
- **After**: Choice of backends with consistent interface

### ✅ Risk Mitigation
- **Before**: Vendor lock-in to genanki library
- **After**: Multiple backend options reduce dependency risk

### ✅ Future Flexibility
- **Before**: Migration would require significant refactoring
- **After**: Backend switching requires minimal changes

### ✅ Testing Capabilities
- **Before**: Single implementation to test
- **After**: Interface validation across multiple backends

---

## Future Considerations

### Potential Backend Consolidation Scenarios

#### Scenario 1: Official Anki Backend Adoption
**Trigger**: Official backend proves superior in production
**Action**: Gradual deprecation of genanki backend
**Timeline**: After 6+ months of production validation

**Benefits**:
- Reduced maintenance burden
- Simpler dependency management
- Access to latest Anki features

**Risks**:
- Loss of fallback option
- Potential integration issues

#### Scenario 2: Continued Dual Backend Support
**Trigger**: Both backends serve different use cases
**Action**: Maintain current architecture
**Timeline**: Ongoing

**Benefits**:
- Maximum flexibility
- Risk mitigation
- User choice

**Risks**:
- Increased maintenance complexity
- Testing overhead

#### Scenario 3: genanki Backend Preference
**Trigger**: genanki proves more reliable or suitable
**Action**: Focus development on genanki backend
**Timeline**: Based on validation results

**Benefits**:
- Proven stability
- Simpler implementation
- Lower complexity

**Risks**:
- Limited future development
- Potential obsolescence

---

## Decision Framework

### Evaluation Criteria for Backend Decisions

1. **Stability**: Error rates, crash frequency, data integrity
2. **Performance**: Generation speed, memory usage, file size
3. **Features**: Available functionality, German language support
4. **Maintenance**: Development activity, community support
5. **Integration**: Compatibility with Anki ecosystem
6. **Testing**: Coverage, reliability, automation

### Review Schedule
- **Monthly**: Monitor usage patterns and error rates
- **Quarterly**: Evaluate performance metrics and user feedback
- **Annually**: Comprehensive architecture review and decision point

---

## Current Recommendation

**Maintain current dual backend architecture** with the following rationale:

### Advantages
- ✅ **Proven Stability**: genanki backend is production-tested
- ✅ **Future Flexibility**: Official backend available when needed
- ✅ **Risk Mitigation**: Fallback options prevent single points of failure
- ✅ **User Choice**: Different users may prefer different backends

### Acceptable Costs
- ⚠️ **Maintenance Overhead**: Manageable with current architecture
- ⚠️ **Testing Complexity**: Mitigated by shared interface
- ⚠️ **Configuration Complexity**: Minimal impact on end users

---

## Conclusion

The current backend abstraction architecture provides valuable flexibility without significant downsides. No components are currently recommended for removal. Future decisions should be based on real-world usage data, performance metrics, and user feedback rather than premature optimization.

**Status**: All current components serve legitimate purposes and should be maintained.