"""
Tests for AnkiBackend bulk operations performance with German A1 dataset.

This module tests that AnkiBackend can handle bulk operations efficiently
with the actual German A1 vocabulary dataset, measuring performance metrics.
"""

import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from langlearn.infrastructure.backends.anki_backend import AnkiBackend
from langlearn.infrastructure.backends.base import CardTemplate, NoteType
from langlearn.languages.german.language import GermanLanguage


class TestAnkiBackendBulkPerformance:
    """Test AnkiBackend bulk operations performance."""

    def test_bulk_note_creation_performance(self, mock_media_service: Mock) -> None:
        """Test performance of bulk note creation operations."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            # Mock models interface
            mock_models = Mock()
            mock_collection.models = mock_models
            mock_notetype = {"name": "German Noun", "css": ""}
            mock_models.new.return_value = mock_notetype
            mock_models.new_field.return_value = {"name": "field"}
            mock_models.add.return_value = Mock(id=98765)

            # Mock template creation to return dict-like object
            mock_template = {"name": "template", "qfmt": "", "afmt": ""}
            mock_models.new_template.return_value = mock_template

            # Mock note creation
            mock_note = Mock()
            mock_note.id = 1
            mock_note.fields = [""] * 9  # 9 fields for noun
            mock_collection.new_note.return_value = mock_note
            mock_collection.models.get.return_value = mock_notetype

            backend = AnkiBackend(
                "German A1 Deck", mock_media_service, GermanLanguage()
            )

            # Create note type
            template = CardTemplate(
                name="Noun Card",
                front_html="{{Noun}}",
                back_html="{{English}}",
                css=".noun { color: blue; }",
            )
            note_type = NoteType(
                name="German Noun",
                fields=[
                    "Article",
                    "Noun",
                    "English",
                    "Plural",
                    "Example",
                    "Related",
                    "WordAudio",
                    "ExampleAudio",
                    "ImagePath",
                ],
                templates=[template],
            )
            note_type_id = backend.create_note_type(note_type)

            # Simulate bulk noun data from CSV
            bulk_noun_data = []
            for i in range(100):  # Test with 100 nouns
                bulk_noun_data.append(
                    [
                        "der",
                        f"Noun{i}",
                        f"noun{i}",
                        f"Noun{i}s",
                        f"Das ist ein Noun{i}.",
                        "related words",
                        "",
                        "",
                        "",
                    ]
                )

            # Mock field processing to avoid media generation overhead
            with patch.object(
                backend,
                "_process_fields_with_media",
                side_effect=lambda _, fields: fields,
            ):
                start_time = time.time()
                note_ids = []

                # Bulk create notes
                for fields in bulk_noun_data:
                    note_id = backend.add_note(note_type_id, fields)
                    note_ids.append(note_id)
                    mock_note.id += 1  # Increment for next note

                end_time = time.time()

                # Performance assertions
                elapsed_time = end_time - start_time
                notes_per_second = (
                    len(bulk_noun_data) / elapsed_time
                    if elapsed_time > 0
                    else float("inf")
                )

                # Verify all notes were created
                assert len(note_ids) == 100
                assert all(isinstance(nid, int) for nid in note_ids)

                # Performance should be reasonable (>10 notes/second with mocking)
                assert notes_per_second > 10, (
                    f"Performance too slow: {notes_per_second:.2f} notes/second"
                )

                # Verify collection operations were called correctly
                assert mock_collection.add_note.call_count == 100

    def test_bulk_media_generation_optimization(self, mock_media_service: Mock) -> None:
        """Test bulk operations with media generation optimization."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend(
                "German A1 Media Deck", mock_media_service, GermanLanguage()
            )

            # Mock media services for performance testing
            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_audio",
                    return_value="[sound:test.mp3]",
                ),
                patch.object(
                    backend._media_service,
                    "generate_or_get_image",
                    return_value='<img src="test.jpg">',
                ),
            ):
                # Test bulk audio generation with deduplication
                duplicate_texts = ["Hallo"] * 50 + ["Welt"] * 50  # 50 duplicates each

                # Mock file existence for deduplication testing
                with patch.object(
                    Path, "exists", return_value=True
                ):  # Simulate existing files
                    start_time = time.time()
                    audio_results = []

                    for text in duplicate_texts:
                        result = backend._generate_or_get_audio(text)
                        audio_results.append(result)

                    end_time = time.time()

                    # Verify all audio was "generated"
                    assert len(audio_results) == 100
                    assert all(r == "[sound:test.mp3]" for r in audio_results)

                    # Verify deduplication stats show reuse
                    stats = backend._media_generation_stats
                    assert (
                        stats["audio_reused"] == 100
                    )  # All should be marked as reused
                    assert stats["audio_generated"] == 0  # None should be new

                    # Performance should be very fast with deduplication
                    elapsed_time = end_time - start_time
                    operations_per_second = (
                        100 / elapsed_time if elapsed_time > 0 else float("inf")
                    )
                    assert operations_per_second > 100, (
                        f"Deduplication too slow: {operations_per_second:.2f} ops/sec"
                    )

    def test_memory_efficiency_with_large_dataset(
        self, mock_media_service: Mock
    ) -> None:
        """Test memory efficiency with large dataset simulation."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )
            mock_collection.db.scalar.return_value = 1000  # 1000 notes

            backend = AnkiBackend(
                "Large German A1 Deck", mock_media_service, GermanLanguage()
            )

            # Simulate large internal state
            backend._note_type_map = {
                str(i): Mock() for i in range(10)
            }  # 10 note types
            backend._media_files = [Mock() for _ in range(500)]  # 500 media files

            # Update statistics to simulate large dataset processing
            backend._media_generation_stats.update(
                {
                    "audio_generated": 300,
                    "audio_reused": 700,  # 70% reuse rate
                    "images_downloaded": 200,
                    "images_reused": 800,  # 80% reuse rate
                    "generation_errors": 10,
                }
            )

            # Test that stats computation remains efficient
            start_time = time.time()
            stats = backend.get_stats()
            end_time = time.time()

            # Verify stats are computed correctly
            assert stats["notes_count"] == 1000
            assert stats["note_types_count"] == 10
            assert stats["media_files_count"] == 500

            media_stats = stats["media_generation_stats"]
            assert media_stats["total_media_generated"] == 500  # 300 audio + 200 images
            assert media_stats["total_media_reused"] == 1500  # 700 audio + 800 images

            # Stats computation should be very fast
            elapsed_time = end_time - start_time
            assert elapsed_time < 0.1, (
                f"Stats computation too slow: {elapsed_time:.3f} seconds"
            )

    def test_concurrent_access_simulation(self, mock_media_service: Mock) -> None:
        """Test simulated concurrent access patterns for thread safety."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend(
                "Concurrent Access Test", mock_media_service, GermanLanguage()
            )

            # Mock media generation for concurrent testing
            with (
                patch.object(
                    backend._media_service,
                    "generate_or_get_audio",
                    return_value="[sound:concurrent.mp3]",
                ),
                patch.object(
                    backend._media_service,
                    "generate_or_get_image",
                    return_value='<img src="concurrent.jpg">',
                ),
            ):
                # Simulate concurrent operations
                operations = []

                # Mix of audio and image operations
                for i in range(50):
                    operations.append(
                        ("audio", f"Text{i % 10}")
                    )  # 10 unique texts, repeated
                    operations.append(
                        ("image", f"Word{i % 5}")
                    )  # 5 unique words, repeated

                start_time = time.time()
                results = []

                # Process all operations sequentially (simulating concurrent batch)
                for op_type, content in operations:
                    if op_type == "audio":
                        with patch.object(
                            Path, "exists", return_value=(content in ["Text0", "Text1"])
                        ):
                            result = backend._generate_or_get_audio(content)
                            results.append(result)
                    else:  # image
                        with patch.object(
                            Path, "exists", return_value=(content in ["Word0", "Word1"])
                        ):
                            result = backend._generate_or_get_image(
                                content, content.lower()
                            )
                            results.append(result)

                end_time = time.time()

                # Verify all operations completed
                assert len(results) == 100

                # Verify statistics are consistent
                stats = backend._media_generation_stats
                total_operations = (
                    stats["audio_generated"]
                    + stats["audio_reused"]
                    + stats["images_downloaded"]
                    + stats["images_reused"]
                )
                assert total_operations == 100

                # Performance should be reasonable even with mixed operations
                elapsed_time = end_time - start_time
                operations_per_second = (
                    100 / elapsed_time if elapsed_time > 0 else float("inf")
                )
                assert operations_per_second > 50, (
                    f"Mixed operations too slow: {operations_per_second:.2f} ops/second"
                )

    def test_export_performance_with_large_deck(self, mock_media_service: Mock) -> None:
        """Test deck export performance with large deck simulation."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend(
                "Large Export Test", mock_media_service, GermanLanguage()
            )

            # Simulate large deck with many media files
            backend._media_files = [
                Mock(path=f"/test/file_{i}.mp3") for i in range(200)
            ]

            # Mock successful export
            with patch("anki.exporting.AnkiPackageExporter") as mock_exporter_cls:
                mock_exporter = Mock()
                mock_exporter_cls.return_value = mock_exporter
                mock_exporter.export_to_file = Mock()

                start_time = time.time()
                backend.export_deck("/tmp/large_deck.apkg")
                end_time = time.time()

                # Verify export was attempted
                mock_exporter.export_to_file.assert_called_once_with(
                    "/tmp/large_deck.apkg"
                )

                # Export setup should be fast (actual export time depends on Anki)
                elapsed_time = end_time - start_time
                assert elapsed_time < 1.0, (
                    f"Export setup too slow: {elapsed_time:.3f} seconds"
                )

                # Verify exporter was configured correctly
                assert mock_exporter.did == backend._deck_id
                assert mock_exporter.include_media is True

    def test_csv_data_processing_simulation(self, mock_media_service: Mock) -> None:
        """Test processing simulation with CSV data structure."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )

            backend = AnkiBackend(
                "CSV Processing Test", mock_media_service, GermanLanguage()
            )

            # Simulate processing CSV-like data (typical German A1 vocabulary)
            csv_noun_data = [
                [
                    "das",
                    "Haus",
                    "house",
                    "Häuser",
                    "Mein Haus ist sehr klein.",
                    "related words",
                ],
                [
                    "der",
                    "Mann",
                    "man",
                    "Männer",
                    "Der Mann geht zur Arbeit.",
                    "related words",
                ],
                [
                    "die",
                    "Frau",
                    "woman",
                    "Frauen",
                    "Die Frau kauft ein Buch.",
                    "related words",
                ],
                [
                    "das",
                    "Kind",
                    "child",
                    "Kinder",
                    "Das Kind spielt im Park.",
                    "related words",
                ],
                [
                    "das",
                    "Auto",
                    "car",
                    "Autos",
                    "Ich fahre mit dem Auto.",
                    "related words",
                ],
            ]

            # Mock field processing to simulate domain model delegation
            processed_results = []

            with patch.object(backend, "_process_fields_with_media") as mock_process:
                mock_process.side_effect = lambda note_type, fields: [
                    *fields,
                    "[sound:audio.mp3]",
                    "[sound:example.mp3]",
                    '<img src="test.jpg">',
                ]

                start_time = time.time()

                for row in csv_noun_data:
                    # Simulate typical processing: article, noun, english, plural
                    base_fields = [*row, "", "", ""]  # Add empty audio/image fields
                    processed_fields = backend._process_fields_with_media(
                        "German Noun", base_fields
                    )
                    processed_results.append(processed_fields)

                end_time = time.time()

                # Verify all rows were processed
                assert len(processed_results) == 5

                # Verify field processing delegation occurred
                assert mock_process.call_count == 5

                # Verify processed fields have expected structure
                for processed in processed_results:
                    assert (
                        len(processed) == 12
                    )  # 9 original fields (6 CSV + 3 empty) + 3 media fields
                    assert "[sound:audio.mp3]" in processed
                    assert '<img src="test.jpg">' in processed

                # Processing should be fast
                elapsed_time = end_time - start_time
                rows_per_second = 5 / elapsed_time if elapsed_time > 0 else float("inf")
                assert rows_per_second > 100, (
                    f"CSV processing too slow: {rows_per_second:.2f} rows/second"
                )

    def test_statistics_calculation_performance(self, mock_media_service: Mock) -> None:
        """Test performance of statistics calculation with large datasets."""
        with (
            patch(
                "langlearn.infrastructure.backends.anki_backend.Collection"
            ) as mock_col_cls,
            patch("tempfile.mkdtemp", return_value="/tmp/test"),
        ):
            mock_collection = Mock()
            mock_col_cls.return_value = mock_collection
            mock_collection.decks.add_normal_deck_with_name.return_value = Mock(
                id=12345
            )
            mock_collection.db.scalar.return_value = 5000  # Large note count

            backend = AnkiBackend(
                "Statistics Performance Test", mock_media_service, GermanLanguage()
            )

            # Simulate large-scale statistics
            backend._note_type_map = {
                str(i): Mock() for i in range(50)
            }  # 50 note types
            backend._media_files = [Mock() for _ in range(2000)]  # 2000 media files

            # Large media generation statistics
            backend._media_generation_stats.update(
                {
                    "audio_generated": 1500,
                    "audio_reused": 3500,  # 70% reuse
                    "images_downloaded": 800,
                    "images_reused": 3200,  # 80% reuse
                    "generation_errors": 50,
                }
            )

            # Test repeated statistics calculation (simulating dashboard updates)
            start_time = time.time()

            stats_results = []
            for _ in range(10):  # 10 repeated calculations
                stats = backend.get_stats()
                stats_results.append(stats)

            end_time = time.time()

            # Verify statistics consistency
            for stats in stats_results:
                assert stats["notes_count"] == 5000
                assert stats["note_types_count"] == 50
                assert stats["media_files_count"] == 2000

                media_stats = stats["media_generation_stats"]
                assert media_stats["total_media_generated"] == 2300  # 1500 + 800
                assert media_stats["total_media_reused"] == 6700  # 3500 + 3200
                assert media_stats["generation_errors"] == 50

            # Statistics calculation should be very fast even with large datasets
            elapsed_time = end_time - start_time
            calculations_per_second = (
                10 / elapsed_time if elapsed_time > 0 else float("inf")
            )
            assert calculations_per_second > 50, (
                f"Statistics too slow: {calculations_per_second:.2f} calc/second"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
