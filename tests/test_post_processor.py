"""Tests for post processing functionality with mocked LLM."""

import pytest
from unittest.mock import Mock, patch

from tiny.ai.post_processor import PostProcessor, PostContent
from tiny.ai.llm_client import LLMClient


def test_process_note_success(test_config, sample_note, mock_llm_response):
    """Test successful note processing with mocked LLM."""
    # Create mock LLM client
    mock_llm_client = Mock(spec=LLMClient)
    mock_llm_client.generate.return_value = mock_llm_response

    processor = PostProcessor(mock_llm_client)
    result = processor.process_note(sample_note)

    # Verify the result
    assert isinstance(result, PostContent)
    assert result.title == "Learning Python Testing with Pytest"
    assert "pytest" in result.content
    assert "fixtures" in result.content

    # Verify LLM was called
    mock_llm_client.generate.assert_called_once()
    call_args = mock_llm_client.generate.call_args[0][0]
    assert sample_note in call_args


def test_process_note_with_code_blocks(test_config, sample_note):
    """Test processing when LLM returns response wrapped in code blocks."""
    response_with_blocks = """```json
{
    "title": "Test Title",
    "content": "Test content",
    "date": "2024-01-15"
}
```"""

    mock_llm_client = Mock(spec=LLMClient)
    mock_llm_client.generate.return_value = response_with_blocks

    processor = PostProcessor(mock_llm_client)
    result = processor.process_note(sample_note)

    assert result.title == "Test Title"
    assert result.content == "Test content"


def test_process_note_invalid_json(test_config, sample_note):
    """Test processing when LLM returns invalid JSON."""
    invalid_response = "This is not valid JSON"

    mock_llm_client = Mock(spec=LLMClient)
    mock_llm_client.generate.return_value = invalid_response

    processor = PostProcessor(mock_llm_client)

    with pytest.raises(ValueError) as exc_info:
        processor.process_note(sample_note)

    assert "Invalid JSON response from AI" in str(exc_info.value)


def test_process_note_missing_required_fields(test_config, sample_note):
    """Test processing when LLM response is missing required fields."""
    incomplete_response = '{"title": "Test Title"}'  # Missing content

    mock_llm_client = Mock(spec=LLMClient)
    mock_llm_client.generate.return_value = incomplete_response

    processor = PostProcessor(mock_llm_client)

    with pytest.raises(ValueError) as exc_info:
        processor.process_note(sample_note)

    assert "Response missing required fields" in str(exc_info.value)


def test_process_note_llm_exception(test_config, sample_note):
    """Test processing when LLM client raises an exception."""
    mock_llm_client = Mock(spec=LLMClient)
    mock_llm_client.generate.side_effect = Exception("LLM service unavailable")

    processor = PostProcessor(mock_llm_client)

    with pytest.raises(Exception) as exc_info:
        processor.process_note(sample_note)

    assert "LLM service unavailable" in str(exc_info.value)


def test_parse_response_with_extra_fields(test_config, sample_note):
    """Test that parsing works with extra fields in response."""
    response_with_extra = """{
    "title": "Test Title",
    "content": "Test content",
    "date": "2024-01-15",
    "extra_field": "this should be ignored",
    "another_extra": 123
}"""

    mock_llm_client = Mock(spec=LLMClient)
    mock_llm_client.generate.return_value = response_with_extra

    processor = PostProcessor(mock_llm_client)
    result = processor.process_note(sample_note)

    # Should work fine, extra fields are ignored
    assert result.title == "Test Title"
    assert result.content == "Test content"


def test_parse_response_with_nested_json(test_config, sample_note):
    """Test parsing response with nested JSON content."""
    response_with_nested = """{
    "title": "JSON Tutorial",
    "content": "Here's how to use JSON: {\\"key\\": \\"value\\"}",
    "date": "2024-01-15"
}"""

    mock_llm_client = Mock(spec=LLMClient)
    mock_llm_client.generate.return_value = response_with_nested

    processor = PostProcessor(mock_llm_client)
    result = processor.process_note(sample_note)

    assert result.title == "JSON Tutorial"
    assert '{"key": "value"}' in result.content


@patch("tiny.ai.post_processor.get_style_examples")
def test_process_note_includes_style_examples(
    mock_get_style, test_config, sample_note, mock_llm_response
):
    """Test that style examples are included in the prompt."""
    mock_get_style.return_value = "Example style content"

    mock_llm_client = Mock(spec=LLMClient)
    mock_llm_client.generate.return_value = mock_llm_response

    processor = PostProcessor(mock_llm_client)
    processor.process_note(sample_note)

    # Verify style examples were fetched
    mock_get_style.assert_called_once()

    # Verify the prompt includes both note content and style examples
    call_args = mock_llm_client.generate.call_args[0][0]
    assert sample_note in call_args
    assert "Example style content" in call_args
