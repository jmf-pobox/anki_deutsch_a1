# 🏗️ Multi-Deck, Multi-Language Architecture Design

**Current Status**: 🟡 **PARTIALLY IMPLEMENTED**

## Implementation Status

### ✅ **Currently Implemented**
- **Language-specific structure**: `src/langlearn/languages/german/` with models, records, templates
- **Multiple German decks**: `languages/german/a1/`, `a1.1/`, `business/`, `default/` with CSV data
- **German record system**: 15+ record types with factory pattern
- **DeckManager**: Subdeck management with "::" naming convention
- **Multi-language foundation**: Korean and Russian directories exist

### 🚧 **Planned/Not Yet Implemented**
- **Deck configuration system**: YAML-based deck configs
- **AssetManager**: Hash-based asset management and deduplication
- **MultiDeckBuilder**: Unified builder for multiple deck types
- **CLI interface**: Command-line deck generation
- **Asset manifest system**: Tracking and sharing across decks

## Executive Summary

This document describes the current multi-deck, multi-language architecture (partially implemented) and planned enhancements for a fully scalable, Clean Architecture-compliant solution. The architecture emphasizes content creator friendliness, efficient asset management, and future extensibility.

## 📁 1. Directory Structure Design

### **Current vs. Proposed Directory Structure**

**Current Implementation**:
```
anki_deutsch_a1/
├── src/langlearn/languages/        # Language-specific code (✅ implemented)
│   └── german/
│       ├── models/                 # Domain models
│       ├── records/                # Record types (15+ types)
│       ├── templates/              # Card templates
│       └── services/               # German-specific services
├── languages/                      # Content data (✅ implemented)
│   ├── german/
│   │   ├── a1/                    # A1 deck CSVs
│   │   ├── a1.1/                  # A1.1 deck CSVs
│   │   ├── business/              # Business German CSVs
│   │   ├── default/               # Default/legacy CSVs
│   │   └── audio/, images/        # Media files
│   ├── korean/                    # Korean foundation
│   └── russian/                   # Russian foundation
└── data/                          # Legacy compatibility
```

**Proposed Future Structure**:

```
anki_langlearn/
├── decks/                          # Deck definitions (new)
│   ├── config/                     # Deck configuration files
│   │   ├── german_a1_basic.yaml
│   │   ├── german_a1_business.yaml
│   │   ├── german_a2_intermediate.yaml
│   │   ├── russian_a1_basic.yaml
│   │   └── korean_a1_basic.yaml
│   │
│   ├── content/                    # CSV content organized by deck
│   │   ├── german/
│   │   │   ├── a1_basic/
│   │   │   │   ├── nouns.csv
│   │   │   │   ├── verbs.csv
│   │   │   │   └── ...
│   │   │   ├── a1_business/
│   │   │   │   ├── nouns.csv
│   │   │   │   └── ...
│   │   │   └── a2_intermediate/
│   │   │       └── ...
│   │   ├── russian/
│   │   │   └── a1_basic/
│   │   │       └── ...
│   │   └── korean/
│   │       └── a1_basic/
│   │           └── ...
│   │
│   └── templates/                  # Language/deck-specific templates
│       ├── german/
│       │   ├── noun_DE_de.css
│       │   ├── noun_DE_de_front.html
│       │   └── ...
│       ├── russian/
│       │   └── ...
│       └── korean/
│           └── ...
│
├── assets/                         # Shared media assets (renamed from data/)
│   ├── audio/
│   │   ├── german/                # Language-specific audio
│   │   │   ├── a1_basic/
│   │   │   │   └── {hash}.mp3    # Hash-based naming
│   │   │   ├── a1_business/
│   │   │   └── shared/           # Audio shared across German decks
│   │   ├── russian/
│   │   └── korean/
│   │
│   ├── images/
│   │   ├── universal/             # Language-agnostic images
│   │   │   └── {hash}.jpg
│   │   ├── german/                # German-specific images
│   │   │   ├── a1_business/      # Business context images
│   │   │   └── shared/
│   │   └── ...
│   │
│   └── cache/                     # Media cache manifests
│       ├── audio_manifest.json    # Track all audio files
│       └── image_manifest.json    # Track all images
│
├── output/                         # Generated .apkg files
│   ├── german/
│   │   ├── german_a1_basic_v1.0.apkg
│   │   ├── german_a1_business_v1.0.apkg
│   │   └── ...
│   ├── russian/
│   └── korean/
│
└── data/                          # Legacy compatibility symlink → decks/content/german/a1_basic/
```

### **Migration Strategy for Existing Data**

```python
# Migration script to preserve backward compatibility
def migrate_to_multi_deck_structure():
    """One-time migration from legacy to multi-deck structure."""
    
    # 1. Move existing CSV files
    shutil.move("data/*.csv", "decks/content/german/a1_basic/")
    
    # 2. Reorganize audio files with hash preservation
    for audio_file in Path("data/audio").glob("*.mp3"):
        shutil.move(audio_file, "assets/audio/german/a1_basic/")
    
    # 3. Create symlink for backward compatibility
    os.symlink("decks/content/german/a1_basic", "data")
    
    # 4. Generate initial deck config
    create_deck_config("german_a1_basic", legacy=True)
```

## 💾 2. Asset Management Strategy

### **Hash-Based Asset Naming System**

```python
class AssetManager:
    """Centralized asset management with efficient sharing."""
    
    def get_asset_path(
        self,
        content: str,
        asset_type: str,
        language: str,
        deck: str | None = None,
        context: str | None = None
    ) -> Path:
        """Generate deterministic path for any asset."""
        
        # Generate content hash for deduplication
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        if asset_type == "audio":
            # Audio is language-specific
            if self._is_shared_audio(content, language):
                return Path(f"assets/audio/{language}/shared/{content_hash}.mp3")
            else:
                return Path(f"assets/audio/{language}/{deck}/{content_hash}.mp3")
                
        elif asset_type == "image":
            # Images can be universal or context-specific
            if self._is_universal_image(content):
                return Path(f"assets/images/universal/{content_hash}.jpg")
            elif context:
                return Path(f"assets/images/{language}/{context}/{content_hash}.jpg")
            else:
                return Path(f"assets/images/{language}/shared/{content_hash}.jpg")
```

### **Asset Manifest System**

```python
class AssetManifest:
    """Track asset usage across decks for efficient packaging."""
    
    def __init__(self, manifest_path: Path):
        self.manifest = self._load_manifest(manifest_path)
    
    def register_asset(
        self,
        asset_path: Path,
        deck_id: str,
        content: str,
        metadata: dict
    ):
        """Register asset usage by a specific deck."""
        
        asset_key = str(asset_path)
        if asset_key not in self.manifest:
            self.manifest[asset_key] = {
                "content": content,
                "hash": self._calculate_hash(asset_path),
                "decks": [],
                "metadata": metadata,
                "created": datetime.now().isoformat()
            }
        
        if deck_id not in self.manifest[asset_key]["decks"]:
            self.manifest[asset_key]["decks"].append(deck_id)
    
    def get_deck_assets(self, deck_id: str) -> list[Path]:
        """Get all assets used by a specific deck."""
        
        return [
            Path(asset_path)
            for asset_path, info in self.manifest.items()
            if deck_id in info["decks"]
        ]
```

## 🎯 3. Application Interface Design

### **Deck Configuration Schema**

```yaml
# decks/config/german_a1_basic.yaml
deck:
  id: german_a1_basic
  name: "German A1 - Basic Vocabulary"
  language: german
  level: a1
  variant: basic
  version: "1.0.0"
  
content:
  base_path: "decks/content/german/a1_basic"
  files:
    - nouns.csv
    - verbs.csv
    - adjectives.csv
    - adverbs.csv
    - prepositions.csv
    - phrases.csv
    - negations.csv
    
templates:
  path: "decks/templates/german"
  custom_overrides:
    noun: "noun_a1_basic.html"  # Optional deck-specific template
    
media:
  audio:
    voice: "Marlene"  # AWS Polly voice
    speed: 1.0
    shared_with: ["german_a1_business"]  # Share audio with other decks
  images:
    preferred_context: "everyday"  # Context for Pexels searches
    fallback_to_universal: true
    
export:
  output_dir: "output/german"
  filename_pattern: "{id}_v{version}.apkg"
  include_metadata: true
```

### **CLI Interface Design**

```python
# New CLI interface for deck generation
class DeckCLI:
    """Command-line interface for multi-deck generation."""
    
    @click.command()
    @click.option('--deck', '-d', required=True, help='Deck configuration ID')
    @click.option('--media/--no-media', default=True, help='Generate media files')
    @click.option('--force', '-f', is_flag=True, help='Regenerate existing assets')
    @click.option('--output', '-o', help='Override output path')
    def generate(deck: str, media: bool, force: bool, output: str | None):
        """Generate a single Anki deck from configuration."""
        
        # Load deck configuration
        config = DeckConfig.load(f"decks/config/{deck}.yaml")
        
        # Initialize builder with deck config
        builder = MultiDeckBuilder(config)
        
        # Load content from configured sources
        builder.load_content()
        
        # Generate media if requested
        if media:
            builder.generate_media(force_regenerate=force)
        
        # Build and export deck
        output_path = output or config.get_output_path()
        builder.export_deck(output_path)
        
        click.echo(f"✅ Generated {deck} → {output_path}")

# Usage examples:
# python -m langlearn generate --deck german_a1_basic
# python -m langlearn generate --deck russian_a1_basic --no-media
# python -m langlearn generate --deck korean_a1_basic --force
```

## 🏛️ 4. Architecture Integration

### **Enhanced DeckBuilder for Multi-Deck Support**

```python
class MultiDeckBuilder(DeckBuilder):
    """Extended DeckBuilder with multi-deck, multi-language support."""
    
    def __init__(self, deck_config: DeckConfig):
        """Initialize with deck configuration."""
        
        self.config = deck_config
        self.language = deck_config.language
        self.deck_id = deck_config.id
        
        # Initialize base DeckBuilder
        super().__init__(
            deck_name=deck_config.name,
            backend_type="anki"
        )
        
        # Initialize language-specific services
        self._init_language_services()
        
        # Initialize asset manager
        self.asset_manager = AssetManager()
        self.asset_manifest = AssetManifest(
            Path(f"assets/cache/{self.deck_id}_manifest.json")
        )
    
    def _init_language_services(self):
        """Initialize language-specific services."""
        
        # Language-specific template service
        template_dir = Path(self.config.templates.path)
        self._template_service = TemplateService(template_dir)
        
        # Language-specific audio service
        self._audio_service = self._create_audio_service(self.language)
        
        # Language-specific validation
        self._validator = self._create_validator(self.language)
    
    def load_content(self):
        """Load content from deck-specific CSV files."""
        
        base_path = Path(self.config.content.base_path)
        
        for csv_file in self.config.content.files:
            file_path = base_path / csv_file
            if file_path.exists():
                self._load_csv_with_validation(file_path)
    
    def generate_media(self, force_regenerate: bool = False):
        """Generate media with smart asset sharing."""
        
        for record in self._loaded_records:
            # Check if asset already exists
            existing_asset = self._find_existing_asset(record)
            
            if existing_asset and not force_regenerate:
                # Register existing asset for this deck
                self.asset_manifest.register_asset(
                    existing_asset, self.deck_id, record.to_dict(), {}
                )
            else:
                # Generate new asset
                new_asset = self._generate_new_asset(record)
                self.asset_manifest.register_asset(
                    new_asset, self.deck_id, record.to_dict(), {}
                )
```

### **Enhanced MediaEnricher for Multi-Language**

```python
class MultiLanguageMediaEnricher(StandardMediaEnricher):
    """MediaEnricher with multi-language support."""
    
    def __init__(
        self,
        media_service: MediaServiceProtocol,
        language: str,
        deck_id: str,
        asset_manager: AssetManager
    ):
        super().__init__(media_service)
        self.language = language
        self.deck_id = deck_id
        self.asset_manager = asset_manager
    
    def enrich_record(
        self,
        record: dict[str, Any],
        domain_model: Any
    ) -> dict[str, Any]:
        """Enrich with language-aware asset management."""
        
        enriched = {}
        
        # Generate audio with language-specific voice
        if hasattr(domain_model, "get_audio_text"):
            audio_text = domain_model.get_audio_text()
            audio_path = self.asset_manager.get_asset_path(
                audio_text, "audio", self.language, self.deck_id
            )
            
            if not audio_path.exists():
                self._generate_language_audio(audio_text, audio_path)
            
            enriched["audio"] = str(audio_path)
        
        # Generate images with context awareness
        if hasattr(domain_model, "get_image_query"):
            query = domain_model.get_image_query()
            context = self._determine_image_context(record)
            
            image_path = self.asset_manager.get_asset_path(
                query, "image", self.language, self.deck_id, context
            )
            
            if not image_path.exists():
                self._generate_contextual_image(query, image_path, context)
            
            enriched["image"] = str(image_path)
        
        return enriched
```

## 🌍 5. Future Language Expansion

### **Language-Specific Adapters**

```python
class LanguageAdapter(ABC):
    """Abstract base for language-specific processing."""
    
    @abstractmethod
    def get_audio_voice(self) -> str:
        """Get TTS voice for this language."""
        pass
    
    @abstractmethod
    def validate_grammar(self, record: BaseRecord) -> bool:
        """Validate language-specific grammar rules."""
        pass
    
    @abstractmethod
    def get_card_fields(self, word_type: str) -> list[str]:
        """Get language-specific card fields."""
        pass

class GermanAdapter(LanguageAdapter):
    """German language adapter."""
    
    def get_audio_voice(self) -> str:
        return "Marlene"  # AWS Polly German voice
    
    def validate_grammar(self, record: BaseRecord) -> bool:
        # German-specific validation (articles, cases, etc.)
        if isinstance(record, NounRecord):
            return record.article in ["der", "die", "das"]
        return True
    
    def get_card_fields(self, word_type: str) -> list[str]:
        if word_type == "noun":
            return ["Article", "Noun", "English", "Plural", "Example"]
        return super().get_card_fields(word_type)

class RussianAdapter(LanguageAdapter):
    """Russian language adapter."""
    
    def get_audio_voice(self) -> str:
        return "Tatyana"  # AWS Polly Russian voice
    
    def validate_grammar(self, record: BaseRecord) -> bool:
        # Russian-specific validation (cases, aspects, etc.)
        if isinstance(record, VerbRecord):
            return self._validate_aspect(record)
        return True

class KoreanAdapter(LanguageAdapter):
    """Korean language adapter."""
    
    def get_audio_voice(self) -> str:
        return "Seoyeon"  # AWS Polly Korean voice
    
    def validate_grammar(self, record: BaseRecord) -> bool:
        # Korean-specific validation (honorifics, particles, etc.)
        if hasattr(record, "honorific_level"):
            return record.honorific_level in ["formal", "informal", "polite"]
        return True
```

### **Language Registry System**

```python
class LanguageRegistry:
    """Central registry for language support."""
    
    _adapters: dict[str, type[LanguageAdapter]] = {
        "german": GermanAdapter,
        "russian": RussianAdapter,
        "korean": KoreanAdapter,
        "spanish": SpanishAdapter,
        "french": FrenchAdapter,
        "japanese": JapaneseAdapter,
        "chinese": ChineseAdapter,
    }
    
    @classmethod
    def get_adapter(cls, language: str) -> LanguageAdapter:
        """Get language adapter instance."""
        
        if language not in cls._adapters:
            raise UnsupportedLanguageError(f"Language '{language}' not supported")
        
        return cls._adapters[language]()
    
    @classmethod
    def register_language(cls, language: str, adapter: type[LanguageAdapter]):
        """Register new language support."""
        
        cls._adapters[language] = adapter
```

## 🚀 6. Implementation Strategy

### **Phase 1: Foundation (Week 1-2)**
1. Create directory structure migration script
2. Implement AssetManager and AssetManifest
3. Create DeckConfig loader and validator
4. Update existing DeckBuilder with config support
5. Maintain full backward compatibility

### **Phase 2: Multi-Deck Support (Week 3-4)**
1. Implement MultiDeckBuilder
2. Create CLI interface
3. Add deck configuration for German variants
4. Test asset sharing between decks
5. Validate .apkg isolation

### **Phase 3: Language Expansion (Week 5-6)**
1. Implement LanguageAdapter system
2. Create LanguageRegistry
3. Add Russian language adapter
4. Create Russian A1 deck configuration
5. Test multi-language generation

### **Phase 4: Optimization (Week 7-8)**
1. Implement asset deduplication
2. Add incremental generation support
3. Create batch deck generation
4. Add deck versioning system
5. Performance optimization

## 🧪 Testing Strategy

### **Multi-Deck Test Suite**

```python
class TestMultiDeckGeneration:
    """Test multi-deck functionality."""
    
    def test_deck_isolation(self):
        """Ensure each deck contains only its assets."""
        
        # Generate two related decks
        builder1 = MultiDeckBuilder(load_config("german_a1_basic"))
        builder1.generate_all_cards()
        deck1_assets = builder1.get_included_assets()
        
        builder2 = MultiDeckBuilder(load_config("german_a1_business"))
        builder2.generate_all_cards()
        deck2_assets = builder2.get_included_assets()
        
        # Verify appropriate isolation
        assert "business_context.jpg" not in deck1_assets
        assert "basic_home.jpg" not in deck2_assets
    
    def test_asset_sharing(self):
        """Test efficient asset sharing."""
        
        # Generate deck with shared assets
        config = load_config("german_a1_basic")
        builder = MultiDeckBuilder(config)
        
        # Check that shared audio is reused
        audio_path1 = builder.get_audio_path("Haus")
        audio_path2 = builder.get_audio_path("Haus", deck="german_a1_business")
        
        assert audio_path1.exists()
        assert audio_path1 == audio_path2  # Same file
    
    def test_language_adapter(self):
        """Test language-specific processing."""
        
        # Test German adapter
        german = LanguageRegistry.get_adapter("german")
        assert german.get_audio_voice() == "Marlene"
        
        # Test Russian adapter
        russian = LanguageRegistry.get_adapter("russian")
        assert russian.get_audio_voice() == "Tatyana"
```

## 📊 Quality Metrics

### **Success Criteria**
- ✅ Zero breaking changes to existing German A1 generation
- ✅ Asset deduplication reduces storage by >30%
- ✅ Deck generation time <5 minutes per 1000 cards
- ✅ Test coverage maintained at >73%
- ✅ Support for 3+ languages validated
- ✅ Content creator can add new deck in <30 minutes

## 🎯 Key Design Decisions

1. **Hash-based asset naming**: Enables automatic deduplication while preventing conflicts
2. **Manifest system**: Tracks asset usage for efficient packaging and cleanup
3. **Language adapters**: Extensible pattern for language-specific logic
4. **Deck configuration**: YAML-based for human readability and version control
5. **Backward compatibility**: Symlinks and legacy paths preserve existing workflows
6. **Asset sharing strategy**: Explicit configuration of shared vs. isolated assets

## 🔧 Migration Path

```bash
# Step 1: Backup existing data
cp -r data/ data_backup/

# Step 2: Run migration script
python scripts/migrate_to_multi_deck.py

# Step 3: Verify legacy compatibility
python run_sample.py  # Should work unchanged

# Step 4: Test new multi-deck
python -m langlearn generate --deck german_a1_basic

# Step 5: Add new deck
python -m langlearn create-deck --template german_a1 --name german_a1_travel
```

This architecture provides a robust foundation for multi-deck, multi-language support while maintaining the Clean Architecture principles and quality standards established in the project. The design emphasizes developer experience, content creator friendliness, and long-term maintainability.