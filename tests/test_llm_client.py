"""Tests for LLM client functionality with mocks."""

import pytest
from unittest.mock import Mock, patch

from tiny.ai.llm_client import LLMClient


def test_llm_client_initialization(test_config):
    """Test LLM client initialization with config."""
    client = LLMClient(test_config)

    assert client.config == test_config
    assert client.model == test_config.model
    assert client.temperature == test_config.temperature
    assert client.max_tokens == test_config.max_tokens


def test_generate_with_test_model(test_config):
    """Test generation with test model (returns mock response)."""
    test_config.model = "test"
    client = LLMClient(test_config)

    prompt = "Tell me about Python testing"
    response = client.generate(prompt)

    assert response.startswith("Test response for prompt:")
    assert "Tell me about Python testing" in response


@patch("tiny.ai.llm_client.litellm.completion")
def test_generate_with_real_model(mock_completion, test_config):
    """Test generation with real model (mocked litellm)."""
    # Setup mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "  Generated response content  "
    mock_completion.return_value = mock_response

    # Use non-test model
    test_config.model = "gpt-3.5-turbo"
    client = LLMClient(test_config)

    prompt = "Generate a blog post"
    response = client.generate(prompt)

    # Verify response is stripped
    assert response == "Generated response content"

    # Verify litellm was called with correct parameters
    mock_completion.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=test_config.temperature,
        max_tokens=test_config.max_tokens,
    )


@patch("tiny.ai.llm_client.litellm.completion")
def test_generate_with_custom_parameters(mock_completion, test_config):
    """Test generation with custom temperature and max_tokens."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_completion.return_value = mock_response

    # Customize config
    test_config.model = "claude-3-sonnet"
    test_config.temperature = 0.8
    test_config.max_tokens = 1500

    client = LLMClient(test_config)
    client.generate("Test prompt")

    # Verify custom parameters were used
    mock_completion.assert_called_once_with(
        model="claude-3-sonnet",
        messages=[{"role": "user", "content": "Test prompt"}],
        temperature=0.8,
        max_tokens=1500,
    )


@patch("tiny.ai.llm_client.litellm.completion")
def test_generate_handles_litellm_exception(mock_completion, test_config):
    """Test that LLM client properly propagates litellm exceptions."""
    mock_completion.side_effect = Exception("API rate limit exceeded")

    test_config.model = "gpt-4"
    client = LLMClient(test_config)

    with pytest.raises(Exception) as exc_info:
        client.generate("Test prompt")

    assert "API rate limit exceeded" in str(exc_info.value)


def test_generate_with_empty_prompt(test_config):
    """Test generation with empty prompt using test model."""
    test_config.model = "test"
    client = LLMClient(test_config)

    response = client.generate("")

    assert response.startswith("Test response for prompt:")
    assert response.endswith("...")


def test_generate_with_long_prompt(test_config):
    """Test generation with very long prompt using test model."""
    test_config.model = "test"
    client = LLMClient(test_config)

    long_prompt = "This is a very long prompt. " * 100
    response = client.generate(long_prompt)

    assert response.startswith("Test response for prompt:")
    # Should truncate to 50 characters in test mode
    assert len(response.split("Test response for prompt: ")[1].replace("...", "")) == 50


@patch("tiny.ai.llm_client.litellm.completion")
def test_generate_message_format(mock_completion, test_config):
    """Test that messages are formatted correctly for litellm."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_completion.return_value = mock_response

    test_config.model = "gpt-3.5-turbo"
    client = LLMClient(test_config)

    prompt = "Hello, AI!"
    client.generate(prompt)

    # Check that messages were formatted correctly
    call_args = mock_completion.call_args
    messages = call_args[1]["messages"]

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == prompt
