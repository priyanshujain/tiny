from click.testing import CliRunner
from tiny.cli import cli
import tempfile
from pathlib import Path


class TestCLI:
    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Tiny CLI tool for processing notes and posts" in result.output
        assert "write" in result.output.lower()

    def test_write_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["write", "--help"])

        assert result.exit_code == 0
        assert "Write commands for generating content" in result.output
        assert "post" in result.output.lower()

    def test_write_post_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["write", "post", "--help"])

        assert result.exit_code == 0
        assert "Convert notes to posts" in result.output
        assert "--input-path" in result.output
        assert "--output-path" in result.output
        assert "required" in result.output

    def test_write_post_missing_input_path(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["write", "post"])

        assert result.exit_code != 0
        assert "Missing option '--input-path'" in result.output

    def test_write_post_nonexistent_input_file(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["write", "post", "--input-path", "nonexistent.md"])

        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()

    def test_write_post_to_stdout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            note_file = tmp_path / "test_note.txt"
            note_file.write_text("This is a test note content for stdout test.")

            runner = CliRunner()
            result = runner.invoke(
                cli, ["write", "post", "--input-path", str(note_file)]
            )

            assert result.exit_code == 0
            assert "Successfully processed to stdout" in result.output

    def test_write_post_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            note_file = tmp_path / "test_note.txt"
            note_file.write_text("This is a test note content for file output test.")

            output_file = tmp_path / "output_post.txt"

            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "write",
                    "post",
                    "--input-path",
                    str(note_file),
                    "--output-path",
                    str(output_file),
                ],
            )

            assert result.exit_code == 0
            assert "Successfully processed:" in result.output
            assert str(output_file) in result.output
            assert output_file.exists()

            content = output_file.read_text()
            assert len(content) > 0

    def test_write_post_creates_output_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            note_file = tmp_path / "test_note.txt"
            note_file.write_text("This is a test note content.")

            output_dir = tmp_path / "nested" / "output"
            output_file = output_dir / "post.txt"

            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "write",
                    "post",
                    "--input-path",
                    str(note_file),
                    "--output-path",
                    str(output_file),
                ],
            )

            assert result.exit_code == 0
            assert output_dir.exists()
            assert output_file.exists()
