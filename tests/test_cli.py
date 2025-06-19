"""Simple tests for the CLI."""

from pathlib import Path
from click.testing import CliRunner
from tiny.cli import main


class TestCLI:
    """Simple test class for CLI functionality."""

    def test_main_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        
        assert result.exit_code == 0
        assert "Convert notes to posts" in result.output

    def test_main_missing_file(self):
        """Test CLI with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(main, ["nonexistent.md"])
        
        assert result.exit_code != 0
        assert "does not exist" in result.output