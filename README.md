# Itch

MCP server and CLI tool for Socratic questioning - helps AI agents interactively explore topics with users through guided inquiry.

## Features

- Interactive terminal UI for answering questions (via [questionary](https://github.com/tmbo/questionary))
- **Multiple question types**: select (multiple choice), confirm (yes/no), text (free-form), scale (1-5 rating), checkbox (multi-select)
- Optional custom "Other" responses for select/checkbox questions
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

## Question Types

Itch supports five question types to enable diverse Socratic exploration:

| Type | Description | Choices Required |
|------|-------------|------------------|
| `select` | Multiple choice (default) | Yes (2+) |
| `confirm` | Yes/No boolean | No |
| `text` | Free-form text input | No |
| `scale` | 1-5 rating with optional labels | No |
| `checkbox` | Multi-select | Yes (1+) |

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
      "type": "select",
      "choices": [
        {"label": "Practical applications", "value": "practical"},
        {"label": "Theoretical foundations", "value": "theory"},
        {"label": "Career opportunities", "value": "career"}
      ]
    },
    {
      "text": "Would you like to explore this topic further?",
      "type": "confirm"
    },
    {
      "text": "What specific questions do you have?",
      "type": "text"
    },
    {
      "text": "How confident are you with the basics?",
      "type": "scale",
      "scale_labels": ["Not at all", "Very confident"]
    },
    {
      "text": "Which learning resources do you prefer?",
      "type": "checkbox",
      "choices": [
        {"label": "Online courses", "value": "courses"},
        {"label": "Books", "value": "books"},
        {"label": "Hands-on projects", "value": "projects"},
        {"label": "Tutorials", "value": "tutorials"}
      ]
    }
  ]
}
```

### Question Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The question to display |
| `type` | string | No | Question type: `select` (default), `confirm`, `text`, `scale`, `checkbox` |
| `choices` | array | Conditional | Required for `select` (2+) and `checkbox` (1+) |
| `id` | int | No | Question ID (auto-assigned if not provided) |
| `allows_custom` | bool | No | Show "Other" option for custom answers (default: true, select/checkbox only) |
| `scale_labels` | [string, string] | No | Labels for scale endpoints, e.g., `["Low", "High"]` |

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
    {"question_id": 2, "selected_value": "true", "is_custom": false},
    {"question_id": 3, "selected_value": "How do neural networks work?", "is_custom": false},
    {"question_id": 4, "selected_value": "3", "is_custom": false},
    {"question_id": 5, "selected_value": "courses,projects", "is_custom": false}
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

**Answer value formats by type:**
- `select`: The selected choice's `value`
- `confirm`: `"true"` or `"false"`
- `text`: The entered text string
- `scale`: `"1"` through `"5"`
- `checkbox`: Comma-separated values, e.g., `"a,b,c"`

### Validation Rules

- **Topic**: Required, non-empty string
- **Questions**: 1-20 questions required
- **Select questions**: Must have at least 2 choices
- **Checkbox questions**: Must have at least 1 choice
- **Each choice**: Must have non-empty label and value
- **Scale labels**: If provided, must be exactly 2 elements

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
