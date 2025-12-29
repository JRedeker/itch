"""Data models for Itch."""

from typing import Literal

from pydantic import BaseModel, Field

# Question types supported by itch
QuestionType = Literal["select", "confirm", "text", "scale", "checkbox"]


class Choice(BaseModel):
    """A single choice option for a question."""

    label: str = Field(description="Display text shown to user")
    value: str = Field(description="Identifier returned when this choice is selected")


class Question(BaseModel):
    """A Socratic question with configurable type and answer format."""

    id: int | None = Field(default=None, description="Question ID (auto-assigned if not provided)")
    text: str = Field(description="The question text to display")
    type: QuestionType = Field(
        default="select",
        description="Question type: select, confirm, text, scale, or checkbox",
    )
    choices: list[Choice] = Field(
        default_factory=list,
        description="List of answer choices (required for select/checkbox types)",
    )
    allows_custom: bool = Field(
        default=True,
        description="Whether to show 'Other' option (select/checkbox only)",
    )
    scale_labels: tuple[str, str] | None = Field(
        default=None,
        description="Labels for scale endpoints, e.g., ('Not at all', 'Completely')",
    )


class Answer(BaseModel):
    """User's answer to a question."""

    question_id: int = Field(description="ID of the question being answered")
    selected_value: str = Field(
        description="Selected choice value, text, or comma-separated checkbox values"
    )
    is_custom: bool = Field(default=False, description="True if user provided a custom answer")


class ItchSession(BaseModel):
    """A complete Itch questioning session."""

    topic: str
    questions: list[Question] = Field(default_factory=list)
    answers: list[Answer] = Field(default_factory=list)
    max_questions: int = 5


class ItchResponse(BaseModel):
    """Response from an Itch questioning session."""

    status: Literal["complete", "cancelled", "error"] = Field(
        description="Session status: 'complete', 'cancelled', or 'error'"
    )
    topic: str = Field(description="The topic that was explored")
    questions: list[Question] = Field(
        default_factory=list, description="Questions that were asked (echoed back)"
    )
    answers: list[Answer] = Field(
        default_factory=list, description="User's answers to the questions"
    )
    error: str | None = Field(default=None, description="Error message if status is 'error'")
