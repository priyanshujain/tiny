"""Post writer for creating simple text files."""

import sys
from pathlib import Path

from tiny.ai.post_processor import PostContent
from tiny.config import TinyConfig
from tiny.logging import get_logger

logger = get_logger("processors.post_writer")


class PostWriter:
    """Writer for simple text post files."""

    def __init__(self, config: TinyConfig):
        """Initialize the post writer."""
        self.config = config
        logger.debug("PostWriter initialized")

    def write_post_to_file(self, post_content: PostContent, output_path: Path) -> Path:
        """
        Write a simple text file from post content to specified path.

        Args:
            post_content: Post content with title and content
            output_path: Path where the post file should be written

        Returns:
            Path to the written file
        """
        logger.debug(f"Writing post to file: {output_path}")

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            text_content = f"{post_content.title}\n\n{post_content.content}"

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            logger.info(f"Successfully written post file: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to write post file {output_path}: {e}")
            raise

    def write_post_to_stdout(self, post_content: PostContent) -> None:
        """
        Write post content to stdout console.

        Args:
            post_content: Post content with title and content
        """
        logger.debug("Writing post to stdout")

        text_content = f"{post_content.title}\n\n{post_content.content}"
        print(text_content, file=sys.stdout)
        logger.info("Successfully written post to stdout")

    def write_post(self, post_content: PostContent, filename: str) -> Path:
        """
        Legacy method for backward compatibility.
        Write a simple text file from post content using current directory.

        Args:
            post_content: Post content with title and content
            filename: Name of the file to write

        Returns:
            Path to the written file
        """
        logger.debug(f"Using legacy write_post method with filename: {filename}")
        file_path = Path(filename)
        return self.write_post_to_file(post_content, file_path)
