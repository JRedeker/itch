# Itch - Agent Instructions

Instructions for AI coding agents working on this project.

## Project Overview

Itch is an MCP server and CLI tool for Socratic questioning. It enables AI agents to
interactively explore topics with users through pre-generated questions.

**Key components:**
- `src/itch/server.py` - MCP server with single `itch` tool
- `src/itch/cli.py` - Typer CLI with `ask`, `demo`, `version` commands
- `src/itch/models.py` - Pydantic models (Question, Choice, Answer, ItchResponse)
- `src/itch/questioner.py` - Interactive questionnaire using questionary
- `src/itch/prompts.py` - Internal prompt templates (NOT exposed via MCP)

## Build & Development Commands

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

## Testing

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

# Run with coverage (if installed)
uv run pytest --cov=itch
```

## Linting & Type Checking

```bash
# Run ruff linter (strict ruleset)
uv run ruff check src/ tests/

# Run ruff with auto-fix
uv run ruff check --fix src/ tests/

# Run ty type checker (Astral's fast type checker)
uv run ty check src/

# Run all checks
uv run ruff check src/ tests/ && uv run ty check src/ && uv run pytest
```

## Code Style Guidelines

### Python Version
- Target Python 3.11+ (see `pyproject.toml`)
- Use modern syntax: `list[X]` not `List[X]`, `X | None` not `Optional[X]`

### Formatting
- Line length: 100 characters
- Use ruff for linting with strict ruleset (50+ rule categories enabled)
- Use ty for type checking (Astral's 10,500+ tokens/sec type checker)

### Imports
Order imports as: stdlib, third-party, local. Use absolute imports.
```python
import json
import subprocess
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from itch.models import Answer, Choice, Question
```

### Type Hints
- Always use type hints for function signatures
- Use `Annotated` with `Field` for MCP tool parameters
- Use `Literal` for constrained string types
- Use `| None` instead of `Optional`

```python
def validate_questions(
    questions: list[Question],
) -> tuple[list[Question], str | None]:
    ...

status: Literal["complete", "cancelled", "error"]
```

### Pydantic Models
- Use `Field(description=...)` for all fields exposed to MCP
- Use `Field(default_factory=list)` for mutable defaults
- Document models with docstrings

```python
class Choice(BaseModel):
    """A single choice option for a question."""
    label: str = Field(description="Display text shown to user")
    value: str = Field(description="Identifier returned when selected")
```

### Naming Conventions
- Classes: PascalCase (`ItchResponse`, `Question`)
- Functions/variables: snake_case (`validate_questions`, `processed_questions`)
- Constants: UPPER_SNAKE_CASE (`MAX_QUESTIONS`, `SESSION_TIMEOUT`)
- Private functions: prefix with underscore (`_helper_function`)

### Error Handling
- Return structured error responses, don't raise exceptions to MCP clients
- Use tuple returns for validation: `(result, error_message)`
- Include context in error messages (e.g., question index)

```python
if not questions:
    return [], "At least one question is required"

if len(q.choices) < MIN_CHOICES:
    return [], f"Question {i + 1} must have at least {MIN_CHOICES} choices"
```

### Docstrings
Use triple quotes for all public functions and classes:
```python
def validate_questions(
    questions: list[Question],
) -> tuple[list[Question], str | None]:
    """Validate questions and auto-assign IDs.
    
    Returns:
        Tuple of (processed_questions, error_message).
        error_message is None on success.
    """
```

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

<!-- OPENSPEC:START -->
Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts
- Sounds ambiguous and you need the authoritative spec before coding
<!-- OPENSPEC:END -->
