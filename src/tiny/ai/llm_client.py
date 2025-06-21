"""Simple LLM client using LiteLLM."""

import litellm

from tiny.config import TinyConfig
from tiny.logging import get_logger

logger = get_logger("ai.llm_client")


class LLMClient:
    """Simple client for interacting with LLMs via LiteLLM."""

    def __init__(self, config: TinyConfig):
        """Initialize the LLM client."""
        self.config = config
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        logger.debug(
            f"LLMClient initialized with model: {self.model}, temperature: {self.temperature}, max_tokens: {self.max_tokens}"
        )

    def generate(self, user_prompt: str, system_prompt: str | None = None) -> str:
        """
        Generate text using LiteLLM.

        Args:
            user_prompt: The user prompt to send to the LLM
            system_prompt: Optional system prompt to provide context/instructions

        Returns:
            Raw string response from the LLM
        """
        logger.debug(
            f"Generating response with model: {self.model}, prompt length: {len(user_prompt)}"
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            logger.debug(f"Added system prompt (length: {len(system_prompt)})")
        messages.append({"role": "user", "content": user_prompt})

        logger.info(f"Generating response with {self.model}...")

        try:
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
                response_text = response.choices[0].message.content.strip()
                logger.info(
                    f"Successfully generated response (length: {len(response_text)})"
                )
                logger.debug(f"Response preview: {response_text[:100]}...")
                return response_text
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
