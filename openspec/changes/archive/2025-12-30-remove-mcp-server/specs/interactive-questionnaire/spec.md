# interactive-questionnaire Spec Delta

## MODIFIED Requirements

### Requirement: CLI Commands

The system SHALL provide CLI commands for asking questions and running demos, with full support for all question types.

#### Scenario: Ask command with JSON input
- **GIVEN** valid JSON with topic and questions
- **WHEN** user runs `itch ask --topic X --questions JSON`
- **THEN** the system parses all question fields including `type` and `scale_labels`, runs interactive session, and outputs answers as JSON

#### Scenario: Ask command parses question types
- **GIVEN** questions with various types (select, confirm, text, scale, checkbox)
- **WHEN** user runs `itch ask` with the questions
- **THEN** the system correctly parses the `type` field and routes to appropriate questioner handlers

#### Scenario: Ask command parses scale labels
- **GIVEN** a scale question with `scale_labels: ["Low", "High"]`
- **WHEN** user runs `itch ask` with the question
- **THEN** the system correctly parses `scale_labels` as a tuple and displays "1 - Low" and "5 - High" endpoints

#### Scenario: Ask command with missing type defaults to select
- **GIVEN** a question without a `type` field
- **WHEN** user runs `itch ask` with the question
- **THEN** the system defaults to `type: "select"`

#### Scenario: Ask command with null scale_labels
- **GIVEN** a scale question without `scale_labels` field
- **WHEN** user runs `itch ask` with the question
- **THEN** the system displays scale options 1-5 without endpoint labels

#### Scenario: Demo command with topic
- **GIVEN** a known topic with predefined questions
- **WHEN** user runs `itch demo learning`
- **THEN** the system runs an interactive session with predefined example questions for the topic

#### Scenario: Demo with unknown topic
- **GIVEN** an unknown topic
- **WHEN** user runs `itch demo` with a topic that has no predefined questions
- **THEN** the system generates generic fallback questions about the topic

#### Scenario: Invalid JSON input
- **GIVEN** malformed JSON in --questions argument
- **WHEN** user runs `itch ask --topic X --questions "not valid json"`
- **THEN** the system exits with code 1 and displays "Error parsing questions JSON" message

#### Scenario: Unknown question type graceful fallback
- **GIVEN** a question with unrecognized `type` value (e.g., `type: "invalid"`)
- **WHEN** user runs `itch ask` with the question
- **THEN** the system defaults to "select" type (graceful degradation via Pydantic validation)

#### Scenario: Empty scale_labels array handled
- **GIVEN** a scale question with `scale_labels: []` (empty array)
- **WHEN** user runs `itch ask` with the question
- **THEN** the system treats it as null and displays unlabeled scale options
