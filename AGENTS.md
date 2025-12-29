# Itch - Agent Instructions

Instructions for AI coding agents working on this project.

## Project Overview

Itch is an MCP server and CLI tool for Socratic questioning. It enables AI agents to interactively explore topics with users through pre-generated questions.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Integration Options                     │
├─────────────────────────────┬───────────────────────────────┤
│   OpenCode Plugin           │   MCP Server                  │
│   (plugin/index.ts)         │   (src/itch/server.py)        │
│   - TypeScript wrapper      │   - FastMCP server            │
│   - Spawns Python CLI       │   - Direct Python execution   │
└─────────────────────────────┴───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Python CLI Layer                         │
│   src/itch/cli.py - Typer CLI (ask, demo, version)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Components                          │
├─────────────────────────────┬───────────────────────────────┤
│   src/itch/questioner.py    │   src/itch/models.py          │
│   - Interactive UI          │   - Pydantic models           │
│   - questionary integration │   - Question, Choice, Answer  │
└─────────────────────────────┴───────────────────────────────┘
```

### Key Components

| File | Description |
|------|-------------|
| `src/itch/server.py` | MCP server with single `itch` tool |
| `src/itch/cli.py` | Typer CLI with `ask`, `demo`, `version` commands |
| `src/itch/models.py` | Pydantic models (Question, Choice, Answer, ItchResponse, QuestionType) |
| `src/itch/questioner.py` | Interactive questionnaire with type-specific handlers |
| `src/itch/prompts.py` | Internal prompt templates (NOT exposed via MCP) |
| `plugin/index.ts` | OpenCode plugin (TypeScript wrapper for Python CLI) |

## Build & Development Commands

### Python

```bash
# Install dependencies
uv sync

# Install with dev dependencies  
uv sync --all-extras

# Run MCP server
uv run itch-server

# Run CLI
uv run itch --help
uv run itch demo learning
uv run itch version
```

### OpenCode Plugin (TypeScript)

```bash
# Navigate to plugin directory
cd plugin

# Install dependencies
npm install

# Type check
npm run typecheck

# Lint
npm run lint

# Run all checks
npm run check

# Test plugin locally (from project root)
# Add to opencode.json: "plugins": ["./plugin"]
```

## Quality Checks

### Run All Checks

```bash
# Python checks
uv run ruff check src/ tests/ && uv run ty check src/ && uv run pytest

# TypeScript checks (in plugin/)
cd plugin && npm run check
```

### Python Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a single test file
uv run pytest tests/test_server.py

# Run a single test class
uv run pytest tests/test_server.py::TestValidateQuestions

# Run a single test method
uv run pytest tests/test_server.py::TestValidateQuestions::test_empty_questions_list

# Run tests matching a pattern
uv run pytest -k "validation"

# Run with coverage
uv run pytest --cov=itch
```

### Python Linting & Type Checking

```bash
# Run ruff linter (strict ruleset with 50+ rule categories)
uv run ruff check src/ tests/

# Run ruff with auto-fix
uv run ruff check --fix src/ tests/

# Run ty type checker (Astral's fast type checker)
uv run ty check src/
```

### TypeScript Linting & Type Checking

```bash
cd plugin

# Type check with TypeScript compiler
npm run typecheck    # or: npx tsc --noEmit

# Lint with ESLint (strict TypeScript rules)
npm run lint         # or: npx eslint index.ts

# Run both
npm run check
```

## Code Style Guidelines

### Python

**Version & Syntax:**
- Target Python 3.11+ (see `pyproject.toml`)
- Use modern syntax: `list[X]` not `List[X]`, `X | None` not `Optional[X]`

**Formatting:**
- Line length: 100 characters
- Use ruff for linting with strict ruleset
- Use ty for type checking

**Imports:**
Order imports as: stdlib, third-party, local. Use absolute imports.
```python
import json
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from itch.models import Answer, Choice, Question
```

**Type Hints:**
```python
def validate_questions(
    questions: list[Question],
) -> tuple[list[Question], str | None]:
    ...

status: Literal["complete", "cancelled", "error"]
```

**Pydantic Models:**
```python
class Choice(BaseModel):
    """A single choice option for a question."""
    label: str = Field(description="Display text shown to user")
    value: str = Field(description="Identifier returned when selected")
```

**Error Handling:**
- Return structured error responses, don't raise exceptions to MCP clients
- Use tuple returns for validation: `(result, error_message)`
- Include context in error messages (e.g., question index)

### TypeScript

**Style:**
- Use `tool.schema` (Zod) for schema definitions
- Use the `tool()` helper from `@opencode-ai/plugin`
- Return JSON strings from tool execute functions

**Example:**
```typescript
import { tool } from "@opencode-ai/plugin";
const z = tool.schema;

const QuestionSchema = z.object({
  text: z.string().min(1).describe("The question text"),
  choices: z.array(ChoiceSchema).min(2),
});
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `ItchResponse`, `Question` |
| Functions/variables | snake_case (Python) / camelCase (TS) | `validate_questions` / `validateQuestions` |
| Constants | UPPER_SNAKE_CASE | `MAX_QUESTIONS`, `DEFAULT_TIMEOUT_MS` |
| Private functions | underscore prefix | `_helper_function` |

## Testing Patterns

- Use pytest with classes for grouping related tests
- Test file naming: `test_<module>.py`
- Test function naming: `test_<what_is_being_tested>`

```python
class TestValidateQuestions:
    """Tests for the validate_questions function."""

    def test_empty_questions_list(self):
        """Test that empty questions list returns error."""
        questions, error = validate_questions([])
        assert error == "At least one question is required"
```

## OpenSpec Integration

This project uses OpenSpec for spec-driven development. See `openspec/AGENTS.md` for:
- Creating change proposals
- Spec format and conventions
- Project structure guidelines

**When to use OpenSpec:**
- Adding new features or capabilities
- Making breaking changes
- Changing architecture or patterns

**Current changes:**
- `add-question-types` - Add multiple question types (select, confirm, text, scale, checkbox)

<!-- OPENSPEC:START -->
Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts
- Sounds ambiguous and you need the authoritative spec before coding
<!-- OPENSPEC:END -->

## Plugin Architecture Notes

The OpenCode plugin (`plugin/index.ts`) uses a hybrid architecture:

1. **TypeScript wrapper** - Registers `itch` tool with OpenCode
2. **Python subprocess** - Spawns `itch ask` CLI for interactive questioning
3. **Multi-step discovery** - Finds Python itch via: `ITCH_PATH` → PATH → `uv run`

**Key design decisions:**
- Client-side validation before spawning subprocess (fail fast)
- Environment variable configuration (`ITCH_TIMEOUT`, `ITCH_DEBUG`, `ITCH_PATH`)
- Structured JSON responses matching Python models
- Timeout handling with subprocess termination
- Exit code 130 detection for user cancellation (Ctrl+C)
