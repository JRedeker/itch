## ADDED Requirements

### Requirement: Question Type Support

The system SHALL support multiple question types to enable diverse Socratic exploration patterns.

#### Scenario: Select question (multiple choice)

- **WHEN** question has type "select" with choices
- **THEN** the system displays choices as selectable options and returns the selected value

#### Scenario: Confirm question (yes/no)

- **WHEN** question has type "confirm"
- **THEN** the system displays a yes/no prompt and returns a boolean value as string ("true"/"false")

#### Scenario: Text question (free-form)

- **WHEN** question has type "text"
- **THEN** the system displays a text input prompt and returns the entered string

#### Scenario: Scale question (1-5 rating)

- **WHEN** question has type "scale"
- **THEN** the system displays options 1-5 with optional endpoint labels and returns the selected number as string

#### Scenario: Scale question with labels

- **WHEN** question has type "scale" and scale_labels is ["Not at all", "Completely"]
- **THEN** the system displays "1 - Not at all" through "5 - Completely" as options

#### Scenario: Checkbox question (multi-select)

- **WHEN** question has type "checkbox" with choices
- **THEN** the system allows selecting multiple options and returns a comma-separated list of values

### Requirement: Question Type Validation

The system SHALL validate question configuration based on type.

#### Scenario: Select requires choices

- **WHEN** question has type "select" with empty or missing choices
- **THEN** the system returns validation error "Select questions require at least 2 choices"

#### Scenario: Checkbox requires choices

- **WHEN** question has type "checkbox" with empty or missing choices
- **THEN** the system returns validation error "Checkbox questions require at least 1 choice"

#### Scenario: Confirm ignores choices

- **WHEN** question has type "confirm" with choices provided
- **THEN** the system ignores the choices and displays yes/no prompt

#### Scenario: Text ignores choices

- **WHEN** question has type "text" with choices provided
- **THEN** the system ignores the choices and displays text input

### Requirement: Backward Compatible Default Type

The system SHALL default to "select" type for backward compatibility.

#### Scenario: Question without type field

- **WHEN** question is provided without a type field
- **THEN** the system treats it as type "select" and requires choices

#### Scenario: Existing API unchanged

- **WHEN** client sends questions in the pre-existing format (no type field)
- **THEN** the system processes them identically to the previous behavior

## MODIFIED Requirements

### Requirement: Custom Answer Support

The system SHALL allow users to provide custom answers when the question type and configuration allow it.

#### Scenario: Custom answer option displayed

- **WHEN** question has type "select" and allows_custom set to true
- **THEN** the system displays "Other (type your own answer)" as an additional choice

#### Scenario: User selects custom answer

- **WHEN** user selects the custom answer option
- **THEN** the system prompts for free-text input and records the answer with is_custom flag set to true

#### Scenario: Custom answer disabled

- **WHEN** question has allows_custom set to false
- **THEN** the system does not display the custom answer option

#### Scenario: Custom answer not applicable

- **WHEN** question has type "confirm", "text", or "scale"
- **THEN** the system ignores allows_custom (these types have inherent custom input or fixed options)

#### Scenario: Checkbox with custom answer

- **WHEN** question has type "checkbox" and allows_custom set to true
- **THEN** the system displays "Other" as an additional selectable option that prompts for text when selected
