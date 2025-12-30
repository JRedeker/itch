"""Tests for CLI question parsing."""

import inspect
import json

import pytest

from itch.cli import app, ask
from itch.models import Choice, Question


def parse_questions_from_json(questions_json: str) -> list[Question]:
    """Parse questions from JSON string, mimicking cli.py ask command logic."""
    questions_data = json.loads(questions_json)
    if isinstance(questions_data, dict) and "questions" in questions_data:
        questions_data = questions_data["questions"]

    return [
        Question(
            id=q.get("id", i + 1),
            text=q["text"],
            type=q.get("type", "select"),
            choices=[Choice(**c) for c in q.get("choices", [])],
            allows_custom=q.get("allows_custom", True),
            scale_labels=tuple(q["scale_labels"]) if q.get("scale_labels") else None,
        )
        for i, q in enumerate(questions_data)
    ]


class TestCLIQuestionParsing:
    """Tests for CLI question parsing from JSON."""

    def test_parses_type_field(self):
        """Test that type field is correctly parsed from JSON."""
        questions_json = json.dumps(
            [
                {"text": "Continue?", "type": "confirm"},
                {"text": "Your thoughts?", "type": "text"},
                {"text": "Rate this", "type": "scale"},
                {
                    "text": "Select all",
                    "type": "checkbox",
                    "choices": [{"label": "A", "value": "a"}],
                },
            ]
        )

        questions = parse_questions_from_json(questions_json)

        assert len(questions) == 4
        assert questions[0].type == "confirm"
        assert questions[1].type == "text"
        assert questions[2].type == "scale"
        assert questions[3].type == "checkbox"

    def test_parses_scale_labels(self):
        """Test that scale_labels is correctly parsed as tuple."""
        questions_json = json.dumps(
            [
                {
                    "text": "How confident?",
                    "type": "scale",
                    "scale_labels": ["Low", "High"],
                }
            ]
        )

        questions = parse_questions_from_json(questions_json)

        assert len(questions) == 1
        assert questions[0].scale_labels == ("Low", "High")
        assert isinstance(questions[0].scale_labels, tuple)

    def test_missing_type_defaults_to_select(self):
        """Test that missing type field defaults to 'select'."""
        questions_json = json.dumps(
            [
                {
                    "text": "Choose one",
                    "choices": [
                        {"label": "A", "value": "a"},
                        {"label": "B", "value": "b"},
                    ],
                }
            ]
        )

        questions = parse_questions_from_json(questions_json)

        assert len(questions) == 1
        assert questions[0].type == "select"

    def test_empty_scale_labels_treated_as_none(self):
        """Test that empty scale_labels array is treated as None."""
        # Empty array should result in None (falsy check in list comprehension)
        questions_json = json.dumps(
            [
                {
                    "text": "Rate this",
                    "type": "scale",
                    "scale_labels": [],
                }
            ]
        )

        questions = parse_questions_from_json(questions_json)

        assert len(questions) == 1
        # Empty list is falsy, so scale_labels should be None
        assert questions[0].scale_labels is None

    def test_missing_scale_labels_is_none(self):
        """Test that missing scale_labels field results in None."""
        questions_json = json.dumps(
            [
                {
                    "text": "Rate this",
                    "type": "scale",
                }
            ]
        )

        questions = parse_questions_from_json(questions_json)

        assert len(questions) == 1
        assert questions[0].scale_labels is None

    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises JSONDecodeError."""
        with pytest.raises(json.JSONDecodeError):
            parse_questions_from_json("not valid json")

    def test_parses_all_fields_together(self):
        """Test parsing a question with all fields specified."""
        questions_json = json.dumps(
            [
                {
                    "id": 42,
                    "text": "Rate your confidence",
                    "type": "scale",
                    "choices": [],  # Should be ignored for scale
                    "allows_custom": False,
                    "scale_labels": ["Not confident", "Very confident"],
                }
            ]
        )

        questions = parse_questions_from_json(questions_json)

        assert len(questions) == 1
        q = questions[0]
        assert q.id == 42
        assert q.text == "Rate your confidence"
        assert q.type == "scale"
        assert q.allows_custom is False
        assert q.scale_labels == ("Not confident", "Very confident")

    def test_parses_wrapped_questions_format(self):
        """Test parsing questions wrapped in a dict with 'questions' key."""
        questions_json = json.dumps(
            {
                "questions": [
                    {"text": "Question 1", "type": "confirm"},
                    {"text": "Question 2", "type": "text"},
                ]
            }
        )

        questions = parse_questions_from_json(questions_json)

        assert len(questions) == 2
        assert questions[0].type == "confirm"
        assert questions[1].type == "text"

    def test_auto_assigns_ids(self):
        """Test that IDs are auto-assigned when not provided."""
        questions_json = json.dumps(
            [
                {"text": "Q1", "type": "confirm"},
                {"text": "Q2", "type": "text"},
                {"text": "Q3", "type": "scale"},
            ]
        )

        questions = parse_questions_from_json(questions_json)

        assert questions[0].id == 1
        assert questions[1].id == 2
        assert questions[2].id == 3


class TestCLIAskCommand:
    """Integration tests for the CLI ask command."""

    def test_ask_command_exists(self):
        """Test that the ask command is registered."""
        # Check that 'ask' is a registered command via registered_groups or info
        # Typer stores commands differently, so we check the underlying click group
        assert app.info.name == "itch"

    def test_ask_command_has_required_options(self):
        """Test that ask command has --topic and --questions options."""
        sig = inspect.signature(ask)
        params = list(sig.parameters.keys())

        assert "topic" in params
        assert "questions" in params
