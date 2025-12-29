# opencode-itch

OpenCode plugin for Socratic questioning - explore topics through guided inquiry.

## Installation

### 1. Clone and install the Python package

```bash
# Clone the repository
git clone https://github.com/JRedeker/itch.git
cd itch

# Install with uv (recommended)
uv sync

# Or install in editable mode with pip
pip install -e .
```

### 2. Add the plugin to OpenCode

Add the plugin path to your `opencode.json`:

```json
{
  "plugins": ["/path/to/itch/plugin"]
}
```

For example, if you cloned to `~/dev/itch`:

```json
{
  "plugins": ["~/dev/itch/plugin"]
}
```

## Usage

The plugin provides an `itch` tool that presents interactive questions to users and collects their responses.

### Example

When the LLM uses the itch tool, it generates questions like:

```json
{
  "topic": "learning preferences",
  "questions": [
    {
      "text": "What aspect of learning interests you most?",
      "choices": [
        { "label": "Visual learning with diagrams", "value": "visual" },
        { "label": "Hands-on practice", "value": "practice" },
        { "label": "Reading documentation", "value": "docs" },
        { "label": "Video tutorials", "value": "video" }
      ]
    }
  ]
}
```

The user sees an interactive terminal interface to select answers or provide custom responses.

## Configuration

Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ITCH_PATH` | (auto-detect) | Path to itch executable |
| `ITCH_TIMEOUT` | `300000` (5 min) | Subprocess timeout in milliseconds |
| `ITCH_DEBUG` | `false` | Enable debug logging |

The plugin auto-detects the itch CLI in this order:
1. `ITCH_PATH` environment variable (if set)
2. `itch` command in PATH
3. `uv run itch` (if uv is available)

## Optional: Create a Slash Command

OpenCode doesn't auto-install slash commands from plugins. To add a `/itch` command, create `.opencode/command/itch.md` in your project:

```markdown
---
description: Explore a topic through Socratic questioning
---
Generate 3-5 thoughtful Socratic questions about: $ARGUMENTS

Then use the itch tool to present them interactively and collect responses.
Summarize what we learned about the user's perspective.
```

## Requirements

- Python 3.11+
- The itch repository cloned and installed
- OpenCode with Bun runtime

## License

MIT
