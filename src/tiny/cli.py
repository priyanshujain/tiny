"""CLI interface for the tiny agent."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import get_config


console = Console()


@click.group()
@click.version_option()
def main():
    """Tiny - AI agent to convert daily notes into blog posts."""
    pass


@main.command()
@click.argument("note_file", type=click.Path(exists=True, path_type=Path))
@click.option("--deploy", is_flag=True, help="Deploy to website after processing")
@click.option("--dry-run", is_flag=True, help="Show what would be done without executing")
def process(note_file: Path, deploy: bool, dry_run: bool):
    """Process a single note file into a blog post."""
    config = get_config()
    
    console.print(Panel(
        f"Processing note: [bold blue]{note_file}[/bold blue]",
        title="Tiny Agent",
        border_style="blue"
    ))
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Import here to avoid circular imports
        from .processors.note_parser import NoteParser
        from .ai.vertex_client import VertexAIClient
        from .processors.blog_generator import BlogGenerator
        from .website.file_manager import FileManager
        from .website.index_updater import IndexUpdater
        from .git.operations import GitOperations
        
        task = progress.add_task("Parsing note...", total=6)
        
        # Step 1: Parse note
        parser = NoteParser()
        note_content = parser.parse(note_file)
        progress.update(task, advance=1, description="Generating blog content with AI...")
        
        # Step 2: Generate blog content
        ai_client = VertexAIClient(config)
        blog_content = ai_client.generate_blog_post(note_content)
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
            progress.update(task, advance=1, description="Deploying..." if deploy else "Complete!")
            
            # Step 6: Deploy (optional)
            if deploy:
                git_ops.deploy()
        else:
            progress.update(task, advance=3, description="Dry run complete!")
        
        progress.update(task, advance=1)
    
    console.print(f"[green]✓[/green] Successfully processed: {blog_file_path}")
    if deploy and not dry_run:
        console.print("[green]✓[/green] Deployed to website")


@main.command()
@click.argument("notes_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--deploy", is_flag=True, help="Deploy to website after processing all notes")
def batch(notes_dir: Path, deploy: bool):
    """Process multiple notes from a directory."""
    config = get_config()
    
    # Find all markdown files
    note_files = list(notes_dir.glob("*.md"))
    if not note_files:
        console.print("[yellow]No .md files found in directory[/yellow]")
        return
    
    console.print(Panel(
        f"Processing {len(note_files)} notes from: [bold blue]{notes_dir}[/bold blue]",
        title="Batch Processing",
        border_style="blue"
    ))
    
    for note_file in note_files:
        try:
            # Process each note (without individual deployment)
            process.callback(note_file, deploy=False, dry_run=False)
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to process {note_file}: {e}")
    
    if deploy:
        from .git.operations import GitOperations
        git_ops = GitOperations(config)
        git_ops.deploy()
        console.print("[green]✓[/green] Batch deployment complete")


@main.command()
def setup():
    """Initial setup and configuration."""
    config = get_config()
    
    console.print(Panel(
        "Setting up tiny agent configuration",
        title="Setup",
        border_style="green"
    ))
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        console.print("Creating .env file...")
        env_content = """# Tiny Agent Configuration

# Google Cloud / Vertex AI
# Option 1: Use Application Default Credentials (recommended)
# Just run: gcloud auth application-default login
# GOOGLE_CLOUD_PROJECT=your-gcp-project-id  # Optional if gcloud default project is set

# Option 2: Use Service Account Key File
# GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
# GOOGLE_CLOUD_PROJECT=your-gcp-project-id

VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-flash

# Website settings
WEBSITE_PATH=../priyanshujain.dev
WRITINGS_DIR=src/pages/writings
WRITINGS_INDEX_FILE=src/pages/writings/index.js

# Git settings
GIT_REMOTE=origin
GIT_BRANCH=main

# Notes settings
NOTES_DIR=notes

# AI settings
MAX_TOKENS=2000
TEMPERATURE=0.7
"""
        env_file.write_text(env_content)
        console.print("[green]✓[/green] Created .env file")
    else:
        console.print("[yellow]⚠[/yellow] .env file already exists")
    
    # Create notes directory
    notes_dir = Path(config.notes_dir)
    notes_dir.mkdir(exist_ok=True)
    console.print(f"[green]✓[/green] Created notes directory: {notes_dir}")
    
    # Create example note
    example_note = notes_dir / "example.md"
    if not example_note.exists():
        example_content = """# Daily Reflection - 2025-01-06

Today I had some interesting thoughts about AI and software development.

Key insights:
- AI tools are changing how we approach problem-solving
- The importance of maintaining human oversight
- Need to balance automation with creativity

This reminded me of building that ERP system - technology should enhance human capability, not replace it entirely.
"""
        example_note.write_text(example_content)
        console.print(f"[green]✓[/green] Created example note: {example_note}")
    
    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("Next steps:")
    console.print("1. Set up Google Cloud authentication:")
    console.print("   Option A (Recommended): gcloud auth application-default login")
    console.print("   Option B: Set GOOGLE_APPLICATION_CREDENTIALS in .env")
    console.print("2. Run: tiny process notes/example.md --dry-run")


if __name__ == "__main__":
    main()