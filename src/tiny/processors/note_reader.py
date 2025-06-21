"""Simple note file reader for supported formats."""

from pathlib import Path

from tiny.logging import get_logger

logger = get_logger("processors.note_reader")


class UnsupportedFileTypeError(Exception):
    """Raised when trying to read an unsupported file type."""

    pass


def read_note_file(note_file: Path) -> str:
    """
    Read content from a note file.

    Args:
        note_file: Path to the note file

    Returns:
        Raw file content as string

    Raises:
        FileNotFoundError: If the file doesn't exist
        UnsupportedFileTypeError: If file extension is not supported
    """
    logger.debug(f"Reading note file: {note_file}")

    if not note_file.exists():
        logger.error(f"Note file not found: {note_file}")
        raise FileNotFoundError(f"Note file not found: {note_file}")

    supported_extensions = {".md", ".txt", ".notes"}
    if note_file.suffix.lower() not in supported_extensions:
        logger.error(f"Unsupported file type: {note_file.suffix}")
        raise UnsupportedFileTypeError(
            f"Unsupported file type: {note_file.suffix}. "
            f"Supported types: {', '.join(sorted(supported_extensions))}"
        )

    try:
        content = note_file.read_text(encoding="utf-8")
        logger.info(
            f"Successfully read note file: {note_file} ({len(content)} characters)"
        )
        return content
    except Exception as e:
        logger.error(f"Failed to read note file {note_file}: {e}")
        raise
