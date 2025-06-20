"""CLI interface for the tiny agent."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from tiny.config import get_config

console = Console()


@click.group()
def cli():
    """Tiny CLI tool for processing notes and posts."""
    pass


@cli.group()
def write():
    """Write commands for generating content."""
    pass


@write.command()
@click.option(
    "--input-path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to input note file",
)
@click.option(
    "--output-path",
    type=click.Path(path_type=Path),
    help="Path to output post file (prints to stdout if not provided)",
)
def post(input_path: Path, output_path: Path | None):
    """Convert notes to posts."""
    config = get_config()

    console.print(
        Panel(
            f"Processing note: [bold blue]{input_path}[/bold blue]",
            title="Tiny Agent",
            border_style="blue",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Import here to avoid circular imports
        from tiny.processors.note_reader import read_note_file
        from tiny.ai.llm_client import LLMClient
        from tiny.ai.post_processor import PostProcessor
        from tiny.processors.post_writer import PostWriter

        task = progress.add_task("Reading note...", total=3)

        # Step 1: Read note
        note_content = read_note_file(input_path)
        progress.update(task, advance=1, description="Generating post content...")

        # Step 2: Generate post content
        llm_client = LLMClient(config)
        post_processor = PostProcessor(llm_client)
        post_content = post_processor.process_note(note_content)
        progress.update(task, advance=1, description="Creating post...")

        # Step 3: Write post
        post_writer = PostWriter(config)
        if output_path:
            post_file_path = post_writer.write_post_to_file(post_content, output_path)
            progress.update(task, advance=1, description="Complete!")
            console.print(f"[green]✓[/green] Successfully processed: {post_file_path}")
        else:
            post_writer.write_post_to_stdout(post_content)
            progress.update(task, advance=1, description="Complete!")
            console.print("[green]✓[/green] Successfully processed to stdout")
