"""Simple LLM client using LiteLLM."""

from typing import Any, Optional, override

from langchain.callbacks.manager import Callbacks
from langchain.schema import LLMResult
from langchain_litellm import ChatLiteLLM

from tiny.config import TinyConfig
from tiny.logging import get_logger

logger = get_logger("ai.llm_client")


class CustomChatLiteLLM(ChatLiteLLM):
    def _fix_tool_choice(self, kwargs: dict) -> dict:
        if kwargs.get("tool_choice") == "any":
            kwargs["tool_choice"] = "auto"
        return kwargs

    @override
    def generate(
        self,
        messages: list,
        stop: Optional[list[str]] = None,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> LLMResult:
        kwargs = self._fix_tool_choice(kwargs)
        return super().generate(messages, stop=stop, callbacks=callbacks, **kwargs)

    @override
    def invoke(self, input, config=None, **kwargs: Any) -> Any:
        kwargs = self._fix_tool_choice(kwargs)
        return super().invoke(input, config=config, **kwargs)

    @override
    async def ainvoke(self, input, config=None, **kwargs: Any) -> Any:
        kwargs = self._fix_tool_choice(kwargs)
        return await super().ainvoke(input, config=config, **kwargs)

    @override
    def stream(self, input, config=None, **kwargs: Any) -> Any:
        kwargs = self._fix_tool_choice(kwargs)
        return super().stream(input, config=config, **kwargs)

    @override
    async def astream(self, input, config=None, **kwargs: Any) -> Any:
        kwargs = self._fix_tool_choice(kwargs)
        return super().astream(input, config=config, **kwargs)

    @override
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        kwargs = self._fix_tool_choice(kwargs)
        return super().__call__(*args, **kwargs)


class LLMClient:
    """Simple client for interacting with LLMs via LiteLLM."""

    def __init__(self, config: TinyConfig):
        """Initialize the LLM client."""
        self.config = config
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

        self.client = CustomChatLiteLLM(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=False,
        )

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

        if self.model == "test":
            logger.info("Using test mode - returning mock response")
            return f"Test response for prompt: {user_prompt[:50]}..."
        else:
            response = self.client.generate(
                messages=messages,
                stop=None,
                callbacks=None,
            )

            try:
                if not response.generations or not response.generations[0]:
                    raise ValueError("LLM returned empty generations")

                generation = response.generations[0][0]
                response_text = generation.text.strip() if generation.text else ""

                if not response_text:
                    logger.warning("LLM returned empty response text")

                logger.info(
                    f"Successfully generated response ({len(response_text)} chars)"
                )
                return response_text

            except (IndexError, AttributeError) as e:
                logger.error(f"Failed to parse LLM response structure: {e}")
                raise ValueError(f"Invalid LLM response format: {e}") from e
