# Tasks: Add Question Types

## 1. Python Models

- [x] 1.1 Add `QuestionType` literal type (`select`, `confirm`, `text`, `scale`, `checkbox`)
- [x] 1.2 Add `type` field to `Question` model with default `"select"`
- [x] 1.3 Add `scale_labels` field (optional tuple for low/high labels)
- [x] 1.4 Make `choices` optional (only required for select/checkbox)
- [x] 1.5 Update `Answer` model to support list values for checkbox

## 2. Questioner Implementation

- [x] 2.1 Add `ask_confirm()` function using `questionary.confirm()`
- [x] 2.2 Add `ask_text()` function using `questionary.text()`
- [x] 2.3 Add `ask_scale()` function using `questionary.select()` with 1-5 scale
- [x] 2.4 Add `ask_checkbox()` function using `questionary.checkbox()`
- [x] 2.5 Update `ask_question()` dispatcher to route by question type
- [x] 2.6 Update `display_question_header()` to show type-appropriate hints

## 3. Server Validation

- [x] 3.1 Update `validate_questions()` to validate type-specific requirements
- [x] 3.2 Ensure select/checkbox require choices
- [x] 3.3 Ensure confirm/text don't require choices
- [x] 3.4 Validate scale_labels format when provided

## 4. TypeScript Plugin

- [x] 4.1 Add `QuestionTypeSchema` Zod union
- [x] 4.2 Update `QuestionSchema` with type field
- [x] 4.3 Add `scale_labels` field to schema
- [x] 4.4 Make choices optional with conditional validation
- [x] 4.5 Update `AnswerSchema` for multi-value checkbox responses

## 5. Testing

- [x] 5.1 Add unit tests for each question type rendering
- [x] 5.2 Add validation tests for type-specific requirements
- [x] 5.3 Add integration test with mixed question types
- [x] 5.4 Test backward compatibility (questions without type field)

## 6. Documentation

- [x] 6.1 Update README with new question types
- [x] 6.2 Update AGENTS.md with model changes
- [x] 6.3 Add examples for each question type
