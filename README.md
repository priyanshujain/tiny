# Tiny

Convert daily notes into blog posts using AI.

## Setup

```bash
# Install
uv sync

# Setup (creates .env and directories)
uv run tiny setup
```

## Configuration

Edit `.env` file:

```bash
# Choose any LLM provider
MODEL=vertex_ai/gemini-2.5-flash
# MODEL=gpt-4o
# MODEL=claude-3-5-sonnet-20241022

# Add provider-specific API keys as needed
# OPENAI_API_KEY=your-key
# ANTHROPIC_API_KEY=your-key

# Website settings
WEBSITE_PATH=../your-website
WRITINGS_DIR=src/pages/writings
WRITINGS_INDEX_FILE=src/pages/writings/index.js
```

## Usage

```bash
# Process a note file
uv run tiny process notes/my-note.md

# Process and deploy
uv run tiny process notes/my-note.md --deploy

# Process multiple notes
uv run tiny batch notes/

# Preview changes
uv run tiny process notes/my-note.md --dry-run
```

## How it works

1. Reads your note file
2. Converts to blog post using AI
3. Creates React component
4. Updates website index
5. Commits to git (if --deploy)

## Note format

Any text file works. Example:

```markdown
# Today's thoughts

Had an interesting conversation about AI...

Key points:
- AI is changing software development
- Need to balance automation with creativity
```

Gets converted to a polished blog post in your style.