# Itch

MCP server and CLI tool for Socratic questioning - helps AI agents interactively explore topics with users.

## Installation

```bash
uv sync
```

## Usage

### As MCP Server

```bash
itch-server
```

### CLI Demo

```bash
itch demo learning
itch demo "machine learning" --max 5
```

## MCP Tool

The `itch` tool accepts a topic and pre-generated questions, then presents them interactively to the user.

**Important**: AI agents must generate questions before calling the tool. The server does not generate questions.

### Example Call

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

### Question Format

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The question to display |
| `choices` | array | Yes | List of answer options (min 2) |
| `id` | int | No | Question ID (auto-assigned if missing) |
| `allows_custom` | bool | No | Show "Other" option (default: true) |

### Choice Format

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Display text shown to user |
| `value` | string | Yes | Identifier returned when selected |

### Response

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

Status can be `complete`, `cancelled` (user interrupted), or `error`.

### Validation

- Topic: Required, non-empty
- Questions: 1-20 required
- Each question: Must have text and at least 2 choices
- Each choice: Must have label and value
