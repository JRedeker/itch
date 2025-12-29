"""Tests for the MCP server validation logic."""

import pytest

from itch.models import Choice, Question
from itch.server import validate_questions


class TestValidateQuestions:
    """Tests for the validate_questions function."""

    def test_empty_questions_list(self):
        """Test that empty questions list returns error."""
        questions, error = validate_questions([])
        assert error == "At least one question is required"
        assert questions == []

    def test_too_many_questions(self):
        """Test that more than 20 questions returns error."""
        questions = [
            Question(
                text=f"Question {i}",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            )
            for i in range(21)
        ]
        result, error = validate_questions(questions)
        assert error == "Maximum 20 questions allowed per session"
        assert result == []

    def test_question_missing_text(self):
        """Test that question with empty text returns error."""
        questions = [
            Question(
                text="",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            )
        ]
        result, error = validate_questions(questions)
        assert error == "Question 1 is missing text"
        assert result == []

    def test_question_whitespace_only_text(self):
        """Test that question with whitespace-only text returns error."""
        questions = [
            Question(
                text="   ",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            )
        ]
        result, error = validate_questions(questions)
        assert error == "Question 1 is missing text"
        assert result == []

    def test_question_insufficient_choices(self):
        """Test that question with fewer than 2 choices returns error."""
        questions = [
            Question(
                text="What is your favorite color?",
                choices=[Choice(label="Red", value="red")],
            )
        ]
        result, error = validate_questions(questions)
        assert error == "Question 1 must have at least 2 choices"
        assert result == []

    def test_choice_missing_label(self):
        """Test that choice with empty label returns error."""
        questions = [
            Question(
                text="What is your favorite color?",
                choices=[
                    Choice(label="", value="red"),
                    Choice(label="Blue", value="blue"),
                ],
            )
        ]
        result, error = validate_questions(questions)
        assert error == "Question 1, choice 1 is missing label"
        assert result == []

    def test_choice_missing_value(self):
        """Test that choice with empty value returns error."""
        questions = [
            Question(
                text="What is your favorite color?",
                choices=[
                    Choice(label="Red", value=""),
                    Choice(label="Blue", value="blue"),
                ],
            )
        ]
        result, error = validate_questions(questions)
        assert error == "Question 1, choice 1 is missing value"
        assert result == []

    def test_duplicate_question_ids(self):
        """Test that duplicate question IDs return error."""
        questions = [
            Question(
                id=1,
                text="Question 1",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            ),
            Question(
                id=1,
                text="Question 2",
                choices=[
                    Choice(label="C", value="c"),
                    Choice(label="D", value="d"),
                ],
            ),
        ]
        result, error = validate_questions(questions)
        assert error == "Duplicate question ID: 1"
        assert result == []

    def test_auto_assign_ids(self):
        """Test that IDs are auto-assigned when not provided."""
        questions = [
            Question(
                text="Question 1",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            ),
            Question(
                text="Question 2",
                choices=[
                    Choice(label="C", value="c"),
                    Choice(label="D", value="d"),
                ],
            ),
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2

    def test_mixed_ids_and_auto_assign(self):
        """Test that auto-assignment works with some explicit IDs."""
        questions = [
            Question(
                id=5,
                text="Question with ID 5",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            ),
            Question(
                text="Question without ID",
                choices=[
                    Choice(label="C", value="c"),
                    Choice(label="D", value="d"),
                ],
            ),
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 2
        assert result[0].id == 5
        # Second question gets ID 2 (based on index, avoiding collision with 5)
        assert result[1].id == 2

    def test_valid_questions(self):
        """Test that valid questions pass validation."""
        questions = [
            Question(
                id=1,
                text="What is your favorite color?",
                choices=[
                    Choice(label="Red", value="red"),
                    Choice(label="Blue", value="blue"),
                    Choice(label="Green", value="green"),
                ],
                allows_custom=True,
            ),
            Question(
                id=2,
                text="What is your favorite animal?",
                choices=[
                    Choice(label="Dog", value="dog"),
                    Choice(label="Cat", value="cat"),
                ],
                allows_custom=False,
            ),
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 2
        assert result[0].text == "What is your favorite color?"
        assert result[1].allows_custom is False

    def test_max_questions_boundary(self):
        """Test that exactly 20 questions passes validation."""
        questions = [
            Question(
                text=f"Question {i}",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            )
            for i in range(20)
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 20
