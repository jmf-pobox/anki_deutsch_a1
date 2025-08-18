"""
Tests for AnkiBackend core methods that were missing coverage.

This module tests the critical AnkiBackend methods that had no test coverage:
- create_note_type: Complete Anki note type creation
- add_note: Note addition with field processing and tags
- _process_fields_with_media: Domain model delegation
- export_deck: Deck export with multiple fallback strategies
"""

from unittest.mock import Mock, patch

import pytest

from langlearn.backends.anki_backend import AnkiBackend
from langlearn.backends.base import CardTemplate, NoteType


class TestAnkiBackendCoreMethodsCoverage:
    """Test AnkiBackend core methods for complete coverage."""

    def test_create_note_type_complete_flow(self) -> None:
        """Test complete note type creation flow."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            # Set up detailed mocks
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            # Mock the models interface for note type creation
            mock_models = Mock()
            mock_collection.models = mock_models
            mock_notetype = {"name": "German Verb", "css": ""}
            mock_models.new.return_value = mock_notetype

            # Mock field creation
            mock_field = {"name": "test_field"}
            mock_models.new_field.return_value = mock_field

            # Mock template creation
            mock_template = {"name": "test_template", "qfmt": "", "afmt": ""}
            mock_models.new_template.return_value = mock_template

            # Mock the add operation returning changes with ID
            mock_changes = Mock()
            mock_changes.id = 98765
            mock_models.add.return_value = mock_changes

            backend = AnkiBackend("Test Deck")

            # Create note type with templates
            template = CardTemplate(
                name="Conjugation Card",
                front_html="{{Infinitive}}",
                back_html="{{PresentTense}}",
                css=".verb { color: blue; }",
            )
            note_type = NoteType(
                name="German Verb",
                fields=["Infinitive", "PresentTense", "Example"],
                templates=[template],
            )

            note_type_id = backend.create_note_type(note_type)

            # Verify complete flow
            assert note_type_id == "1"  # First note type
            mock_models.new.assert_called_once_with("German Verb")
            assert mock_models.new_field.call_count == 3  # 3 fields
            assert mock_models.add_field.call_count == 3  # 3 fields added
            mock_models.new_template.assert_called_once_with("Conjugation Card")
            mock_models.add_template.assert_called_once()
            mock_models.add.assert_called_once()

            # Verify CSS was set
            assert mock_notetype["css"] == ".verb { color: blue; }"

            # Verify internal state
            assert len(backend._note_type_map) == 1
            assert backend._next_note_type_id == 2

    def test_create_note_type_without_templates(self) -> None:
        """Test note type creation without templates."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            mock_models = Mock()
            mock_collection.models = mock_models
            mock_notetype = {"name": "Simple Type"}
            mock_models.new.return_value = mock_notetype
            mock_models.new_field.return_value = {"name": "field"}
            mock_models.add.return_value = Mock(id=54321)

            backend = AnkiBackend("Test Deck")

            # Create note type without templates
            note_type = NoteType(
                name="Simple Type",
                fields=["Word", "Translation"],
                templates=[],  # No templates
            )

            note_type_id = backend.create_note_type(note_type)

            # Verify no template processing occurred
            assert note_type_id == "1"
            mock_models.new_template.assert_not_called()
            mock_models.add_template.assert_not_called()
            # CSS should not be set for empty templates
            assert "css" not in mock_notetype

    def test_add_note_complete_flow(self) -> None:
        """Test complete note addition flow."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck")

            # Set up note type mapping
            from anki.models import NotetypeId

            backend._note_type_map["test_id"] = NotetypeId(67890)

            # Mock note type retrieval
            mock_notetype = {"name": "German Noun"}
            mock_collection.models.get.return_value = mock_notetype

            # Mock note creation
            mock_note = Mock()
            mock_note.id = 11111
            mock_note.fields = ["", "", ""]  # 3 empty fields
            mock_collection.new_note.return_value = mock_note

            # Mock field processing
            processed_fields = ["Hund", "dog", "Der Hund bellt."]
            with patch.object(
                backend, "_process_fields_with_media", return_value=processed_fields
            ) as mock_process:
                # Add note with tags
                note_id = backend.add_note(
                    note_type_id="test_id",
                    fields=["Hund", "dog", "Der Hund bellt."],
                    tags=["animals", "nouns"],
                )

                # Verify complete flow
                assert note_id == 11111
                mock_collection.models.get.assert_called_once_with(NotetypeId(67890))
                mock_collection.new_note.assert_called_once_with(mock_notetype)
                mock_process.assert_called_once_with(
                    "test_id", ["Hund", "dog", "Der Hund bellt."]
                )

                # Verify fields were set
                assert mock_note.fields[0] == "Hund"
                assert mock_note.fields[1] == "dog"
                assert mock_note.fields[2] == "Der Hund bellt."

                # Verify tags were set
                assert mock_note.tags == ["animals", "nouns"]

                # Verify note was added to collection
                mock_collection.add_note.assert_called_once_with(
                    mock_note, backend._deck_id
                )

    def test_add_note_invalid_note_type_error(self) -> None:
        """Test error handling for invalid note type ID."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            # Try to add note with non-existent note type
            with pytest.raises(ValueError, match="Note type ID invalid_id not found"):
                backend.add_note("invalid_id", ["field1", "field2"])

    def test_add_note_without_tags(self) -> None:
        """Test adding note without tags."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck")

            from anki.models import NotetypeId

            backend._note_type_map["test_id"] = NotetypeId(67890)

            mock_notetype = {"name": "Test Type"}
            mock_collection.models.get.return_value = mock_notetype

            mock_note = Mock()
            mock_note.id = 22222
            mock_note.fields = ["", ""]
            mock_collection.new_note.return_value = mock_note

            with patch.object(
                backend,
                "_process_fields_with_media",
                return_value=["word", "translation"],
            ):
                # Add note without tags (None)
                note_id = backend.add_note(
                    "test_id", ["word", "translation"], tags=None
                )

                assert note_id == 22222
                # With Mock objects, tags will be set, so we verify the call worked

    def test_add_note_notetype_not_found_error(self) -> None:
        """Test error when note type is not found in collection."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck")

            from anki.models import NotetypeId

            backend._note_type_map["test_id"] = NotetypeId(99999)

            # Mock collection returns None (note type not found)
            mock_collection.models.get.return_value = None

            with pytest.raises(ValueError, match="Note type not found: 99999"):
                backend.add_note("test_id", ["field1", "field2"])

    def test_process_fields_with_media_note_type_id_resolution(self) -> None:
        """Test field processing with note type ID resolution."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck")

            # Set up note type mapping and mock resolution
            from anki.models import NotetypeId

            backend._note_type_map["1"] = NotetypeId(12345)
            mock_notetype = {"name": "German Adjective"}
            mock_collection.models.get.return_value = mock_notetype

            # Mock ModelFactory to return a processor
            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "schön",
                    "beautiful",
                    "processed_field",
                ]
                mock_factory.return_value = mock_processor

                fields = ["schön", "beautiful", "original_field"]
                result = backend._process_fields_with_media("1", fields)

                # Verify note type was resolved and processor was used
                mock_collection.models.get.assert_called_once_with(NotetypeId(12345))
                mock_factory.assert_called_once_with("German Adjective")
                mock_processor.process_fields_for_media_generation.assert_called_once_with(
                    fields, backend._domain_media_generator
                )
                assert result == ["schön", "beautiful", "processed_field"]

    def test_process_fields_with_media_direct_name_input(self) -> None:
        """Test field processing with direct note type name (backward compatibility)."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            # Mock ModelFactory for direct name usage
            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor"
            ) as mock_factory:
                mock_processor = Mock()
                mock_processor.process_fields_for_media_generation.return_value = [
                    "processed1",
                    "processed2",
                ]
                mock_factory.return_value = mock_processor

                fields = ["original1", "original2"]
                result = backend._process_fields_with_media("German Verb", fields)

                # Should use the name directly without resolution
                mock_factory.assert_called_once_with("German Verb")
                assert result == ["processed1", "processed2"]

    def test_process_fields_with_media_unsupported_type(self) -> None:
        """Test field processing for unsupported note type."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            # Mock ModelFactory to return None (unsupported type)
            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor",
                return_value=None,
            ):
                fields = ["field1", "field2"]
                result = backend._process_fields_with_media("Unsupported Type", fields)

                # Should return original fields unchanged
                assert result == fields

    def test_process_fields_with_media_exception_handling(self) -> None:
        """Test exception handling in field processing."""
        with (
            patch("langlearn.backends.anki_backend.Collection"),
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            backend = AnkiBackend("Test Deck")

            # Mock ModelFactory to raise exception
            with patch(
                "langlearn.models.model_factory.ModelFactory.create_field_processor",
                side_effect=Exception("Processing error"),
            ):
                fields = ["field1", "field2"]
                result = backend._process_fields_with_media("German Noun", fields)

                # Should return original fields on exception
                assert result == fields

    def test_export_deck_export_to_file_method(self) -> None:
        """Test deck export using export_to_file method."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck")
            backend._media_files = [Mock(), Mock()]  # 2 media files

            # Mock AnkiPackageExporter with export_to_file method
            with patch("anki.exporting.AnkiPackageExporter") as mock_exporter_cls:
                mock_exporter = Mock()
                mock_exporter_cls.return_value = mock_exporter
                # Mock hasattr to return True for export_to_file
                mock_exporter.export_to_file = Mock()

                backend.export_deck("/output/test.apkg")

                # Verify exporter was created and configured
                mock_exporter_cls.assert_called_once_with(mock_collection)
                assert mock_exporter.did == backend._deck_id
                assert mock_exporter.include_media is True

                # Verify export_to_file was called
                mock_exporter.export_to_file.assert_called_once_with(
                    "/output/test.apkg"
                )

    def test_export_deck_exportinto_fallback(self) -> None:
        """Test deck export fallback to exportInto method."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck")

            with patch("anki.exporting.AnkiPackageExporter") as mock_exporter_cls:
                mock_exporter = Mock()
                mock_exporter_cls.return_value = mock_exporter
                # Remove export_to_file, add exportInto
                del mock_exporter.export_to_file
                mock_exporter.exportInto = Mock()

                backend.export_deck("/output/fallback.apkg")

                # Should fallback to exportInto
                mock_exporter.exportInto.assert_called_once_with(
                    "/output/fallback.apkg"
                )

    def test_export_deck_collection_fallback(self) -> None:
        """Test deck export fallback to collection method."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )
            mock_collection.export_anki_package = Mock()

            backend = AnkiBackend("Test Deck")

            with patch("anki.exporting.AnkiPackageExporter") as mock_exporter_cls:
                mock_exporter = Mock()
                mock_exporter_cls.return_value = mock_exporter
                # Remove both methods to trigger collection fallback
                del mock_exporter.export_to_file
                del mock_exporter.exportInto

                backend.export_deck("/output/collection.apkg")

                # Should fallback to collection export
                mock_collection.export_anki_package.assert_called_once_with(
                    "/output/collection.apkg", [backend._deck_id], True
                )

    def test_export_deck_logging_functionality(self) -> None:
        """Test export deck logging functionality."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend("Test Deck")
            backend._media_files = [Mock(), Mock(), Mock()]  # 3 media files

            # Mock exporter for successful export
            with patch("anki.exporting.AnkiPackageExporter") as mock_exporter_cls:
                mock_exporter = Mock()
                mock_exporter_cls.return_value = mock_exporter
                mock_exporter.export_to_file = Mock()

                with patch(
                    "langlearn.backends.anki_backend.logger.info"
                ) as mock_logger:
                    backend.export_deck("/output/logged.apkg")

                    # Verify logging occurred
                    mock_logger.assert_called_once_with(
                        "Exporting deck with 3 media files"
                    )

    def test_get_stats_exception_handling(self) -> None:
        """Test exception handling in get_stats method."""
        with (
            patch("langlearn.backends.anki_backend.Collection") as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            # Mock database to raise exception
            mock_db = Mock()
            mock_db.scalar.side_effect = Exception("Database error")
            mock_collection.db = mock_db

            backend = AnkiBackend("Test Deck")
            backend._note_type_map = {"1": Mock()}
            backend._media_files = [Mock(), Mock()]

            # Should handle exception gracefully
            stats = backend.get_stats()

            # Basic stats should still be available
            assert stats["deck_name"] == "Test Deck"
            assert stats["note_types_count"] == 1
            assert stats["media_files_count"] == 2
            # notes_count should be 0 due to exception
            assert stats["notes_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
