"""MCP Server for Itch - Socratic questioning tool."""

import json
import subprocess
import sys
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from itch.models import Answer, ItchResponse, Question

# Create the MCP server
mcp = FastMCP(
    "Itch",
    instructions="""\
Itch is a Socratic questioning tool that helps explore topics through interactive dialogue.

Use the 'itch' tool to run an interactive questioning session with the user.
You must provide ALL questions upfront - the tool does not generate questions.

Workflow:
1. Generate Socratic questions about the topic (this is YOUR responsibility)
2. Call 'itch' with the topic and your pre-generated questions
3. The tool presents questions to the user and collects their answers
4. You receive the answers for further discussion

Question Types:
- select: Multiple choice (default) - requires 2+ choices
- confirm: Yes/No question - no choices needed
- text: Free-form text input - no choices needed
- scale: 1-5 rating - no choices needed, optional scale_labels
- checkbox: Multi-select - requires 1+ choices

Required question format:
- Each question needs 'text' (the question)
- 'type' is optional (defaults to "select")
- 'choices' required for select/checkbox types
- Each choice needs 'label' (display text) and 'value' (identifier)
- Optional: 'id' (auto-assigned), 'allows_custom' (default true)
- Optional: 'scale_labels' for scale type, e.g., ["Not at all", "Completely"]

Example:
{
  "topic": "machine learning",
  "questions": [
    {"text": "What interests you?", "choices": [
      {"label": "Applications", "value": "apps"},
      {"label": "Theory", "value": "theory"}
    ]},
    {"text": "Continue exploring?", "type": "confirm"},
    {"text": "Any specific questions?", "type": "text"},
    {"text": "Confidence level?", "type": "scale", "scale_labels": ["Low", "High"]}
  ]
}""",
)

# Constants
MAX_QUESTIONS = 20
MIN_CHOICES_SELECT = 2
MIN_CHOICES_CHECKBOX = 1
SCALE_LABELS_LENGTH = 2
SESSION_TIMEOUT = 300  # 5 minutes
SIGINT_EXIT_CODE = 130  # Standard exit code for SIGINT (Ctrl+C)


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
    """Validate questions and auto-assign IDs. Returns (processed_questions, error_message)."""
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


@mcp.tool()
def itch(
    topic: Annotated[str, Field(description="The topic to explore through Socratic questioning")],
    questions: Annotated[
        list[Question],
        Field(
            description=(
                "List of questions (1-20). Types: select (2+ choices), "
                "confirm, text, scale, checkbox (1+ choices)."
            )
        ),
    ],
) -> ItchResponse:
    """Run an interactive Socratic questioning session with the user.

    Present pre-generated questions to the user interactively and collect their answers.
    All questions must be provided upfront - the tool does not generate questions.

    Question types:
    - select: Multiple choice (default) - requires 2+ choices
    - confirm: Yes/No boolean question
    - text: Free-form text input
    - scale: 1-5 rating with optional endpoint labels
    - checkbox: Multi-select - requires 1+ choices

    Returns:
        ItchResponse with status, topic, questions (echoed), and answers array.
        Status is 'complete' on success, 'cancelled' if interrupted, or 'error' on failure.
    """
    # Validate topic
    if not topic or not topic.strip():
        return ItchResponse(
            status="error",
            topic=topic or "",
            error="Topic is required",
        )

    topic = topic.strip()

    # Validate and process questions
    processed_questions, error = validate_questions(questions)
    if error:
        return ItchResponse(
            status="error",
            topic=topic,
            error=error,
        )

    # Prepare questions for CLI (convert to dict for JSON serialization)
    questions_data = [q.model_dump() for q in processed_questions]

    try:
        # Run the CLI subprocess to collect answers
        result = subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "itch.cli",
                "ask",
                "--topic",
                topic,
                "--questions",
                json.dumps(questions_data),
            ],
            capture_output=True,
            text=True,
            timeout=SESSION_TIMEOUT,
            check=False,
        )

        # Check for cancellation (indicated by specific return code or empty output)
        if result.returncode != 0:
            stderr = result.stderr.strip() if result.stderr else ""
            # Check if it was a user cancellation
            if "cancelled" in stderr.lower() or result.returncode == SIGINT_EXIT_CODE:
                # Try to parse partial answers from stdout
                partial_answers: list[Answer] = []
                if result.stdout.strip():
                    try:
                        answers_data = json.loads(result.stdout)
                        partial_answers = [Answer(**a) for a in answers_data]
                    except (json.JSONDecodeError, ValueError):
                        pass

                return ItchResponse(
                    status="cancelled",
                    topic=topic,
                    questions=processed_questions,
                    answers=partial_answers,
                )

            return ItchResponse(
                status="error",
                topic=topic,
                questions=processed_questions,
                error=stderr or "CLI exited with error",
            )

        # Parse the CLI output (JSON)
        try:
            answers_data = json.loads(result.stdout)
            answers = [Answer(**a) for a in answers_data]
            return ItchResponse(
                status="complete",
                topic=topic,
                questions=processed_questions,
                answers=answers,
            )
        except json.JSONDecodeError as e:
            return ItchResponse(
                status="error",
                topic=topic,
                questions=processed_questions,
                error=f"Failed to parse CLI output: {e}",
            )

    except subprocess.TimeoutExpired:
        return ItchResponse(
            status="error",
            topic=topic,
            questions=processed_questions,
            error="Session timed out after 5 minutes",
        )
    except OSError as e:
        return ItchResponse(
            status="error",
            topic=topic,
            questions=processed_questions,
            error=f"Failed to run CLI: {e}",
        )


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
