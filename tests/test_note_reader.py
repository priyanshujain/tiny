"""Tests for note file reading functionality."""

import pytest

from tiny.processors.note_reader import read_note_file, UnsupportedFileTypeError


def test_read_existing_markdown_file(sample_note_file, sample_note):
    """Test reading an existing markdown file."""
    content = read_note_file(sample_note_file)
    assert content == sample_note
    assert "# My Daily Notes" in content
    assert "pytest" in content


def test_read_nonexistent_file(temp_posts_dir):
    """Test reading a file that doesn't exist."""
    nonexistent_file = temp_posts_dir / "does_not_exist.md"

    with pytest.raises(FileNotFoundError):
        read_note_file(nonexistent_file)


def test_unsupported_file_extension(temp_posts_dir):
    """Test reading a file with unsupported extension."""
    unsupported_file = temp_posts_dir / "test.pdf"
    unsupported_file.write_text("some content")

    with pytest.raises(UnsupportedFileTypeError) as exc_info:
        read_note_file(unsupported_file)

    assert "Unsupported file type: .pdf" in str(exc_info.value)
    assert ".md, .notes, .txt" in str(exc_info.value)


def test_supported_file_extensions(temp_posts_dir):
    """Test that all supported file extensions work."""
    test_content = "Test content"
    supported_extensions = [".md", ".txt", ".notes"]

    for ext in supported_extensions:
        test_file = temp_posts_dir / f"test{ext}"
        test_file.write_text(test_content, encoding="utf-8")

        content = read_note_file(test_file)
        assert content == test_content


def test_read_empty_file(temp_posts_dir):
    """Test reading an empty file."""
    empty_file = temp_posts_dir / "empty.md"
    empty_file.write_text("", encoding="utf-8")

    content = read_note_file(empty_file)
    assert content == ""


def test_read_file_with_unicode(temp_posts_dir):
    """Test reading a file with unicode characters."""
    unicode_content = "Hello 🌍! This is a test with émojis and ñice characters."
    unicode_file = temp_posts_dir / "unicode.md"
    unicode_file.write_text(unicode_content, encoding="utf-8")

    content = read_note_file(unicode_file)
    assert content == unicode_content
