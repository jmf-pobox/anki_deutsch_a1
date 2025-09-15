"""Unit tests for TemplateService."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from langlearn.core.backends.base import CardTemplate
from langlearn.core.services.template_service import TemplateFiles, TemplateService


class TestTemplateService:
    """Test TemplateService functionality."""

    @pytest.fixture
    def temp_template_dir(self) -> Generator[Path]:
        """Create temporary template directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)

            # Create test template files with DE_de naming
            (template_dir / "adjective_DE_de_front.html").write_text(
                "<div>{{Word}} front</div>"
            )
            (template_dir / "adjective_DE_de_back.html").write_text(
                "<div>{{Word}} back</div>"
            )
            (template_dir / "adjective_DE_de.css").write_text(
                ".card { background: white; }"
            )

            # Create legacy naming convention files
            (template_dir / "noun_DE_de_front.html").write_text(
                "<div>{{Noun}} front legacy</div>"
            )
            (template_dir / "noun_DE_de_back.html").write_text(
                "<div>{{Noun}} back legacy</div>"
            )
            (template_dir / "noun_DE_de.css").write_text(".card { background: blue; }")

            yield template_dir

    @pytest.fixture
    def template_service(self, temp_template_dir: Path) -> TemplateService:
        """TemplateService instance for testing."""
        return TemplateService(temp_template_dir)

    def test_init_valid_directory(self, temp_template_dir: Path) -> None:
        """Test TemplateService initialization with valid directory."""
        service = TemplateService(temp_template_dir)
        assert service._template_dir == temp_template_dir
        assert service._cache == {}

    def test_init_invalid_directory(self) -> None:
        """Test TemplateService initialization with invalid directory."""
        with pytest.raises(FileNotFoundError, match="Template directory not found"):
            TemplateService(Path("/nonexistent/directory"))

    def test_get_template_modern_naming(
        self, template_service: TemplateService
    ) -> None:
        """Test loading template with modern naming convention."""
        template = template_service.get_template("adjective")

        assert isinstance(template, CardTemplate)
        assert template.name == "German Adjective with Media"
        assert template.front_html == "<div>{{Word}} front</div>"
        assert template.back_html == "<div>{{Word}} back</div>"
        assert template.css == ".card { background: white; }"

    def test_get_template_missing_template(
        self, template_service: TemplateService
    ) -> None:
        """Test error handling when template files don't exist."""
        from langlearn.exceptions import TemplateError

        with pytest.raises(TemplateError, match="Front template not found"):
            template_service.get_template("nonexistent_card_type")

    def test_template_caching(self, template_service: TemplateService) -> None:
        """Test that templates are cached after first load."""
        # First load
        template1 = template_service.get_template("adjective")

        # Second load should return cached version
        template2 = template_service.get_template("adjective")

        # Should be the same object (cached)
        assert template1 is template2
        assert len(template_service._cache) == 1

    def test_get_template_files_modern(self, template_service: TemplateService) -> None:
        """Test _get_template_files with modern naming."""
        template_files = template_service._get_template_files("adjective")

        assert isinstance(template_files, TemplateFiles)
        assert template_files.front_html == "<div>{{Word}} front</div>"
        assert template_files.back_html == "<div>{{Word}} back</div>"
        assert template_files.css == ".card { background: white; }"

    def test_get_template_files_legacy(self, template_service: TemplateService) -> None:
        """Test that _get_template_files works with DE_de naming convention."""
        # Should work since we have noun_DE_de files in the fixture
        template_files = template_service._get_template_files("noun")

        assert isinstance(template_files, TemplateFiles)
        assert template_files.front_html == "<div>{{Noun}} front legacy</div>"
        assert template_files.back_html == "<div>{{Noun}} back legacy</div>"
        assert template_files.css == ".card { background: blue; }"

    def test_missing_template_files(self, template_service: TemplateService) -> None:
        """Test handling of missing template files."""
        from langlearn.exceptions import TemplateError

        with pytest.raises(TemplateError, match="Front template not found"):
            template_service.get_template("nonexistent")

    def test_read_template_file_success(
        self, temp_template_dir: Path, template_service: TemplateService
    ) -> None:
        """Test successful template file reading."""
        test_file = temp_template_dir / "test.html"
        test_file.write_text("<div>Test content</div>")

        content = template_service._read_template_file(test_file)
        assert content == "<div>Test content</div>"

    def test_read_template_file_missing(
        self, template_service: TemplateService
    ) -> None:
        """Test reading missing template file."""
        missing_file = Path("/nonexistent/file.html")

        with pytest.raises(FileNotFoundError, match="Template file not found"):
            template_service._read_template_file(missing_file)

    def test_clear_cache(self, template_service: TemplateService) -> None:
        """Test cache clearing functionality."""
        # Load a template to populate cache
        template_service.get_template("adjective")
        assert len(template_service._cache) == 1

        # Clear cache
        template_service.clear_cache()
        assert len(template_service._cache) == 0

    def test_get_available_card_types(self, template_service: TemplateService) -> None:
        """Test getting available card types."""
        card_types = template_service.get_available_card_types()

        # Should find both templates with card type names extracted correctly
        assert "adjective" in card_types
        assert "noun" in card_types  # DE_de suffix removed to get card type
        assert len(card_types) == 2

        # Should be sorted
        assert card_types == sorted(card_types)

    def test_get_template_files_encoding(self, temp_template_dir: Path) -> None:
        """Test template file reading with UTF-8 encoding."""
        # Create file with German umlauts using DE_de naming
        german_content = "<div>Schön {{Word}}</div>"
        (temp_template_dir / "german_DE_de_front.html").write_text(
            german_content, encoding="utf-8"
        )
        (temp_template_dir / "german_DE_de_back.html").write_text("<div>Back</div>")
        (temp_template_dir / "german_DE_de.css").write_text(".card {}")

        service = TemplateService(temp_template_dir)
        template_files = service._get_template_files("german")

        assert template_files.front_html == german_content
