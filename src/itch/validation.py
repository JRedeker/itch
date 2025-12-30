"""Validation logic for Itch questions.

This module contains the validation functions extracted from the MCP server
for use by CLI tests and other components.
"""

from itch.models import Question

# Constants
MAX_QUESTIONS = 20
MIN_CHOICES_SELECT = 2
MIN_CHOICES_CHECKBOX = 1
SCALE_LABELS_LENGTH = 2


def _validate_choices(q: Question, i: int, min_choices: int) -> str | None:
    """Validate choices for a question. Returns error message or None."""
    if len(q.choices) < min_choices:
        type_name = q.type.capitalize()
        return f"Question {i + 1}: {type_name} questions require at least {min_choices} choice(s)"

    for j, choice in enumerate(q.choices):
        if not choice.label or not choice.label.strip():
            return f"Question {i + 1}, choice {j + 1} is missing label"
        if not choice.value or not choice.value.strip():
            return f"Question {i + 1}, choice {j + 1} is missing value"

    return None


def _validate_question_type(q: Question, i: int) -> str | None:
    """Validate type-specific requirements. Returns error message or None."""
    if q.type == "select":
        return _validate_choices(q, i, MIN_CHOICES_SELECT)
    if q.type == "checkbox":
        return _validate_choices(q, i, MIN_CHOICES_CHECKBOX)
    if (
        q.type == "scale"
        and q.scale_labels is not None
        and len(q.scale_labels) != SCALE_LABELS_LENGTH
    ):
        return f"Question {i + 1}: scale_labels must have exactly 2 elements"
    # confirm and text types don't require choices
    return None


def _assign_question_id(q: Question, i: int, seen_ids: set[int]) -> tuple[Question, str | None]:
    """Assign ID to question if needed. Returns (question, error_message)."""
    if q.id is not None:
        if q.id in seen_ids:
            return q, f"Duplicate question ID: {q.id}"
        seen_ids.add(q.id)
        return q, None

    # Auto-assign ID
    new_id = i + 1
    while new_id in seen_ids:
        new_id += 1
    seen_ids.add(new_id)
    return Question(
        id=new_id,
        text=q.text,
        type=q.type,
        choices=q.choices,
        allows_custom=q.allows_custom,
        scale_labels=q.scale_labels,
    ), None


def validate_questions(
    questions: list[Question],
) -> tuple[list[Question], str | None]:
    """Validate questions and auto-assign IDs.

    Args:
        questions: List of Question objects to validate.

    Returns:
        Tuple of (processed_questions, error_message).
        If validation succeeds, error_message is None.
        If validation fails, processed_questions is an empty list.
    """
    if not questions:
        return [], "At least one question is required"

    if len(questions) > MAX_QUESTIONS:
        return [], f"Maximum {MAX_QUESTIONS} questions allowed per session"

    processed: list[Question] = []
    seen_ids: set[int] = set()

    for i, q in enumerate(questions):
        # Validate text
        if not q.text or not q.text.strip():
            return [], f"Question {i + 1} is missing text"

        # Type-specific validation
        type_error = _validate_question_type(q, i)
        if type_error:
            return [], type_error

        # Handle ID assignment
        question_with_id, id_error = _assign_question_id(q, i, seen_ids)
        if id_error:
            return [], id_error
        processed.append(question_with_id)

    return processed, None
