# Tiny

Convert daily notes into first drafts for posts, articles, or essays.

```
❯ uv run tiny --help
Uninstalled 1 package in 1ms
Installed 1 package in 2ms
Usage: tiny [OPTIONS] COMMAND [ARGS]...

  Tiny CLI tool for processing notes and posts.

Options:
  --debug  Enable debug logging
  --info   Enable info logging
  --help   Show this message and exit.

Commands:
  write  Write commands for generating content.
```

## Usage

```shell
uv run tiny write post input-path=notes/my-note.txt
```

## Tests

```shell
uv run pytest
```

## Note format

Any text file works.