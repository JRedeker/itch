"""Tests for the MCP server validation logic."""

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
        """Test that select question with fewer than 2 choices returns error."""
        questions = [
            Question(
                text="What is your favorite color?",
                type="select",
                choices=[Choice(label="Red", value="red")],
            )
        ]
        result, error = validate_questions(questions)
        assert error == "Question 1: Select questions require at least 2 choice(s)"
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


class TestQuestionTypeValidation:
    """Tests for question type-specific validation."""

    def test_confirm_type_no_choices_required(self):
        """Test that confirm type questions don't require choices."""
        questions = [
            Question(
                text="Do you want to continue?",
                type="confirm",
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 1
        assert result[0].type == "confirm"

    def test_text_type_no_choices_required(self):
        """Test that text type questions don't require choices."""
        questions = [
            Question(
                text="What are your thoughts?",
                type="text",
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 1
        assert result[0].type == "text"

    def test_scale_type_no_choices_required(self):
        """Test that scale type questions don't require choices."""
        questions = [
            Question(
                text="How confident are you?",
                type="scale",
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 1
        assert result[0].type == "scale"

    def test_scale_type_with_labels(self):
        """Test that scale type questions can have optional labels."""
        questions = [
            Question(
                text="How confident are you?",
                type="scale",
                scale_labels=("Not at all", "Very confident"),
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 1
        assert result[0].scale_labels == ("Not at all", "Very confident")

    def test_checkbox_type_requires_one_choice(self):
        """Test that checkbox type requires at least 1 choice."""
        questions = [
            Question(
                text="Which apply?",
                type="checkbox",
                choices=[],
            )
        ]
        result, error = validate_questions(questions)
        assert error == "Question 1: Checkbox questions require at least 1 choice(s)"
        assert result == []

    def test_checkbox_type_valid_with_one_choice(self):
        """Test that checkbox type is valid with 1 choice."""
        questions = [
            Question(
                text="Which apply?",
                type="checkbox",
                choices=[Choice(label="Option A", value="a")],
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 1
        assert result[0].type == "checkbox"

    def test_select_type_is_default(self):
        """Test that select is the default type."""
        questions = [
            Question(
                text="Choose one",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert result[0].type == "select"

    def test_confirm_ignores_choices(self):
        """Test that confirm type ignores any provided choices."""
        questions = [
            Question(
                text="Continue?",
                type="confirm",
                choices=[
                    Choice(label="Yes", value="yes"),
                    Choice(label="No", value="no"),
                ],
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 1
        # Choices are preserved but ignored by the questioner

    def test_text_ignores_choices(self):
        """Test that text type ignores any provided choices."""
        questions = [
            Question(
                text="What do you think?",
                type="text",
                choices=[
                    Choice(label="Option", value="option"),
                ],
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 1


class TestMixedQuestionTypes:
    """Tests for mixed question type sessions."""

    def test_mixed_types_valid(self):
        """Test that a mix of question types passes validation."""
        questions = [
            Question(
                text="What interests you?",
                type="select",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            ),
            Question(
                text="Continue exploring?",
                type="confirm",
            ),
            Question(
                text="Any specific questions?",
                type="text",
            ),
            Question(
                text="How confident are you?",
                type="scale",
                scale_labels=("Not at all", "Very"),
            ),
            Question(
                text="Which apply to you?",
                type="checkbox",
                choices=[
                    Choice(label="Option 1", value="1"),
                    Choice(label="Option 2", value="2"),
                    Choice(label="Option 3", value="3"),
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

    def test_backward_compatibility_no_type_field(self):
        """Test that questions without type field work (default to select)."""
        questions = [
            Question(
                text="Old-style question",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            )
        ]
        result, error = validate_questions(questions)
        assert error is None
        assert len(result) == 1
        assert result[0].type == "select"
