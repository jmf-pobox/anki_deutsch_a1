"""Template management service for Anki card templates."""

import logging
from pathlib import Path
from typing import NamedTuple

from langlearn.core.backends.base import CardTemplate, NoteType
from langlearn.exceptions import TemplateError

logger = logging.getLogger(__name__)


class TemplateFiles(NamedTuple):
    """Template files for a card type."""

    front_html: str
    back_html: str
    css: str


class TemplateService:
    """Manages Anki card templates with external file loading and caching.

    This service loads card templates from external HTML/CSS files,
    providing a clean interface for template management with caching
    for performance.
    """

    def __init__(self, template_dir: Path) -> None:
        """Initialize TemplateService.

        Args:
            template_dir: Directory containing template files
        """
        self._template_dir = template_dir
        self._cache: dict[str, CardTemplate] = {}

        if not self._template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")

    def get_template(self, card_type: str) -> CardTemplate:
        """Get template for a card type with caching.

        Args:
            card_type: Type of card (adjective, noun, verb, etc.)

        Returns:
            CardTemplate with loaded HTML and CSS

        Raises:
            FileNotFoundError: If template files are missing
        """
        if card_type not in self._cache:
            self._cache[card_type] = self._load_template(card_type)
        return self._cache[card_type]

    def _load_template(self, card_type: str) -> CardTemplate:
        """Load template from external files.

        Args:
            card_type: Type of card template to load

        Returns:
            CardTemplate with loaded content
        """
        try:
            template_files = self._get_template_files(card_type)

            # Handle special naming for article templates
            if card_type == "artikel_gender":
                template_name = "German Artikel Gender with Media"
            elif card_type == "artikel_context":
                template_name = "German Artikel Context with Media"
            elif card_type == "artikel_gender_cloze":
                template_name = "German Artikel Gender Cloze"
            elif card_type == "artikel_context_cloze":
                template_name = "German Artikel Context Cloze"
            else:
                template_name = f"German {card_type.title()} with Media"

            return CardTemplate(
                name=template_name,
                front_html=template_files.front_html,
                back_html=template_files.back_html,
                css=template_files.css,
            )
        except Exception as e:
            logger.error(f"Error loading template for {card_type}: {e}")
            raise

    def _get_template_files(self, card_type: str) -> TemplateFiles:
        """Load template files for a card type.

        Args:
            card_type: Type of card template

        Returns:
            TemplateFiles with loaded content
        """
        # Try actual template naming convention with DE_de suffix
        front_file = self._template_dir / f"{card_type}_DE_de_front.html"
        back_file = self._template_dir / f"{card_type}_DE_de_back.html"
        css_file = self._template_dir / f"{card_type}_DE_de.css"

        # Validate that all required template files exist
        if not front_file.exists():
            raise TemplateError(f"Front template not found: {front_file}")
        if not back_file.exists():
            raise TemplateError(f"Back template not found: {back_file}")
        if not css_file.exists():
            raise TemplateError(f"CSS template not found: {css_file}")

        # Load files
        front_html = self._read_template_file(front_file)
        back_html = self._read_template_file(back_file)
        css = self._read_template_file(css_file)

        return TemplateFiles(front_html=front_html, back_html=back_html, css=css)

    def _read_template_file(self, file_path: Path) -> str:
        """Read a template file and return its contents.

        Args:
            file_path: Path to the template file

        Returns:
            Contents of the template file

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"Loaded template file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Error reading template file {file_path}: {e}")
            raise

    def create_modern_templates(self) -> None:
        """Create modern template files with enhanced styling.

        This method creates template files with the modern responsive
        styling from legacy templates, preserving all the improvements
        made to the templates.
        """
        # Create modern templates for each card type
        card_types = ["adjective", "adverb", "noun", "negation"]

        for card_type in card_types:
            self._create_card_type_templates(card_type)

    def _create_card_type_templates(self, card_type: str) -> None:
        """Create modern template files for a specific card type.

        Args:
            card_type: Type of card to create templates for
        """
        # This would contain the modern templates
        # For now, we'll use the templates that are already embedded
        # in template files as the source of truth
        pass

    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._cache.clear()
        logger.debug("Template cache cleared")

    def get_available_card_types(self) -> list[str]:
        """Get list of available card types based on template files.

        Returns:
            List of card types that have template files
        """
        card_types: set[str] = set()

        for file_path in self._template_dir.glob("*front.html"):
            # Extract card type from filename
            name = file_path.stem
            if name.endswith("_DE_de_front"):
                card_type = name[:-12]  # Remove "_DE_de_front"
                card_types.add(card_type)
            elif name.endswith("_front"):
                card_type = name[:-6]  # Remove "_front"
                card_types.add(card_type)

        return sorted(card_types)

    def get_noun_note_type(self) -> NoteType:
        """Get complete NoteType for German nouns.

        Returns:
            NoteType configured for German noun cards
        """
        template = self.get_template("noun")

        return NoteType(
            name="German Noun with Media",
            fields=[
                "Noun",
                "Article",
                "English",
                "Plural",
                "Example",
                "Related",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            templates=[template],
        )

    def get_adjective_note_type(self) -> NoteType:
        """Get complete NoteType for German adjectives.

        Returns:
            NoteType configured for German adjective cards
        """
        template = self.get_template("adjective")

        return NoteType(
            name="German Adjective with Media",
            fields=[
                "Word",
                "English",
                "Example",
                "Comparative",
                "Superlative",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            templates=[template],
        )

    def get_adverb_note_type(self) -> NoteType:
        """Get complete NoteType for German adverbs.

        Returns:
            NoteType configured for German adverb cards
        """
        template = self.get_template("adverb")

        return NoteType(
            name="German Adverb with Media",
            fields=[
                "Word",
                "English",
                "Type",
                "Example",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            templates=[template],
        )

    def get_negation_note_type(self) -> NoteType:
        """Get complete NoteType for German negations.

        Returns:
            NoteType configured for German negation cards
        """
        template = self.get_template("negation")

        return NoteType(
            name="German Negation with Media",
            fields=[
                "Word",
                "English",
                "Type",
                "Example",
                "Image",
                "WordAudio",
                "ExampleAudio",
            ],
            templates=[template],
        )
