"""Integration tests for Itch CLI and validation module."""

import json

from itch.models import Choice, Question
from itch.validation import validate_questions


class TestValidationModuleParity:
    """Tests to verify validation module matches expected plugin behavior."""

    def test_validation_accepts_all_question_types(self):
        """Test that validation accepts all 5 question types."""
        questions = [
            Question(
                text="Select question",
                type="select",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            ),
            Question(
                text="Confirm question",
                type="confirm",
            ),
            Question(
                text="Text question",
                type="text",
            ),
            Question(
                text="Scale question",
                type="scale",
                scale_labels=("Low", "High"),
            ),
            Question(
                text="Checkbox question",
                type="checkbox",
                choices=[
                    Choice(label="Option 1", value="1"),
                ],
            ),
        ]

        result, error = validate_questions(questions)

        assert error is None
        assert len(result) == 5
        assert result[0].type == "select"
        assert result[1].type == "confirm"
        assert result[2].type == "text"
        assert result[3].type == "scale"
        assert result[4].type == "checkbox"

    def test_validation_rejects_select_without_choices(self):
        """Test that validation rejects select questions without 2+ choices."""
        questions = [
            Question(
                text="Select question",
                type="select",
                choices=[Choice(label="A", value="a")],  # Only 1 choice
            ),
        ]

        _, error = validate_questions(questions)

        assert error is not None
        assert "at least 2 choice" in error.lower()

    def test_validation_rejects_checkbox_without_choices(self):
        """Test that validation rejects checkbox questions without choices."""
        questions = [
            Question(
                text="Checkbox question",
                type="checkbox",
                choices=[],
            ),
        ]

        _, error = validate_questions(questions)

        assert error is not None
        assert "at least 1 choice" in error.lower()

    def test_validation_preserves_scale_labels(self):
        """Test that scale_labels tuple is preserved through validation."""
        questions = [
            Question(
                text="Rate this",
                type="scale",
                scale_labels=("Not at all", "Completely"),
            ),
        ]

        result, error = validate_questions(questions)

        assert error is None
        assert result[0].scale_labels == ("Not at all", "Completely")


class TestCLIValidationConsistency:
    """Tests to verify CLI and validation module produce consistent results."""

    def test_json_roundtrip_preserves_question_type(self):
        """Test that question type survives JSON serialization."""
        original = Question(
            id=1,
            text="Confirm this",
            type="confirm",
        )

        # Serialize to JSON (as plugin would send)
        json_data = original.model_dump()
        json_str = json.dumps(json_data)

        # Parse back (as CLI would receive)
        parsed_data = json.loads(json_str)
        restored = Question(**parsed_data)

        assert restored.type == "confirm"

    def test_json_roundtrip_preserves_scale_labels(self):
        """Test that scale_labels survives JSON serialization."""
        original = Question(
            id=1,
            text="Rate this",
            type="scale",
            scale_labels=("Low", "High"),
        )

        # Serialize to JSON
        json_data = original.model_dump()
        json_str = json.dumps(json_data)

        # Parse back
        parsed_data = json.loads(json_str)
        # Note: JSON converts tuple to list, so we need to convert back
        if parsed_data.get("scale_labels"):
            parsed_data["scale_labels"] = tuple(parsed_data["scale_labels"])
        restored = Question(**parsed_data)

        assert restored.scale_labels == ("Low", "High")

    def test_validation_after_json_roundtrip(self):
        """Test that validation works after JSON roundtrip."""
        original_questions = [
            Question(
                text="Select one",
                type="select",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            ),
            Question(
                text="Yes or no?",
                type="confirm",
            ),
        ]

        # Serialize
        json_str = json.dumps([q.model_dump() for q in original_questions])

        # Parse back (mimicking CLI)
        parsed_data = json.loads(json_str)
        restored_questions = [Question(**q) for q in parsed_data]

        # Validate
        result, error = validate_questions(restored_questions)

        assert error is None
        assert len(result) == 2
        assert result[0].type == "select"
        assert result[1].type == "confirm"


class TestEdgeCases:
    """Edge case tests for the integration."""

    def test_empty_string_scale_labels_handled(self):
        """Test that empty strings in scale_labels are handled."""
        questions = [
            Question(
                text="Rate this",
                type="scale",
                scale_labels=("", ""),  # Empty labels
            ),
        ]

        result, error = validate_questions(questions)

        # Empty string labels should be allowed (they're valid strings)
        assert error is None
        assert result[0].scale_labels == ("", "")

    def test_allows_custom_preserved(self):
        """Test that allows_custom flag is preserved through validation."""
        questions = [
            Question(
                text="Select one",
                type="select",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
                allows_custom=False,
            ),
        ]

        result, error = validate_questions(questions)

        assert error is None
        assert result[0].allows_custom is False

    def test_unicode_in_questions(self):
        """Test that unicode characters are handled correctly."""
        questions = [
            Question(
                text="你好吗?",  # Chinese: How are you?
                type="select",
                choices=[
                    Choice(label="很好 (Good)", value="good"),
                    Choice(label="不好 (Bad)", value="bad"),
                ],
            ),
        ]

        result, error = validate_questions(questions)

        assert error is None
        assert "你好" in result[0].text
