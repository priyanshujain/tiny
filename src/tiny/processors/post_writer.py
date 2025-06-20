"""Post writer for creating simple text files."""

import logging
from pathlib import Path

from tiny.ai.post_processor import PostContent
from tiny.config import TinyConfig


logger = logging.getLogger(__name__)


class PostWriter:
    """Writer for simple text post files."""

    def __init__(self, config: TinyConfig):
        """Initialize the post writer."""
        self.config = config

    def write_post(self, post_content: PostContent, filename: str) -> Path:
        """
        Write a simple text file from post content.

        Args:
            post_content: Post content with title and content

        Returns:
            Path to the written file
        """
        posts_dir = Path(self.config.posts_dir)
        posts_dir.mkdir(parents=True, exist_ok=True)
        file_path = posts_dir / filename

        text_content = f"{post_content.title}\n\n{post_content.content}"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        logger.info(f"Written post file: {file_path}")
        return file_path