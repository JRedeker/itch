# interactive-questionnaire Specification

## Purpose
TBD - created by archiving change simplify-mcp-interface. Update Purpose after archive.
## Requirements
### Requirement: Question Presentation

The system SHALL display each question with a formatted header showing question number and total, followed by multiple choice options.

#### Scenario: Display question with progress

- **WHEN** presenting question 2 of 5
- **THEN** the system displays a panel with "Question 2/5" header and the question text

#### Scenario: Display multiple choice options

- **WHEN** a question has choices with labels and values
- **THEN** the system displays each choice as a selectable option with keyboard shortcuts

### Requirement: Custom Answer Support

The system SHALL allow users to provide custom answers when the question allows it.

#### Scenario: Custom answer option displayed

- **WHEN** question has allows_custom set to true
- **THEN** the system displays "Other (type your own answer)" as an additional choice

#### Scenario: User selects custom answer

- **WHEN** user selects the custom answer option
- **THEN** the system prompts for free-text input and records the answer with is_custom flag set to true

#### Scenario: Custom answer disabled

- **WHEN** question has allows_custom set to false
- **THEN** the system does not display the custom answer option

### Requirement: Answer Collection

The system SHALL collect answers sequentially and support session cancellation.

#### Scenario: Complete all questions

- **WHEN** user answers all questions in sequence
- **THEN** the system returns a list of Answer objects with question_id, selected_value, and is_custom flag

#### Scenario: User cancels session

- **WHEN** user presses Ctrl+C during a question
- **THEN** the system displays cancellation message and returns answers collected so far

### Requirement: Session Summary

The system SHALL display a summary of the completed session showing all questions and answers.

#### Scenario: Display summary after completion

- **WHEN** questionnaire completes (all answered or cancelled)
- **THEN** the system displays a panel with topic, each question text, and corresponding answer (marking custom answers)

### Requirement: CLI Commands

The system SHALL provide CLI commands for asking questions and running demos.

#### Scenario: Ask command with JSON input

- **WHEN** user runs `itch ask --topic X --questions JSON`
- **THEN** the system parses questions, runs interactive session, and outputs answers as JSON

#### Scenario: Demo command with topic

- **WHEN** user runs `itch demo learning`
- **THEN** the system runs an interactive session with predefined example questions for the topic

#### Scenario: Demo with unknown topic

- **WHEN** user runs `itch demo` with a topic that has no predefined questions
- **THEN** the system generates generic fallback questions about the topic

