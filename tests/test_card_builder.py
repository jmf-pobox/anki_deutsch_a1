"""Tests for CardBuilder service."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from langlearn.backends.base import CardTemplate, NoteType
from langlearn.models.records import BaseRecord, create_record
from langlearn.services.card_builder import CardBuilder
from langlearn.services.template_service import TemplateService


class TestCardBuilder:
    """Test CardBuilder service functionality."""

    @pytest.fixture
    def mock_template_service(self) -> Mock:
        """Create mock template service."""
        mock_service = Mock(spec=TemplateService)

        # Create mock templates for different record types
        mock_templates = {
            "noun": CardTemplate(
                name="German Noun with Media",
                front_html="{{Noun}} ({{Article}})",
                back_html="{{English}}",
                css=".card { color: blue; }",
            ),
            "adjective": CardTemplate(
                name="German Adjective with Media",
                front_html="{{Word}}",
                back_html="{{English}}",
                css=".card { color: green; }",
            ),
            "adverb": CardTemplate(
                name="German Adverb with Media",
                front_html="{{Word}}",
                back_html="{{English}} ({{Type}})",
                css=".card { color: orange; }",
            ),
            "negation": CardTemplate(
                name="German Negation with Media",
                front_html="{{Word}}",
                back_html="{{English}} ({{Type}})",
                css=".card { color: red; }",
            ),
            "verb_conjugation": CardTemplate(
                name="German Verb Conjugation with Media",
                front_html="{{Infinitive}} - {{Tense}}",
                back_html="{{Ich}}, {{Du}}, {{Er}}",
                css=".card { color: purple; }",
            ),
            "verb_imperative": CardTemplate(
                name="German Verb Imperative with Media",
                front_html="{{Infinitive}} - Commands",
                back_html="{{DuForm}}, {{IhrForm}}, {{SieForm}}",
                css=".card { color: brown; }",
            ),
        }

        mock_service.get_template.side_effect = lambda card_type: mock_templates[
            card_type
        ]
        return mock_service

    @pytest.fixture
    def card_builder(self, mock_template_service: Mock) -> CardBuilder:
        """Create CardBuilder instance for testing."""
        return CardBuilder(template_service=mock_template_service)

    def test_card_builder_initialization(self) -> None:
        """Test CardBuilder initialization."""
        # Test with mock template service
        mock_service = Mock(spec=TemplateService)
        builder = CardBuilder(template_service=mock_service)
        assert builder._template_service is mock_service

        # Test with default initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            template_dir = temp_path / "src" / "langlearn" / "templates"
            template_dir.mkdir(parents=True)

            # Create a minimal template file
            (template_dir / "noun_front.html").write_text("{{Noun}}")
            (template_dir / "noun_back.html").write_text("{{English}}")
            (template_dir / "noun_style.css").write_text(".card {}")

            builder = CardBuilder(project_root=temp_path)
            assert isinstance(builder._template_service, TemplateService)

    def test_build_card_from_noun_record(self, card_builder: CardBuilder) -> None:
        """Test building card from noun record."""
        # Create noun record
        record = create_record(
            "noun", ["Katze", "die", "cat", "Katzen", "Die Katze ist süß.", "Tier"]
        )

        # Build card
        field_values, note_type = card_builder.build_card_from_record(record)

        # Verify field values
        assert len(field_values) == 9  # 9 fields for noun
        assert field_values[0] == "Katze"  # Noun
        assert field_values[1] == "die"  # Article
        assert field_values[2] == "cat"  # English
        assert field_values[3] == "Katzen"  # Plural
        assert field_values[4] == "Die Katze ist süß."  # Example
        assert field_values[5] == "Tier"  # Related
        assert field_values[6] == ""  # Image (empty)
        assert field_values[7] == ""  # WordAudio (empty)
        assert field_values[8] == ""  # ExampleAudio (empty)

        # Verify note type
        assert isinstance(note_type, NoteType)
        assert note_type.name == "German Noun with Media"
        assert len(note_type.fields) == 9
        assert "Noun" in note_type.fields
        assert "Article" in note_type.fields

    def test_build_card_from_noun_record_with_enriched_data(
        self, card_builder: CardBuilder
    ) -> None:
        """Test building card from noun record with enriched media data."""
        # Create noun record
        record = create_record(
            "noun", ["Katze", "die", "cat", "Katzen", "Die Katze ist süß.", "Tier"]
        )

        # Create enriched data with media
        enriched_data = {
            "image": "cat_image.jpg",
            "word_audio": "die_katze.mp3",
            "example_audio": "example_sentence.mp3",
        }

        # Build card
        field_values, note_type = card_builder.build_card_from_record(
            record, enriched_data
        )

        # Verify enriched field values
        assert field_values[6] == '<img src="cat_image.jpg" />'  # Image formatted
        assert field_values[7] == "[sound:die_katze.mp3]"  # WordAudio formatted
        assert field_values[8] == "[sound:example_sentence.mp3]"  # ExampleAudio

    def test_build_card_from_adjective_record(self, card_builder: CardBuilder) -> None:
        """Test building card from adjective record."""
        # Create adjective record
        record = create_record(
            "adjective",
            ["schön", "beautiful", "Das ist schön.", "schöner", "am schönsten"],
        )

        # Build card
        field_values, note_type = card_builder.build_card_from_record(record)

        # Verify field values
        assert len(field_values) == 8  # 8 fields for adjective
        assert field_values[0] == "schön"  # Word
        assert field_values[1] == "beautiful"  # English
        assert field_values[2] == "Das ist schön."  # Example
        assert field_values[3] == "schöner"  # Comparative
        assert field_values[4] == "am schönsten"  # Superlative
        assert field_values[5] == ""  # Image (empty)
        assert field_values[6] == ""  # WordAudio (empty)
        assert field_values[7] == ""  # ExampleAudio (empty)

        # Verify note type
        assert note_type.name == "German Adjective with Media"

    def test_build_card_from_adverb_record(self, card_builder: CardBuilder) -> None:
        """Test building card from adverb record."""
        # Create adverb record
        record = create_record("adverb", ["hier", "here", "location", "Ich bin hier."])

        # Build card
        field_values, note_type = card_builder.build_card_from_record(record)

        # Verify field values
        assert len(field_values) == 7  # 7 fields for adverb
        assert field_values[0] == "hier"  # Word
        assert field_values[1] == "here"  # English
        assert field_values[2] == "location"  # Type
        assert field_values[3] == "Ich bin hier."  # Example
        assert field_values[4] == ""  # Image (empty)
        assert field_values[5] == ""  # WordAudio (empty)
        assert field_values[6] == ""  # ExampleAudio (empty)

        # Verify note type
        assert note_type.name == "German Adverb with Media"

    def test_build_card_from_negation_record(self, card_builder: CardBuilder) -> None:
        """Test building card from negation record."""
        # Create negation record
        record = create_record(
            "negation", ["nicht", "not", "general", "Das ist nicht gut."]
        )

        # Build card
        field_values, note_type = card_builder.build_card_from_record(record)

        # Verify field values
        assert len(field_values) == 7  # 7 fields for negation
        assert field_values[0] == "nicht"  # Word
        assert field_values[1] == "not"  # English
        assert field_values[2] == "general"  # Type
        assert field_values[3] == "Das ist nicht gut."  # Example

        # Verify note type
        assert note_type.name == "German Negation with Media"

    def test_build_cards_from_multiple_records(self, card_builder: CardBuilder) -> None:
        """Test building cards from multiple records."""
        # Create multiple records
        records = [
            create_record(
                "noun", ["Katze", "die", "cat", "Katzen", "Die Katze ist süß.", "Tier"]
            ),
            create_record(
                "adjective",
                ["schön", "beautiful", "Das ist schön.", "schöner", "am schönsten"],
            ),
            create_record("adverb", ["hier", "here", "location", "Ich bin hier."]),
        ]

        # Build cards
        cards = card_builder.build_cards_from_records(records)

        # Verify results
        assert len(cards) == 3

        # Check each card
        noun_fields, noun_note_type = cards[0]
        assert len(noun_fields) == 9
        assert noun_note_type.name == "German Noun with Media"

        adj_fields, adj_note_type = cards[1]
        assert len(adj_fields) == 8
        assert adj_note_type.name == "German Adjective with Media"

        adv_fields, adv_note_type = cards[2]
        assert len(adv_fields) == 7
        assert adv_note_type.name == "German Adverb with Media"

    def test_build_cards_from_records_with_enriched_data(
        self, card_builder: CardBuilder
    ) -> None:
        """Test building cards from records with enriched data."""
        # Create records
        records = [
            create_record(
                "noun", ["Katze", "die", "cat", "Katzen", "Die Katze ist süß.", "Tier"]
            ),
            create_record(
                "adjective",
                ["schön", "beautiful", "Das ist schön.", "schöner", "am schönsten"],
            ),
        ]

        # Create enriched data
        enriched_data_list = [
            {"image": "cat.jpg", "word_audio": "katze.mp3"},
            {"image": "beautiful.jpg", "word_audio": "schoen.mp3"},
        ]

        # Build cards
        cards = card_builder.build_cards_from_records(records, enriched_data_list)

        # Verify enriched data was applied
        noun_fields, _ = cards[0]
        assert noun_fields[6] == '<img src="cat.jpg" />'
        assert noun_fields[7] == "[sound:katze.mp3]"

        adj_fields, _ = cards[1]
        assert adj_fields[5] == '<img src="beautiful.jpg" />'
        assert adj_fields[6] == "[sound:schoen.mp3]"

    def test_field_value_formatting(self, card_builder: CardBuilder) -> None:
        """Test field value formatting for different field types."""
        # Test audio formatting
        audio_value = card_builder._format_field_value("WordAudio", "test.mp3")
        assert audio_value == "[sound:test.mp3]"

        # Test image formatting
        image_value = card_builder._format_field_value("Image", "test.jpg")
        assert image_value == '<img src="test.jpg" />'

        # Test already formatted values are not double-formatted
        already_formatted_audio = card_builder._format_field_value(
            "WordAudio", "[sound:test.mp3]"
        )
        assert already_formatted_audio == "[sound:test.mp3]"

        already_formatted_image = card_builder._format_field_value(
            "Image", '<img src="test.jpg" />'
        )
        assert already_formatted_image == '<img src="test.jpg" />'

        # Test text fields are unchanged
        text_value = card_builder._format_field_value("English", "hello")
        assert text_value == "hello"

        # Test None values become empty strings
        none_value = card_builder._format_field_value("English", None)
        assert none_value == ""

    def test_get_supported_record_types(self, card_builder: CardBuilder) -> None:
        """Test getting supported record types."""
        types = card_builder.get_supported_record_types()
        assert set(types) == {
            "noun",
            "adjective",
            "adverb",
            "negation",
            "verb",
            "phrase",
            "preposition",
            "verb_conjugation",
            "verb_imperative",
        }

    def test_validate_record_for_card_building_valid(
        self, card_builder: CardBuilder
    ) -> None:
        """Test validation with valid records."""
        # Valid noun
        noun_record = create_record(
            "noun", ["Katze", "die", "cat", "Katzen", "Example", "Tier"]
        )
        assert card_builder.validate_record_for_card_building(noun_record) is True

        # Valid adjective
        adj_record = create_record(
            "adjective", ["schön", "beautiful", "Example", "schöner", "am schönsten"]
        )
        assert card_builder.validate_record_for_card_building(adj_record) is True

    def test_validate_record_for_card_building_invalid(
        self, card_builder: CardBuilder
    ) -> None:
        """Test validation with invalid records."""
        # Missing required fields for noun (missing english)
        noun_record = create_record(
            "noun", ["Katze", "die", "", "Katzen", "Example", "Tier"]
        )
        assert card_builder.validate_record_for_card_building(noun_record) is False

        # Missing required fields for adjective (missing english)
        adj_record = create_record(
            "adjective", ["schön", "", "Example", "schöner", "am schönsten"]
        )
        assert card_builder.validate_record_for_card_building(adj_record) is False

    def test_build_cards_with_error_handling(self, card_builder: CardBuilder) -> None:
        """Test error handling during card building."""
        # Create records, one valid and one that will cause an error
        records = [
            create_record("noun", ["Katze", "die", "cat", "Katzen", "Example", "Tier"]),
        ]

        # Mock the template service to raise an error for the second call
        mock_template_service = card_builder._template_service
        assert hasattr(mock_template_service.get_template, "side_effect")
        mock_template_service.get_template.side_effect = [
            CardTemplate("Test", "{{Noun}}", "{{English}}", ""),
            Exception("Template error"),
        ]

        # Add a record that will cause template error (use NounRecord)
        records.append(
            create_record(
                "noun",
                ["Hund", "der", "dog", "Hunde", "Der Hund bellt.", "Tier"],
            )
        )

        # Build cards - should handle error gracefully
        # Convert to BaseRecord list for type compatibility
        base_records: list[BaseRecord] = list(records)
        cards = card_builder.build_cards_from_records(base_records)

        # Should only return the successful card
        assert len(cards) == 1

    def test_anki_field_to_record_field_mapping(
        self, card_builder: CardBuilder
    ) -> None:
        """Test mapping between Anki field names and record field names."""
        # Test common mappings
        assert card_builder._map_anki_field_to_record_field("Image", "noun") == "image"
        assert (
            card_builder._map_anki_field_to_record_field("WordAudio", "noun")
            == "word_audio"
        )
        assert (
            card_builder._map_anki_field_to_record_field("English", "noun") == "english"
        )

        # Test noun-specific mappings
        assert card_builder._map_anki_field_to_record_field("Noun", "noun") == "noun"
        assert (
            card_builder._map_anki_field_to_record_field("Article", "noun") == "article"
        )

        # Test adjective-specific mappings
        assert (
            card_builder._map_anki_field_to_record_field("Word", "adjective") == "word"
        )
        assert (
            card_builder._map_anki_field_to_record_field("Comparative", "adjective")
            == "comparative"
        )

        # Test fallback to lowercase
        assert (
            card_builder._map_anki_field_to_record_field("UnknownField", "noun")
            == "unknownfield"
        )


class TestCardBuilderIntegration:
    """Test CardBuilder integration with real components."""

    @pytest.fixture
    def card_builder(self) -> CardBuilder:
        """Create CardBuilder with mock template service."""
        mock_service = Mock(spec=TemplateService)

        # Create mock templates for verb record types
        mock_templates = {
            "verb_conjugation": CardTemplate(
                name="German Verb Conjugation with Media",
                front_html="{{Infinitive}} - {{Tense}}",
                back_html="{{Ich}}, {{Du}}, {{Er}}",
                css=".card { color: purple; }",
            ),
            "verb_imperative": CardTemplate(
                name="German Verb Imperative with Media",
                front_html="{{Infinitive}} - Commands",
                back_html="{{DuForm}}, {{IhrForm}}, {{SieForm}}",
                css=".card { color: brown; }",
            ),
        }

        mock_service.get_template.side_effect = lambda card_type: mock_templates[
            card_type
        ]
        return CardBuilder(template_service=mock_service)

    def test_card_builder_with_real_template_service(self) -> None:
        """Test CardBuilder with real TemplateService."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            template_dir = temp_path / "templates"
            template_dir.mkdir()

            # Create template files (TemplateService expects specific naming convention)
            (template_dir / "noun_front.html").write_text("{{Noun}} ({{Article}})")
            (template_dir / "noun_back.html").write_text("{{English}}")
            (template_dir / "noun.css").write_text(".card { color: blue; }")

            # Create CardBuilder with real template service
            template_service = TemplateService(template_dir)
            card_builder = CardBuilder(template_service=template_service)

            # Create record and build card
            record = create_record(
                "noun", ["Katze", "die", "cat", "Katzen", "Example", "Tier"]
            )
            field_values, note_type = card_builder.build_card_from_record(record)

            # Verify results
            assert len(field_values) == 9
            assert field_values[0] == "Katze"
            assert note_type.name == "German Noun with Media"
            assert note_type.templates[0].front_html == "{{Noun}} ({{Article}})"

    def test_build_card_from_verb_conjugation_record(
        self, card_builder: CardBuilder
    ) -> None:
        """Test building card from verb conjugation record."""
        record = create_record(
            "verb_conjugation",
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "haben",
                "present",
                "arbeite",
                "arbeitest",
                "arbeitet",
                "arbeiten",
                "arbeitet",
                "arbeiten",
                "Ich arbeite jeden Tag.",
            ],
        )

        field_values, note_type = card_builder.build_card_from_record(record)

        # Verify field count and values
        assert len(field_values) == 16  # All verb conjugation fields
        assert field_values[0] == "arbeiten"  # Infinitive
        assert field_values[1] == "to work"  # English
        assert field_values[2] == "regelmäßig"  # Classification
        assert field_values[3] == ""  # Separable (False -> "")
        assert field_values[4] == "haben"  # Auxiliary
        assert field_values[5] == "present"  # Tense
        assert field_values[6] == "arbeite"  # Ich
        assert field_values[7] == "arbeitest"  # Du
        assert field_values[8] == "arbeitet"  # Er
        assert field_values[9] == "arbeiten"  # Wir
        assert field_values[10] == "arbeitet"  # Ihr
        assert field_values[11] == "arbeiten"  # Sie
        assert field_values[12] == "Ich arbeite jeden Tag."  # Example

        # Verify note type
        assert note_type.name == "German Verb Conjugation with Media"
        assert len(note_type.fields) == 16

    def test_build_card_from_verb_imperative_record(
        self, card_builder: CardBuilder
    ) -> None:
        """Test building card from verb imperative record."""
        record = create_record(
            "verb_imperative",
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "arbeite",
                "arbeitet",
                "arbeiten Sie",
                "Arbeite schneller!",
                "Arbeitet zusammen!",
                "Arbeiten Sie bitte hier!",
            ],
        )

        field_values, note_type = card_builder.build_card_from_record(record)

        # Verify field count and values (updated for new fields)
        assert len(field_values) == 18  # All verb imperative fields including new ones
        assert field_values[0] == "arbeiten"  # Infinitive
        assert field_values[1] == "to work"  # English
        assert field_values[2] == "to work"  # Meaning (same as English)
        assert field_values[3] == "regelmäßig"  # Classification
        assert field_values[4] == ""  # Separable (False -> "")
        assert field_values[5] == "arbeite"  # DuForm
        assert field_values[6] == "arbeitet"  # IhrForm
        assert field_values[7] == "arbeiten Sie"  # SieForm
        assert field_values[8] == ""  # WirForm (not provided)
        assert field_values[9] == "Arbeite schneller!"  # ExampleDu
        assert field_values[10] == "Arbeitet zusammen!"  # ExampleIhr
        assert field_values[11] == "Arbeiten Sie bitte hier!"  # ExampleSie

        # Verify note type
        assert note_type.name == "German Verb Imperative with Media"
        assert len(note_type.fields) == 18  # Updated for new fields

    def test_verb_record_separable_formatting(self, card_builder: CardBuilder) -> None:
        """Test that separable verb field is formatted correctly."""
        # Test separable=True
        separable_record = create_record(
            "verb_conjugation",
            [
                "aufstehen",
                "to get up",
                "unregelmäßig",
                "true",
                "sein",
                "present",
                "stehe auf",
                "stehst auf",
                "steht auf",
                "stehen auf",
                "steht auf",
                "stehen auf",
                "Ich stehe um 7 Uhr auf.",
            ],
        )

        field_values, _ = card_builder.build_card_from_record(separable_record)
        assert field_values[3] == "Yes"  # Separable=True -> "Yes"

        # Test separable=False
        non_separable_record = create_record(
            "verb_conjugation",
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "haben",
                "present",
                "arbeite",
                "arbeitest",
                "arbeitet",
                "arbeiten",
                "arbeitet",
                "arbeiten",
                "Ich arbeite.",
            ],
        )

        field_values, _ = card_builder.build_card_from_record(non_separable_record)
        assert field_values[3] == ""  # Separable=False -> ""

    def test_verb_audio_field_formatting(self, card_builder: CardBuilder) -> None:
        """Test that verb audio fields are formatted correctly."""
        record = create_record(
            "verb_imperative",
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "arbeite",
                "arbeitet",
                "arbeiten Sie",
                "Arbeite!",
                "Arbeitet!",
                "Arbeiten Sie!",
            ],
        )

        enriched_data = {
            "word_audio": "arbeiten.mp3",
            "du_audio": "arbeite.mp3",
            "ihr_audio": "arbeitet.mp3",
            "sie_audio": "arbeiten_sie.mp3",
        }

        field_values, _ = card_builder.build_card_from_record(record, enriched_data)

        # Check audio field formatting (updated indices for new field order)
        assert field_values[13] == "[sound:arbeiten.mp3]"  # WordAudio
        assert field_values[14] == "[sound:arbeite.mp3]"  # DuAudio
        assert field_values[15] == "[sound:arbeitet.mp3]"  # IhrAudio
        assert field_values[16] == "[sound:arbeiten_sie.mp3]"  # SieAudio

    def test_get_supported_record_types_includes_verbs(
        self, card_builder: CardBuilder
    ) -> None:
        """Test that supported record types includes verb types."""
        supported_types = card_builder.get_supported_record_types()

        assert "verb" in supported_types
        assert "verb_conjugation" in supported_types
        assert "verb_imperative" in supported_types
        assert (
            len(supported_types) == 9
        )  # noun, adjective, adverb, negation, verb, phrase, preposition,
        #    verb_conjugation, verb_imperative

    def test_validate_verb_conjugation_record_validation(
        self, card_builder: CardBuilder
    ) -> None:
        """Test validation of verb conjugation records."""
        # Valid record
        valid_record = create_record(
            "verb_conjugation",
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "haben",
                "present",
                "arbeite",
                "arbeitest",
                "arbeitet",
                "arbeiten",
                "arbeitet",
                "arbeiten",
                "Ich arbeite.",
            ],
        )

        assert card_builder.validate_record_for_card_building(valid_record) is True

        # Since Pydantic validation prevents creating invalid records,
        # we test CardBuilder validation by using a different record type
        # that CardBuilder doesn't support

        noun_record = create_record(
            "noun", ["Katze", "die", "cat", "Katzen", "Example", "Tier"]
        )

        # Temporarily change the record type to simulate unsupported type
        original_class_name = noun_record.__class__.__name__
        noun_record.__class__.__name__ = "UnsupportedRecord"

        assert card_builder.validate_record_for_card_building(noun_record) is False

        # Restore original class name
        noun_record.__class__.__name__ = original_class_name

    def test_validate_verb_imperative_record_validation(
        self, card_builder: CardBuilder
    ) -> None:
        """Test validation of verb imperative records."""
        # Valid record
        valid_record = create_record(
            "verb_imperative",
            [
                "arbeiten",
                "to work",
                "regelmäßig",
                "false",
                "arbeite",
                "arbeitet",
                "arbeiten Sie",
                "Arbeite!",
                "Arbeitet!",
                "Arbeiten Sie!",
            ],
        )

        assert card_builder.validate_record_for_card_building(valid_record) is True
