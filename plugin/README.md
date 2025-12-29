# opencode-itch

OpenCode plugin for Socratic questioning - explore topics through guided inquiry.

## Installation

### 1. Install the Python package

```bash
# Using pip
pip install itch

# Using pipx (recommended for CLI tools)
pipx install itch

# Using uv
uv pip install itch
```

### 2. Add to OpenCode config

Add `opencode-itch` to your `opencode.json`:

```json
{
  "plugins": ["opencode-itch"]
}
```

Or install directly:

```bash
npm install opencode-itch
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
- The `itch` Python package installed
- OpenCode with Bun runtime

## License

MIT
