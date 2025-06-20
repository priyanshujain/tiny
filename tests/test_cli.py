from click.testing import CliRunner
from tiny.cli import cli
import tempfile
from pathlib import Path

class TestCLI:
    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Convert notes to posts" in result.output

    def test_main_missing_file(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["nonexistent.md"])

        assert result.exit_code != 0
        assert "does not exist" in result.output
        
    def test_main_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            note_file = tmp_path / "test_note.txt"
            note_file.write_text("This is a test note content.")

            runner = CliRunner()
            result = runner.invoke(cli, [str(note_file)])

            assert result.exit_code == 0
            assert "Successfully processed" in result.output
            assert "test_note.txt" in result.output

            post_file = Path("posts") / "test_note.txt"
            assert post_file.exists()
