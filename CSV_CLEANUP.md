# CSV Legacy Columns Cleanup Plan

## 🔍 **Analysis Summary**

This document outlines a plan for safely removing legacy `word_audio`, `example_audio`, and `image_path` columns from CSV files. These columns were used in earlier versions of the system but are now superseded by dynamic media generation.

## 📊 **Current State Analysis**

### CSV File Status
| **CSV File** | **Legacy Columns** | **Populated Data** | **Status** |
|--------------|-------------------|-------------------|------------|
| `adjectives.csv` | ✅ ~~Has columns~~ | ✅ 98 entries, 200 existing files | **✅ COMPLETED** |
| `nouns.csv` | ✅ ~~Has columns~~ | ❌ Empty (all blank) | **✅ COMPLETED** |
| `adverbs.csv` | ✅ ~~Has columns~~ | ❌ Empty (all blank) | **✅ COMPLETED** |
| `negations.csv` | ✅ ~~Has columns~~ | ❌ Empty (all blank) | **✅ COMPLETED** |
| Other CSV files | ❌ No columns | N/A | **NO ACTION NEEDED** |

### Legacy Column Usage
**Legacy columns found in:**
- **`word_audio`**: Path to pre-generated audio for vocabulary word
- **`example_audio`**: Path to pre-generated audio for example sentence  
- **`image_path`**: Path to pre-generated image for vocabulary word

**Only `adjectives.csv` contains populated legacy data** - all other CSV files have empty legacy columns.

## 🔧 **Current System Architecture**

### Media Generation Flow
The current system uses a **hybrid approach**:

1. **Check Legacy Columns First**: If `image_path`/`word_audio`/`example_audio` exist and files exist on disk, use them
2. **Dynamic Generation Fallback**: If legacy fields are empty/missing, generate media dynamically using:
   - AWS Polly for audio generation
   - Pexels API for image generation with AI-enhanced search queries
   - Intelligent caching and deduplication

### Code Impact Analysis
**Files with legacy column references:**
- **160 occurrences across 15 source files**
- **371 occurrences across 15 test files**
- **Primary locations**: Domain models, card generators, media managers

**Critical observation**: The system **prioritizes dynamic generation over legacy columns**, using legacy data only as fallback when files exist on disk.

## ⚠️ **Risks and Dependencies**

### High-Risk Items
1. **`adjectives.csv` Data Loss**: 98 adjectives have legacy image/audio paths that may reference actual files
2. **Backup Dependency**: Need to verify backup files exist before removal
3. **Test Suite Impact**: 371 test references must be updated to remove legacy field expectations

### Medium-Risk Items
1. **Domain Model Fields**: All models define legacy fields as Pydantic `Field()` definitions
2. **Card Generator Logic**: Card generators check legacy fields before generating new media
3. **CSV Service Parsing**: CSV reader expects these columns to exist

### Low-Risk Items
1. **Empty Column Removal**: 15+ CSV files with empty legacy columns (safe to remove)
2. **Factory Methods**: Model factories pass empty strings for legacy fields

## 📋 **Cleanup Phases**

### **Phase 1: Pre-Cleanup Verification** 
**Objective**: Ensure no data loss and verify system behavior

**Tasks**:
1. **Audit Existing Media Files**
   ```bash
   # Check if legacy paths in adjectives.csv point to actual files
   cd data/
   grep -E "(\.mp3|\.jpg)$" adjectives.csv | xargs -I {} test -f {} && echo "File exists: {}"
   ```

2. **Create Comprehensive Backup**
   ```bash
   # Backup all CSV files with legacy columns
   cp adjectives.csv backups/adjectives_pre_cleanup_$(date +%Y%m%d).csv
   cp nouns.csv backups/nouns_pre_cleanup_$(date +%Y%m%d).csv
   cp adverbs.csv backups/adverbs_pre_cleanup_$(date +%Y%m%d).csv
   cp negations.csv backups/negations_pre_cleanup_$(date +%Y%m%d).csv
   ```

3. **Media Generation Test**
   ```bash
   # Test that dynamic media generation works for adjectives
   hatch run python -c "
   from langlearn.models.adjective import Adjective
   adj = Adjective(word='test', english='test', example='Das ist test.', comparative='', superlative='', word_audio='', example_audio='', image_path='')
   print('Dynamic generation available:', adj.get_image_search_terms())
   "
   ```

### **Phase 2: Domain Model Updates**
**Objective**: Remove legacy field definitions while maintaining backward compatibility

**Tasks**:
1. **Update Pydantic Models** - Remove `Field()` definitions:
   ```python
   # REMOVE from models: adjective.py, noun.py, adverb.py, negation.py
   word_audio: str = Field("", description="Path to audio file for the word")
   example_audio: str = Field("", description="Path to audio file for the example")  
   image_path: str = Field("", description="Path to image file")
   ```

2. **Update Model Factory** - Remove empty string assignments:
   ```python
   # REMOVE from model_factory.py
   word_audio="",
   example_audio="", 
   image_path="",
   ```

3. **Run Tests**: Verify all domain model tests pass after field removal

### **Phase 3: CSV Column Removal**
**Objective**: Remove legacy columns from CSV files

**✅ COMPLETED: Phase 3a - Empty Columns Removed**
Non-adjective CSV files have been cleaned:
- ✅ `nouns.csv`: 105 rows, legacy columns removed
- ✅ `adverbs.csv`: 39 rows, legacy columns removed  
- ✅ `negations.csv`: 12 rows, legacy columns removed

**✅ COMPLETED: Phase 3b - Adjectives Migration**:

**Analysis Complete**: 98 adjectives with legacy media data migrated successfully:
- ✅ **Word Audio**: 4 files preserved, 94 missing (already absent)
- ✅ **Example Audio**: 98 files preserved, 0 missing
- ✅ **Images**: 98 files preserved, 0 missing  
- **Result**: SUCCESS - All 200 existing files preserved during migration

**Migration Completed**:
- ✅ **CSV Structure**: Legacy columns removed successfully
- ✅ **File Preservation**: All 200 existing media files preserved
- ✅ **Domain Model**: Updated to remove legacy field definitions
- ✅ **Card Generators**: Updated to remove legacy field references
- ✅ **Tests**: All 522 tests passing after migration
- ✅ **Backup Safety**: Full backup created at `data/backups/adjectives_legacy_backup_*.csv`

### **Phase 4: Code Cleanup**  
**Objective**: Remove all references to legacy columns from codebase

**Tasks**:

1. **Card Generators Cleanup**:
   ```python
   # REMOVE legacy checks from card generators
   if adjective.image_path and Path(adjective.image_path).exists():
       # Remove this fallback logic
   ```

2. **Test Updates**: Update 371 test references:
   ```python
   # UPDATE test instantiations to remove legacy parameters
   Adjective(word="test", english="test", example="Test.", comparative="", superlative="")
   # Remove: word_audio="", example_audio="", image_path=""
   ```

3. **Remove Unused Imports**:
   ```python
   # Clean up any Path imports only used for legacy file checks
   ```

### **Phase 5: Validation and Testing**
**Objective**: Ensure system works correctly after cleanup

**Tasks**:

1. **Full Test Suite**: `hatch run test` - All 522 tests must pass
2. **Dynamic Generation Test**: Verify media generation works for all word types
3. **Integration Test**: Generate a complete deck and verify media is created
4. **Performance Test**: Measure any performance impact from removing legacy fallbacks

## 🚀 **Implementation Timeline**

| **Phase** | **Duration** | **Risk Level** | **Dependencies** |
|-----------|--------------|----------------|------------------|
| Phase 1: Verification | 1-2 hours | Low | File system access |
| Phase 2: Domain Models | 2-3 hours | Medium | Test suite |
| Phase 3: CSV Updates | 3-4 hours | High | Custom migration script |
| Phase 4: Code Cleanup | 4-6 hours | Medium | Complete codebase review |
| Phase 5: Validation | 1-2 hours | Low | Working test environment |
| **TOTAL** | **11-17 hours** | **Medium-High** | **Development environment** |

## 📋 **Success Criteria**

### **Functional Requirements**
- ✅ All CSV files no longer contain `word_audio`, `example_audio`, `image_path` columns
- ✅ All 522 tests pass after cleanup
- ✅ Dynamic media generation works for all vocabulary types
- ✅ Deck generation produces identical results (except file paths)
- ✅ No legacy column references remain in codebase

### **Quality Requirements**  
- ✅ No data loss (verified through backups and migration logs)
- ✅ Code coverage remains above 73.84%
- ✅ All ruff checks pass
- ✅ MyPy type checking passes
- ✅ Documentation updated to reflect changes

### **Performance Requirements**
- ✅ Media generation time remains acceptable (< 5s per word)
- ✅ CSV loading time not significantly impacted
- ✅ Memory usage not significantly increased

## 🔄 **Rollback Plan**

### **Emergency Rollback**
If issues are discovered after cleanup:

1. **Restore CSV Files**:
   ```bash
   cp backups/adjectives_pre_cleanup_YYYYMMDD.csv data/adjectives.csv
   # Restore other backed up files
   ```

2. **Revert Code Changes**:
   ```bash
   git revert <cleanup-commit-hash>
   ```

3. **Re-run Tests**:
   ```bash
   hatch run test  # Verify system is back to working state
   ```

## 📝 **Additional Notes**

### **Design Decisions**
1. **Progressive Cleanup**: Phases allow for early detection of issues
2. **Backup-First Approach**: All data preserved before any changes
3. **Test-Driven**: Each phase includes validation steps
4. **Risk Mitigation**: High-risk items addressed with custom tooling

### **Future Considerations**
1. **CSV Schema Validation**: Consider adding CSV schema validation to prevent legacy columns from being re-added
2. **Migration Tooling**: Custom migration script could be generalized for future schema changes
3. **Documentation Updates**: Update CSV format documentation to reflect new schema

### **Related Files Modified**
This cleanup will require changes to approximately **30+ files**:
- 4 CSV files (data removal)
- 4 domain model files (field removal)  
- 1 model factory file (parameter removal)
- 4 card generator files (logic simplification)
- 15+ test files (assertion updates)
- 1 new migration script (custom tooling)

---

**⚠️ RECOMMENDATION**: Execute this cleanup in a dedicated branch with comprehensive testing before merging to main. The hybrid nature of the current system (legacy + dynamic) provides good backward compatibility, but requires careful migration to avoid data loss.