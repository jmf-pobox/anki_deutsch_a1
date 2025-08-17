# German A1 Anki Project - Architecture Refactoring

## 🎯 Current Status: **REFACTORING PHASE**
**Date Started**: August 2025  
**Objective**: Restore original clean architecture while preserving official Anki library and modern features  
**Quality Standards**: Full mypy --strict, SRP compliance, comprehensive testing

---

## 📋 Phase 1: Service Layer Restoration (Week 1)

### 🔧 Extract Media Generation Services
- [ ] **Create MediaService class** 
  - [ ] Extract media generation logic from monolithic AnkiBackend
  - [ ] Implement MediaGenerationConfig dataclass with slots
  - [ ] Add dependency injection for AudioService and PexelsService
  - [ ] Preserve context-aware image search functionality
  - [ ] Maintain audio compression and exponential backoff features

- [ ] **Create GermanLanguageService**
  - [ ] Extract German pattern matching from AnkiBackend
  - [ ] Move context extraction logic to dedicated service
  - [ ] Implement combined audio text generation (noun article+plural, adjective forms)
  - [ ] Add German grammar validation helpers

- [ ] **Create TemplateService** 
  - [ ] Extract template management from create_deck.py
  - [ ] Move templates to external files (HTML/CSS/config)
  - [ ] Preserve modern responsive styling and hint buttons
  - [ ] Implement template caching and loading

### 🃏 Restore Card Generator Pattern
- [ ] **Implement BaseCardGenerator[T] with generics**
  - [ ] Create abstract base class following Template Method pattern
  - [ ] Add type-safe generic implementation using PEP 695 syntax
  - [ ] Implement proper dependency injection for services

- [ ] **Create specialized card generators**
  - [ ] AdjectiveCardGenerator with combined audio generation
  - [ ] NounCardGenerator with article+plural audio
  - [ ] AdverbCardGenerator with conceptual image mapping
  - [ ] NegationCardGenerator with red-themed templates
  - [ ] Each generator follows SRP with single card type responsibility

---

## 📋 Phase 2: Backend Architecture Cleanup (Week 2)

### 🏗️ Refactor AnkiBackend Class
- [ ] **Reduce AnkiBackend to core responsibilities**
  - [ ] Remove German-specific logic (move to services)
  - [ ] Remove media generation (delegate to MediaService)
  - [ ] Remove template management (delegate to TemplateService)  
  - [ ] Keep only: note type creation, note adding, deck export, collection management

- [ ] **Implement clean DeckBackend interface**
  - [ ] Restore abstract base class with minimal interface
  - [ ] Ensure both genanki and official Anki backends implement same interface
  - [ ] Maintain polymorphic behavior for seamless switching

- [ ] **Create DeckManager and MediaManager**
  - [ ] Extract deck organization logic to DeckManager
  - [ ] Extract media handling logic to MediaManager  
  - [ ] Preserve subdeck functionality and media deduplication
  - [ ] Maintain SHA-256 hashing and corruption detection

### 🎯 Create GermanDeckBuilder Orchestrator
- [ ] **Implement composition-based architecture**
  - [ ] Create GermanDeckBuilder that orchestrates all services
  - [ ] Use dependency injection throughout for testability
  - [ ] Implement builder pattern for flexible deck construction
  - [ ] Preserve all existing functionality through clean composition

---

## 📋 Phase 3: Domain Model Enhancement (Week 2)

### 📊 Enhanced Pydantic Models  
- [ ] **Improve existing models with context awareness**
  - [ ] Add context extraction methods to Adjective model
  - [ ] Add combined audio text methods to Noun model
  - [ ] Enhance validation with better German grammar rules
  - [ ] Preserve all existing validation while adding new capabilities

- [ ] **Create domain enums and value objects**
  - [ ] AdjectiveCategory enum for semantic classification
  - [ ] GermanCase enum for grammatical cases
  - [ ] MediaAssets value object for generated media
  - [ ] AudioQuality and ImageSize configuration enums

### 🗂️ Data Processing Improvements
- [ ] **Enhance CSV processing**
  - [ ] Maintain generic CSVService but add German-specific loaders
  - [ ] Implement type-safe data loading with better error handling
  - [ ] Add data validation at boundary with comprehensive logging
  - [ ] Preserve backup functionality during processing

---

## 📋 Phase 4: Template and Styling Preservation (Week 3)

### 🎨 External Template System
- [ ] **Convert hard-coded templates to files**
  - [ ] Create template directory structure (front.html, back.html, style.css)
  - [ ] Preserve all modern CSS: responsive design, dark mode, mobile optimization
  - [ ] Maintain hint button functionality and audio button positioning
  - [ ] Keep accessibility improvements and gradients/shadows

- [ ] **Implement template configuration**
  - [ ] Create YAML/JSON config files for template metadata
  - [ ] Add template validation and loading error handling
  - [ ] Implement template inheritance for shared styling
  - [ ] Maintain German-specific features (gender colors, case tables)

### 📱 Feature Preservation  
- [ ] **Ensure no functionality regression**
  - [ ] Context-aware image search with sentence analysis
  - [ ] Combined audio files (adjective forms, noun article+plural)
  - [ ] Subdeck organization with Anki "::" naming
  - [ ] Audio compression (16kHz) and image optimization (medium size)
  - [ ] Exponential backoff for API rate limiting

---

## 📋 Phase 5: Testing and Quality Assurance (Week 3)

### 🧪 Comprehensive Testing Strategy
- [ ] **Unit tests for all new classes**
  - [ ] Test all services with mocked dependencies
  - [ ] Test card generators with sample data
  - [ ] Test domain models with edge cases
  - [ ] Achieve 100% test coverage on new code

- [ ] **Integration tests with keyring**
  - [ ] Test complete deck building process
  - [ ] Test API integrations with real credentials from keyring
  - [ ] Test performance benchmarks (maintain 3,900+ notes/second)
  - [ ] Test template rendering and media generation

### 📏 Code Quality Standards
- [ ] **Full mypy --strict compliance**
  - [ ] Add comprehensive type hints to all functions
  - [ ] Use PEP 695 generic syntax throughout
  - [ ] Eliminate all type errors and warnings

- [ ] **ruff compliance and formatting**
  - [ ] Apply automatic formatting with ruff format
  - [ ] Fix all linting issues with ruff check
  - [ ] Configure pre-commit hooks for quality gates

### 📊 Performance Validation
- [ ] **Benchmark performance against current implementation**
  - [ ] Maintain bulk operation speed (3,900+ notes/second)
  - [ ] Validate memory usage with large datasets
  - [ ] Test database optimization features (VACUUM, integrity checks)
  - [ ] Ensure no performance regression from architecture changes

---

## 📋 Phase 6: Documentation and Final Validation (Week 4)

### 📖 Architecture Documentation
- [ ] **Update DESIGN.md with new architecture**
  - [ ] Document the restored clean architecture
  - [ ] Explain service composition patterns
  - [ ] Provide examples of proper extension points
  - [ ] Include performance characteristics and trade-offs

- [ ] **Create migration guide**
  - [ ] Document changes from monolithic to clean architecture
  - [ ] Provide before/after comparisons
  - [ ] Explain benefits of new structure
  - [ ] Include troubleshooting guide

### ✅ Final Validation
- [ ] **End-to-end testing**
  - [ ] Generate complete German A1 deck with all word types
  - [ ] Validate media generation and deduplication  
  - [ ] Test subdeck organization and template rendering
  - [ ] Verify official Anki library integration works perfectly

- [ ] **Code review and cleanup**
  - [ ] Remove unused code from refactoring
  - [ ] Ensure all docstrings are comprehensive
  - [ ] Validate architectural principles are followed
  - [ ] Confirm all AI.md coding standards are met

---

## 🎯 Success Criteria

### ✅ Architecture Quality
- **Clean Separation**: Services, models, cards, backends have clear boundaries
- **Single Responsibility**: Each class has one reason to change
- **Dependency Injection**: All dependencies are injected, not created internally
- **Type Safety**: Full mypy --strict compliance with zero errors
- **Testability**: All business logic is unit testable with mocked dependencies

### ✅ Feature Preservation  
- **Official Anki Library**: All LIBRARY_REFACTOR.md achievements maintained
- **Performance**: 3,900+ notes/second bulk operations preserved
- **German Features**: Context-aware images, combined audio, subdeck organization
- **Modern Templates**: Responsive CSS, dark mode, hint buttons preserved
- **Media Handling**: SHA-256 deduplication, compression, API rate limiting

### ✅ Code Quality Standards
- **Testing**: 100% unit test coverage, integration tests with keyring
- **Documentation**: Comprehensive docstrings and architectural documentation
- **Maintainability**: Easy to extend with new card types and features  
- **Performance**: No regression in generation speed or memory usage

---

## 📈 Expected Benefits

🔧 **Maintainable Architecture**: Easy to understand, modify, and extend  
🧪 **Improved Testability**: All business logic isolated and testable  
⚡ **Preserved Performance**: All speed optimizations maintained  
🎨 **Enhanced Flexibility**: Easy to add new card types and templates  
🛡️ **Type Safety**: Comprehensive type checking prevents runtime errors  
📚 **Better Documentation**: Clear code structure with comprehensive docs  

**Result**: Production-quality German language learning platform with clean, maintainable architecture that preserves all advanced features and performance characteristics.