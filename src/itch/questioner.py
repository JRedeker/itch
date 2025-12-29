"""Interactive questionnaire using questionary."""

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from itch.models import Answer, Choice, Question

console = Console()

CUSTOM_ANSWER_LABEL = "Other (type your own answer)"


def display_question_header(question: Question, current: int, total: int) -> None:
    """Display a formatted question header."""
    header = Text()
    header.append(f"Question {current}/{total}", style="bold cyan")
    console.print(Panel(question.text, title=str(header), border_style="blue"))


def build_choices(question: Question) -> list[questionary.Choice]:
    """Build questionary choices from question model."""
    choices = [
        questionary.Choice(title=choice.label, value=choice.value) for choice in question.choices
    ]
    if question.allows_custom:
        choices.append(questionary.Choice(title=CUSTOM_ANSWER_LABEL, value="__custom__"))
    return choices


def ask_question(question: Question, current: int, total: int) -> Answer | None:
    """Ask a single question interactively and return the answer.

    Note: question.id should be assigned before calling this function.
    If id is None, current index is used as fallback.
    """
    display_question_header(question, current, total)

    choices = build_choices(question)

    selected = questionary.select(
        "Select your answer:",
        choices=choices,
        use_shortcuts=True,
        style=questionary.Style(
            [
                ("selected", "fg:cyan bold"),
                ("pointer", "fg:cyan bold"),
                ("highlighted", "fg:cyan"),
                ("question", "bold"),
            ]
        ),
    ).ask()

    if selected is None:
        # User cancelled (Ctrl+C)
        return None

    # Use question.id if available, otherwise fall back to current index
    question_id = question.id if question.id is not None else current

    if selected == "__custom__":
        custom_answer = questionary.text(
            "Enter your answer:",
            style=questionary.Style([("question", "bold")]),
        ).ask()

        if custom_answer is None:
            return None

        return Answer(
            question_id=question_id,
            selected_value=custom_answer,
            is_custom=True,
        )

    return Answer(
        question_id=question_id,
        selected_value=selected,
        is_custom=False,
    )


def run_questionnaire(questions: list[Question]) -> list[Answer]:
    """Run through all questions and collect answers."""
    answers: list[Answer] = []
    total = len(questions)

    console.print()
    console.print(
        Panel(
            f"You will be asked {total} question(s). "
            "Select an answer or choose 'Other' to provide your own.",
            title="Instructions",
            border_style="green",
        )
    )
    console.print()

    for i, question in enumerate(questions, 1):
        answer = ask_question(question, i, total)
        if answer is None:
            console.print("\n[yellow]Session cancelled by user.[/yellow]")
            break
        answers.append(answer)
        console.print()

    return answers


def display_summary(topic: str, questions: list[Question], answers: list[Answer]) -> None:
    """Display a summary of the session."""
    console.print()
    console.print(Panel(f"Session Complete: {topic}", border_style="green"))

    for answer in answers:
        question = next((q for q in questions if q.id == answer.question_id), None)
        if question:
            answer_text = answer.selected_value
            if answer.is_custom:
                answer_text = f"[italic]{answer_text}[/italic] (custom)"
            console.print(f"  [cyan]Q{answer.question_id}:[/cyan] {question.text}")
            console.print(f"  [green]A:[/green] {answer_text}")
            console.print()
