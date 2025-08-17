#!/usr/bin/env python3
"""
Script to create Anki German A1 deck with automatic media generation.
"""

import csv
import os
from pathlib import Path

from langlearn.backends import AnkiBackend, CardTemplate, NoteType


def create_adjective_note_type() -> NoteType:
    """Create a German adjective note type with media support."""
    template = CardTemplate(
        name="German Adjective with Media",
        front_html="""
        {{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}
        
        <div class="part-of-speech">Adjektiv</div>
        
        <div class="hint-container">
            <button class="hint-button" onclick="showHint()">💡 Hint</button>
            <div id="hint-content" class="hint-content hidden">{{English}}</div>
        </div>
        
        <script>
        function showHint() {
            var hint = document.getElementById('hint-content');
            var button = document.querySelector('.hint-button');
            hint.classList.remove('hidden');
            button.style.display = 'none';
        }
        </script>
        """,
        back_html="""
        {{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}
        
        <div class="adjective-forms">
            <div class="word-with-audio">
                <span class="german">{{Word}}</span>
                {{#WordAudio}}<span class="inline-audio">🔊 {{WordAudio}}</span>{{/WordAudio}}
            </div>
            {{#Comparative}}<div class="comparative-forms">
                <div class="form-item"><strong>Comparative:</strong> {{Comparative}}</div>
                <div class="form-item"><strong>Superlative:</strong> {{Superlative}}</div>
            </div>{{/Comparative}}
        </div>
        
        <div class="example-with-audio">
            <span class="example-sentence">{{Example}}</span>
            {{#ExampleAudio}}<span class="inline-audio">🔊 {{ExampleAudio}}</span>{{/ExampleAudio}}
        </div>
        
        <div class="back-hint-container">
            <button class="hint-button" onclick="showBackHint()">💡 Hint</button>
            <div id="back-hint-content" class="hint-content hidden">{{English}}</div>
        </div>
        
        <script>
        function showBackHint() {
            var hint = document.getElementById('back-hint-content');
            var button = document.querySelector('.back-hint-container .hint-button');
            hint.classList.remove('hidden');
            button.style.display = 'none';
        }
        </script>
        """,
        css="""
        .card {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f8f9fa;
            padding: 20px;
            color: #333;
        }
        .german {
            font-size: 28px;
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 15px;
        }
        .english {
            font-size: 20px;
            color: #444;
            margin: 15px 0;
            font-weight: 500;
        }
        .example-sentence {
            font-size: 16px;
            color: #666;
            font-style: italic;
            margin: 15px 0;
            padding: 10px;
            background: #f0f4f8;
            border-left: 3px solid #2c5aa0;
            border-radius: 5px;
        }
        .image-container {
            margin: 10px 0;
        }
        img {
            max-width: 250px;
            max-height: 170px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .part-of-speech {
            font-size: 16px;
            color: #666;
            font-style: italic;
            margin: 20px 0;
            padding: 8px 16px;
            background: #f8f9fa;
            border-radius: 20px;
            border: 1px solid #ddd;
            display: inline-block;
        }
        .word-with-audio {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        .adjective-forms {
            background: #f8f9fa;
            border: 2px solid #2c5aa0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: inline-block;
        }
        .comparative-forms {
            margin-top: 10px;
            font-size: 14px;
        }
        .form-item {
            margin: 5px 0;
            color: #555;
        }
        .example-with-audio {
            margin: 15px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .inline-audio {
            font-size: 12px;
            color: #666;
            background: #f1f3f4;
            padding: 4px 8px;
            border-radius: 12px;
            border: 1px solid #ddd;
            cursor: pointer;
            transition: background-color 0.2s;
            display: inline-block;
        }
        .inline-audio:hover {
            background: #e8f0fe;
            border-color: #2c5aa0;
        }
        .hint-container {
            margin: 20px 0;
        }
        .back-hint-container {
            margin: 25px 0 15px 0;
        }
        .hint-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 25px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .hint-button:hover {
            background: #45a049;
        }
        .hint-content {
            font-size: 18px;
            color: #2c5aa0;
            font-weight: bold;
            margin-top: 15px;
            padding: 15px;
            background: #e8f4fd;
            border-radius: 10px;
            border: 2px solid #2c5aa0;
        }
        .hidden {
            display: none;
        }
        """,
    )

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


def create_adverb_note_type() -> NoteType:
    """Create a German adverb note type with media support."""
    template = CardTemplate(
        name="German Adverb with Media",
        front_html="""
        {{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}
        
        <div class="part-of-speech">Adverb</div>
        
        <div class="adverb-type">{{Type}}</div>
        
        <div class="hint-container">
            <button class="hint-button" onclick="showHint()">💡 Hint</button>
            <div id="hint-content" class="hint-content hidden">{{English}}</div>
        </div>
        
        <script>
        function showHint() {
            var hint = document.getElementById('hint-content');
            var button = document.querySelector('.hint-button');
            hint.classList.remove('hidden');
            button.style.display = 'none';
        }
        </script>
        """,
        back_html="""
        {{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}
        
        <div class="adverb-section">
            <div class="word-with-audio">
                <span class="german">{{Word}}</span>
                {{#WordAudio}}<span class="inline-audio">🔊 {{WordAudio}}</span>{{/WordAudio}}
            </div>
            <div class="adverb-type-display">
                <span class="type-label">Type:</span> <span class="type-value">{{Type}}</span>
            </div>
        </div>
        
        <div class="example-with-audio">
            <span class="example-sentence">{{Example}}</span>
            {{#ExampleAudio}}<span class="inline-audio">🔊 {{ExampleAudio}}</span>{{/ExampleAudio}}
        </div>
        
        <div class="back-hint-container">
            <button class="hint-button" onclick="showBackHint()">💡 Hint</button>
            <div id="back-hint-content" class="hint-content hidden">{{English}}</div>
        </div>
        
        <script>
        function showBackHint() {
            var hint = document.getElementById('back-hint-content');
            var button = document.querySelector('.back-hint-container .hint-button');
            hint.classList.remove('hidden');
            button.style.display = 'none';
        }
        </script>
        """,
        css="""
        .card {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f8f9fa;
            padding: 20px;
            color: #333;
        }
        .german {
            font-size: 28px;
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 15px;
        }
        .english {
            font-size: 20px;
            color: #444;
            margin: 15px 0;
            font-weight: 500;
        }
        .example-sentence {
            font-size: 16px;
            color: #666;
            font-style: italic;
            margin: 15px 0;
            padding: 10px;
            background: #f0f4f8;
            border-left: 3px solid #2c5aa0;
            border-radius: 5px;
        }
        .image-container {
            margin: 10px 0;
        }
        img {
            max-width: 250px;
            max-height: 170px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .part-of-speech {
            font-size: 16px;
            color: #666;
            font-style: italic;
            margin: 20px 0;
            padding: 8px 16px;
            background: #f8f9fa;
            border-radius: 20px;
            border: 1px solid #ddd;
            display: inline-block;
        }
        .adverb-type {
            font-size: 14px;
            color: #888;
            margin: 10px 0;
            padding: 4px 12px;
            background: #e8f4fd;
            border-radius: 15px;
            display: inline-block;
            text-transform: capitalize;
        }
        .word-with-audio {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        .adverb-section {
            background: #f8f9fa;
            border: 2px solid #2c5aa0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: inline-block;
        }
        .adverb-type-display {
            margin-top: 10px;
            font-size: 14px;
            color: #555;
        }
        .type-label {
            font-weight: bold;
        }
        .type-value {
            color: #2c5aa0;
            text-transform: capitalize;
        }
        .example-with-audio {
            margin: 15px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .inline-audio {
            font-size: 12px;
            color: #666;
            background: #f1f3f4;
            padding: 4px 8px;
            border-radius: 12px;
            border: 1px solid #ddd;
            cursor: pointer;
            transition: background-color 0.2s;
            display: inline-block;
        }
        .inline-audio:hover {
            background: #e8f0fe;
            border-color: #2c5aa0;
        }
        .hint-container {
            margin: 20px 0;
        }
        .back-hint-container {
            margin: 25px 0 15px 0;
        }
        .hint-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 25px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .hint-button:hover {
            background: #45a049;
        }
        .hint-content {
            font-size: 18px;
            color: #2c5aa0;
            font-weight: bold;
            margin-top: 15px;
            padding: 15px;
            background: #e8f4fd;
            border-radius: 10px;
            border: 2px solid #2c5aa0;
        }
        .hidden {
            display: none;
        }
        """,
    )

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


def create_negation_note_type() -> NoteType:
    """Create a German negation note type with media support."""
    template = CardTemplate(
        name="German Negation with Media",
        front_html="""
        {{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}
        
        <div class="part-of-speech">Negation</div>
        
        <div class="negation-type">{{Type}}</div>
        
        <div class="hint-container">
            <button class="hint-button" onclick="showHint()">💡 Hint</button>
            <div id="hint-content" class="hint-content hidden">{{English}}</div>
        </div>
        
        <script>
        function showHint() {
            var hint = document.getElementById('hint-content');
            var button = document.querySelector('.hint-button');
            hint.classList.remove('hidden');
            button.style.display = 'none';
        }
        </script>
        """,
        back_html="""
        {{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}
        
        <div class="negation-section">
            <div class="word-with-audio">
                <span class="german">{{Word}}</span>
                {{#WordAudio}}<span class="inline-audio">🔊 {{WordAudio}}</span>{{/WordAudio}}
            </div>
            <div class="negation-type-display">
                <span class="type-label">Type:</span> <span class="type-value">{{Type}}</span>
            </div>
        </div>
        
        <div class="example-with-audio">
            <span class="example-sentence">{{Example}}</span>
            {{#ExampleAudio}}<span class="inline-audio">🔊 {{ExampleAudio}}</span>{{/ExampleAudio}}
        </div>
        
        <div class="back-hint-container">
            <button class="hint-button" onclick="showBackHint()">💡 Hint</button>
            <div id="back-hint-content" class="hint-content hidden">{{English}}</div>
        </div>
        
        <script>
        function showBackHint() {
            var hint = document.getElementById('back-hint-content');
            var button = document.querySelector('.back-hint-container .hint-button');
            hint.classList.remove('hidden');
            button.style.display = 'none';
        }
        </script>
        """,
        css="""
        .card {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f8f9fa;
            padding: 20px;
            color: #333;
        }
        .german {
            font-size: 28px;
            font-weight: bold;
            color: #dc3545;
            margin-bottom: 15px;
        }
        .english {
            font-size: 20px;
            color: #444;
            margin: 15px 0;
            font-weight: 500;
        }
        .example-sentence {
            font-size: 16px;
            color: #666;
            font-style: italic;
            margin: 15px 0;
            padding: 10px;
            background: #f0f4f8;
            border-left: 3px solid #dc3545;
            border-radius: 5px;
        }
        .image-container {
            margin: 10px 0;
        }
        img {
            max-width: 250px;
            max-height: 170px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .part-of-speech {
            font-size: 16px;
            color: #666;
            font-style: italic;
            margin: 20px 0;
            padding: 8px 16px;
            background: #f8f9fa;
            border-radius: 20px;
            border: 1px solid #ddd;
            display: inline-block;
        }
        .negation-type {
            font-size: 14px;
            color: #888;
            margin: 10px 0;
            padding: 4px 12px;
            background: #ffeaa7;
            border-radius: 15px;
            display: inline-block;
            text-transform: capitalize;
        }
        .word-with-audio {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        .negation-section {
            background: #fff5f5;
            border: 2px solid #dc3545;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: inline-block;
        }
        .negation-type-display {
            margin-top: 10px;
            font-size: 14px;
            color: #555;
        }
        .type-label {
            font-weight: bold;
        }
        .type-value {
            color: #dc3545;
            text-transform: capitalize;
        }
        .example-with-audio {
            margin: 15px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .inline-audio {
            font-size: 12px;
            color: #666;
            background: #f1f3f4;
            padding: 4px 8px;
            border-radius: 12px;
            border: 1px solid #ddd;
            cursor: pointer;
            transition: background-color 0.2s;
            display: inline-block;
        }
        .inline-audio:hover {
            background: #e8f0fe;
            border-color: #dc3545;
        }
        .hint-container {
            margin: 20px 0;
        }
        .back-hint-container {
            margin: 25px 0 15px 0;
        }
        .hint-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 25px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .hint-button:hover {
            background: #45a049;
        }
        .hint-content {
            font-size: 18px;
            color: #dc3545;
            font-weight: bold;
            margin-top: 15px;
            padding: 15px;
            background: #fff5f5;
            border-radius: 10px;
            border: 2px solid #dc3545;
        }
        .hidden {
            display: none;
        }
        """,
    )

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


def create_noun_note_type() -> NoteType:
    """Create a German noun note type with media support."""
    template = CardTemplate(
        name="German Noun with Media",
        front_html="""
        {{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}
        
        <div class="part-of-speech">Substantiv</div>
        
        <div class="hint-container">
            <button class="hint-button" onclick="showHint()">💡 Hint</button>
            <div id="hint-content" class="hint-content hidden">{{English}}</div>
        </div>
        
        <script>
        function showHint() {
            var hint = document.getElementById('hint-content');
            var button = document.querySelector('.hint-button');
            hint.classList.remove('hidden');
            button.style.display = 'none';
        }
        </script>
        """,
        back_html="""
        {{#Image}}<div class="image-container">{{Image}}</div>{{/Image}}
        
        <div class="noun-section">
            <div class="word-with-audio">
                <span class="german">{{Article}} {{Word}}</span>
                {{#WordAudio}}<span class="inline-audio">🔊 {{WordAudio}}</span>{{/WordAudio}}
            </div>
            {{#Plural}}<div class="plural-forms">
                <div class="form-item"><strong>Plural:</strong> die {{Plural}}</div>
            </div>{{/Plural}}
        </div>
        
        <div class="example-with-audio">
            <span class="example-sentence">{{Example}}</span>
            {{#ExampleAudio}}<span class="inline-audio">🔊 {{ExampleAudio}}</span>{{/ExampleAudio}}
        </div>
        
        {{#Related}}<div class="related-words">
            <strong>Related:</strong> {{Related}}
        </div>{{/Related}}
        
        <div class="back-hint-container">
            <button class="hint-button" onclick="showBackHint()">💡 Hint</button>
            <div id="back-hint-content" class="hint-content hidden">{{English}}</div>
        </div>
        
        <script>
        function showBackHint() {
            var hint = document.getElementById('back-hint-content');
            var button = document.querySelector('.back-hint-container .hint-button');
            hint.classList.remove('hidden');
            button.style.display = 'none';
        }
        </script>
        """,
        css="""
        .card {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f8f9fa;
            padding: 20px;
            color: #333;
        }
        .german {
            font-size: 28px;
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 15px;
        }
        .english {
            font-size: 20px;
            color: #444;
            margin: 15px 0;
            font-weight: 500;
        }
        .example-sentence {
            font-size: 16px;
            color: #666;
            font-style: italic;
            margin: 15px 0;
            padding: 10px;
            background: #f0f4f8;
            border-left: 3px solid #2c5aa0;
            border-radius: 5px;
        }
        .image-container {
            margin: 10px 0;
        }
        img {
            max-width: 250px;
            max-height: 170px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .part-of-speech {
            font-size: 16px;
            color: #666;
            font-style: italic;
            margin: 20px 0;
            padding: 8px 16px;
            background: #f8f9fa;
            border-radius: 20px;
            border: 1px solid #ddd;
            display: inline-block;
        }
        .article-badge {
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
            padding: 8px 16px;
            border-radius: 15px;
            display: inline-block;
            text-transform: uppercase;
        }
        .article-der {
            background: #e3f2fd;
            color: #1976d2;
            border: 2px solid #1976d2;
        }
        .article-die {
            background: #fce4ec;
            color: #c2185b;
            border: 2px solid #c2185b;
        }
        .article-das {
            background: #e8f5e8;
            color: #388e3c;
            border: 2px solid #388e3c;
        }
        .word-with-audio {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        .noun-section {
            background: #f8f9fa;
            border: 2px solid #2c5aa0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: inline-block;
        }
        .plural-forms {
            margin-top: 10px;
            font-size: 14px;
        }
        .form-item {
            margin: 5px 0;
            color: #555;
        }
        .article-info {
            margin-top: 10px;
            font-size: 14px;
        }
        .article-label {
            font-weight: bold;
            color: #555;
        }
        .example-with-audio {
            margin: 15px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .related-words {
            font-size: 14px;
            color: #666;
            margin: 15px 0;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 8px;
            border-left: 3px solid #999;
        }
        .inline-audio {
            font-size: 12px;
            color: #666;
            background: #f1f3f4;
            padding: 4px 8px;
            border-radius: 12px;
            border: 1px solid #ddd;
            cursor: pointer;
            transition: background-color 0.2s;
            display: inline-block;
        }
        .inline-audio:hover {
            background: #e8f0fe;
            border-color: #2c5aa0;
        }
        .hint-container {
            margin: 20px 0;
        }
        .back-hint-container {
            margin: 25px 0 15px 0;
        }
        .hint-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 25px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .hint-button:hover {
            background: #45a049;
        }
        .hint-content {
            font-size: 18px;
            color: #2c5aa0;
            font-weight: bold;
            margin-top: 15px;
            padding: 15px;
            background: #e8f4fd;
            border-radius: 10px;
            border: 2px solid #2c5aa0;
        }
        .noun-word {
            font-size: 32px;
            font-weight: bold;
            color: #2c5aa0;
            margin: 20px 0;
            text-align: center;
        }
        .hidden {
            display: none;
        }
        """,
    )

    return NoteType(
        name="German Noun with Media",
        fields=[
            "Word",
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


def load_adjectives_from_csv(
    backend: AnkiBackend, note_type_id: str, csv_path: Path
) -> int:
    """Load adjectives from CSV and create cards with automatic media generation."""
    cards_added = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["word"].strip():  # Skip empty rows
                continue

            # Fields: [Word, English, Example, Comparative, Superlative, Image, WordAudio, ExampleAudio]
            fields = [
                row["word"],
                row["english"],
                row["example"],
                row["comparative"],
                row["superlative"],
                "",  # Image - will be auto-generated/found
                "",  # WordAudio - will be auto-generated
                "",  # ExampleAudio - will be auto-generated
            ]

            try:
                backend.add_note(note_type_id, fields, tags=["adjective", "a1"])
                cards_added += 1
                print(f"  Added adjective: {row['word']}")
            except Exception as e:
                print(f"  Error adding {row['word']}: {e}")

    return cards_added


def load_adverbs_from_csv(
    backend: AnkiBackend, note_type_id: str, csv_path: Path
) -> int:
    """Load adverbs from CSV and create cards with automatic media generation."""
    cards_added = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["word"].strip():  # Skip empty rows
                continue

            # Fields: [Word, English, Type, Example, Image, WordAudio, ExampleAudio]
            fields = [
                row["word"],
                row["english"],
                row["type"],
                row["example"],
                "",  # Image - will be auto-generated/found for visual adverbs
                "",  # WordAudio - will be auto-generated
                "",  # ExampleAudio - will be auto-generated
            ]

            try:
                backend.add_note(
                    note_type_id, fields, tags=["adverb", "a1", row["type"]]
                )
                cards_added += 1
                print(f"  Added adverb: {row['word']} ({row['type']})")
            except Exception as e:
                print(f"  Error adding {row['word']}: {e}")

    return cards_added


def load_negations_from_csv(
    backend: AnkiBackend, note_type_id: str, csv_path: Path
) -> int:
    """Load negations from CSV and create cards with automatic media generation."""
    cards_added = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["word"].strip():  # Skip empty rows
                continue

            # Fields: [Word, English, Type, Example, Image, WordAudio, ExampleAudio]
            fields = [
                row["word"],
                row["english"],
                row["type"],
                row["example"],
                "",  # Image - will be auto-generated for conceptual negations
                "",  # WordAudio - will be auto-generated
                "",  # ExampleAudio - will be auto-generated
            ]

            try:
                backend.add_note(
                    note_type_id, fields, tags=["negation", "a1", row["type"]]
                )
                cards_added += 1
                print(f"  Added negation: {row['word']} ({row['type']})")
            except Exception as e:
                print(f"  Error adding {row['word']}: {e}")

    return cards_added


def load_nouns_from_csv(backend: AnkiBackend, note_type_id: str, csv_path: Path) -> int:
    """Load nouns from CSV and create cards with automatic media generation."""
    cards_added = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("noun", "").strip():  # Skip empty rows
                continue

            # Fields: [Word, Article, English, Plural, Example, Related, Image, WordAudio, ExampleAudio]
            fields = [
                row["noun"],
                row.get("article", ""),
                row["english"],
                row.get("plural", ""),
                row.get("example", ""),
                row.get("related", ""),
                "",  # Image - will be auto-generated for concrete nouns
                "",  # WordAudio - will be auto-generated (combined article+noun, plural)
                "",  # ExampleAudio - will be auto-generated
            ]

            try:
                backend.add_note(
                    note_type_id, fields, tags=["noun", "a1", row["article"]]
                )
                cards_added += 1
                print(f"  Added noun: {row['article']} {row['noun']}")
            except Exception as e:
                print(f"  Error adding {row['noun']}: {e}")

    return cards_added


def main() -> None:
    """Create an Anki deck with automatic media generation."""
    print("=== German A1 Deck Generator ===")
    print("Creating deck with automatic audio and image generation...")

    # Get paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent.parent
    data_dir = project_dir / "data"
    output_dir = project_dir / "output"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create backend
    backend = AnkiBackend(
        "German A1 Vocabulary",
        "German A1 vocabulary with automatic audio and image generation",
    )

    total_cards = 0

    # Process adjectives in their own subdeck
    adjectives_file = data_dir / "adjectives.csv"
    if adjectives_file.exists():
        print(f"\nProcessing adjectives from {adjectives_file}")
        backend.set_current_subdeck("Adjectives")
        print(f"📁 Creating subdeck: {backend.get_current_deck_name()}")
        adjective_note_type = create_adjective_note_type()
        adjective_note_type_id = backend.create_note_type(adjective_note_type)
        cards_added = load_adjectives_from_csv(
            backend, adjective_note_type_id, adjectives_file
        )
        total_cards += cards_added
        print(f"Added {cards_added} adjective cards to subdeck")
    else:
        print(f"Warning: {adjectives_file} not found")

    # Process adverbs in their own subdeck
    adverbs_file = data_dir / "adverbs.csv"
    if adverbs_file.exists():
        print(f"\nProcessing adverbs from {adverbs_file}")
        backend.set_current_subdeck("Adverbs")
        print(f"📁 Creating subdeck: {backend.get_current_deck_name()}")
        adverb_note_type = create_adverb_note_type()
        adverb_note_type_id = backend.create_note_type(adverb_note_type)
        cards_added = load_adverbs_from_csv(backend, adverb_note_type_id, adverbs_file)
        total_cards += cards_added
        print(f"Added {cards_added} adverb cards to subdeck")
    else:
        print(f"Info: {adverbs_file} not found, skipping adverbs")

    # Process nouns in their own subdeck
    nouns_file = data_dir / "nouns.csv"
    if nouns_file.exists():
        print(f"\nProcessing nouns from {nouns_file}")
        backend.set_current_subdeck("Nouns")
        print(f"📁 Creating subdeck: {backend.get_current_deck_name()}")
        noun_note_type = create_noun_note_type()
        noun_note_type_id = backend.create_note_type(noun_note_type)
        cards_added = load_nouns_from_csv(backend, noun_note_type_id, nouns_file)
        total_cards += cards_added
        print(f"Added {cards_added} noun cards to subdeck")
    else:
        print(f"Info: {nouns_file} not found, skipping nouns")

    # Process negations in their own subdeck
    negations_file = data_dir / "negations.csv"
    if negations_file.exists():
        print(f"\nProcessing negations from {negations_file}")
        backend.set_current_subdeck("Negations")
        print(f"📁 Creating subdeck: {backend.get_current_deck_name()}")
        negation_note_type = create_negation_note_type()
        negation_note_type_id = backend.create_note_type(negation_note_type)
        cards_added = load_negations_from_csv(
            backend, negation_note_type_id, negations_file
        )
        total_cards += cards_added
        print(f"Added {cards_added} negation cards to subdeck")
    else:
        print(f"Info: {negations_file} not found, skipping negations")

    # Show statistics
    print("\n=== Generation Statistics ===")
    stats = backend.get_stats()
    if "media_generation_stats" in stats:
        media_gen = stats["media_generation_stats"]
        print(f"✅ Audio generated: {media_gen['audio_generated']}")
        print(f"♻️  Audio reused: {media_gen['audio_reused']}")
        print(f"🖼️  Images downloaded: {media_gen['images_downloaded']}")
        print(f"♻️  Images reused: {media_gen['images_reused']}")
        print(f"❌ Generation errors: {media_gen['generation_errors']}")
        print(f"🆕 Total new media: {media_gen['total_media_generated']}")
        print(f"🔄 Total reused media: {media_gen['total_media_reused']}")

    if "media_stats" in stats:
        media_stats = stats["media_stats"]
        print(f"📦 Media files in deck: {media_stats['files_added']}")
        print(f"🚫 Duplicates skipped: {media_stats['duplicates_skipped']}")

    print(f"📚 Total cards created: {total_cards}")

    # Show subdeck organization
    print("\n📁 Deck Structure:")
    print(f"   Main deck: {backend.deck_name}")
    if hasattr(backend, "_subdecks") and backend._subdecks:
        for subdeck_name in backend._subdecks.keys():
            print(f"   └── {subdeck_name}")

    # Export deck
    output_file = output_dir / "German_A1_Vocabulary.apkg"
    try:
        backend.export_deck(str(output_file))
        print(f"\n✅ Deck exported to: {output_file}")
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        return
    finally:
        # Clean up backend explicitly
        backend.close()

    print("🎉 Generation complete! Audio and images added automatically.")


if __name__ == "__main__":
    main()
