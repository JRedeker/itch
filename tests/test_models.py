"""Tests for Itch models."""

from itch.models import Answer, Choice, ItchResponse, ItchSession, Question


def test_choice_model():
    """Test Choice model creation."""
    choice = Choice(label="Test Choice", value="test")
    assert choice.label == "Test Choice"
    assert choice.value == "test"


def test_question_model():
    """Test Question model creation."""
    question = Question(
        id=1,
        text="What is the meaning of life?",
        choices=[
            Choice(label="42", value="42"),
            Choice(label="Love", value="love"),
        ],
    )
    assert question.id == 1
    assert question.text == "What is the meaning of life?"
    assert len(question.choices) == 2
    assert question.allows_custom is True


def test_question_model_optional_id():
    """Test Question model with optional ID."""
    question = Question(
        text="What is your name?",
        choices=[
            Choice(label="Alice", value="alice"),
            Choice(label="Bob", value="bob"),
        ],
    )
    assert question.id is None
    assert question.text == "What is your name?"


def test_answer_model():
    """Test Answer model creation."""
    answer = Answer(question_id=1, selected_value="42", is_custom=False)
    assert answer.question_id == 1
    assert answer.selected_value == "42"
    assert answer.is_custom is False


def test_itch_session():
    """Test ItchSession model."""
    session = ItchSession(topic="Testing", max_questions=3)
    assert session.topic == "Testing"
    assert session.max_questions == 3
    assert session.questions == []
    assert session.answers == []


def test_itch_response_complete():
    """Test ItchResponse with complete status."""
    response = ItchResponse(
        status="complete",
        topic="Testing",
        questions=[
            Question(
                id=1,
                text="Test question",
                choices=[
                    Choice(label="A", value="a"),
                    Choice(label="B", value="b"),
                ],
            )
        ],
        answers=[Answer(question_id=1, selected_value="a", is_custom=False)],
    )
    assert response.status == "complete"
    assert response.topic == "Testing"
    assert len(response.questions) == 1
    assert len(response.answers) == 1
    assert response.error is None


def test_itch_response_error():
    """Test ItchResponse with error status."""
    response = ItchResponse(
        status="error",
        topic="Testing",
        error="Something went wrong",
    )
    assert response.status == "error"
    assert response.error == "Something went wrong"
    assert response.questions == []
    assert response.answers == []


def test_itch_response_cancelled():
    """Test ItchResponse with cancelled status."""
    response = ItchResponse(
        status="cancelled",
        topic="Testing",
        answers=[Answer(question_id=1, selected_value="partial", is_custom=False)],
    )
    assert response.status == "cancelled"
    assert len(response.answers) == 1
