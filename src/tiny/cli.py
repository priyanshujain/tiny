"""CLI interface for the tiny agent."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from tiny.config import get_config
from tiny.logging import setup_logging

console = Console()


@click.group()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.option(
    "--info",
    is_flag=True,
    help="Enable info logging",
)
@click.pass_context
def cli(ctx: click.Context, debug: bool, info: bool):
    """Tiny CLI tool for processing notes and posts."""
    ctx.ensure_object(dict)

    config = get_config()
    if debug:
        log_level = "DEBUG"
    elif info:
        log_level = "INFO"
    else:
        log_level = config.log_level

    logger, log_file_path = setup_logging(log_level)

    ctx.obj["logger"] = logger
    ctx.obj["log_file_path"] = log_file_path
    ctx.obj["config"] = config

    logger.info(f"Starting tiny CLI with log level: {log_level}")
    logger.debug(f"Log file: {log_file_path}")


@cli.group()
@click.pass_context
def write(ctx: click.Context):
    """Write commands for generating content."""
    logger = ctx.obj["logger"]
    logger.debug("Entering write command group")


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
@click.pass_context
def post(ctx: click.Context, input_path: Path, output_path: Path | None):
    """Convert notes to posts."""
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    logger.info(f"Starting post conversion for: {input_path}")
    logger.debug(f"Output path: {output_path}")

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

        logger.debug("Starting note reading process")
        note_content = read_note_file(input_path)
        logger.info(
            f"Successfully read note file, content length: {len(note_content)} characters"
        )
        progress.update(task, advance=1, description="Generating post content...")

        logger.debug("Initializing LLM client and post processor")
        llm_client = LLMClient(config)
        post_processor = PostProcessor(llm_client)
        logger.debug("Starting post content generation")
        post_content = post_processor.process_note(note_content)
        logger.info(
            f"Successfully generated post content: '{post_content.title}' ({len(post_content.content)} characters)"
        )
        progress.update(task, advance=1, description="Creating post...")

        logger.debug("Initializing post writer")
        post_writer = PostWriter(config)
        if output_path:
            logger.debug(f"Writing post to file: {output_path}")
            post_file_path = post_writer.write_post_to_file(post_content, output_path)
            progress.update(task, advance=1, description="Complete!")
            logger.info(f"Successfully wrote post to file: {post_file_path}")
            console.print(f"[green]✓[/green] Successfully processed: {post_file_path}")
        else:
            logger.debug("Writing post to stdout")
            post_writer.write_post_to_stdout(post_content)
            progress.update(task, advance=1, description="Complete!")
            logger.info("Successfully wrote post to stdout")
            console.print("[green]✓[/green] Successfully processed to stdout")
