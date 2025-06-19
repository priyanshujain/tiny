"""Simple LLM client using LiteLLM."""

import logging

import litellm

from tiny.config import TinyConfig


logger = logging.getLogger(__name__)


class LLMClient:
    """Simple client for interacting with LLMs via LiteLLM."""

    def __init__(self, config: TinyConfig):
        """Initialize the LLM client."""
        self.config = config
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

    def generate(self, prompt: str) -> str:
        """
        Generate text using LiteLLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            Raw string response from the LLM
        """
        # Create messages
        messages = [
            {"role": "user", "content": prompt},
        ]

        # Generate response
        logger.info(f"Generating response with {self.model}...")

        # Handle test mode
        if self.model == "test":
            logger.info("Using test mode - returning mock response")
            return f"Test response for prompt: {prompt[:50]}..."
        else:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            # Return the raw response
            response_text = response.choices[0].message.content.strip()
            logger.info("Successfully generated response")
            return response_text
