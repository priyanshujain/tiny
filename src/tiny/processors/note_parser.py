"""Simple note file reader for supported formats."""

from pathlib import Path


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
    if not note_file.exists():
        raise FileNotFoundError(f"Note file not found: {note_file}")

    supported_extensions = {".md", ".txt", ".notes"}
    if note_file.suffix.lower() not in supported_extensions:
        raise UnsupportedFileTypeError(
            f"Unsupported file type: {note_file.suffix}. "
            f"Supported types: {', '.join(sorted(supported_extensions))}"
        )

    return note_file.read_text(encoding="utf-8")
