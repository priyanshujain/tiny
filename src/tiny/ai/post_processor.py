"""Post processor for converting notes to posts."""

import json
from dataclasses import dataclass

from tiny.ai.llm_client import LLMClient
from tiny.ai.prompts import get_style_examples
from tiny.logging import get_logger

logger = get_logger("ai.post_processor")


# System and user prompt constants
SYSTEM_PROMPT = """You are an expert content creator who specializes in converting raw notes into engaging blog posts. 
Your goal is to transform informal notes into well-structured, readable content while maintaining the original ideas and insights.
Always return your response as valid JSON with 'title' and 'content' fields."""

USER_PROMPT_TEMPLATE = """Please convert the following notes into a well-structured blog post.

Style Examples:
{style_examples}

Notes to convert:
{notes}

Return as JSON with 'title' and 'content' fields."""


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
        logger.debug("PostProcessor initialized")

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
        logger.debug(f"Processing note (length: {len(note_content)})")
        logger.info("Processing note with AI...")

        style_examples = get_style_examples()
        logger.debug(f"Retrieved {len(style_examples)} style examples")

        user_prompt = USER_PROMPT_TEMPLATE.format(
            notes=note_content, style_examples=style_examples
        )
        logger.debug(f"Built user prompt (length: {len(user_prompt)})")

        try:
            response = self.llm_client.generate(user_prompt, SYSTEM_PROMPT)
            logger.debug(f"AI response received (length: {len(response)})")

            post_data = self._parse_response(response)

            result = PostContent(title=post_data["title"], content=post_data["content"])
            logger.info(f"Successfully processed note into post: '{result.title}'")
            return result

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
        logger.debug("Parsing AI response as JSON")

        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
                logger.debug("Removed JSON code block prefix")
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
                logger.debug("Removed JSON code block suffix")
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)
            logger.debug(f"Successfully parsed JSON with keys: {list(data.keys())}")

            if "title" not in data or "content" not in data:
                logger.error(
                    f"Response missing required fields. Available fields: {list(data.keys())}"
                )
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
