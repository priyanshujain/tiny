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
@click.option("--deploy", is_flag=True, help="Deploy to website after processing")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without executing"
)
def main(note_file: Path, deploy: bool, dry_run: bool):
    """Convert notes to blog posts."""
    config = get_config()

    console.print(
        Panel(
            f"Processing note: [bold blue]{note_file}[/bold blue]",
            title="Tiny Agent",
            border_style="blue",
        )
    )

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Import here to avoid circular imports
        from tiny.processors.note_parser import read_note_file
        from tiny.ai.llm_client import LLMClient
        from tiny.processors.blog_generator import BlogGenerator
        from tiny.website.index_updater import IndexUpdater
        from tiny.git.operations import GitOperations

        task = progress.add_task("Reading note...", total=6)

        # Step 1: Read note
        note_content = read_note_file(note_file)
        progress.update(
            task, advance=1, description="Generating blog content..."
        )

        # Step 2: Generate blog content
        llm_client = LLMClient(config)
        blog_content = llm_client.generate_blog_post(note_content)
        progress.update(task, advance=1, description="Creating blog post file...")

        # Step 3: Generate blog post file
        blog_gen = BlogGenerator(config)
        blog_file_path = blog_gen.generate(blog_content)
        progress.update(task, advance=1, description="Updating writings index...")

        if not dry_run:
            # Step 4: Update writings index
            index_updater = IndexUpdater(config)
            index_updater.add_entry(blog_content)
            progress.update(task, advance=1, description="Committing changes...")

            # Step 5: Git operations
            git_ops = GitOperations(config)
            git_ops.commit_changes(f"Add new blog post: {blog_content.title}")
            progress.update(
                task, advance=1, description="Deploying..." if deploy else "Complete!"
            )

            # Step 6: Deploy (optional)
            if deploy:
                git_ops.deploy()
        else:
            progress.update(task, advance=3, description="Dry run complete!")

        progress.update(task, advance=1)

    console.print(f"[green]✓[/green] Successfully processed: {blog_file_path}")
    if deploy and not dry_run:
        console.print("[green]✓[/green] Deployed to website")


if __name__ == "__main__":
    main()
