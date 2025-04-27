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
    log_dir / "anthropic.log", maxBytes=1024 * 1024, backupCount=5  # 1MB
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

    def __init__(self) -> None:
        """Initialize the service with API credentials.

        Raises:
            ValueError: If the API key cannot be found in environment or keyring
        """
        # Try to get API key from environment first
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        # Fall back to keyring if not in environment
        if not api_key:
            api_key = keyring.get_password("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("Key ANTHROPIC_API_KEY not found in system keyring")

        self.api_key = api_key
        self.model = "claude-3-7-sonnet-20250219"  # Updated to current model
        self.client = Anthropic(api_key=self.api_key)
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

    def generate_pexels_query(self, model: Any) -> str:
        """Generate a Pexels query for the given model."""
        prompt = f"""You are a helpful assistant that generates search queries
for finding relevant images.
Given a German word '{model.word}' meaning '{model.english}' with example
'{model.example}',
generate a short, specific Pexels search query in English that would find
a relevant image.

Guidelines:
- Keep the query between 2-4 words
- Focus on concrete, visual aspects
- Include size/scale descriptors when relevant
- Use common synonyms if helpful
- Ensure query relates directly to the word meaning and example

Output only the search query, nothing else."""

        try:
            response = self._generate_response(
                prompt,
                max_tokens=50,  # Reduced since we only need a short query
                temperature=0.3,  # Lower temperature for more consistent results
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating Pexels query: {e}")
            raise
