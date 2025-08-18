"""Tests for card generators."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from langlearn.backends import AnkiBackend, CardTemplate, NoteType
from langlearn.cards import AdjectiveCardGenerator, BaseCardGenerator, NounCardGenerator
from langlearn.models.adjective import Adjective
from langlearn.models.noun import Noun
from langlearn.services.template_service import TemplateService


class TestBaseCardGenerator:
    """Test the BaseCardGenerator abstract class."""

    def test_base_card_generator_is_abstract(self) -> None:
        """Test that BaseCardGenerator cannot be instantiated directly."""
        backend = Mock()
        template_service = Mock()

        with pytest.raises(TypeError):
            BaseCardGenerator(backend, template_service, "test")  # type: ignore

    def test_base_card_generator_generic_typing(self) -> None:
        """Test that BaseCardGenerator supports generic typing."""
        # This test verifies that the generic typing works correctly
        # by checking that we can create concrete subclasses with specific types

        class TestCardGenerator(BaseCardGenerator[str]):
            def _get_field_names(self) -> list[str]:
                return ["Field1", "Field2"]

            def _extract_fields(self, data: str) -> list[str]:
                return [data, "test"]

        backend = Mock()
        template_service = Mock()
        generator = TestCardGenerator(backend, template_service, "test")

        assert generator._card_type == "test"
        assert generator._backend is backend
        assert generator._template_service is template_service


class TestNounCardGenerator:
    """Test the NounCardGenerator class."""

    @pytest.fixture
    def backend(self) -> Mock:
        """Create a mock backend for testing."""
        backend = Mock(spec=AnkiBackend)
        backend.create_note_type.return_value = "note_type_123"
        backend.add_note.return_value = None
        return backend

    @pytest.fixture
    def template_service(self) -> Mock:
        """Create a mock template service for testing."""
        template_service = Mock(spec=TemplateService)
        template_service.get_template.return_value = CardTemplate(
            name="German Noun with Media",
            front_html="{{Noun}} {{Article}}",
            back_html="{{FrontSide}}<hr>{{English}}",
            css=".card { font-family: Arial; }",
        )
        return template_service

    @pytest.fixture
    def noun_data(self) -> Noun:
        """Create sample noun data for testing."""
        return Noun(
            noun="Katze",
            article="die",
            english="cat",
            plural="die Katzen",
            example="Die Katze schläft.",
            related="Tier",
            word_audio="",
            example_audio="",
            image_path="",
        )

    def test_noun_card_generator_initialization(
        self, backend: Mock, template_service: Mock
    ) -> None:
        """Test noun card generator initialization."""
        generator = NounCardGenerator(backend, template_service)

        assert generator._card_type == "noun"
        assert generator._backend is backend
        assert generator._template_service is template_service

    def test_get_field_names(self, backend: Mock, template_service: Mock) -> None:
        """Test that field names are returned correctly."""
        generator = NounCardGenerator(backend, template_service)

        expected_fields = [
            "Noun",
            "Article",
            "English",
            "Plural",
            "Example",
            "Related",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

        assert generator._get_field_names() == expected_fields

    def test_extract_fields(
        self, backend: Mock, template_service: Mock, noun_data: Noun
    ) -> None:
        """Test field extraction from noun data."""
        generator = NounCardGenerator(backend, template_service)

        fields = generator._extract_fields(noun_data)

        expected_fields = [
            "Katze",
            "die",
            "cat",
            "die Katzen",
            "Die Katze schläft.",
            "Tier",
            "",  # Image (filled by backend)
            "",  # WordAudio (filled by backend)
            "",  # ExampleAudio (filled by backend)
        ]

        assert fields == expected_fields

    def test_note_type_creation_and_caching(
        self, backend: Mock, template_service: Mock
    ) -> None:
        """Test that note type is created and cached properly."""
        generator = NounCardGenerator(backend, template_service)

        # First access should create the note type
        note_type_id = generator.note_type_id
        assert note_type_id == "note_type_123"

        # Verify template service was called
        template_service.get_template.assert_called_once_with("noun")

        # Verify backend was called with correct note type
        backend.create_note_type.assert_called_once()
        created_note_type = backend.create_note_type.call_args[0][0]
        assert isinstance(created_note_type, NoteType)
        assert created_note_type.name == "German Noun with Media"

        # Second access should return cached value
        note_type_id_2 = generator.note_type_id
        assert note_type_id_2 == "note_type_123"

        # Backend should not be called again
        assert backend.create_note_type.call_count == 1

    def test_add_card(
        self, backend: Mock, template_service: Mock, noun_data: Noun
    ) -> None:
        """Test adding a card through the generator."""
        generator = NounCardGenerator(backend, template_service)

        generator.add_card(noun_data)

        # Verify backend was called with correct parameters
        backend.add_note.assert_called_once_with(
            "note_type_123",
            [
                "Katze",
                "die",
                "cat",
                "die Katzen",
                "Die Katze schläft.",
                "Tier",
                "",  # Image
                "",  # WordAudio
                "",  # ExampleAudio
            ],
        )

    def test_note_type_creation_failure(
        self, backend: Mock, template_service: Mock
    ) -> None:
        """Test handling of note type creation failure."""
        backend.create_note_type.return_value = None
        generator = NounCardGenerator(backend, template_service)

        with pytest.raises(RuntimeError, match="Failed to create note type for noun"):
            _ = generator.note_type_id


class TestAdjectiveCardGenerator:
    """Test the AdjectiveCardGenerator class."""

    @pytest.fixture
    def backend(self) -> Mock:
        """Create a mock backend for testing."""
        backend = Mock(spec=AnkiBackend)
        backend.create_note_type.return_value = "note_type_789"
        backend.add_note.return_value = None
        return backend

    @pytest.fixture
    def template_service(self) -> Mock:
        """Create a mock template service for testing."""
        template_service = Mock(spec=TemplateService)
        template_service.get_template.return_value = CardTemplate(
            name="German Adjective with Media",
            front_html="{{Word}}",
            back_html="{{FrontSide}}<hr>{{English}}",
            css=".card { font-family: Arial; }",
        )
        return template_service

    @pytest.fixture
    def adjective_data(self) -> Adjective:
        """Create sample adjective data for testing."""
        return Adjective(
            word="schön",
            english="beautiful",
            example="Das Haus ist schön.",
            comparative="schöner",
            superlative="am schönsten",
            word_audio="",
            example_audio="",
            image_path="",
        )

    def test_adjective_card_generator_initialization(
        self, backend: Mock, template_service: Mock
    ) -> None:
        """Test adjective card generator initialization."""
        generator = AdjectiveCardGenerator(backend, template_service)

        assert generator._card_type == "adjective"
        assert generator._backend is backend
        assert generator._template_service is template_service

    def test_get_field_names(self, backend: Mock, template_service: Mock) -> None:
        """Test that field names are returned correctly."""
        generator = AdjectiveCardGenerator(backend, template_service)

        expected_fields = [
            "Word",
            "English",
            "Example",
            "Comparative",
            "Superlative",
            "Image",
            "WordAudio",
            "ExampleAudio",
        ]

        assert generator._get_field_names() == expected_fields

    def test_extract_fields(
        self, backend: Mock, template_service: Mock, adjective_data: Adjective
    ) -> None:
        """Test field extraction from adjective data."""
        generator = AdjectiveCardGenerator(backend, template_service)

        fields = generator._extract_fields(adjective_data)

        expected_fields = [
            "schön",
            "beautiful",
            "Das Haus ist schön.",
            "schöner",
            "am schönsten",
            "",  # Image (filled by backend)
            "",  # WordAudio (filled by backend)
            "",  # ExampleAudio (filled by backend)
        ]

        assert fields == expected_fields

    def test_add_card(
        self, backend: Mock, template_service: Mock, adjective_data: Adjective
    ) -> None:
        """Test adding an adjective card through the generator."""
        generator = AdjectiveCardGenerator(backend, template_service)

        generator.add_card(adjective_data)

        # Verify backend was called with correct parameters
        backend.add_note.assert_called_once_with(
            "note_type_789",
            [
                "schön",
                "beautiful",
                "Das Haus ist schön.",
                "schöner",
                "am schönsten",
                "",  # Image
                "",  # WordAudio
                "",  # ExampleAudio
            ],
        )


class TestCardGeneratorIntegration:
    """Integration tests for card generators with real backend."""

    def test_card_generator_with_real_template_service(self, tmp_path: Path) -> None:
        """Test card generator with a real template service."""
        # Create a temporary template directory with test files
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        # Create test template files
        (template_dir / "noun_front.html").write_text("{{Noun}} {{Article}}")
        (template_dir / "noun_back.html").write_text("{{FrontSide}}<hr>{{English}}")
        (template_dir / "noun.css").write_text(".card { font-family: Arial; }")

        # Create real services
        template_service = TemplateService(template_dir)
        backend = Mock()
        backend.create_note_type.return_value = "note_type_real"
        backend.add_note.return_value = None

        # Test the generator
        generator = NounCardGenerator(backend, template_service)
        noun_data = Noun(
            noun="Test",
            article="das",
            english="test",
            plural="Tests",
            example="Das ist ein Test.",
            related="Prüfung",
            word_audio="",
            example_audio="",
            image_path="",
        )

        generator.add_card(noun_data)

        # Verify template was loaded correctly
        backend.create_note_type.assert_called_once()
        created_note_type = backend.create_note_type.call_args[0][0]
        assert created_note_type.name == "German Noun with Media"
        assert "{{Noun}} {{Article}}" in created_note_type.templates[0].front_html
        assert (
            "{{FrontSide}}<hr>{{English}}" in created_note_type.templates[0].back_html
        )
        assert ".card { font-family: Arial; }" in created_note_type.templates[0].css
