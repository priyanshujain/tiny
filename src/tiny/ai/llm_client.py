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

    def generate(self, user_prompt: str, system_prompt: str | None = None) -> str:
        """
        Generate text using LiteLLM.

        Args:
            user_prompt: The user prompt to send to the LLM
            system_prompt: Optional system prompt to provide context/instructions

        Returns:
            Raw string response from the LLM
        """
        # Create messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        # Generate response
        logger.info(f"Generating response with {self.model}...")

        # Handle test mode
        if self.model == "test":
            logger.info("Using test mode - returning mock response")
            return f"Test response for prompt: {user_prompt[:50]}..."
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
