# Production CSV File Inventory

## Overview

This document provides a complete inventory of all CSV files in the German Language Learning System, their current status, and recommendations for maintenance.

## CSV File Status Categories

- **✅ ACTIVE**: Currently used in production, properly integrated
- **🔧 UNINTEGRATED**: Valid data but not yet integrated into the system
- **⚠️ LEGACY**: Deprecated, maintained for backward compatibility
- **🗑️ OBSOLETE**: Should be removed, no longer needed

## Active CSV Files (Currently Integrated)

### ✅ Core Word Types

| File | Status | Record Type | Rows | Integration | Notes |
|------|--------|-------------|------|-------------|-------|
| nouns.csv | ✅ ACTIVE | noun | ~150 | Clean Pipeline | Articles, plurals, examples |
| adjectives.csv | ✅ ACTIVE | adjective | ~80 | Clean Pipeline | Comparative/superlative forms |
| adverbs.csv | ✅ ACTIVE | adverb | ~40 | Clean Pipeline | Location, time, manner types |
| negations.csv | ✅ ACTIVE | negation | ~10 | Clean Pipeline | Negation patterns |
| prepositions.csv | ✅ ACTIVE | preposition | ~30 | Legacy FieldProcessor | Case requirements |
| phrases.csv | ✅ ACTIVE | phrase | ~50 | Legacy FieldProcessor | Common expressions |
| verbs.csv | ✅ ACTIVE | verb | ~97 | Legacy FieldProcessor | Single-tense conjugations with separable info |
| verbs_unified.csv | ✅ ACTIVE | verb_conjugation | ~500 | Clean Pipeline | Multi-tense conjugations |

### Integration Status:
- **Clean Pipeline Architecture**: noun, adjective, adverb, negation, verb_conjugation
- **Legacy FieldProcessor**: verb, preposition, phrase (backward compatibility)

## Unintegrated CSV Files (Valid but Not in System)

### 🔧 Numbers

| File | Status | Rows | Purpose | Integration Needed |
|------|--------|------|---------|-------------------|
| cardinal_numbers.csv | 🔧 UNINTEGRATED | ~30 | Counting numbers 1-100 | Create CardinalNumberRecord |
| ordinal_numbers.csv | 🔧 UNINTEGRATED | ~20 | First, second, third, etc. | Create OrdinalNumberRecord |

### 🔧 Grammar Components

| File | Status | Rows | Purpose | Integration Needed |
|------|--------|------|---------|-------------------|
| conjunctions.csv | 🔧 UNINTEGRATED | ~20 | und, aber, oder, etc. | Create ConjunctionRecord |
| interjections.csv | 🔧 UNINTEGRATED | ~15 | Ach, Oh, Na ja, etc. | Create InterjectionRecord |

### 🔧 Pronouns

| File | Status | Rows | Purpose | Integration Needed |
|------|--------|------|---------|-------------------|
| personal_pronouns.csv | 🔧 UNINTEGRATED | ~40 | ich, du, er, sie, etc. | Create PersonalPronounRecord |
| other_pronouns.csv | 🔧 UNINTEGRATED | ~60 | Possessive, demonstrative | Create PronounRecord |

## Legacy and Backup Files

### ⚠️ Verb File Versions

| File | Status | Rows | Purpose | Notes |
|------|--------|------|---------|-------|
| verbs.csv | ✅ ACTIVE | ~97 | Current single-tense version | Contains separable column |
| verbs_enhanced.csv | ⚠️ LEGACY | ~97 | Enhanced version without separable | Intermediate evolution |
| verbs_backup_original.csv | ⚠️ LEGACY | ~97 | Original simpler version | 7 columns only |

### ✅ Old Verb System (REMOVED)

| File | Status | Rows | Replaced By | Action Completed |
|------|--------|------|-------------|------------------|
| ~~regular_verbs.csv~~ | ✅ REMOVED | ~100 | verbs_unified.csv | ✅ Deleted 2025-08-22 |
| ~~irregular_verbs.csv~~ | ✅ REMOVED | ~80 | verbs_unified.csv | ✅ Deleted 2025-08-22 |
| ~~separable_verbs.csv~~ | ✅ REMOVED | ~40 | verbs_unified.csv | ✅ Deleted 2025-08-22 |

**Note**: verbs.csv was retained and evolved rather than removed, alongside verbs_unified.csv for different use cases.

## ✅ Removed Backup Files  

### ✅ Automatic Backups (REMOVED)

| File Pattern | Purpose | Action Completed |
|--------------|---------|------------------|
| ~~*.csv.backup~~ | Auto-created during enrichment | ✅ Deleted 2025-08-22 |
| ~~*.csv.column_rename_backup~~ | Created during meaning→english migration | ✅ Deleted 2025-08-22 |

**✅ CLEANUP COMPLETE**: All backup files have been successfully removed:
- ~~nouns.csv.backup~~ ✅ REMOVED
- ~~verbs.csv.backup~~ ✅ REMOVED  
- ~~verbs_unified.csv.backup~~ ✅ REMOVED
- ~~verbs_unified.csv.column_rename_backup~~ ✅ REMOVED
- ~~phrases.csv.backup~~ ✅ REMOVED
- ~~prepositions.csv.backup~~ ✅ REMOVED
- ~~personal_pronouns.csv.backup~~ ✅ REMOVED
- ~~other_pronouns.csv.backup~~ ✅ REMOVED

**Note**: Historical backups remain in the `data/backups/` directory for reference.

## Integration Priority Recommendations

### High Priority (Core Learning Components)
1. **personal_pronouns.csv** - Essential for basic German
2. **cardinal_numbers.csv** - Fundamental vocabulary
3. **conjunctions.csv** - Needed for sentence construction

### Medium Priority (Enhanced Learning)
4. **ordinal_numbers.csv** - Dates and ordering
5. **other_pronouns.csv** - Possessives and demonstratives

### Low Priority (Advanced Features)
6. **interjections.csv** - Conversational fluency

## Migration Tasks

### Immediate Actions
1. ✅ Verify all verb data is in verbs_unified.csv
2. ⬜ Create Record classes for unintegrated CSV files
3. ⬜ Update RecordMapper to handle new record types
4. ⬜ Add new CSV files to deck_builder.py mapping

### Cleanup Actions
1. ✅ Remove backup files after verification - **COMPLETED 2025-08-22**
2. ✅ Archive legacy verb CSV files - **COMPLETED 2025-08-22**
3. ⬜ Consolidate pronoun CSV files if appropriate

## Data Quality Status

### Verified Clean
- ✅ nouns.csv - Validated, english column correct
- ✅ adjectives.csv - Validated, english column correct
- ✅ verbs_unified.csv - Validated, english column correct
- ✅ adverbs.csv - Validated structure
- ✅ negations.csv - Validated structure

### Needs Review  
- ⚠️ Pronoun files - May have overlapping data

## File Size Summary

| Category | Files | Total Rows (est.) | Status |
|----------|-------|------------------|--------|
| Active Integrated | 7 | ~900 | ✅ Production ready |
| Unintegrated | 6 | ~200 | 🔧 Awaiting integration |
| ~~Legacy~~ | ~~4~~ | ~~270~~ | ✅ **REMOVED 2025-08-22** |
| ~~Backups~~ | ~~8~~ | ~~N/A~~ | ✅ **REMOVED 2025-08-22** |

**Updated Summary**: 13 total CSV files remain (7 active + 6 unintegrated), with 12 obsolete files successfully removed.

## System Configuration

Current deck_builder.py CSV mapping:
```python
csv_files = {
    "nouns.csv": "noun",
    "adjectives.csv": "adjective", 
    "adverbs.csv": "adverb",
    "negations.csv": "negation",
    "prepositions.csv": "preposition",
    "phrases.csv": "phrase",
    "verbs_unified.csv": "verb_conjugation",
    # Legacy disabled:
    "verbs.csv": "verb",
    # "regular_verbs.csv": "verb",  # REMOVED
    # "irregular_verbs.csv": "verb",  # REMOVED
    # "separable_verbs.csv": "verb",  # REMOVED
}
```

## Recommendations

### For New Development
1. Use only ACTIVE CSV files
2. Follow PROD-CSV-SPEC.md for any modifications
3. Add new word types to verbs_unified.csv pattern
4. Maintain english column naming convention

### For Maintenance
1. Schedule removal of backup files
2. Archive legacy verb CSVs to separate directory
3. Implement integration for high-priority unintegrated files
4. Consider consolidating pronoun files

### For Quality Assurance
1. Run validation against PROD-CSV-SPEC.md
2. Check for duplicate entries across legacy/active files
3. Verify all example sentences are complete
4. Ensure UTF-8 encoding for special characters

## Next Steps

1. **Immediate**: Review and approve this inventory
2. **This Week**: Integrate personal_pronouns.csv and cardinal_numbers.csv
3. **This Month**: Complete integration of all unintegrated files
4. **Next Month**: Archive legacy files and remove backups

## Version History

- **1.0** (2024-01): Initial inventory after meaning→english migration
  - Identified 7 active, 6 unintegrated, 4 legacy files
  - Documented integration priorities
  - Established cleanup plan