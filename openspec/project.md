# Project Context

## Purpose
Itch is a CLI tool and OpenCode plugin that enables AI agents to interactively explore topics with users through Socratic questioning. It provides a structured way for AI agents to ask probing questions and collect user responses via multiple-choice options or custom answers.

## Tech Stack
- Python 3.11+
- Typer (CLI framework)
- Rich (terminal formatting)
- Questionary (interactive prompts)
- Pydantic (data models)
- OpenCode Plugin SDK (TypeScript)

## Project Conventions

### Code Style
- Use type hints throughout
- Follow PEP 8 with 100-character line length
- Use Pydantic models for data validation
- Prefer explicit over implicit

### Architecture Patterns
- OpenCode plugin provides the integration point for AI agents
- Plugin spawns Python CLI subprocess for interactive user input
- Two-phase flow: AI generates questions → CLI presents to user
- JSON communication between plugin and CLI

### Testing Strategy
- Unit tests with pytest
- Test models independently
- Mock subprocess calls for CLI tests
- Integration tests for validation parity

### Git Workflow
- Feature branches from main
- Descriptive commit messages
- PR-based code review

## Domain Context
- **Socratic Method**: Questioning technique that encourages critical thinking
- **OpenCode Plugin**: Integration mechanism for AI agents in OpenCode
- **Interactive CLI**: Terminal-based user interface with keyboard navigation

## Important Constraints
- CLI must support non-TTY environments (subprocess from plugin)
- Questions limited to 1-20 per session
- 5-minute timeout on interactive sessions
- JSON format for inter-process communication

## External Dependencies
- Questionary for interactive prompts (requires TTY)
- OpenCode Plugin SDK for agent integration
