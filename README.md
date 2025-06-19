# Tiny - AI Blog Generator

An AI agent that converts daily notes into polished blog posts and automatically publishes them to your website.

## Features

- **AI-Powered Content Generation**: Uses Google Vertex AI (Gemini) to convert raw notes into your writing style
- **Automatic Website Integration**: Creates React components and updates your Gatsby website
- **Git Automation**: Commits, pushes, and deploys changes automatically  
- **Style Matching**: Learns from your existing blog posts to maintain consistent voice and tone
- **Multiple Note Formats**: Supports Markdown, plain text, and YAML notes

## Quick Start

1. **Install and Setup**:
   ```bash
   uv run tiny setup
   ```

2. **Set up Google Cloud authentication** (choose one option):

   **Option A (Recommended) - Application Default Credentials:**
   ```bash
   gcloud auth application-default login
   # Optionally set default project: gcloud config set project your-project-id
   ```

   **Option B - Service Account Key:**
   ```bash
   # Edit .env with your Google Cloud project details
   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   ```

3. **Process your first note**:
   ```bash
   uv run tiny process notes/example.md
   ```

4. **Deploy to website**:
   ```bash
   uv run tiny process notes/my-note.md --deploy
   ```

## Commands

- `tiny setup` - Initial configuration and setup
- `tiny process <note_file>` - Convert a single note to blog post
- `tiny batch <notes_dir>` - Process multiple notes from a directory
- `tiny process <note_file> --deploy` - Process and deploy to website
- `tiny process <note_file> --dry-run` - Preview what would be done

## Note Format

Create notes in Markdown format:

```markdown
# Daily Reflection - 2025-01-06

Today I had some interesting thoughts about AI and software development.

Key insights:
- AI tools are changing how we approach problem-solving
- The importance of maintaining human oversight
- Need to balance automation with creativity

This reminded me of building that ERP system - technology should enhance human capability, not replace it entirely.
```

The AI will convert this into a polished two-paragraph blog post matching your writing style.

## Configuration

The `.env` file contains all configuration options:

```bash
# Google Cloud / Vertex AI
# Option 1: Use Application Default Credentials (recommended)
# Just run: gcloud auth application-default login
# GOOGLE_CLOUD_PROJECT=your-project-id  # Optional if gcloud default project is set

# Option 2: Use Service Account Key File
# GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
# GOOGLE_CLOUD_PROJECT=your-project-id

VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-flash

# Website settings  
WEBSITE_PATH=../priyanshujain.dev
WRITINGS_DIR=src/pages/writings
WRITINGS_INDEX_FILE=src/pages/writings/index.js

# Git settings
GIT_REMOTE=origin
GIT_BRANCH=main
```

## How It Works

1. **Parse Notes**: Extracts content from various note formats
2. **AI Generation**: Uses Vertex AI to convert notes into your writing style
3. **React Component**: Creates a properly formatted blog post component
4. **Index Update**: Adds the new post to your writings index in chronological order
5. **Git Operations**: Commits changes and pushes to repository
6. **Deployment**: Triggers Netlify deployment via your existing deploy script

## Development

```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev

# Run linting
uv run ruff check
uv run black --check .

# Run tests
uv run pytest
``` 
