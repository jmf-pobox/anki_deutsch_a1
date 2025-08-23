"""Card Specification Generator for comprehensive card type documentation.

This service introspects the entire card generation system to produce accurate
documentation of all card types, their Anki note types, front/back content,
and field data origins (CSV, Pexels, AWS Polly).
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from langlearn.backends.base import CardTemplate
from langlearn.services.card_builder import CardBuilder
from langlearn.services.template_service import TemplateService
from langlearn.testing.anki_simulator import AnkiRenderSimulator

logger = logging.getLogger(__name__)


@dataclass
class FieldSpecification:
    """Specification for a single card field."""

    name: str
    data_source: str  # "CSV", "Pexels", "AWS_Polly", "Generated", "Computed"
    description: str
    example_value: str
    required: bool = False


@dataclass
class CardTypeSpecification:
    """Complete specification for a card type."""

    card_type: str
    anki_note_type_name: str
    description: str
    front_content_description: str
    back_content_description: str
    fields: list[FieldSpecification]
    template_files: list[str]
    cloze_deletion: bool = False
    learning_objective: str = ""


class CardSpecificationGenerator:
    """Generates comprehensive documentation of all card types in the system.

    This service introspects CardBuilder, TemplateService, and existing templates
    to automatically generate accurate documentation of all card specifications.
    """

    def __init__(
        self,
        card_builder: CardBuilder | None = None,
        template_service: TemplateService | None = None,
        project_root: Path | None = None,
    ) -> None:
        """Initialize CardSpecificationGenerator.

        Args:
            card_builder: CardBuilder service (created if None)
            template_service: TemplateService (created if None)
            project_root: Project root for finding templates
        """
        self._project_root = project_root or Path.cwd()

        if template_service is None:
            template_dir = self._project_root / "src" / "langlearn" / "templates"
            template_service = TemplateService(template_dir)

        if card_builder is None:
            card_builder = CardBuilder(template_service, project_root)

        self._card_builder = card_builder
        self._template_service = template_service
        self._template_dir = self._project_root / "src" / "langlearn" / "templates"

        logger.debug("CardSpecificationGenerator initialized")

    def generate_all_specifications(self) -> list[CardTypeSpecification]:
        """Generate specifications for all card types in the system.

        Returns:
            List of complete card type specifications
        """
        logger.info("Generating specifications for all card types")

        specifications = []

        # Get all supported record types from CardBuilder
        supported_types = self._card_builder.get_supported_record_types()

        # Add specialized card types that aren't in record types
        specialized_types = [
            "artikel_gender",
            "artikel_context",
            "artikel_gender_cloze",
            "artikel_context_cloze",
            "noun_article_recognition",
            "noun_case_context",
        ]

        all_card_types = supported_types + specialized_types

        for card_type in all_card_types:
            try:
                spec = self._generate_card_specification(card_type)
                specifications.append(spec)
                logger.debug("Generated specification for %s", card_type)
            except Exception as e:
                logger.warning(
                    "Failed to generate specification for %s: %s", card_type, e
                )
                continue

        logger.info("Generated %d card type specifications", len(specifications))
        return specifications

    def _generate_card_specification(self, card_type: str) -> CardTypeSpecification:
        """Generate specification for a single card type.

        Args:
            card_type: Type of card to generate specification for

        Returns:
            Complete card type specification
        """
        # Load template to get Anki note type name and structure
        template = self._template_service.get_template(card_type)

        # Get field names from CardBuilder
        field_names = self._card_builder._get_field_names_for_record_type(card_type)

        # Create field specifications
        fields = []
        for field_name in field_names:
            field_spec = self._generate_field_specification(field_name, card_type)
            fields.append(field_spec)

        # Determine template files
        template_files = self._get_template_files_for_card_type(card_type)

        # Analyze content for descriptions
        front_description, back_description = self._analyze_template_content(template)

        # Determine if this is a cloze deletion card
        is_cloze = self._is_cloze_deletion_card(template)

        # Generate learning objective
        learning_objective = self._generate_learning_objective(card_type)

        return CardTypeSpecification(
            card_type=card_type,
            anki_note_type_name=template.name,
            description=self._generate_card_description(card_type),
            front_content_description=front_description,
            back_content_description=back_description,
            fields=fields,
            template_files=template_files,
            cloze_deletion=is_cloze,
            learning_objective=learning_objective,
        )

    def _generate_field_specification(
        self, field_name: str, card_type: str
    ) -> FieldSpecification:
        """Generate specification for a single field.

        Args:
            field_name: Name of the field
            card_type: Card type this field belongs to

        Returns:
            Field specification with data source and description
        """
        # Determine data source based on field characteristics
        data_source = self._determine_field_data_source(field_name, card_type)

        # Generate description
        description = self._generate_field_description(field_name, card_type)

        # Generate example value
        example_value = self._generate_example_value(field_name, card_type)

        # Determine if field is required
        required_fields = self._card_builder._get_required_fields_for_record_type(
            card_type
        )
        record_field = self._card_builder._map_anki_field_to_record_field(
            field_name, card_type
        )
        is_required = record_field in required_fields

        return FieldSpecification(
            name=field_name,
            data_source=data_source,
            description=description,
            example_value=example_value,
            required=is_required,
        )

    def _determine_field_data_source(self, field_name: str, card_type: str) -> str:
        """Determine the data source for a field.

        Args:
            field_name: Name of the field
            card_type: Card type this field belongs to

        Returns:
            Data source identifier
        """
        # Audio fields are generated by AWS Polly
        if "Audio" in field_name:
            return "AWS_Polly"

        # Image fields are from Pexels API
        if field_name == "Image":
            return "Pexels"

        # Generated/computed fields
        computed_fields = {
            "FrontText",
            "BackText",
            "Text",
            "CaseRule",
            "CaseUsage",
            "ArtikelTypBestimmt",
            "ArtikelTypUnbestimmt",
            "ArtikelTypVerneinend",
            "CaseNominative",
            "CaseAccusative",
            "CaseDative",
            "CaseGenitive",
            "CaseNominativ",
            "CaseAkkusativ",
            "CaseDativ",
            "CaseGenitiv",
            "NounOnly",
            "NounEnglish",
            "NounEnglishWithArticle",
        }

        if field_name in computed_fields:
            return "Generated"

        # Explanation fields are generated by German explanation factory
        if field_name == "Explanation":
            return "Generated"

        # All other fields come from CSV data - specify the actual CSV file
        return self._get_csv_file_for_card_type(card_type)

    def _get_csv_file_for_card_type(self, card_type: str) -> str:
        """Get the specific CSV file used for a card type.

        Args:
            card_type: Type of card

        Returns:
            Specific CSV filename
        """
        # Map card types to their CSV files
        csv_mappings = {
            "noun": "nouns.csv",
            "adjective": "adjectives.csv",
            "adverb": "adverbs.csv",
            "negation": "negations.csv",
            "verb": "verbs_unified.csv",
            "phrase": "phrases.csv",
            "preposition": "prepositions.csv",
            "verb_conjugation": "verbs_unified.csv",
            "verb_imperative": "verbs_unified.csv",
            # Article-based cards use the unified articles file
            "artikel_gender": "articles_unified.csv",
            "artikel_context": "articles_unified.csv",
            "artikel_gender_cloze": "articles_unified.csv",
            "artikel_context_cloze": "articles_unified.csv",
            # Noun-article practice cards combine both sources
            "noun_article_recognition": "nouns.csv + articles_unified.csv",
            "noun_case_context": "nouns.csv + articles_unified.csv",
        }

        return csv_mappings.get(card_type, "CSV")

    def _generate_field_description(self, field_name: str, card_type: str) -> str:
        """Generate human-readable description for a field.

        Args:
            field_name: Name of the field
            card_type: Card type this field belongs to

        Returns:
            Human-readable field description
        """
        # Standard field descriptions
        descriptions = {
            # Content fields
            "Word": "The main German word being learned",
            "Noun": "German noun with proper capitalization",
            "Verb": "German verb in infinitive form",
            "Infinitive": "German verb in infinitive form",
            "Phrase": "German phrase or expression",
            "Preposition": "German preposition",
            "Article": "German article (der, die, das)",
            # Translation fields
            "English": "English translation or meaning",
            "Meaning": "English meaning of the word",
            # Grammar fields
            "Case": "German grammatical case (Nominativ, Akkusativ, Dativ, Genitiv)",
            "Gender": "German grammatical gender (masculine, feminine, neuter)",
            "Plural": "Plural form of the noun",
            "Type": "Classification or type of word",
            "Classification": "Verb classification (regular, irregular, modal, etc.)",
            "Separable": "Whether the verb is separable (Yes/No)",
            "Auxiliary": "Auxiliary verb used (haben/sein)",
            "Tense": "Verb tense (present, preterite, perfect, etc.)",
            # Conjugation fields
            "Ich": "First person singular conjugation (ich)",
            "Du": "Second person singular conjugation (du)",
            "Er": "Third person singular conjugation (er/sie/es)",
            "Wir": "First person plural conjugation (wir)",
            "Ihr": "Second person plural conjugation (ihr)",
            "Sie": "Third person plural/formal conjugation (Sie/sie)",
            # Present tense shortcuts
            "PresentIch": "Present tense first person (ich)",
            "PresentDu": "Present tense second person (du)",
            "PresentEr": "Present tense third person (er/sie/es)",
            "Perfect": "Perfect tense form (haben/sein + past participle)",
            # Imperative forms
            "DuForm": "Imperative form for 'du'",
            "IhrForm": "Imperative form for 'ihr'",
            "SieForm": "Imperative form for 'Sie'",
            "WirForm": "Imperative form for 'wir'",
            # Adjective forms
            "Comparative": "Comparative form of adjective",
            "Superlative": "Superlative form of adjective",
            # Example fields
            "Example": "Example sentence using the word",
            "Example1": "First example sentence",
            "Example2": "Second example sentence",
            "ExampleDu": "Example sentence with du imperative",
            "ExampleIhr": "Example sentence with ihr imperative",
            "ExampleSie": "Example sentence with Sie imperative",
            "ExampleNom": "Example sentence in nominative case",
            "Context": "Context or situation where phrase is used",
            "Related": "Related words or expressions",
            # Generated content fields
            "FrontText": "Generated text for card front",
            "BackText": "Generated text for card back",
            "Text": "Generated cloze deletion text",
            "Explanation": "Generated German grammar explanation",
            "CaseRule": "Generated case rule explanation",
            "CaseUsage": "Generated case usage explanation",
            # Media fields
            "Image": "Generated image from Pexels API",
            "WordAudio": "Generated pronunciation audio from AWS Polly",
            "ExampleAudio": "Generated example sentence audio from AWS Polly",
            "PhraseAudio": "Generated phrase audio from AWS Polly",
            "DuAudio": "Generated audio for du imperative",
            "IhrAudio": "Generated audio for ihr imperative",
            "SieAudio": "Generated audio for Sie imperative",
            "WirAudio": "Generated audio for wir imperative",
            "ArticleAudio": "Generated audio for article pronunciation",
            "Example1Audio": "Generated audio for first example",
            "Example2Audio": "Generated audio for second example",
            # Article declension fields
            "Nominative": "Nominative case article form",
            "Accusative": "Accusative case article form",
            "Dative": "Dative case article form",
            "Genitive": "Genitive case article form",
            # Conditional visibility fields
            "ArtikelTypBestimmt": "Conditional field for definite articles",
            "ArtikelTypUnbestimmt": "Conditional field for indefinite articles",
            "ArtikelTypVerneinend": "Conditional field for negative articles",
            "CaseNominative": "Conditional highlighting for nominative case",
            "CaseAccusative": "Conditional highlighting for accusative case",
            "CaseDative": "Conditional highlighting for dative case",
            "CaseGenitive": "Conditional highlighting for genitive case",
            "CaseNominativ": "Conditional highlighting for Nominativ",
            "CaseAkkusativ": "Conditional highlighting for Akkusativ",
            "CaseDativ": "Conditional highlighting for Dativ",
            "CaseGenitiv": "Conditional highlighting for Genitiv",
            # Extracted/computed fields
            "NounOnly": "Extracted noun without article",
            "NounEnglish": "English translation of extracted noun",
            "NounEnglishWithArticle": "English translation including article",
            "ArticleForm": "Specific article form for this case",
        }

        return descriptions.get(field_name, f"Field for {field_name.lower()}")

    def _generate_example_value(self, field_name: str, card_type: str) -> str:
        """Generate example value for a field.

        Args:
            field_name: Name of the field
            card_type: Card type this field belongs to

        Returns:
            Example value for the field
        """
        # Example values by field name
        examples = {
            # Content fields
            "Word": "schön",
            "Noun": "Haus",
            "Verb": "arbeiten",
            "Infinitive": "sprechen",
            "Phrase": "Guten Tag",
            "Preposition": "mit",
            "Article": "das",
            # Translation fields
            "English": "beautiful",
            "Meaning": "to work",
            # Grammar fields
            "Case": "Akkusativ",
            "Gender": "neutrum",
            "Plural": "Häuser",
            "Type": "modal",
            "Classification": "regular",
            "Separable": "Yes",
            "Auxiliary": "haben",
            "Tense": "present",
            # Conjugation fields
            "Ich": "ich spreche",
            "Du": "du sprichst",
            "Er": "er spricht",
            "Wir": "wir sprechen",
            "Ihr": "ihr sprecht",
            "Sie": "sie sprechen",
            # Present tense
            "PresentIch": "ich arbeite",
            "PresentDu": "du arbeitest",
            "PresentEr": "er arbeitet",
            "Perfect": "ich habe gearbeitet",
            # Imperative forms
            "DuForm": "sprich!",
            "IhrForm": "sprecht!",
            "SieForm": "sprechen Sie!",
            "WirForm": "sprechen wir!",
            # Adjective forms
            "Comparative": "schöner",
            "Superlative": "am schönsten",
            # Example fields
            "Example": "Das Haus ist schön.",
            "Example1": "Ich gehe mit dem Auto.",
            "Example2": "Mit dir ist alles besser.",
            "ExampleDu": "Sprich lauter!",
            "ExampleIhr": "Sprecht deutlicher!",
            "ExampleSie": "Sprechen Sie bitte langsamer!",
            "ExampleNom": "Der Mann arbeitet hier.",
            "Context": "greeting someone",
            "Related": "Hallo, Auf Wiedersehen",
            # Generated content fields
            "FrontText": "What is the German word for 'beautiful'?",
            "BackText": "schön",
            "Text": "Das {{c1::Haus}} ist groß.",
            "Explanation": "Neutrum - Geschlecht erkennen",
            "CaseRule": "Maskulin Akkusativ = den",
            "CaseUsage": "the direct object",
            # Media fields
            "Image": '<img src="house_001.jpg" />',
            "WordAudio": "[sound:haus_pronunciation.mp3]",
            "ExampleAudio": "[sound:example_sentence.mp3]",
            "PhraseAudio": "[sound:guten_tag.mp3]",
            "DuAudio": "[sound:sprich_imperative.mp3]",
            "IhrAudio": "[sound:sprecht_imperative.mp3]",
            "SieAudio": "[sound:sprechen_sie_imperative.mp3]",
            "WirAudio": "[sound:sprechen_wir_imperative.mp3]",
            "ArticleAudio": "[sound:das_pronunciation.mp3]",
            "Example1Audio": "[sound:example1.mp3]",
            "Example2Audio": "[sound:example2.mp3]",
            # Article declension fields
            "Nominative": "das",
            "Accusative": "das",
            "Dative": "dem",
            "Genitive": "des",
            # Conditional visibility fields
            "ArtikelTypBestimmt": "true",
            "ArtikelTypUnbestimmt": "",
            "ArtikelTypVerneinend": "",
            "CaseNominative": "true",
            "CaseAccusative": "",
            "CaseDative": "",
            "CaseGenitive": "",
            "CaseNominativ": "true",
            "CaseAkkusativ": "",
            "CaseDativ": "",
            "CaseGenitiv": "",
            # Extracted/computed fields
            "NounOnly": "Haus",
            "NounEnglish": "house",
            "NounEnglishWithArticle": "the house",
            "ArticleForm": "dem",
        }

        return examples.get(field_name, f"example_{field_name.lower()}")

    def _get_template_files_for_card_type(self, card_type: str) -> list[str]:
        """Get list of template files for a card type.

        Args:
            card_type: Type of card

        Returns:
            List of template file names
        """
        files = []

        # Modern naming pattern (preferred)
        front_file = f"{card_type}_front.html"
        back_file = f"{card_type}_back.html"
        css_file = f"{card_type}.css"

        if (self._template_dir / front_file).exists():
            files.append(front_file)
        if (self._template_dir / back_file).exists():
            files.append(back_file)
        if (self._template_dir / css_file).exists():
            files.append(css_file)

        # German localized pattern (DE_de suffix)
        de_front = f"{card_type}_DE_de_front.html"
        de_back = f"{card_type}_DE_de_back.html"
        de_css = f"{card_type}_DE_de.css"

        if (self._template_dir / de_front).exists():
            files.append(de_front)
        if (self._template_dir / de_back).exists():
            files.append(de_back)
        if (self._template_dir / de_css).exists():
            files.append(de_css)

        return files

    def _analyze_template_content(self, template: CardTemplate) -> tuple[str, str]:
        """Analyze template HTML to describe front and back content.

        Args:
            template: CardTemplate to analyze

        Returns:
            Tuple of (front_description, back_description)
        """
        front_html = template.front_html
        back_html = template.back_html

        # Simple content analysis based on common patterns
        front_desc = "Card front content"
        back_desc = "Card back content"

        # Analyze front content
        if "{{c1::" in front_html or "{{cloze:" in front_html:
            front_desc = "Cloze deletion question with blanked text"
        elif "hint" in front_html.lower() or "💡" in front_html:
            front_desc = "Question with optional hint button"
        elif "{{#Image}}" in front_html:
            front_desc = "Visual question with image support"

        # Analyze back content
        if "{{c1::" in back_html or "{{cloze:" in back_html:
            back_desc = "Cloze deletion answer with revealed text"
        elif "forms" in back_html.lower() or "declension" in back_html.lower():
            back_desc = "Answer with grammar forms and examples"
        elif "audio" in back_html.lower() or "🔊" in back_html:
            back_desc = "Answer with audio pronunciation support"

        return front_desc, back_desc

    def _is_cloze_deletion_card(self, template: CardTemplate) -> bool:
        """Check if template uses cloze deletion format.

        Args:
            template: CardTemplate to check

        Returns:
            True if template uses cloze deletion
        """
        # Check for cloze markers in template content
        has_cloze_markers = (
            "{{c1::" in template.front_html
            or "{{c1::" in template.back_html
            or "{{cloze:" in template.front_html
            or "{{cloze:" in template.back_html
            or "cloze" in template.name.lower()
        )

        return has_cloze_markers

    def _generate_learning_objective(self, card_type: str) -> str:
        """Generate learning objective for a card type.

        Args:
            card_type: Type of card

        Returns:
            Learning objective description
        """
        objectives = {
            "noun": "Learn German noun vocabulary with correct articles and "
            "plural forms",
            "adjective": "Master German adjective vocabulary with "
            "comparative/superlative forms",
            "adverb": "Learn German adverb vocabulary and usage patterns",
            "negation": "Master German negation words and their proper usage",
            "verb": "Learn German verb vocabulary with basic present tense conjugation",
            "verb_conjugation": "Master German verb conjugation across all "
            "persons and tenses",
            "verb_imperative": "Learn German imperative (command) forms for "
            "all persons",
            "phrase": "Learn common German phrases and expressions with context",
            "preposition": "Master German prepositions with their required "
            "grammatical cases",
            "artikel_gender": "Learn to recognize German noun genders (der/die/das)",
            "artikel_context": "Master German article changes in different "
            "grammatical cases",
            "artikel_gender_cloze": "Practice German gender recognition through "
            "cloze deletion",
            "artikel_context_cloze": "Practice German case usage through "
            "cloze deletion",
            "noun_article_recognition": "Learn which article goes with each "
            "German noun",
            "noun_case_context": "Master German noun declension in different cases",
        }

        return objectives.get(card_type, f"Learn German {card_type} patterns")

    def _generate_card_description(self, card_type: str) -> str:
        """Generate description for a card type.

        Args:
            card_type: Type of card

        Returns:
            Card type description
        """
        descriptions = {
            "noun": "Basic German noun cards with article, plural, and "
            "example sentences",
            "adjective": "German adjective cards with comparative/superlative forms",
            "adverb": "German adverb cards with type classification and usage examples",
            "negation": "German negation word cards (nicht, kein, nie, etc.)",
            "verb": "Basic German verb cards with present tense conjugation",
            "verb_conjugation": "Comprehensive German verb conjugation cards by tense",
            "verb_imperative": "German imperative (command) form cards for all persons",
            "phrase": "Common German phrase cards with contextual usage",
            "preposition": "German preposition cards with case requirements "
            "and examples",
            "artikel_gender": "German article gender recognition cards (der/die/das)",
            "artikel_context": "German article case usage cards (nom/acc/dat/gen)",
            "artikel_gender_cloze": "Cloze deletion cards for German gender "
            "recognition",
            "artikel_context_cloze": "Cloze deletion cards for German case usage",
            "noun_article_recognition": "Practice cards for learning "
            "noun-article pairs",
            "noun_case_context": "Practice cards for noun declension in "
            "different cases",
        }

        return descriptions.get(card_type, f"German {card_type} learning cards")

    def generate_markdown_documentation(
        self, specifications: list[CardTypeSpecification]
    ) -> str:
        """Generate markdown documentation from specifications.

        Args:
            specifications: List of card type specifications

        Returns:
            Markdown documentation string
        """
        markdown_lines = [
            "# German Anki Card Type Specifications",
            "",
            "This document provides comprehensive specifications for all German "
            "language card types in the system.",
            "Generated automatically by CardSpecificationGenerator to ensure "
            "accuracy and completeness.",
            "",
            f"**Total Card Types**: {len(specifications)}",
            "",
            "## Table of Contents",
            "",
        ]

        # Generate table of contents
        for i, spec in enumerate(specifications, 1):
            anchor = spec.card_type.replace("_", "-")
            markdown_lines.append(f"{i}. [{spec.card_type.title()}](#{anchor})")

        markdown_lines.extend(["", "---", ""])

        # Generate detailed specifications
        for spec in specifications:
            markdown_lines.extend(self._generate_card_type_markdown(spec))
            markdown_lines.append("---")
            markdown_lines.append("")

        return "\n".join(markdown_lines)

    def _generate_card_type_markdown(self, spec: CardTypeSpecification) -> list[str]:
        """Generate markdown section for a single card type.

        Args:
            spec: Card type specification

        Returns:
            List of markdown lines
        """
        # Get the CSV source file for this card type
        csv_source = self._get_csv_file_for_card_type(spec.card_type)

        lines = [
            f"## {spec.card_type.title()}",
            "",
            f"**Anki Note Type**: `{spec.anki_note_type_name}`",
            f"**Description**: {spec.description}",
            f"**Learning Objective**: {spec.learning_objective}",
            f"**Cloze Deletion**: {'Yes' if spec.cloze_deletion else 'No'}",
            f"**CSV Data Source**: `{csv_source}`",
            "",
            "### Card Content",
            "",
            f"**Front**: {spec.front_content_description}",
            f"**Back**: {spec.back_content_description}",
            "",
            "### Template Files",
            "",
        ]

        for template_file in spec.template_files:
            lines.append(f"- `{template_file}`")

        if not spec.template_files:
            lines.append("- *No template files found*")

        lines.extend(
            [
                "",
                "### Field Specifications",
                "",
                "| Field | Source | Required | Description | Example |",
                "|-------|--------|----------|-------------|---------|",
            ]
        )

        for field in spec.fields:
            required = "✅" if field.required else "❌"
            lines.append(
                f"| `{field.name}` | {field.data_source} | {required} | "
                f"{field.description} | `{field.example_value}` |"
            )

        lines.extend(["", ""])

        return lines

    def simulate_card_rendering_examples(
        self, specifications: list[CardTypeSpecification]
    ) -> dict[str, dict[str, str]]:
        """Generate card rendering examples for all specifications.

        Args:
            specifications: List of card type specifications

        Returns:
            Dictionary mapping card_type to rendering examples
        """
        examples = {}

        for spec in specifications:
            if spec.cloze_deletion:
                # Generate cloze deletion example
                example_fields = {}
                example_content = ""

                for field in spec.fields:
                    if field.name == "Text":
                        example_content = field.example_value
                    else:
                        example_fields[field.name] = field.example_value

                if example_content:
                    rendering = AnkiRenderSimulator.simulate_card_display(
                        example_fields, example_content
                    )
                    examples[spec.card_type] = {
                        "front": rendering["front"],
                        "back": rendering["back"],
                        "template": example_content,
                    }

        return examples
