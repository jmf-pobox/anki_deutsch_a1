import csv
import random
import os
import shutil
import tempfile
from typing import TYPE_CHECKING

import genanki  # type: ignore

from .services import AudioService

if TYPE_CHECKING:
    from genanki import Deck, Model  # type: ignore


class AnkiDeckGenerator:
    """A class for generating custom Anki decks for German A1 vocabulary."""

    def __init__(self, deck_name: str = "German A1 Vocabulary"):
        """Initialize the deck generator with a given deck name.

        Args:
            deck_name: The name of the Anki deck to create
        """
        # Create a unique ID for the deck and models
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.noun_model_id = random.randrange(1 << 30, 1 << 31)
        self.verb_model_id = random.randrange(1 << 30, 1 << 31)
        self.adj_model_id = random.randrange(1 << 30, 1 << 31)
        self.prep_model_id = random.randrange(1 << 30, 1 << 31)
        self.phrase_model_id = random.randrange(1 << 30, 1 << 31)

        # Create the deck
        self.deck = genanki.Deck(  # type: ignore
            self.deck_id,
            deck_name,
            "German A1 vocabulary deck generated by Langlearn",
        )

        # Initialize services
        self.audio_service = AudioService()

        # Track media files
        self.media_files: set[str] = set()  # Set of media file paths
        self.media_dir = tempfile.mkdtemp()
        
        # Store project root for resolving relative paths
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        # Define the models (note types)
        self._define_models()

    def __del__(self):
        """Clean up temporary media directory."""
        if hasattr(self, 'media_dir'):
            shutil.rmtree(self.media_dir, ignore_errors=True)

    def _read_template_file(self, template_path: str) -> str:
        """Read a template file and return its contents.

        Args:
            template_path: Path to the template file

        Returns:
            Contents of the template file
        """
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        full_path = os.path.join(template_dir, template_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def _define_models(self) -> None:
        """Define the various note types for different word categories."""
        # Noun model
        self.noun_model = genanki.Model(  # type: ignore
            self.noun_model_id,
            "German Noun",
            fields=[
                {"name": "Noun"},
                {"name": "Article"},
                {"name": "English"},
                {"name": "Plural"},
                {"name": "Example"},
                {"name": "Related"},
                {"name": "Audio"},
            ],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": """
                        {{Noun}}<br>
                        {{Article}}
                        {{#Audio}}<br>{{Audio}}{{/Audio}}
                    """,
                    "afmt": """
                        {{FrontSide}}
                        <hr id=answer>
                        {{English}}<br>
                        Plural: {{Plural}}<br>
                        Example: {{Example}}<br>
                        Related: {{Related}}
                    """,
                }
            ],
            css="""
                .card {
                    font-family: Arial, sans-serif;
                    font-size: 18px;
                    text-align: center;
                    background-color: #f5f5f5;
                    padding: 20px;
                }
                .german {
                    font-size: 24px;
                    font-weight: bold;
                    color: #669933;
                }
                .english {
                    font-size: 20px;
                    color: #333;
                    margin: 10px 0;
                }
            """,
        )

        # Verb model
        self.verb_model = genanki.Model(
            self.verb_model_id,
            "German Verb",
            fields=[
                {"name": "Verb"},
                {"name": "English"},
                {"name": "Present_Ich"},
                {"name": "Present_Du"},
                {"name": "Present_Er"},
                {"name": "Perfect"},
                {"name": "Example"},
                {"name": "ExampleAudio"},
            ],
            templates=[
                {
                    "name": "German Verb Card",
                    "qfmt": "{{Verb}}",
                    "afmt": """
                        <div class="german">{{Verb}}</div>
                        <hr>
                        <div class="english">{{English}}</div>
                        <div class="conjugation">
                            <b>Present tense:</b><br>
                            ich {{Present_Ich}}<br>
                            du {{Present_Du}}<br>
                            er/sie/es {{Present_Er}}
                        </div>
                        <div class="perfect"><b>Perfect:</b> {{Perfect}}</div>
                        <div class="example"><b>Example:</b> {{Example}}</div>
                        {{#ExampleAudio}}{{ExampleAudio}}{{/ExampleAudio}}
                    """,
                },
            ],
            css="""
                .card {
                    font-family: Arial, sans-serif;
                    font-size: 18px;
                    text-align: center;
                    background-color: #f5f5f5;
                    padding: 20px;
                }
                .german {
                    font-size: 24px;
                    font-weight: bold;
                    color: #669933;
                }
                .english {
                    font-size: 20px;
                    color: #333;
                    margin: 10px 0;
                }
                .conjugation, .perfect, .example {
                    text-align: left;
                    margin: 5px 0;
                }
            """,
        )

        # Adjective/Adverb model
        self.adj_model = genanki.Model(
            self.adj_model_id,
            "German Adjective/Adverb",
            fields=[
                {"name": "Word"},
                {"name": "English"},
                {"name": "Example"},
                {"name": "Comparative"},
                {"name": "Superlative"},
                {"name": "Image"},
                {"name": "WordAudio"},
                {"name": "ExampleAudio"},
            ],
            templates=[
                {
                    "name": "German Adjective Card",
                    "qfmt": self._read_template_file("adjectives/card_front.html"),
                    "afmt": self._read_template_file("adjectives/card_back.html"),
                },
            ],
            css=self._read_template_file("adjectives/style.css"),
        )

        # Preposition model
        self.prep_model = genanki.Model(
            self.prep_model_id,
            "German Preposition",
            fields=[
                {"name": "Preposition"},
                {"name": "English"},
                {"name": "Case"},
                {"name": "Example1"},
                {"name": "Example2"},
                {"name": "Example1Audio"},
                {"name": "Example2Audio"},
            ],
            templates=[
                {
                    "name": "German Preposition Card",
                    "qfmt": "{{Preposition}}",
                    "afmt": """
                        <div class="german">{{Preposition}}</div>
                        <hr>
                        <div class="english">{{English}}</div>
                        <div class="case"><b>Case:</b> {{Case}}</div>
                        <div class="example"><b>Example 1:</b> {{Example1}}</div>
                        {{#Example1Audio}}{{Example1Audio}}{{/Example1Audio}}
                        <div class="example"><b>Example 2:</b> {{Example2}}</div>
                        {{#Example2Audio}}{{Example2Audio}}{{/Example2Audio}}
                    """,
                },
            ],
            css="""
                .card {
                    font-family: Arial, sans-serif;
                    font-size: 18px;
                    text-align: center;
                    background-color: #f5f5f5;
                    padding: 20px;
                }
                .german {
                    font-size: 24px;
                    font-weight: bold;
                    color: #993366;
                }
                .english {
                    font-size: 20px;
                    color: #333;
                    margin: 10px 0;
                }
                .case, .example {
                    text-align: left;
                    margin: 5px 0;
                }
            """,
        )

        # Phrase model
        self.phrase_model = genanki.Model(
            self.phrase_model_id,
            "German Phrase",
            fields=[
                {"name": "Phrase"},
                {"name": "English"},
                {"name": "Context"},
                {"name": "Related"},
                {"name": "PhraseAudio"},
            ],
            templates=[
                {
                    "name": "German Phrase Card",
                    "qfmt": "{{Phrase}}",
                    "afmt": """
                        <div class="german">{{Phrase}}</div>
                        {{#PhraseAudio}}{{PhraseAudio}}{{/PhraseAudio}}
                        <hr>
                        <div class="english">{{English}}</div>
                        <div class="context"><b>Context:</b> {{Context}}</div>
                        <div class="related">{{Related}}</div>
                    """,
                },
            ],
            css="""
                .card {
                    font-family: Arial, sans-serif;
                    font-size: 18px;
                    text-align: center;
                    background-color: #f5f5f5;
                    padding: 20px;
                }
                .german {
                    font-size: 24px;
                    font-weight: bold;
                    color: #339999;
                }
                .english {
                    font-size: 20px;
                    color: #333;
                    margin: 10px 0;
                }
                .context, .related {
                    text-align: left;
                    margin: 5px 0;
                }
            """,
        )

    def _add_media_file(self, file_path: str) -> str:
        """Add a media file to the deck and return its Anki reference.

        Args:
            file_path: Path to the media file

        Returns:
            Anki media reference for the file
        """
        if not file_path:
            return ""

        # Convert to absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.project_root, file_path)

        if not os.path.exists(file_path):
            print(f"Warning: Media file not found: {file_path}")
            return ""

        # Store the full path for later use
        self.media_files.add(file_path)
        
        # For all media files, we just need the filename
        return os.path.basename(file_path)

    def add_noun(
        self,
        noun: str,
        article: str,
        english: str,
        plural: str,
        example: str,
        related: str = "",
        audio_filename: str | None = None,
    ) -> None:
        """Add a noun card to the deck.

        Args:
            noun: The German noun
            article: The article (der/die/das)
            english: English translation
            plural: Plural form
            example: Example sentence
            related: Related words/phrases
            audio_filename: Audio filename for the card
        """
        note = genanki.Note(
            model=self.noun_model,
            fields=[
                noun,
                article,
                english,
                plural,
                example,
                related,
                audio_filename or "",
            ],
        )
        self.deck.add_note(note)  # type: ignore[no-untyped-call]

    def add_verb(
        self,
        verb: str,
        english: str,
        present_ich: str,
        present_du: str,
        present_er: str,
        perfect: str,
        example: str,
        example_audio: str = "",
    ) -> None:
        """Add a verb card to the deck.

        Args:
            verb: The German verb in infinitive
            english: English translation
            present_ich: Present tense 1st person singular
            present_du: Present tense 2nd person singular
            present_er: Present tense 3rd person singular
            perfect: Perfect tense form
            example: Example sentence
            example_audio: Audio for the example sentence
        """
        note = genanki.Note(
            model=self.verb_model,
            fields=[
                verb,
                english,
                present_ich,
                present_du,
                present_er,
                perfect,
                example,
                example_audio,
            ],
        )
        self.deck.add_note(note)  # type: ignore

    def add_adjective(
        self, 
        word: str, 
        english: str, 
        example: str, 
        comparative: str = "", 
        superlative: str = "",
        image: str = "",
        word_audio: str = "",
        example_audio: str = "",
    ) -> None:
        """Add an adjective/adverb card to the deck.

        Args:
            word: The German adjective/adverb
            english: English translation
            example: Example sentence
            comparative: Comparative form
            superlative: Superlative form
            image: HTML img tag for the image
            word_audio: Audio filename for the word
            example_audio: Audio filename for the example
        """
        note = genanki.Note(
            model=self.adj_model, 
            fields=[word, english, example, comparative, superlative, image, word_audio, example_audio]
        )
        self.deck.add_note(note)  # type: ignore[no-untyped-call]

    def add_preposition(
        self,
        preposition: str,
        english: str,
        case: str,
        example1: str,
        example2: str = "",
        example1_audio: str = "",
        example2_audio: str = "",
    ) -> None:
        """Add a preposition card to the deck.

        Args:
            preposition: The German preposition
            english: English translation
            case: Case it takes (Akkusativ/Dativ)
            example1: First example sentence
            example2: Second example sentence
            example1_audio: Audio for the first example
            example2_audio: Audio for the second example
        """
        note = genanki.Note(
            model=self.prep_model,
            fields=[
                preposition,
                english,
                case,
                example1,
                example2,
                example1_audio,
                example2_audio,
            ],
        )
        self.deck.add_note(note)  # type: ignore

    def add_phrase(
        self,
        phrase: str,
        english: str,
        context: str,
        related: str = "",
        phrase_audio: str = "",
    ) -> None:
        """Add a phrase card to the deck.

        Args:
            phrase: The German phrase
            english: English translation
            context: Usage context
            related: Related expressions
            phrase_audio: Audio for the phrase
        """
        note = genanki.Note(
            model=self.phrase_model,
            fields=[
                phrase,
                english,
                context,
                related,
                phrase_audio,
            ],
        )
        self.deck.add_note(note)  # type: ignore

    def save_deck(self, filename: str) -> None:
        """Save the deck to an .apkg file.

        Args:
            filename: The filename to save the deck to
        """
        # Create the package with media files
        package = genanki.Package(self.deck)  # type: ignore
        
        # Add all media files to the package
        media_files: list[str] = []
        for src_path in self.media_files:
            if os.path.exists(src_path):
                # Get the original filename
                original_name = os.path.basename(src_path)
                # Create a temporary copy with the original name
                temp_path = os.path.join(self.media_dir, original_name)
                shutil.copy2(src_path, temp_path)
                media_files.append(temp_path)
        
        package.media_files = media_files
        
        # Write the package
        package.write_to_file(filename)  # type: ignore
        print(f"Deck saved to {filename}")

    def load_from_csv(self, csv_file: str, word_type: str) -> None:
        """Load words from a CSV file based on their type.

        Args:
            csv_file: Path to the CSV file
            word_type: Type of word (noun, verb, adjective, preposition, phrase)
        """
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if word_type == "noun":
                    # Handle audio files for nouns
                    audio_filename = row.get("audio_filename", "")
                    if audio_filename:
                        audio_ref = self._add_media_file(audio_filename)
                        audio_ref = f"[sound:{audio_ref}]" if audio_ref else ""
                    else:
                        audio_ref = ""

                    self.add_noun(
                        row["noun"],
                        row["article"],
                        row["english"],
                        row["plural"],
                        row["example"],
                        row.get("related", ""),
                        audio_ref,
                    )
                elif word_type == "verb":
                    # Handle audio files for verbs
                    example_audio = row.get("example_audio", "")
                    if example_audio:
                        example_audio_ref = self._add_media_file(example_audio)
                        example_audio_ref = f"[sound:{example_audio_ref}]" if example_audio_ref else ""
                    else:
                        example_audio_ref = ""

                    self.add_verb(
                        row["verb"],
                        row["english"],
                        row["present_ich"],
                        row["present_du"],
                        row["present_er"],
                        row["perfect"],
                        row["example"],
                        example_audio_ref,
                    )
                elif word_type == "adjective":
                    # Get image path and create HTML img tag if image exists
                    image_path = row.get("image_path", "")
                    if image_path:
                        # Add media file and get reference
                        media_ref = self._add_media_file(image_path)
                        image_html = f'<img src="{media_ref}">' if media_ref else ""
                    else:
                        image_html = ""

                    # Handle audio files
                    word_audio_path = row.get("word_audio", "")
                    example_audio_path = row.get("example_audio", "")
                    
                    # Add word audio with [sound:] wrapper
                    if word_audio_path:
                        word_audio_ref = self._add_media_file(word_audio_path)
                        word_audio_ref = f"[sound:{word_audio_ref}]" if word_audio_ref else ""
                    else:
                        word_audio_ref = ""

                    # Add example audio with [sound:] wrapper
                    if example_audio_path:
                        example_audio_ref = self._add_media_file(example_audio_path)
                        example_audio_ref = f"[sound:{example_audio_ref}]" if example_audio_ref else ""
                    else:
                        example_audio_ref = ""
                    
                    self.add_adjective(
                        row["word"],
                        row["english"],
                        row["example"],
                        row.get("comparative", ""),
                        row.get("superlative", ""),
                        image_html,
                        word_audio_ref,
                        example_audio_ref,
                    )
                elif word_type == "preposition":
                    # Handle audio files for prepositions
                    example1_audio = row.get("example1_audio", "")
                    example2_audio = row.get("example2_audio", "")
                    
                    if example1_audio:
                        example1_audio_ref = self._add_media_file(example1_audio)
                        example1_audio_ref = f"[sound:{example1_audio_ref}]" if example1_audio_ref else ""
                    else:
                        example1_audio_ref = ""

                    if example2_audio:
                        example2_audio_ref = self._add_media_file(example2_audio)
                        example2_audio_ref = f"[sound:{example2_audio_ref}]" if example2_audio_ref else ""
                    else:
                        example2_audio_ref = ""

                    self.add_preposition(
                        row["preposition"],
                        row["english"],
                        row["case"],
                        row["example1"],
                        row.get("example2", ""),
                        example1_audio_ref,
                        example2_audio_ref,
                    )
                elif word_type == "phrase":
                    # Handle audio files for phrases
                    phrase_audio = row.get("phrase_audio", "")
                    if phrase_audio:
                        phrase_audio_ref = self._add_media_file(phrase_audio)
                        phrase_audio_ref = f"[sound:{phrase_audio_ref}]" if phrase_audio_ref else ""
                    else:
                        phrase_audio_ref = ""

                    self.add_phrase(
                        row["phrase"],
                        row["english"],
                        row["context"],
                        row.get("related", ""),
                        phrase_audio_ref,
                    )

    def _get_audio(self, text: str) -> bytes | None:
        """Get audio for text using AWS Polly."""
        try:
            response = self.audio_service.synthesize_speech(  # type: ignore
                Text=text,
                OutputFormat="mp3",
                VoiceId="Vicki",
                Engine="neural",
                LanguageCode="de-DE",
            )
            if "AudioStream" in response:
                return response["AudioStream"].read()  # type: ignore[no-any-return]
        except Exception as e:
            print(f"Error getting audio: {e}")
            return None
        return None


def generate_audio(text: str, output_dir: str | None = None) -> str | None:
    """Generate audio for the given text using AWS Polly.

    Args:
        text: The text to convert to speech
        output_dir: Optional directory to store the audio file

    Returns:
        Path to the generated audio file or None if generation failed
    """
    service = AudioService(output_dir=output_dir) if output_dir else AudioService()
    return service.generate_audio(text)


def create_deck(name: str, description: str) -> "Deck":  # type: ignore[valid-type]
    """Create a new Anki deck."""
    deck_id = random.randrange(1 << 30, 1 << 31)
    return genanki.Deck(deck_id, name, description)  # type: ignore[no-untyped-call]


def add_note(deck: "Deck", fields: list[str], model: "Model") -> None:  # type: ignore[valid-type]
    """Add a note to the deck."""
    note = genanki.Note(model=model, fields=fields)  # type: ignore[no-untyped-call]
    deck.add_note(note)  # type: ignore[no-untyped-call]


def write_to_file(deck: "Deck", file: str, timestamp: float | None = None) -> None:  # type: ignore[valid-type]
    """Write the deck to a file."""
    package = genanki.Package(deck)  # type: ignore[no-untyped-call]
    package.write_to_file(file)  # type: ignore[no-untyped-call]
