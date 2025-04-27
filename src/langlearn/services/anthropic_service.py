"""Service for generating Pexels search queries using Anthropic's Claude API."""

import logging
import logging.handlers
from pathlib import Path
from typing import cast

import anthropic
import keyring
from anthropic.types import ContentBlock, Message, TextBlock
from pydantic import BaseModel

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
    """Service for interacting with Anthropic's Claude API to generate Pexels search queries."""

    def __init__(self) -> None:
        """Initialize the Anthropic service with API key from environment or keyring."""
        key = "ANTHROPIC_API_KEY"
        api_key = keyring.get_password(key, key)
        if not api_key:
            raise ValueError(f"Key {key} not found in system keyring")

        # Log the first few characters of the API key for debugging
        if api_key:
            logger.debug("API key prefix: %s...", api_key[:10])
            logger.debug("API key length: %d", len(api_key))

        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_pexels_query(self, model: BaseModel) -> str:
        """
        Generate a Pexels search query based on the given Pydantic model.

        Args:
            model: A Pydantic model instance to generate a query for

        Returns:
            str: A search query suitable for Pexels API

        Raises:
            ValueError: If the model type is not supported or no response received
        """
        # Get the model's class name for type-specific handling
        model_type = model.__class__.__name__

        # Create a prompt based on the model type
        prompt = self._create_prompt(model, model_type)
        logger.info("Generated prompt for %s: %s", model_type, prompt)

        # Get the response from Claude
        response: Message = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=100,
            temperature=0.7,
            system="You are a helpful assistant that generates search queries for the Pexels image API.",
            messages=[{"role": "user", "content": prompt}],
        )

        # Log the response for debugging
        logger.info("Received response: %s", response)

        # Extract and clean the query
        if not response.content:
            raise ValueError("No content received from Claude")

        # Handle both TextBlock and dict response types
        content: ContentBlock = response.content[0]
        if isinstance(content, TextBlock):
            query = content.text.strip()
        elif isinstance(content, dict) and "text" in content:
            query = cast("str", content["text"]).strip()
        else:
            raise ValueError(f"Unexpected content type: {type(content)}")

        logger.info("Extracted query: %s", query)
        return query

    def _create_prompt(self, model: BaseModel, model_type: str) -> str:
        """
        Create a prompt for Claude based on the model type and data.

        Args:
            model: The Pydantic model instance
            model_type: The name of the model class

        Returns:
            str: A formatted prompt for Claude
        """
        # Get model fields and their values
        model_data = model.model_dump()

        # Extract key fields that are most relevant for image search
        search_relevant_fields = ["word", "noun", "verb", "english", "example"]
        key_data = {
            k: v for k, v in model_data.items() if k in search_relevant_fields and v
        }

        # Create a more detailed prompt focusing on specific, visual elements
        base_prompt = (
            "You are helping to generate search queries for finding high-quality, relevant images on Pexels. "
            "Given a German language learning model, generate a detailed, specific search query that would return "
            "appropriate, visually clear images for the word or concept.\n\n"
            "Guidelines for the search query:\n"
            "1. Be specific and descriptive - include adjectives, settings, and context\n"
            "2. Focus on concrete, visual elements that would appear in photographs\n"
            "3. If the concept is abstract, suggest imagery that clearly symbolizes or represents it\n"
            "4. Include relevant context from the example sentence\n"
            "5. Use natural language that would return high-quality stock photos\n"
            "6. Avoid generic or vague terms\n"
            "7. Consider cultural context and appropriateness\n\n"
            f"Model data: {key_data}\n\n"
            "Generate a detailed, specific search query that would return high-quality, relevant images. "
            "The query should be in English and focus on concrete, visual elements. "
            "Return ONLY the search query, nothing else."
        )

        return base_prompt
