# Project Context

## Purpose
Itch is an MCP server and CLI tool that enables AI agents to interactively explore topics with users through Socratic questioning. It provides a structured way for AI agents to ask probing questions and collect user responses via multiple-choice options or custom answers.

## Tech Stack
- Python 3.11+
- FastMCP (MCP Python SDK)
- Typer (CLI framework)
- Rich (terminal formatting)
- Questionary (interactive prompts)
- Pydantic (data models)

## Project Conventions

### Code Style
- Use type hints throughout
- Follow PEP 8 with 100-character line length
- Use Pydantic models for data validation
- Prefer explicit over implicit

### Architecture Patterns
- MCP server exposes tools for AI agents to initiate questioning
- CLI subprocess handles interactive user input
- Two-phase flow: AI generates questions → CLI presents to user
- JSON communication between MCP tools and CLI

### Testing Strategy
- Unit tests with pytest
- Test models independently
- Mock subprocess calls for CLI tests

### Git Workflow
- Feature branches from main
- Descriptive commit messages
- PR-based code review

## Domain Context
- **Socratic Method**: Questioning technique that encourages critical thinking
- **MCP (Model Context Protocol)**: Protocol for AI agents to access external tools
- **Interactive CLI**: Terminal-based user interface with keyboard navigation

## Important Constraints
- CLI must support non-TTY environments (subprocess from MCP)
- Questions limited to 1-20 per session
- 5-minute timeout on interactive sessions
- JSON format for inter-process communication

## External Dependencies
- MCP Python SDK for server implementation
- Questionary for interactive prompts (requires TTY)
