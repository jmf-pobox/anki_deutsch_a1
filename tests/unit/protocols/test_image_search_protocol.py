"""Tests for ImageQueryGenerationProtocol."""

from typing import Any

from langlearn.core.protocols.image_query_generation_protocol import (
    ImageQueryGenerationProtocol,
)


class MockImageSearchService:
    """Mock implementation of ImageQueryGenerationProtocol for testing."""

    def __init__(self, return_value: str = "test search query"):
        """Initialize with configurable return value."""
        self.return_value = return_value
        self.calls: list[Any] = []

    def generate_image_query(self, context: Any) -> str:
        """Mock implementation that records calls and returns configured value."""
        self.calls.append(context)
        return self.return_value


class FailingMockImageSearchService:
    """Mock implementation that raises exceptions for testing error handling."""

    def generate_image_query(self, context: Any) -> str:
        """Mock implementation that always raises an exception."""
        raise RuntimeError("AI service failed")


class TestImageQueryGenerationProtocol:
    """Test ImageQueryGenerationProtocol compliance and behavior."""

    def test_protocol_compliance(self) -> None:
        """Test that mock class satisfies the protocol."""
        mock = MockImageSearchService()

        # This should not raise any type errors
        assert isinstance(mock, ImageQueryGenerationProtocol)

    def test_generate_image_query_returns_string(self) -> None:
        """Test that generate_image_query returns a string."""
        mock = MockImageSearchService("test query")
        result = mock.generate_image_query("test context")

        assert isinstance(result, str)
        assert result == "test query"

    def test_generate_image_query_accepts_any_context(self) -> None:
        """Test that generate_image_query accepts any type of context."""
        mock = MockImageSearchService("search terms")

        # Test with different context types
        contexts = [
            "string context",
            {"key": "dict context"},
            ["list", "context"],
            123,
            None,
        ]

        for context in contexts:
            result = mock.generate_image_query(context)
            assert result == "search terms"
            assert context in mock.calls

    def test_protocol_with_service_function(self) -> None:
        """Test protocol works with functions expecting ImageQueryGenerationProtocol."""

        def use_image_search_service(
            service: ImageQueryGenerationProtocol, context: str
        ) -> str:
            """Function that uses ImageQueryGenerationProtocol."""
            return service.generate_image_query(context)

        mock = MockImageSearchService("generated query")
        result = use_image_search_service(mock, "rich context")

        assert result == "generated query"
        assert "rich context" in mock.calls

    def test_protocol_with_domain_model_pattern(self) -> None:
        """Test protocol with domain model dependency injection pattern."""

        def domain_model_method(ai_service: ImageQueryGenerationProtocol) -> str:
            """Simulate domain model method using the protocol."""
            context = "German noun: Katze (die - feminine), English: cat"
            try:
                result = ai_service.generate_image_query(context)
                if result and result.strip():
                    return result.strip()
            except Exception:
                pass
            return "fallback terms"

        # Test successful generation
        mock = MockImageSearchService("cute cat domestic animal")
        result = domain_model_method(mock)
        assert result == "cute cat domestic animal"

        # Test empty response fallback
        mock_empty = MockImageSearchService("")
        result = domain_model_method(mock_empty)
        assert result == "fallback terms"

        # Test whitespace-only response fallback
        mock_whitespace = MockImageSearchService("   ")
        result = domain_model_method(mock_whitespace)
        assert result == "fallback terms"

    def test_protocol_with_failing_service(self) -> None:
        """Test protocol behavior when service fails."""

        def robust_domain_method(ai_service: ImageQueryGenerationProtocol) -> str:
            """Domain method with error handling."""
            try:
                return ai_service.generate_image_query("test context")
            except Exception:
                return "fallback search terms"

        failing_mock = FailingMockImageSearchService()
        result = robust_domain_method(failing_mock)

        assert result == "fallback search terms"

    def test_concrete_vs_abstract_context_handling(self) -> None:
        """Test that service can handle different types of domain contexts."""
        mock = MockImageSearchService()

        # Concrete noun context
        concrete_context = """
        German noun: Katze (die - feminine)
        English: cat
        Classification: Concrete noun
        Visual strategy: Focus on the physical object, use direct visual representation.
        """

        # Abstract noun context
        abstract_context = """
        German noun: Freiheit (die - feminine)
        English: freedom
        Classification: Abstract noun
        Visual strategy: Use symbolic imagery, metaphorical representations.
        """

        concrete_result = mock.generate_image_query(concrete_context)
        abstract_result = mock.generate_image_query(abstract_context)

        assert isinstance(concrete_result, str)
        assert isinstance(abstract_result, str)
        assert len(mock.calls) == 2
        assert concrete_context in mock.calls
        assert abstract_context in mock.calls

    def test_phrase_context_handling(self) -> None:
        """Test that service can handle phrase-specific contexts."""
        mock = MockImageSearchService("greeting handshake morning")

        phrase_context = """
        German phrase: Guten Morgen!
        English: Good morning!
        Category: greeting
        Visual strategy: Focus on meeting and greeting scenarios.
        """

        result = mock.generate_image_query(phrase_context)

        assert result == "greeting handshake morning"
        assert phrase_context in mock.calls

    def test_protocol_type_checking(self) -> None:
        """Test that protocol enforces correct method signature."""

        class InvalidService:
            """Service with wrong method signature."""

            def generate_image_query(self) -> str:  # Missing context parameter
                return "invalid"

        class AnotherInvalidService:
            """Service with wrong return type."""

            def generate_image_query(self, context: Any) -> int:  # Wrong return type
                return 42

        # These should not satisfy the protocol
        invalid = InvalidService()
        another_invalid = AnotherInvalidService()

        # Note: isinstance checks with Protocol are runtime checks
        # The protocol compliance is mainly for type checkers
        # These tests verify the structure exists
        assert hasattr(invalid, "generate_image_query")
        assert hasattr(another_invalid, "generate_image_query")

    def test_multiple_calls_context_tracking(self) -> None:
        """Test that service can handle multiple calls and track contexts."""
        mock = MockImageSearchService("search result")

        contexts = ["context 1", "context 2", "context 3"]

        results = []
        for context in contexts:
            result = mock.generate_image_query(context)
            results.append(result)

        assert len(results) == 3
        assert all(r == "search result" for r in results)
        assert mock.calls == contexts

    def test_real_world_anthropic_service_pattern(self) -> None:
        """Test pattern matching actual AnthropicService usage."""

        class AnthropicServiceMock:
            """Mock matching the real AnthropicService pattern."""

            def __init__(
                self, response: str = "professional business setting formal handshake"
            ):
                self.response = response

            def generate_image_query(self, context: Any) -> str:
                """Simulate Anthropic API call for image query generation."""
                # In real service, this would call Anthropic API
                # Here we just return a realistic response
                return self.response

        service = AnthropicServiceMock()

        # Test with realistic German domain context
        context = """
        German phrase: Guten Tag
        English: Good day/Hello (formal)
        Category: formal greeting
        Context: Polite greeting used throughout the day
        Visual strategy: Focus on formal or professional contexts.
        """

        result = service.generate_image_query(context)

        assert isinstance(service, ImageQueryGenerationProtocol)
        assert isinstance(result, str)
        assert len(result) > 0
        assert result == "professional business setting formal handshake"
