"""CLI interface for the tiny agent."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from tiny.config import get_config

console = Console()


@click.command()
@click.argument("note_file", type=click.Path(exists=True, path_type=Path))
def cli(note_file: Path):
    """Convert notes to posts."""
    config = get_config()

    console.print(
        Panel(
            f"Processing note: [bold blue]{note_file}[/bold blue]",
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
        note_content = read_note_file(note_file)
        progress.update(task, advance=1, description="Generating post content...")

        # Step 2: Generate post content
        llm_client = LLMClient(config)
        post_processor = PostProcessor(llm_client)
        post_content = post_processor.process_note(note_content)
        progress.update(task, advance=1, description="Creating post file...")

        # Step 3: Write post file
        post_writer = PostWriter(config)
        post_file_path = post_writer.write_post(post_content, note_file.name)
        progress.update(task, advance=1, description="Complete!")

        progress.update(task, advance=1)

    console.print(f"[green]✓[/green] Successfully processed: {post_file_path}")