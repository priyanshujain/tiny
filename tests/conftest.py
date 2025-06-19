"""Pytest configuration and fixtures for tiny tests."""

import tempfile
from pathlib import Path

import pytest

from tiny.config import TinyConfig


@pytest.fixture
def sample_note():
    """Sample note content for testing."""
    return """# My Daily Notes

Today I learned about Python testing with pytest. Here are the key points:

- Fixtures provide reusable test data
- Mocking helps isolate units under test
- Tests should be simple and focused

I also worked on a new project called "tiny" which converts notes to blog posts using AI.

## Next Steps
- Write more tests
- Improve the CLI interface
- Add better error handling
"""


@pytest.fixture
def temp_posts_dir():
    """Temporary directory for test post outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_llm_response():
    """Mock LLM response in expected JSON format."""
    return """{
    "title": "Learning Python Testing with Pytest",
    "content": "Today I explored the world of Python testing using pytest. The experience taught me several valuable lessons about writing effective tests.\\n\\nKey concepts I learned include fixtures for reusable test data, mocking for isolating units under test, and the importance of keeping tests simple and focused. These fundamentals form the foundation of good testing practices.\\n\\nI also made progress on my 'tiny' project, which uses AI to convert daily notes into polished blog posts. This combination of learning and building has been particularly rewarding.",
    "date": "2024-01-15"
}"""


@pytest.fixture
def test_config(temp_posts_dir):
    """Test configuration with temporary directories."""
    return TinyConfig(
        model="test",
        posts_dir=str(temp_posts_dir),
        temperature=0.5,
        max_tokens=2000,
    )


@pytest.fixture
def sample_note_file(temp_posts_dir, sample_note):
    """Sample note file for testing file operations."""
    note_file = temp_posts_dir / "test_note.md"
    note_file.write_text(sample_note, encoding="utf-8")
    return note_file
