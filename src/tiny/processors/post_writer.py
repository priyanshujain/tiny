"""Post writer for creating simple text files."""

import logging
import re
from datetime import datetime
from pathlib import Path

from tiny.ai.post_processor import PostContent
from tiny.config import TinyConfig


logger = logging.getLogger(__name__)


class PostWriter:
    """Writer for simple text post files."""

    def __init__(self, config: TinyConfig):
        """Initialize the post writer."""
        self.config = config

    def write_post(self, post_content: PostContent) -> Path:
        """
        Write a simple text file from post content.

        Args:
            post_content: Post content with title and content

        Returns:
            Path to the written file
        """
        # Generate filename from title
        filename = self._title_to_filename(post_content.title)

        # Create the posts directory if it doesn't exist
        posts_dir = Path(self.config.posts_dir)
        posts_dir.mkdir(parents=True, exist_ok=True)
        file_path = posts_dir / f"{filename}.txt"

        # Generate simple text content: title on first line, then content
        text_content = f"{post_content.title}\n\n{post_content.content}"

        # Write the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        logger.info(f"Written post file: {file_path}")
        return file_path

    def _title_to_filename(self, title: str) -> str:
        """
        Convert post title to a valid filename.

        Args:
            title: Post title

        Returns:
            URL-safe filename
        """
        # Convert to lowercase
        filename = title.lower()

        # Replace spaces and special characters with hyphens
        filename = re.sub(r"[^a-z0-9]+", "-", filename)

        # Remove leading/trailing hyphens
        filename = filename.strip("-")

        # Ensure it's not empty
        if not filename:
            filename = f"post-{datetime.now().strftime('%Y%m%d')}"

        return filename
