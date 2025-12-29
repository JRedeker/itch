# Capability: OpenCode Plugin

OpenCode plugin integration for Itch, enabling native tool registration, event hooks, and npm distribution.

## ADDED Requirements

### Requirement: Plugin Entry Point

The plugin SHALL export a default function conforming to the OpenCode Plugin interface that initializes the Itch tool and event handlers.

#### Scenario: Plugin initialization
- **GIVEN** OpenCode loads the plugin
- **WHEN** the plugin function is called with context
- **THEN** it returns an object with `tool` and optionally `event` handlers

#### Scenario: Context access
- **GIVEN** the plugin is initializing
- **WHEN** the context is provided
- **THEN** the plugin has access to `directory`, `$` (shell), and `project` information

### Requirement: Itch Tool Registration

The plugin SHALL register an `itch` tool using `@opencode-ai/plugin` SDK that mirrors the MCP server's functionality.

#### Scenario: Tool schema definition
- **GIVEN** the itch tool is registered
- **WHEN** OpenCode queries available tools
- **THEN** the tool has description, and args schema for `topic` (string) and `questions` (array of Question objects)

#### Scenario: Question object schema
- **GIVEN** a question is provided to the itch tool
- **WHEN** the schema is validated
- **THEN** each question has `text` (string) and `choices` (array of {label, value} objects)

#### Scenario: Optional question fields
- **GIVEN** a question is provided
- **WHEN** `id` or `allows_custom` are omitted
- **THEN** defaults are applied (auto-increment ID, allows_custom=true)

### Requirement: Client-Side Validation

The plugin SHALL validate questions in TypeScript before spawning the Python subprocess to fail fast with clear error messages.

#### Scenario: Empty questions list
- **GIVEN** an empty questions array
- **WHEN** the itch tool is called
- **THEN** returns error "At least one question is required" without spawning subprocess

#### Scenario: Too many questions
- **GIVEN** more than 20 questions
- **WHEN** the itch tool is called
- **THEN** returns error "Maximum 20 questions allowed" without spawning subprocess

#### Scenario: Question missing text
- **GIVEN** a question with empty or whitespace-only text
- **WHEN** the itch tool is called
- **THEN** returns error identifying the specific question index

#### Scenario: Insufficient choices
- **GIVEN** a question with fewer than 2 choices
- **WHEN** the itch tool is called
- **THEN** returns error identifying the specific question index

### Requirement: Python Package Discovery

The plugin SHALL resolve the itch Python package location using a multi-step fallback chain.

#### Scenario: Explicit path override
- **GIVEN** `ITCH_PATH` environment variable is set
- **WHEN** resolving the itch command
- **THEN** uses the specified path directly

#### Scenario: Global installation
- **GIVEN** `itch` command exists in PATH (via pip/pipx)
- **WHEN** resolving the itch command
- **THEN** uses `itch` directly

#### Scenario: uv-based execution
- **GIVEN** `itch` is not in PATH but `uv` is available
- **WHEN** resolving the itch command
- **THEN** uses `uv run itch`

#### Scenario: Package not found
- **GIVEN** none of the resolution methods succeed
- **WHEN** resolving the itch command
- **THEN** returns error with installation instructions for pip and uv

### Requirement: Python Subprocess Execution

The plugin SHALL spawn the Python CLI to execute interactive questioning sessions.

#### Scenario: Successful execution
- **GIVEN** valid topic and questions
- **WHEN** the itch tool is called
- **THEN** spawns the resolved itch command with `ask --topic <topic> --questions <json>`
- **AND** returns the parsed JSON response

#### Scenario: Subprocess timeout
- **GIVEN** the Python process does not respond within the configured timeout
- **WHEN** the timeout expires
- **THEN** the subprocess is terminated
- **AND** an error response with status "error" is returned

#### Scenario: User cancellation
- **GIVEN** the user presses Ctrl+C during questioning
- **WHEN** the subprocess exits with code 130
- **THEN** returns response with status "cancelled" and any partial answers

### Requirement: Plugin Configuration

The plugin SHALL support configuration via environment variables.

#### Scenario: Timeout configuration
- **GIVEN** `ITCH_TIMEOUT` environment variable is set
- **WHEN** the plugin spawns a subprocess
- **THEN** uses the specified timeout value in milliseconds

#### Scenario: Debug logging
- **GIVEN** `ITCH_DEBUG` environment variable is set to "true"
- **WHEN** the plugin executes
- **THEN** logs detailed debug information to console

#### Scenario: Default configuration
- **GIVEN** no environment variables are set
- **WHEN** the plugin executes
- **THEN** uses defaults: 5-minute timeout, no debug logging

### Requirement: Error Handling

The plugin SHALL provide clear, actionable error messages for common failure scenarios.

#### Scenario: Invalid JSON response
- **GIVEN** the subprocess completes
- **WHEN** stdout is not valid JSON
- **THEN** returns error with the raw output for debugging

#### Scenario: TTY not available
- **GIVEN** the environment does not support interactive prompts
- **WHEN** questionary fails to initialize
- **THEN** returns error explaining interactive mode requirement

#### Scenario: Subprocess crash
- **GIVEN** the Python process exits with non-zero code (not 130)
- **WHEN** checking the result
- **THEN** returns error with stderr content if available

### Requirement: npm Package Distribution

The plugin SHALL be publishable to npm as `opencode-itch` for easy installation.

#### Scenario: Package installation
- **GIVEN** a user adds `opencode-itch` to their opencode.json plugins array
- **WHEN** OpenCode starts
- **THEN** the plugin is loaded and itch tool is available

#### Scenario: Package metadata
- **GIVEN** the npm package is published
- **WHEN** users search npm for "opencode itch"
- **THEN** the package has keywords (opencode, plugin, socratic, questioning), description, and repository link

#### Scenario: Version compatibility logging
- **GIVEN** the plugin is loaded
- **WHEN** initialization runs
- **THEN** the plugin logs a warning if Python itch version differs from plugin version

### Requirement: Documentation for Slash Command

The plugin README SHALL document how users can optionally create a `/itch` slash command.

#### Scenario: Command template provided
- **GIVEN** a user reads the plugin README
- **WHEN** they want a /itch command
- **THEN** they find a copy-paste template for `.opencode/command/itch.md`

#### Scenario: Command is optional
- **GIVEN** a user installs the plugin
- **WHEN** they do not create the command file
- **THEN** the itch tool still works when invoked directly by the LLM
