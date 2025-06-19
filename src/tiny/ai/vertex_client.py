"""Vertex AI client for blog post generation."""

import json
import logging
from typing import Any, Dict

from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from ..config import TinyConfig
from .prompts import BLOG_CONVERSION_PROMPT, get_style_examples


logger = logging.getLogger(__name__)


class BlogContent(BaseModel):
    """Blog content data model."""
    title: str
    content: str
    date: str


class VertexAIClient:
    """Client for interacting with Vertex AI."""
    
    def __init__(self, config: TinyConfig):
        """Initialize the Vertex AI client."""
        self.config = config
        
        # Prepare kwargs for ChatVertexAI
        llm_kwargs = {
            "model_name": config.vertex_ai_model,
            "location": config.vertex_ai_location,
            "max_output_tokens": config.max_tokens,
            "temperature": config.temperature,
        }
        
        # Only set project if explicitly provided
        if config.google_cloud_project:
            llm_kwargs["project"] = config.google_cloud_project
        
        self.llm = ChatVertexAI(**llm_kwargs)
    
    def generate_blog_post(self, notes: str) -> BlogContent:
        """
        Generate a blog post from notes using Vertex AI.
        
        Args:
            notes: Raw notes content
            
        Returns:
            BlogContent with title, content, and date
        """
        try:
            # Get style examples
            style_examples = get_style_examples()
            
            # Create the prompt
            prompt = BLOG_CONVERSION_PROMPT.format(
                notes=notes,
                style_examples=style_examples
            )
            
            # Create messages
            messages = [
                SystemMessage(content="You are an expert content editor who specializes in converting raw notes into polished blog posts while maintaining the author's authentic voice and style."),
                HumanMessage(content=prompt)
            ]
            
            # Generate response
            logger.info("Generating blog post with Vertex AI...")
            response = self.llm.invoke(messages)
            
            # Parse the JSON response
            response_text = response.content.strip()
            
            # Handle potential markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                # Fallback: try to extract content manually
                return self._fallback_parse(response_text, notes)
            
            # Validate required fields
            if not all(key in parsed_response for key in ["title", "content", "date"]):
                raise ValueError("Response missing required fields: title, content, date")
            
            blog_content = BlogContent(
                title=parsed_response["title"],
                content=parsed_response["content"],
                date=parsed_response["date"]
            )
            
            logger.info(f"Successfully generated blog post: {blog_content.title}")
            return blog_content
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise
    
    def _fallback_parse(self, response_text: str, notes: str) -> BlogContent:
        """
        Fallback parsing when JSON parsing fails.
        
        Args:
            response_text: Raw response from AI
            notes: Original notes for fallback title
            
        Returns:
            BlogContent with extracted or default values
        """
        import re
        from datetime import datetime
        
        logger.warning("Using fallback parsing for AI response")
        
        # Try to extract title
        title_match = re.search(r'"title":\s*"([^"]+)"', response_text)
        title = title_match.group(1) if title_match else self._generate_fallback_title(notes)
        
        # Try to extract content
        content_match = re.search(r'"content":\s*"([^"]+)"', response_text)
        if content_match:
            content = content_match.group(1).replace('\\n', '\n')
        else:
            # Use the response as content if we can't parse it
            content = response_text
        
        # Use current date
        date = datetime.now().strftime("%Y-%m-%d")
        
        return BlogContent(title=title, content=content, date=date)
    
    def _generate_fallback_title(self, notes: str) -> str:
        """Generate a fallback title from notes."""
        # Simple fallback: use first few words or a generic title
        words = notes.split()[:5]
        if words:
            return " ".join(words).title()
        else:
            from datetime import datetime
            return f"Daily Notes - {datetime.now().strftime('%B %d, %Y')}"