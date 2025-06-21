"""Post processor for converting notes to posts."""

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from tiny.ai.llm_client import LLMClient
from tiny.logging import get_logger

logger = get_logger("ai.post_processor")


# System and user prompt constants
POST_SYSTEM_PROMPT = """
You are a ghostwriter who specializes in converting raw notes into engaging posts. You are writing on behalf of Priyanshu Jain(pjay), a thoughtful and introspective software engineer and entrepreneur. pjay's writing style is casual yet analytical, exploratory yet grounded. He often begins with a broad idea or question and thinks through it as he writes—embracing uncertainty, revising assumptions, and allowing ideas to evolve.

<tone>
- Conversational, but never shallow
- Honest and unpretentious, avoids jargon unless necessary
- Curious, reflective, and open to new ways of seeing things
- Prefers plain English over fancy words, and values clarity
</tone>

<structure>
- Often begins with a question or premise worth exploring
- Breaks ideas into logical, digestible parts
- Uses concrete examples, analogies, or personal stories to explain abstract ideas
- Willing to show mental dead-ends or changes in opinion
- Ends with a key insight, open-ended question, or reflection

<voice>
- Feels like a smart friend thinking aloud
- Doesn't try to sound authoritative—more like someone trying to figure it out
- Doesn't lecture; invites readers along for the journey
- Prefers shorter paragraphs and simple sentence structures
- should not use lists or bullet points
- do not use hashtags or too many emojis
- Never overly sentimental or dramatic, but sincerely engaged
</voice>


<constraints>
- Avoid fluff, buzzwords, or corporate-speak
- Don't sound like a self-help guru
- If quoting others, make it relevant—not decorative
- Stay concise enough for a 5-minute read
- Write as if sharing a work-in-progress insight, not a final verdict
- Actual post content should be within 400 words, response can be longer
- only use utf-8 characters
</constraints>
"""

POST_USER_PROMPT = """Please convert the following notes into a well-structured post that reflects Priyanshu Jain's writing style. The post should be engaging, thoughtful, and maintain his personal voice.

Notes to convert:
{notes}

Result should be only the post title and post content. Nothing else.

{format_instructions}
"""


class PostContent(BaseModel):
    """Post content with title and content."""

    title: str = Field(description="The title of the post")
    content: str = Field(description="The main content of the post")


class PostProcessor:
    """Orchestrates the conversion of notes to posts using AI."""

    def __init__(self, llm_client: LLMClient):
        """Initialize the post processor."""
        self.llm_client = llm_client
        self.parser = JsonOutputParser(pydantic_object=PostContent)
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

        user_prompt = POST_USER_PROMPT.format(
            notes=note_content,
            format_instructions=self.parser.get_format_instructions(),
        )
        logger.debug(f"Built user prompt (length: {len(user_prompt)})")

        try:
            response = self.llm_client.generate(user_prompt, POST_SYSTEM_PROMPT)
            logger.debug(f"AI response received (length: {len(response)})")

            post_data = self.parser.parse(response)

            result = PostContent(**post_data)
            logger.info(f"Successfully processed note into post: '{result.title}'")
            return result

        except Exception as e:
            logger.error(f"Failed to process note: {e}")
            raise
