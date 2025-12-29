# Socratic Prompts

The socratic prompts capability provides prompt templates and example questions for generating Socratic-style questions. These are used internally by the CLI demo command and can be referenced by AI agents when preparing questions, but are NOT exposed via MCP.

## ADDED Requirements

### Requirement: System Prompt Template

The system SHALL provide a system prompt template that describes the Socratic questioning approach for reference.

#### Scenario: System prompt content

- **WHEN** the system prompt template is accessed
- **THEN** it describes the Socratic questioner role, including guidance to start with fundamentals, challenge assumptions, connect to broader concepts, and provide meaningful multiple choice options

#### Scenario: Internal use only

- **WHEN** the MCP server is queried for available prompts
- **THEN** the system prompt is NOT exposed as an MCP prompt (it exists only as a reference template in the codebase)

### Requirement: Question Generation Template

The system SHALL provide a generation prompt template that describes the expected JSON structure for questions.

#### Scenario: JSON format specification

- **WHEN** the generation template is accessed
- **THEN** it specifies questions must have id (integer), text (string), and choices array with label and value properties

#### Scenario: Internal use only

- **WHEN** the MCP server is queried for available prompts
- **THEN** the generation template is NOT exposed as an MCP prompt (AI agents generate questions independently before calling the tool)

### Requirement: Example Questions

The system SHALL provide pre-defined example questions for CLI demonstration purposes.

#### Scenario: Example questions for learning topic

- **WHEN** requesting example questions for "learning"
- **THEN** the system provides at least 3 questions about learning with 4 choices each covering different perspectives (career, understanding, growth, practical)

#### Scenario: Example question structure

- **WHEN** example questions are retrieved
- **THEN** each question has id, text, and choices with label and value properties matching the Question model

#### Scenario: Used by demo command

- **WHEN** user runs `itch demo learning`
- **THEN** the CLI uses these predefined example questions for the interactive session

### Requirement: Progressive Depth Guidance

The prompt templates SHALL include guidance for questions that progress from simple to nuanced.

#### Scenario: Question progression guidance

- **WHEN** the generation template is accessed
- **THEN** it includes guidance that questions should start simple and progressively become more nuanced, exploring different dimensions of the topic
