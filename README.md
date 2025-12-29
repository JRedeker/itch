# Itch

MCP server and CLI tool for Socratic questioning - helps AI agents interactively explore topics with users through guided inquiry.

## Features

- Interactive terminal UI for answering questions (via [questionary](https://github.com/tmbo/questionary))
- Multiple-choice questions with optional custom "Other" responses
- Structured JSON responses for AI agent consumption
- Two integration options: OpenCode plugin or standalone MCP server

## Installation

### Option 1: OpenCode Plugin (Recommended)

The OpenCode plugin provides seamless integration with [OpenCode](https://opencode.ai).

**Step 1: Clone and install**

```bash
git clone https://github.com/JRedeker/itch.git
cd itch
uv sync
```

**Step 2: Add to opencode.json**

```json
{
  "plugins": ["/path/to/itch/plugin"]
}
```

**Configuration (optional):**

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ITCH_PATH` | (auto-detect) | Explicit path to itch executable |
| `ITCH_TIMEOUT` | `300000` (5 min) | Subprocess timeout in milliseconds |
| `ITCH_DEBUG` | `false` | Enable debug logging |

See [plugin/README.md](plugin/README.md) for more details.

### Option 2: MCP Server

For use with Claude Desktop, Cursor, or other MCP clients.

**Step 1: Clone and install**

```bash
git clone https://github.com/JRedeker/itch.git
cd itch
uv sync
```

**Step 2: Add to your MCP client config**

```json
{
  "mcpServers": {
    "itch": {
      "command": "uv",
      "args": ["run", "itch-server"],
      "cwd": "/path/to/itch"
    }
  }
}
```

## Usage

### CLI Demo

Try the interactive demo to see how it works:

```bash
uv run itch demo learning
uv run itch demo "machine learning" --max 5
```

### As MCP Server

```bash
uv run itch-server
```

## The `itch` Tool

The `itch` tool accepts a topic and pre-generated questions, then presents them interactively to the user.

**Important**: AI agents must generate questions before calling the tool. The tool does not generate questions - it only presents them and collects responses.

### Example Tool Call

```json
{
  "topic": "machine learning",
  "questions": [
    {
      "text": "What interests you most about ML?",
      "choices": [
        {"label": "Practical applications", "value": "practical"},
        {"label": "Theoretical foundations", "value": "theory"},
        {"label": "Career opportunities", "value": "career"}
      ]
    },
    {
      "text": "How would you describe your current ML knowledge?",
      "choices": [
        {"label": "Complete beginner", "value": "beginner"},
        {"label": "Some familiarity", "value": "familiar"},
        {"label": "Intermediate", "value": "intermediate"},
        {"label": "Advanced", "value": "advanced"}
      ],
      "allows_custom": false
    }
  ]
}
```

### Question Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The question to display |
| `choices` | array | Yes | List of answer options (minimum 2) |
| `id` | int | No | Question ID (auto-assigned if not provided) |
| `allows_custom` | bool | No | Show "Other" option for custom answers (default: true) |

### Choice Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Display text shown to user |
| `value` | string | Yes | Identifier returned when selected |

### Response Schema

```json
{
  "status": "complete",
  "topic": "machine learning",
  "questions": [...],
  "answers": [
    {"question_id": 1, "selected_value": "practical", "is_custom": false},
    {"question_id": 2, "selected_value": "beginner", "is_custom": false}
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"complete"`, `"cancelled"`, or `"error"` |
| `topic` | string | The topic that was explored |
| `questions` | array | The questions that were asked (echoed back) |
| `answers` | array | User's answers to each question |
| `error` | string? | Error message (only if status is `"error"`) |

### Validation Rules

- **Topic**: Required, non-empty string
- **Questions**: 1-20 questions required
- **Each question**: Must have non-empty text and at least 2 choices
- **Each choice**: Must have non-empty label and value

## Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for Python dependency management
- Node.js 22+ (for plugin development)

### Setup

```bash
# Clone the repository
git clone https://github.com/JRedeker/itch.git
cd itch

# Install Python dependencies
uv sync

# Install plugin dependencies (optional)
cd plugin && npm install
```

### Running Tests

```bash
# Python tests
uv run pytest

# All quality checks
uv run ruff check src/ tests/ && uv run ty check src/ && uv run pytest

# TypeScript checks (in plugin/)
cd plugin && npm run check
```

## License

MIT

## Repository

https://github.com/JRedeker/itch
