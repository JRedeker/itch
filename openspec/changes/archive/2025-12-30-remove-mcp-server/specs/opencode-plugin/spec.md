# opencode-plugin Spec Delta

## MODIFIED Requirements

### Requirement: Itch Tool Registration

The plugin SHALL register an `itch` tool using `@opencode-ai/plugin` SDK as the sole integration path for Itch functionality.

#### Scenario: Tool schema definition
- **GIVEN** the itch tool is registered
- **WHEN** OpenCode queries available tools
- **THEN** the tool has description, and args schema for `topic` (string) and `questions` (array of Question objects)

#### Scenario: Question object schema
- **GIVEN** a question is provided to the itch tool
- **WHEN** the schema is validated
- **THEN** each question has `text` (string), optional `type` (select|confirm|text|scale|checkbox), and `choices` (array of {label, value} objects, required for select/checkbox)

#### Scenario: Optional question fields
- **GIVEN** a question is provided
- **WHEN** `id`, `allows_custom`, `type`, or `scale_labels` are omitted
- **THEN** defaults are applied (auto-increment ID, allows_custom=true, type=select, scale_labels=null)

#### Scenario: Primary integration path
- **GIVEN** a user wants to use Itch with an AI agent
- **WHEN** they configure their environment
- **THEN** they install the OpenCode plugin (MCP server is no longer available)

#### Scenario: Plugin discovers Python CLI
- **GIVEN** the plugin is initialized
- **WHEN** the itch tool is invoked
- **THEN** the plugin resolves the Python CLI via ITCH_PATH, PATH lookup, or `uv run itch`

#### Scenario: Plugin handles CLI not found
- **GIVEN** the Python CLI is not installed
- **WHEN** the itch tool is invoked
- **THEN** the plugin returns an error with installation instructions

#### Scenario: Plugin handles subprocess timeout
- **GIVEN** the CLI subprocess exceeds the configured timeout
- **WHEN** the timeout expires
- **THEN** the plugin terminates the subprocess and returns status "error" with timeout message

#### Scenario: Plugin handles user cancellation
- **GIVEN** the user presses Ctrl+C during questioning
- **WHEN** the subprocess exits with code 130
- **THEN** the plugin returns status "cancelled" with any partial answers

## ADDED Requirements

### Requirement: Migration from MCP Server

Users migrating from the MCP server integration SHALL have clear documentation and equivalent functionality in the plugin.

#### Scenario: Feature parity with MCP server
- **GIVEN** a user previously used the MCP server
- **WHEN** they migrate to the OpenCode plugin
- **THEN** all question types, validation rules, and response formats are identical

#### Scenario: Migration documentation
- **GIVEN** a user reads the README
- **WHEN** they look for migration guidance
- **THEN** they find instructions to replace `itch-server` with the OpenCode plugin

#### Scenario: Breaking change acknowledgment
- **GIVEN** a user attempts to run `itch-server`
- **WHEN** the command is not found
- **THEN** documentation explains the MCP server was removed and how to migrate
