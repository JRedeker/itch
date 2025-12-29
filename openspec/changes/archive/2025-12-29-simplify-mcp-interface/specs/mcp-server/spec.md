# MCP Server

The MCP server capability exposes the `itch` tool that AI agents use to conduct Socratic questioning sessions with users. All questions must be provided upfront in a single call.

## ADDED Requirements

### Requirement: Interactive Question Tool

The system SHALL provide an `itch` tool that accepts a topic and a list of pre-generated questions, launching an interactive CLI session to collect user answers. All questions and choices MUST be provided upfront by the AI agent in a single call.

#### Scenario: Successful question session

- **WHEN** AI agent calls `itch` with topic "machine learning" and questions list containing 3 questions each with text and choices
- **THEN** the system validates input, launches the CLI subprocess, presents all questions sequentially to the user, collects answers, and returns status "complete" with topic, questions array (echoed back), and answers array

#### Scenario: Return structured output

- **WHEN** the session completes successfully
- **THEN** the system returns a Pydantic-validated response containing status, topic, questions (as provided), and answers array with question_id, selected_value, and is_custom flag for each answer

### Requirement: Input Validation

The system SHALL validate all input parameters before launching the interactive session, providing clear error messages for invalid input.

#### Scenario: Empty questions list

- **WHEN** AI agent calls `itch` with an empty questions list
- **THEN** the system returns status "error" with message "At least one question is required"

#### Scenario: Too many questions

- **WHEN** AI agent calls `itch` with more than 20 questions
- **THEN** the system returns status "error" with message "Maximum 20 questions allowed per session"

#### Scenario: Question missing text

- **WHEN** AI agent provides a question without a text field
- **THEN** the system returns status "error" with message identifying which question (by index) is missing text

#### Scenario: Question with insufficient choices

- **WHEN** AI agent provides a question with fewer than 2 choices
- **THEN** the system returns status "error" with message "Each question must have at least 2 choices" and identifies the invalid question by index

#### Scenario: Choice missing label or value

- **WHEN** AI agent provides a choice without label or value
- **THEN** the system returns status "error" with message identifying the malformed choice by question and choice index

#### Scenario: Topic validation

- **WHEN** AI agent calls `itch` with an empty or whitespace-only topic
- **THEN** the system returns status "error" with message "Topic is required"

#### Scenario: Question ID auto-assignment

- **WHEN** AI agent provides questions without explicit IDs
- **THEN** the system auto-assigns sequential IDs starting from 1

#### Scenario: Duplicate question IDs

- **WHEN** AI agent provides questions with duplicate IDs
- **THEN** the system returns status "error" with message identifying the duplicate ID

### Requirement: Structured Input Schema

The system SHALL accept questions as a structured list. FastMCP automatically converts JSON input to Pydantic models with validation.

#### Scenario: Question structure with Field descriptions

- **WHEN** AI agent provides questions as JSON
- **THEN** FastMCP converts each question to a Pydantic model accepting: id (optional int, auto-assigned if missing), text (required str, the question to ask), choices (required list of Choice objects, min 2), allows_custom (optional bool, default true)

#### Scenario: Choice structure with Field descriptions

- **WHEN** AI agent provides choices as JSON
- **THEN** FastMCP converts each choice to a Pydantic model accepting: label (required str, display text shown to user), value (required str, identifier returned when selected)

#### Scenario: Pydantic validation errors

- **WHEN** AI agent provides JSON that doesn't match the expected schema
- **THEN** the system returns status "error" with Pydantic validation error details

### Requirement: Error Handling

The system SHALL handle all error conditions gracefully and return structured error responses.

#### Scenario: Session timeout

- **WHEN** the interactive session exceeds 5 minutes without completion
- **THEN** the system returns status "error" with message "Session timed out after 5 minutes"

#### Scenario: CLI process error

- **WHEN** the CLI subprocess exits with non-zero return code
- **THEN** the system returns status "error" with the stderr output or a generic error message

#### Scenario: User cancellation

- **WHEN** user cancels the session (Ctrl+C)
- **THEN** the system returns status "cancelled" with partial answers collected up to cancellation point

#### Scenario: JSON parsing error

- **WHEN** the CLI returns malformed output
- **THEN** the system returns status "error" with message describing the parse failure

### Requirement: Custom Answer Support

The system SHALL support custom free-text answers when enabled for a question.

#### Scenario: Custom answer enabled by default

- **WHEN** a question does not specify allows_custom
- **THEN** the system defaults allows_custom to true, showing "Other" option to the user

#### Scenario: Custom answer disabled

- **WHEN** a question has allows_custom set to false
- **THEN** the system does not show the "Other" option for that question

#### Scenario: Custom answer in response

- **WHEN** user selects "Other" and enters custom text
- **THEN** the answer includes is_custom=true and selected_value contains the user's text

### Requirement: Server Instructions

The system SHALL provide server-level instructions explaining that AI agents must provide pre-generated questions with all choices when calling the `itch` tool.

#### Scenario: Server metadata available

- **WHEN** AI agent connects to the MCP server
- **THEN** the server provides instructions describing: the single-call workflow, required question format (text + choices), optional fields (id, allows_custom), and expected response structure

#### Scenario: Tool description with example

- **WHEN** AI agent lists available tools
- **THEN** the `itch` tool docstring includes a usage example showing the expected JSON structure:
```json
{
  "topic": "machine learning",
  "questions": [
    {
      "text": "What interests you most about ML?",
      "choices": [
        {"label": "Practical applications", "value": "practical"},
        {"label": "Theoretical foundations", "value": "theory"}
      ]
    }
  ]
}
```

#### Scenario: No MCP prompts exposed

- **WHEN** AI agent queries available MCP prompts
- **THEN** the server returns an empty list (prompt generation is the AI agent's responsibility)
