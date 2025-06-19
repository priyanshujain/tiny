"""Tests for post writing functionality."""

from pathlib import Path

from tiny.processors.post_writer import PostWriter
from tiny.ai.post_processor import PostContent


def test_write_simple_post(test_config, temp_posts_dir):
    """Test writing a simple post to file."""
    writer = PostWriter(test_config)
    post_content = PostContent(
        title="My Test Post",
        content="This is the content of my test post.\n\nIt has multiple paragraphs.",
    )

    file_path = writer.write_post(post_content)

    # Verify file was created
    assert file_path.exists()
    assert file_path.parent == temp_posts_dir
    assert file_path.name == "my-test-post.txt"

    # Verify file content
    content = file_path.read_text(encoding="utf-8")
    expected_content = "My Test Post\n\nThis is the content of my test post.\n\nIt has multiple paragraphs."
    assert content == expected_content


def test_title_to_filename_conversion(test_config):
    """Test conversion of various titles to valid filenames."""
    writer = PostWriter(test_config)

    test_cases = [
        ("Simple Title", "simple-title"),
        ("Title With Multiple   Spaces", "title-with-multiple-spaces"),
        ("Title!@#$%^&*()With Special Characters", "title-with-special-characters"),
        ("Title with 123 Numbers", "title-with-123-numbers"),
        ("CamelCase Title", "camelcase-title"),
        ("", "post-20"),  # Will contain current date
        ("   ", "post-20"),  # Will contain current date
        ("---Multiple---Hyphens---", "multiple-hyphens"),
    ]

    for title, expected_start in test_cases:
        filename = writer._title_to_filename(title)
        if expected_start.startswith("post-20"):
            # For empty/whitespace titles, check it starts with post- and has date
            assert filename.startswith("post-20")
            assert len(filename) > 10  # Should include date
        else:
            assert filename == expected_start


def test_write_post_creates_directory(test_config):
    """Test that writing a post creates the posts directory if it doesn't exist."""
    # Use a non-existent subdirectory
    posts_dir = Path(test_config.posts_dir) / "nested" / "subdir"
    test_config.posts_dir = str(posts_dir)

    writer = PostWriter(test_config)
    post_content = PostContent(title="Test Post", content="Test content")

    file_path = writer.write_post(post_content)

    # Verify directory was created
    assert posts_dir.exists()
    assert posts_dir.is_dir()
    assert file_path.exists()


def test_write_post_with_unicode_content(test_config, temp_posts_dir):
    """Test writing a post with unicode characters."""
    writer = PostWriter(test_config)
    post_content = PostContent(
        title="Unicode Test 🌍",
        content="Content with émojis 😀 and special characters: ñáéíóú",
    )

    file_path = writer.write_post(post_content)

    # Verify file was created and content is correct
    assert file_path.exists()
    content = file_path.read_text(encoding="utf-8")
    assert "Unicode Test 🌍" in content
    assert "émojis 😀" in content
    assert "ñáéíóú" in content


def test_write_multiple_posts_same_writer(test_config, temp_posts_dir):
    """Test writing multiple posts with the same writer instance."""
    writer = PostWriter(test_config)

    posts = [
        PostContent(title="First Post", content="First content"),
        PostContent(title="Second Post", content="Second content"),
        PostContent(title="Third Post", content="Third content"),
    ]

    file_paths = []
    for post in posts:
        file_path = writer.write_post(post)
        file_paths.append(file_path)

    # Verify all files exist and have correct content
    assert len(file_paths) == 3
    for i, file_path in enumerate(file_paths):
        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        assert posts[i].title in content
        assert posts[i].content in content
