"""Post processor for converting notes to posts."""

import json
import logging
from dataclasses import dataclass

from tiny.ai.llm_client import LLMClient
from tiny.ai.prompts import POST_CONVERSION_PROMPT, get_style_examples


logger = logging.getLogger(__name__)


@dataclass
class PostContent:
    """Simple post content with title and content only."""

    title: str
    content: str


class PostProcessor:
    """Orchestrates the conversion of notes to posts using AI."""

    def __init__(self, llm_client: LLMClient):
        """Initialize the post processor."""
        self.llm_client = llm_client

    def process_note(self, note_content: str) -> PostContent:
        """
        Process a note and convert it to a post.

        Args:
            note_content: Raw note content to process

        Returns:
            PostContent object with title and content

        Raises:
            ValueError: If the AI response cannot be parsed
            Exception: If AI generation fails
        """
        logger.info("Processing note with AI...")

        # Build the full prompt with style examples
        style_examples = get_style_examples()
        full_prompt = POST_CONVERSION_PROMPT.format(
            notes=note_content, style_examples=style_examples
        )

        try:
            # Call the LLM
            response = self.llm_client.generate(full_prompt)
            logger.debug(f"AI response: {response}")

            # Parse the JSON response
            post_data = self._parse_response(response)

            # Create and return PostContent (ignoring date)
            return PostContent(title=post_data["title"], content=post_data["content"])

        except Exception as e:
            logger.error(f"Failed to process note: {e}")
            raise

    def _parse_response(self, response: str) -> dict:
        """
        Parse the AI response and extract post data.

        Args:
            response: Raw AI response

        Returns:
            Dictionary with title, content, and date

        Raises:
            ValueError: If response cannot be parsed as valid JSON
        """
        try:
            # Clean up the response - remove any markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            # Parse JSON
            data = json.loads(cleaned_response)

            # Validate required fields
            if "title" not in data or "content" not in data:
                raise ValueError("Response missing required fields: title or content")

            logger.info(f"Successfully parsed post: '{data['title']}'")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            raise ValueError(f"Failed to parse AI response: {e}")
