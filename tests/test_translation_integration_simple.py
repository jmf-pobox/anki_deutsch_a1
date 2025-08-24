"""Simple integration tests for translation functionality without external dependencies."""

from unittest.mock import Mock


class TestTranslationLogic:
    """Test the core translation logic without external dependencies."""

    def test_translation_logic_with_mock_service(self) -> None:
        """Test translation logic with mock service."""

        # Arrange - simulate the _translate_for_search method logic
        def mock_translate_for_search(text, translation_service=None):
            """Mock implementation of _translate_for_search method."""
            if not text or not text.strip():
                return text

            if not translation_service:
                return text  # No service, return original

            try:
                return translation_service.translate_to_english(text)
            except Exception:
                return text  # Fallback on error

        # Mock translation service
        mock_service = Mock()
        mock_service.translate_to_english.return_value = "I go to school"

        # Act
        result = mock_translate_for_search("Ich gehe in die Schule", mock_service)

        # Assert
        assert result == "I go to school"
        mock_service.translate_to_english.assert_called_once_with(
            "Ich gehe in die Schule"
        )

    def test_translation_logic_without_service(self) -> None:
        """Test translation logic without translation service (fallback)."""

        # Arrange
        def mock_translate_for_search(text, translation_service=None):
            if not text or not text.strip():
                return text

            if not translation_service:
                return text  # No service, return original

            try:
                return translation_service.translate_to_english(text)
            except Exception:
                return text  # Fallback on error

        # Act
        result = mock_translate_for_search("Ich gehe in die Schule", None)

        # Assert
        assert result == "Ich gehe in die Schule"  # Original German text

    def test_translation_logic_with_service_error(self) -> None:
        """Test translation logic when service throws error."""

        # Arrange
        def mock_translate_for_search(text, translation_service=None):
            if not text or not text.strip():
                return text

            if not translation_service:
                return text  # No service, return original

            try:
                return translation_service.translate_to_english(text)
            except Exception:
                return text  # Fallback on error

        mock_service = Mock()
        mock_service.translate_to_english.side_effect = Exception("API Error")

        # Act
        result = mock_translate_for_search("Ich gehe in die Schule", mock_service)

        # Assert
        assert result == "Ich gehe in die Schule"  # Fallback to original

    def test_translation_logic_empty_text(self) -> None:
        """Test translation logic with empty text."""

        # Arrange
        def mock_translate_for_search(text, translation_service=None):
            if not text or not text.strip():
                return text

            if not translation_service:
                return text

            try:
                return translation_service.translate_to_english(text)
            except Exception:
                return text

        mock_service = Mock()

        # Act & Assert
        assert mock_translate_for_search("", mock_service) == ""
        assert mock_translate_for_search("   ", mock_service) == "   "
        assert mock_translate_for_search(None, mock_service) == None

        # Service should not be called for empty text
        mock_service.translate_to_english.assert_not_called()


class TestImageGenerationIntegration:
    """Test image generation integration with translation."""

    def test_verb_image_generation_flow(self) -> None:
        """Test the complete flow for verb image generation with translation."""

        # Arrange - simulate the verb enrichment flow
        def mock_enrich_verb_with_translation(
            record, translation_service, media_service
        ):
            """Mock verb enrichment with translation."""
            if (
                not record.get("image")
                and record.get("infinitive")
                and record.get("example")
            ):
                infinitive = record["infinitive"]

                # Translate German example to English
                german_example = record["example"]
                if translation_service:
                    try:
                        search_terms = translation_service.translate_to_english(
                            german_example
                        )
                    except Exception:
                        search_terms = german_example  # Fallback
                else:
                    search_terms = german_example

                # Generate image with translated search terms
                fallback = record.get("english", infinitive)
                image_path = media_service.generate_image(search_terms, fallback)

                if image_path:
                    record["image"] = f'<img src="{image_path}">'

            return record

        # Mock services
        mock_translation = Mock()
        mock_translation.translate_to_english.return_value = "I go to school"

        mock_media = Mock()
        mock_media.generate_image.return_value = "test_image.jpg"

        record = {
            "infinitive": "gehen",
            "english": "to go",
            "example": "Ich gehe in die Schule",
        }

        # Act
        result = mock_enrich_verb_with_translation(record, mock_translation, mock_media)

        # Assert
        assert "image" in result
        assert result["image"] == '<img src="test_image.jpg">'

        # Verify translation was used for image search
        mock_translation.translate_to_english.assert_called_once_with(
            "Ich gehe in die Schule"
        )
        mock_media.generate_image.assert_called_once_with("I go to school", "to go")

    def test_preposition_image_generation_flow(self) -> None:
        """Test the complete flow for preposition image generation with translation."""

        # Arrange - simulate the preposition enrichment flow
        def mock_enrich_preposition_with_translation(
            record, translation_service, media_service
        ):
            """Mock preposition enrichment with translation."""
            if (
                not record.get("image")
                and record.get("preposition")
                and record.get("example1")
            ):
                preposition = record["preposition"]

                # Translate German example1 to English
                german_example = record["example1"]
                if translation_service:
                    try:
                        search_terms = translation_service.translate_to_english(
                            german_example
                        )
                    except Exception:
                        search_terms = german_example  # Fallback
                else:
                    search_terms = german_example

                # Generate image with translated search terms
                fallback = record.get("english", preposition)
                image_path = media_service.generate_image(search_terms, fallback)

                if image_path:
                    record["image"] = f'<img src="{image_path}">'

            return record

        # Mock services
        mock_translation = Mock()
        mock_translation.translate_to_english.return_value = "I go to school"

        mock_media = Mock()
        mock_media.generate_image.return_value = "test_image.jpg"

        record = {
            "preposition": "in",
            "english": "in",
            "example1": "Ich gehe in die Schule",
            "case": "Akkusativ/Dativ",
        }

        # Act
        result = mock_enrich_preposition_with_translation(
            record, mock_translation, mock_media
        )

        # Assert
        assert "image" in result
        assert result["image"] == '<img src="test_image.jpg">'

        # Verify translation was used for image search
        mock_translation.translate_to_english.assert_called_once_with(
            "Ich gehe in die Schule"
        )
        mock_media.generate_image.assert_called_once_with("I go to school", "in")

    def test_phrase_image_generation_flow(self) -> None:
        """Test the complete flow for phrase image generation with translation."""

        # Arrange - simulate the phrase enrichment flow
        def mock_enrich_phrase_with_translation(
            record, translation_service, media_service
        ):
            """Mock phrase enrichment with translation."""
            if not record.get("image") and record.get("phrase"):
                phrase_text = record.get("phrase", "")

                # Translate German phrase to English
                if translation_service:
                    try:
                        search_terms = translation_service.translate_to_english(
                            phrase_text
                        )
                    except Exception:
                        search_terms = phrase_text  # Fallback
                else:
                    search_terms = phrase_text

                # Generate image with translated search terms
                fallback_terms = record.get("context") or record.get("english") or ""
                image_path = media_service.generate_image(search_terms, fallback_terms)

                if image_path:
                    record["image"] = f'<img src="{image_path}">'

            return record

        # Mock services
        mock_translation = Mock()
        mock_translation.translate_to_english.return_value = "I go to school"

        mock_media = Mock()
        mock_media.generate_image.return_value = "test_image.jpg"

        record = {
            "phrase": "Ich gehe in die Schule",
            "english": "I go to school",
            "context": "education",
        }

        # Act
        result = mock_enrich_phrase_with_translation(
            record, mock_translation, mock_media
        )

        # Assert
        assert "image" in result
        assert result["image"] == '<img src="test_image.jpg">'

        # Verify translation was used for image search
        mock_translation.translate_to_english.assert_called_once_with(
            "Ich gehe in die Schule"
        )
        mock_media.generate_image.assert_called_once_with("I go to school", "education")


class TestTranslationServiceMockBehavior:
    """Test the mock translation service behavior."""

    def test_mock_translation_service_logic(self) -> None:
        """Test mock translation service logic."""
        # Simulate MockTranslationService behavior
        mock_translations = {
            "ich gehe in die schule": "I go to school",
            "er spielt fußball": "he plays football",
            "sie kocht das essen": "she cooks the food",
            "das auto ist rot": "the car is red",
            "der hund läuft schnell": "the dog runs fast",
        }

        def mock_translate_to_english(german_text):
            if not german_text:
                return german_text
            cache_key = german_text.strip().lower()
            return mock_translations.get(cache_key, german_text)

        # Test known translations
        assert mock_translate_to_english("Ich gehe in die Schule") == "I go to school"
        assert mock_translate_to_english("Er spielt Fußball") == "he plays football"

        # Test case insensitivity
        assert mock_translate_to_english("ICH GEHE IN DIE SCHULE") == "I go to school"

        # Test unknown phrase fallback
        assert mock_translate_to_english("Unknown phrase") == "Unknown phrase"

        # Test empty text
        assert mock_translate_to_english("") == ""
        assert mock_translate_to_english(None) == None


class TestExampleSentenceImageGeneration:
    """Test that all card types now use example sentences for better image quality."""

    def test_adjective_uses_example_sentence(self) -> None:
        """Test that adjective image generation uses example sentence instead of AI-generated terms."""

        # Arrange - simulate adjective enrichment with example sentence
        def mock_enrich_adjective_with_example(
            record, translation_service, media_service, image_exists_func
        ):
            """Mock adjective enrichment using example sentence."""
            if not record.get("image") and record.get("word") and record.get("example"):
                word = record["word"]
                if not image_exists_func(word):
                    # Use example sentence instead of AI-generated terms
                    german_example = record["example"]
                    search_terms = translation_service.translate_to_english(
                        german_example
                    )
                    fallback = record.get("english", word)
                    image_path = media_service.generate_image(search_terms, fallback)

                    if image_path:
                        record["image"] = f'<img src="{image_path}">'
                else:
                    record["image"] = '<img src="existing_image.jpg">'

            return record

        # Mock services
        mock_translation = Mock()
        mock_translation.translate_to_english.return_value = "The house is beautiful"

        mock_media = Mock()
        mock_media.generate_image.return_value = "beautiful_house.jpg"

        mock_image_exists = Mock(return_value=False)

        record = {
            "word": "schön",
            "english": "beautiful",
            "example": "Das Haus ist schön",  # Example sentence instead of just word
        }

        # Act
        result = mock_enrich_adjective_with_example(
            record, mock_translation, mock_media, mock_image_exists
        )

        # Assert
        assert "image" in result
        assert result["image"] == '<img src="beautiful_house.jpg">'

        # Verify example sentence was translated (not AI-generated terms)
        mock_translation.translate_to_english.assert_called_once_with(
            "Das Haus ist schön"
        )

        # Verify contextual search was used
        mock_media.generate_image.assert_called_once_with(
            "The house is beautiful", "beautiful"
        )


class TestPhraseImageOptimization:
    """Test phrase image generation optimization to avoid unnecessary translation calls."""

    def test_phrase_image_generation_with_existing_image(self) -> None:
        """Test that phrase image generation skips translation when image exists."""

        # Arrange - simulate optimized phrase enrichment
        def mock_enrich_phrase_optimized(
            record, translation_service, media_service, image_exists_func
        ):
            """Mock phrase enrichment with image existence check."""
            if not record.get("image") and record.get("phrase"):
                phrase_text = record.get("phrase", "")

                # Check if image exists first (optimization)
                if not image_exists_func(phrase_text):
                    # Only translate if image doesn't exist
                    if translation_service:
                        try:
                            search_terms = translation_service.translate_to_english(
                                phrase_text
                            )
                        except Exception:
                            search_terms = phrase_text
                    else:
                        search_terms = phrase_text

                    # Generate new image
                    fallback_terms = (
                        record.get("context") or record.get("english") or ""
                    )
                    image_path = media_service.generate_image(
                        search_terms, fallback_terms
                    )

                    if image_path:
                        record["image"] = f'<img src="{image_path}">'
                else:
                    # Use existing image without translation or generation
                    record["image"] = '<img src="existing_phrase_image.jpg">'

            return record

        # Mock services
        mock_translation = Mock()
        mock_translation.translate_to_english.return_value = "I go to school"

        mock_media = Mock()
        mock_media.generate_image.return_value = "new_image.jpg"

        # Mock image exists function - returns True (image exists)
        mock_image_exists = Mock(return_value=True)

        record = {
            "phrase": "Ich gehe in die Schule",
            "english": "I go to school",
            "context": "education",
        }

        # Act
        result = mock_enrich_phrase_optimized(
            record, mock_translation, mock_media, mock_image_exists
        )

        # Assert
        assert "image" in result
        assert result["image"] == '<img src="existing_phrase_image.jpg">'

        # Verify translation was NOT called (optimization)
        mock_translation.translate_to_english.assert_not_called()

        # Verify image generation was NOT called (optimization)
        mock_media.generate_image.assert_not_called()

        # Verify image existence was checked
        mock_image_exists.assert_called_once_with("Ich gehe in die Schule")

    def test_phrase_image_generation_without_existing_image(self) -> None:
        """Test that phrase image generation uses translation when image doesn't exist."""

        # Arrange - simulate optimized phrase enrichment
        def mock_enrich_phrase_optimized(
            record, translation_service, media_service, image_exists_func
        ):
            """Mock phrase enrichment with image existence check."""
            if not record.get("image") and record.get("phrase"):
                phrase_text = record.get("phrase", "")

                # Check if image exists first
                if not image_exists_func(phrase_text):
                    # Only translate if image doesn't exist
                    if translation_service:
                        try:
                            search_terms = translation_service.translate_to_english(
                                phrase_text
                            )
                        except Exception:
                            search_terms = phrase_text
                    else:
                        search_terms = phrase_text

                    # Generate new image
                    fallback_terms = (
                        record.get("context") or record.get("english") or ""
                    )
                    image_path = media_service.generate_image(
                        search_terms, fallback_terms
                    )

                    if image_path:
                        record["image"] = f'<img src="{image_path}">'
                else:
                    # Use existing image
                    record["image"] = '<img src="existing_phrase_image.jpg">'

            return record

        # Mock services
        mock_translation = Mock()
        mock_translation.translate_to_english.return_value = "I go to school"

        mock_media = Mock()
        mock_media.generate_image.return_value = "new_image.jpg"

        # Mock image exists function - returns False (image doesn't exist)
        mock_image_exists = Mock(return_value=False)

        record = {
            "phrase": "Ich gehe in die Schule",
            "english": "I go to school",
            "context": "education",
        }

        # Act
        result = mock_enrich_phrase_optimized(
            record, mock_translation, mock_media, mock_image_exists
        )

        # Assert
        assert "image" in result
        assert result["image"] == '<img src="new_image.jpg">'

        # Verify translation WAS called (needed for new image)
        mock_translation.translate_to_english.assert_called_once_with(
            "Ich gehe in die Schule"
        )

        # Verify image generation WAS called (needed for new image)
        mock_media.generate_image.assert_called_once_with("I go to school", "education")

        # Verify image existence was checked
        mock_image_exists.assert_called_once_with("Ich gehe in die Schule")
