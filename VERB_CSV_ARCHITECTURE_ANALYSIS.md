# Verb CSV Architecture Analysis: Wide vs Normalized

**Date**: 2025-08-19  
**Author**: Design Guardian  
**Decision Required**: CSV structure for German verb data  
**Impact**: High - affects entire verb processing pipeline

---

## 🎯 Executive Summary

The user asks whether we should use **one row per verb per tense** in the CSV structure. This represents a fundamental architectural decision between:

1. **Wide Format** (current plan): One row per verb with 25-30 columns
2. **Normalized Format** (proposed): Multiple rows per verb with tense/person grouping

**RECOMMENDATION**: Use **Hybrid Normalized Format** - one row per conjugation pattern (6 rows per verb minimum) to balance data entry simplicity with architectural cleanliness.

---

## 📊 Architecture Comparison

### Option 1: Wide Format (Current Plan)
```csv
infinitive,meaning,classification,separable,auxiliary,present_ich,present_du,present_er,present_wir,present_ihr,present_sie,preterite_ich,preterite_du,preterite_er,preterite_wir,preterite_ihr,preterite_sie,perfect,example
arbeiten,to work,regelmäßig,false,haben,arbeite,arbeitest,arbeitet,arbeiten,arbeitet,arbeiten,arbeitete,arbeitetest,arbeitete,arbeiteten,arbeitetet,arbeiteten,hat gearbeitet,Ich arbeite bei Siemens
```

**Pros**:
- ✅ Single source of truth per verb
- ✅ Easy to validate completeness
- ✅ Aligns with current Noun/Adjective CSV patterns
- ✅ Simple VerbRecord structure

**Cons**:
- ❌ 25-30 columns become unwieldy
- ❌ Difficult to maintain in spreadsheet editors
- ❌ Violates database normalization principles
- ❌ Hard to extend for additional tenses

### Option 2: Fully Normalized (One Row Per Person Per Tense)
```csv
infinitive,meaning,classification,tense,person,form,separable,auxiliary,example
arbeiten,to work,regelmäßig,present,ich,arbeite,false,haben,
arbeiten,to work,regelmäßig,present,du,arbeitest,false,haben,
arbeiten,to work,regelmäßig,present,er,arbeitet,false,haben,
arbeiten,to work,regelmäßig,present,wir,arbeiten,false,haben,
arbeiten,to work,regelmäßig,present,ihr,arbeitet,false,haben,
arbeiten,to work,regelmäßig,present,sie,arbeiten,false,haben,
arbeiten,to work,regelmäßig,preterite,ich,arbeitete,false,haben,
[... 30+ more rows per verb ...]
```

**Pros**:
- ✅ Maximum flexibility
- ✅ Database-friendly structure
- ✅ Easy to add new tenses/persons

**Cons**:
- ❌ 36+ rows per verb (excessive)
- ❌ Massive data duplication
- ❌ Complex validation logic needed
- ❌ Difficult manual data entry

### Option 3: Hybrid Normalized ⭐ RECOMMENDED
```csv
infinitive,meaning,classification,separable,auxiliary,tense,ich,du,er,wir,ihr,sie,example
arbeiten,to work,regelmäßig,false,haben,present,arbeite,arbeitest,arbeitet,arbeiten,arbeitet,arbeiten,Ich arbeite bei Siemens
arbeiten,to work,regelmäßig,false,haben,preterite,arbeitete,arbeitetest,arbeitete,arbeiteten,arbeitetet,arbeiteten,Ich arbeitete gestern
arbeiten,to work,regelmäßig,false,haben,perfect,,,,,,,hat gearbeitet,Ich habe gearbeitet
arbeiten,to work,regelmäßig,false,haben,imperative,,arbeite,,,arbeitet,,Arbeite schneller!
arbeiten,to work,regelmäßig,false,haben,subjunctive,arbeitete,arbeitetest,arbeitete,arbeiteten,arbeitetet,arbeiteten,Wenn ich nur arbeitete
```

**Pros**:
- ✅ **Balanced complexity** - 5-6 rows per verb
- ✅ **Clean data entry** - one row per conjugation pattern
- ✅ **Maintains context** - verb metadata stays with each row
- ✅ **Extensible** - easy to add new tenses
- ✅ **Validation-friendly** - clear pattern requirements

**Cons**:
- ⚠️ Some data duplication (metadata repeated)
- ⚠️ Requires row grouping during processing

---

## 🏗️ Implementation Impact Analysis

### VerbRecord Structure Changes

#### Current (Wide Format):
```python
class VerbRecord(BaseRecord):
    infinitive: str
    meaning: str
    present_ich: str
    present_du: str
    # ... 20+ more conjugation fields
```

#### Proposed (Hybrid Normalized):
```python
class VerbConjugationRecord(BaseRecord):
    """Single conjugation pattern for a verb."""
    infinitive: str
    meaning: str
    classification: str  # regelmäßig/unregelmäßig/gemischt
    separable: bool
    auxiliary: str  # haben/sein
    tense: str  # present/preterite/perfect/imperative/subjunctive
    ich: str | None
    du: str | None
    er: str | None
    wir: str | None
    ihr: str | None
    sie: str | None
    example: str | None

class VerbRecord(BaseRecord):
    """Complete verb with all conjugations."""
    infinitive: str
    meaning: str
    classification: str
    separable: bool
    auxiliary: str
    conjugations: dict[str, VerbConjugationRecord]  # Grouped by tense
```

### RecordMapper Changes

```python
class RecordMapper:
    def map_verb_csv_to_records(self, csv_rows: list[dict]) -> list[VerbRecord]:
        """Group conjugation rows into complete VerbRecords."""
        verb_groups = {}
        
        for row in csv_rows:
            infinitive = row['infinitive']
            if infinitive not in verb_groups:
                verb_groups[infinitive] = {
                    'infinitive': infinitive,
                    'meaning': row['meaning'],
                    'classification': row['classification'],
                    'separable': row['separable'] == 'true',
                    'auxiliary': row['auxiliary'],
                    'conjugations': {}
                }
            
            # Add conjugation for this tense
            conj_record = VerbConjugationRecord.from_csv_row(row)
            verb_groups[infinitive]['conjugations'][row['tense']] = conj_record
        
        return [VerbRecord(**data) for data in verb_groups.values()]
```

### CardBuilder Impact

```python
class VerbCardBuilder:
    def build_core_verb_card(self, verb: VerbRecord) -> tuple:
        """Build main context/meaning card."""
        # Uses infinitive, meaning, classification, example
        
    def build_conjugation_card(self, verb: VerbRecord, tense: str) -> tuple:
        """Build tense-specific conjugation practice card."""
        conjugation = verb.conjugations[tense]
        # Generate cloze deletion or table format
```

---

## 🔄 Clean Pipeline Architecture Alignment

### Current Pipeline (Clean Architecture)
```
CSV → Records → MediaEnricher → CardBuilder → Anki Cards
```

### With Hybrid Normalized Verbs
```
CSV (grouped rows) → RecordMapper (grouping) → VerbRecord → MediaEnricher → CardBuilder → Multiple Card Types
```

**Architecture Compliance**:
- ✅ **Single Responsibility**: RecordMapper handles grouping logic
- ✅ **Clean Separation**: VerbRecord remains a pure data container
- ✅ **Testability**: Each component easily tested in isolation
- ✅ **Extensibility**: New tenses simply add rows to CSV

---

## 📝 Data Entry Experience Comparison

### Manual Entry Complexity

| Format | Rows per Verb | Columns | Entry Difficulty | Error Prone |
|--------|--------------|---------|-----------------|-------------|
| Wide | 1 | 25-30 | Hard (horizontal scrolling) | High |
| Fully Normalized | 36+ | 9 | Very Hard (repetitive) | Very High |
| **Hybrid** ⭐ | 5-6 | 13 | **Moderate (manageable)** | **Low** |

### Example Data Entry (Hybrid)

For a regular verb like "arbeiten":
1. Enter present tense row (all 6 persons)
2. Enter preterite row (all 6 persons)  
3. Enter perfect row (just the perfect form)
4. Enter imperative row (2-3 forms)
5. Optional: subjunctive row

**Total**: 5 rows vs 1 super-wide row vs 36+ normalized rows

---

## ✅ Validation & Quality Assurance

### Validation Requirements

```python
class VerbValidator:
    def validate_verb_completeness(self, verb: VerbRecord) -> list[str]:
        """Ensure verb has required tenses for its level."""
        errors = []
        
        # A1 verbs need present and perfect
        if verb.level == 'A1':
            if 'present' not in verb.conjugations:
                errors.append(f"{verb.infinitive}: missing present tense")
            if 'perfect' not in verb.conjugations:
                errors.append(f"{verb.infinitive}: missing perfect tense")
        
        # Validate conjugation patterns
        for tense, conj in verb.conjugations.items():
            if tense in ['present', 'preterite']:
                # These tenses need all persons
                if not all([conj.ich, conj.du, conj.er, conj.wir, conj.ihr, conj.sie]):
                    errors.append(f"{verb.infinitive} {tense}: incomplete conjugation")
        
        return errors
```

---

## 🚀 Migration Path

### Phase 1: Update CSV Structure
1. Convert existing verbs.csv to hybrid format
2. Create migration script for automation
3. Validate all conjugations preserved

### Phase 2: Implement VerbConjugationRecord
1. Create new record type
2. Update RecordMapper with grouping logic
3. Add comprehensive tests

### Phase 3: Update CardBuilder
1. Implement two-tier card generation
2. Create conjugation card templates
3. Test with sample verbs

### Phase 4: Full Integration
1. Update AnkiBackend for verb support
2. Run complete test suite
3. Generate sample deck for validation

---

## 🎯 Final Recommendation

**USE HYBRID NORMALIZED FORMAT** for the following reasons:

1. **Balanced Complexity**: 5-6 rows per verb is manageable
2. **Clean Architecture Fit**: Works well with RecordMapper grouping
3. **Content Creator Friendly**: Easier than 30 columns or 36+ rows
4. **Future Proof**: Easy to add subjunctive, conditional, etc.
5. **Validation Friendly**: Clear pattern for completeness checking
6. **Two-Tier Card Support**: Aligns with VERBS.md architecture

### Proposed CSV Structure
```csv
infinitive,meaning,classification,separable,auxiliary,tense,ich,du,er,wir,ihr,sie,example
arbeiten,to work,regelmäßig,false,haben,present,arbeite,arbeitest,arbeitet,arbeiten,arbeitet,arbeiten,Ich arbeite bei Siemens
arbeiten,to work,regelmäßig,false,haben,preterite,arbeitete,arbeitetest,arbeitete,arbeiteten,arbeitetet,arbeiteten,Ich arbeitete gestern
arbeiten,to work,regelmäßig,false,haben,perfect,,,,,,,hat gearbeitet,Er hat viel gearbeitet
arbeiten,to work,regelmäßig,false,haben,imperative,,arbeite,,,arbeitet,,Arbeite schneller!
```

This structure:
- ✅ Maintains data integrity
- ✅ Supports efficient processing
- ✅ Enables two-tier card generation
- ✅ Balances normalization with practicality
- ✅ Aligns with Clean Pipeline Architecture

---

## 🔄 Next Steps

1. **Get user confirmation** on hybrid approach
2. **Create sample CSV** with 5-10 verbs
3. **Prototype VerbConjugationRecord**
4. **Test RecordMapper grouping logic**
5. **Validate with CardBuilder integration**

The hybrid normalized approach provides the best balance between data integrity, maintainability, and practical content creation needs while fully supporting the two-tier card system outlined in VERBS.md.