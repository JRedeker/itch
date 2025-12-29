"""MCP Server for Itch - Socratic questioning tool."""

import json
import subprocess
import sys
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from itch.models import Answer, Choice, ItchResponse, Question

# Create the MCP server
mcp = FastMCP(
    "Itch",
    instructions="""Itch is a Socratic questioning tool that helps explore topics through interactive dialogue.

Use the 'itch' tool to run an interactive questioning session with the user.
You must provide ALL questions upfront - the tool does not generate questions.

Workflow:
1. Generate Socratic questions about the topic (this is YOUR responsibility)
2. Call 'itch' with the topic and your pre-generated questions
3. The tool presents questions to the user and collects their answers
4. You receive the answers for further discussion

Required question format:
- Each question needs 'text' (the question) and 'choices' (list of options)
- Each choice needs 'label' (display text) and 'value' (identifier)
- Optional: 'id' (auto-assigned if missing), 'allows_custom' (default true)

Example call:
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
}""",
)

# Constants
MAX_QUESTIONS = 20
MIN_CHOICES = 2
SESSION_TIMEOUT = 300  # 5 minutes


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

        # Validate choices
        if len(q.choices) < MIN_CHOICES:
            return [], f"Question {i + 1} must have at least {MIN_CHOICES} choices"

        for j, choice in enumerate(q.choices):
            if not choice.label or not choice.label.strip():
                return [], f"Question {i + 1}, choice {j + 1} is missing label"
            if not choice.value or not choice.value.strip():
                return [], f"Question {i + 1}, choice {j + 1} is missing value"

        # Handle ID assignment
        if q.id is not None:
            if q.id in seen_ids:
                return [], f"Duplicate question ID: {q.id}"
            seen_ids.add(q.id)
            processed.append(q)
        else:
            # Auto-assign ID
            new_id = i + 1
            while new_id in seen_ids:
                new_id += 1
            seen_ids.add(new_id)
            processed.append(
                Question(
                    id=new_id,
                    text=q.text,
                    choices=q.choices,
                    allows_custom=q.allows_custom,
                )
            )

    return processed, None


@mcp.tool()
def itch(
    topic: Annotated[str, Field(description="The topic to explore through Socratic questioning")],
    questions: Annotated[
        list[Question],
        Field(
            description="List of pre-generated questions with choices (1-20 questions, each with 2+ choices)"
        ),
    ],
) -> ItchResponse:
    """Run an interactive Socratic questioning session with the user.

    Present pre-generated questions to the user interactively and collect their answers.
    All questions must be provided upfront - the tool does not generate questions.

    Example:
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

    Returns:
        ItchResponse with status, topic, questions (echoed), and answers array.
        Status is 'complete' on success, 'cancelled' if user interrupted, or 'error' on failure.
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
        result = subprocess.run(
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
        )

        # Check for cancellation (indicated by specific return code or empty output)
        if result.returncode != 0:
            stderr = result.stderr.strip() if result.stderr else ""
            # Check if it was a user cancellation
            if "cancelled" in stderr.lower() or result.returncode == 130:
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
    except Exception as e:
        return ItchResponse(
            status="error",
            topic=topic,
            questions=processed_questions,
            error=str(e),
        )


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
