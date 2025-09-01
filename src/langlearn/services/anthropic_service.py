"""Service for interacting with Anthropic's Claude API."""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import keyring
from anthropic import Anthropic

if TYPE_CHECKING:
    from anthropic.types import Message

from langlearn.models.adjective import Adjective

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Add file handler for anthropic.log
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "anthropic.log",
    maxBytes=1024 * 1024,
    backupCount=5,  # 1MB
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)


class AnthropicService:
    """Service for generating Pexels search queries using Anthropic's Claude API."""

    client: Anthropic | None

    def __init__(self) -> None:
        """Initialize the service with API credentials.

        Raises:
            ValueError: If the API key cannot be found in environment or keyring
        """
        # Try to get API key from environment first (for CI/CD)
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        # Fall back to keyring if environment variable not set at all
        if api_key is None:
            api_key = keyring.get_password("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY")

        # Allow empty API key in unit test environments (will be mocked)
        from langlearn.utils.environment import is_test_environment

        unit_test_env = is_test_environment(api_key)
        if not api_key and not unit_test_env:
            raise ValueError(
                "Key ANTHROPIC_API_KEY not found in environment or keyring"
            )

        self.api_key = api_key
        self.model = "claude-3-7-sonnet-20250219"  # Updated to current model

        # Only create real client if we have a valid API key and not in unit tests
        if self.api_key and not unit_test_env:
            self.client = Anthropic(api_key=self.api_key)
        else:
            # In unit tests or with empty keys, client will be mocked (None)
            self.client = None

        logger.debug(f"Initialized AnthropicService with model: {self.model}")

    def _generate_response(
        self, prompt: str, max_tokens: int = 100, temperature: float = 0.7
    ) -> str:
        """Generate a response from the Anthropic API.

        Args:
            prompt: The prompt to send to the API
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness in the response (0.0-1.0)

        Returns:
            str: The generated response
        """
        try:
            # Handle case where client is None (test environment)
            if self.client is None:
                raise RuntimeError(
                    "AnthropicService client not initialized - in test environment"
                )

            response: Message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            # The response content is a list of content blocks, each with a type
            # and text
            if response.content and len(response.content) > 0:
                content_block = response.content[0]
                if hasattr(content_block, "text"):
                    return str(content_block.text)
                return str(content_block)
            return ""
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            raise

    def _extract_key_data(self, model: Any) -> str:
        """Extract key data from a model for prompt generation.

        Args:
            model: The model to extract data from

        Returns:
            str: Key data from the model
        """
        try:
            if isinstance(model, Adjective):
                return (
                    f"Word: {model.word}\n"
                    f"English: {model.english}\n"
                    f"Example: {model.example}"
                )
            return str(model)
        except Exception as e:
            logger.error("Error extracting key data: %s", str(e))
            return str(model)

    def generate_translation(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.1,
    ) -> str:
        """Generate a translation using the Anthropic API.

        Args:
            prompt: The translation prompt to send to the API
            max_tokens: Maximum tokens for the response
            temperature: Temperature setting for response consistency

        Returns:
            The generated translation text

        Raises:
            Exception: If the API call fails
        """
        try:
            response = self._generate_response(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating translation: {e}")
            raise

    def generate_pexels_query(self, context: Any) -> str:
        """Generate a Pexels query from rich domain expertise context.
        
        Args:
            context: Rich context string from domain model's _build_search_context()
                    method containing German linguistic expertise and visualization guidance.
        
        Returns:
            Search query string suitable for Pexels API.
        """
        prompt = f"""You are a helpful assistant that generates search queries for finding relevant images.

{context}

Based on the rich context provided above, generate a concise Pexels search query (2-5 words) that captures the key visual concept. Follow the visualization strategy guidance provided and focus on terms that photographers would use to tag their images.

Output only the search query, nothing else."""

        try:
            response = self._generate_response(
                prompt,
                max_tokens=75,  # Increased slightly for context-based queries
                temperature=0.3,  # Lower temperature for more consistent results
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating Pexels query: {e}")
            raise
