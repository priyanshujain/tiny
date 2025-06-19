"""LLM client for blog post generation using LiteLLM."""

import json
import logging

import litellm
from pydantic import BaseModel

from tiny.config import TinyConfig
from tiny.ai.prompts import BLOG_CONVERSION_PROMPT, get_style_examples


logger = logging.getLogger(__name__)


class BlogContent(BaseModel):
    """Blog content data model."""

    title: str
    content: str
    date: str


class LLMClient:
    """Client for interacting with LLMs via LiteLLM."""

    def __init__(self, config: TinyConfig):
        """Initialize the LLM client."""
        self.config = config
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

    def generate_blog_post(self, notes: str) -> BlogContent:
        """
        Generate a blog post from notes using LiteLLM.

        Args:
            notes: Raw notes content

        Returns:
            BlogContent with title, content, and date
        """
        # Get style examples
        style_examples = get_style_examples()

        # Create the prompt
        prompt = BLOG_CONVERSION_PROMPT.format(
            notes=notes, style_examples=style_examples
        )

        # Create messages
        messages = [
            {
                "role": "system",
                "content": "You are an expert content editor who specializes in converting raw notes into polished blog posts while maintaining the author's authentic voice and style.",
            },
            {"role": "user", "content": prompt},
        ]

        # Generate response
        logger.info(f"Generating blog post with {self.model}...")
        response = litellm.completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Parse the response
        response_text = response.choices[0].message.content.strip()

        # Handle potential markdown code blocks
        if response_text.startswith("```json"):
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        # Parse JSON response
        parsed_response = json.loads(response_text)

        # Validate required fields
        if not all(key in parsed_response for key in ["title", "content", "date"]):
            raise ValueError("Response missing required fields: title, content, date")

        blog_content = BlogContent(
            title=parsed_response["title"],
            content=parsed_response["content"],
            date=parsed_response["date"],
        )

        logger.info(f"Successfully generated blog post: {blog_content.title}")
        return blog_content
