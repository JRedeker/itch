"""Interactive questionnaire using questionary."""

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from itch.models import Answer, Question

console = Console()

CUSTOM_ANSWER_LABEL = "Other (type your own answer)"

# Scale constants
SCALE_MIN = 1
SCALE_MAX = 5

# Type hints for display
TYPE_HINTS = {
    "select": "Select one option",
    "confirm": "Yes or No",
    "text": "Type your response",
    "scale": f"Rate {SCALE_MIN}-{SCALE_MAX}",
    "checkbox": "Select multiple (space to toggle, enter to confirm)",
}

# Default questionary style
QUESTIONARY_STYLE = questionary.Style(
    [
        ("selected", "fg:cyan bold"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan"),
        ("question", "bold"),
    ]
)


def display_question_header(question: Question, current: int, total: int) -> None:
    """Display a formatted question header with type hint."""
    header = Text()
    header.append(f"Question {current}/{total}", style="bold cyan")

    hint = TYPE_HINTS.get(question.type, "")
    subtitle = f"[dim]{hint}[/dim]" if hint else None

    console.print(Panel(question.text, title=str(header), subtitle=subtitle, border_style="blue"))


def build_choices(question: Question) -> list[questionary.Choice]:
    """Build questionary choices from question model."""
    choices = [
        questionary.Choice(title=choice.label, value=choice.value) for choice in question.choices
    ]
    if question.allows_custom and question.type in ("select", "checkbox"):
        choices.append(questionary.Choice(title=CUSTOM_ANSWER_LABEL, value="__custom__"))
    return choices


def ask_select(question: Question, question_id: int) -> Answer | None:
    """Ask a select (multiple choice) question."""
    choices = build_choices(question)

    selected = questionary.select(
        "Select your answer:",
        choices=choices,
        use_shortcuts=True,
        style=QUESTIONARY_STYLE,
    ).ask()

    if selected is None:
        return None

    if selected == "__custom__":
        custom_answer = questionary.text(
            "Enter your answer:",
            style=QUESTIONARY_STYLE,
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


def ask_confirm(_question: Question, question_id: int) -> Answer | None:
    """Ask a yes/no confirmation question."""
    result = questionary.confirm(
        "Your answer:",
        default=True,
        style=QUESTIONARY_STYLE,
    ).ask()

    if result is None:
        return None

    return Answer(
        question_id=question_id,
        selected_value=str(result).lower(),  # "true" or "false"
        is_custom=False,
    )


def ask_text(_question: Question, question_id: int) -> Answer | None:
    """Ask a free-form text question."""
    result = questionary.text(
        "Your answer:",
        style=QUESTIONARY_STYLE,
    ).ask()

    if result is None:
        return None

    return Answer(
        question_id=question_id,
        selected_value=result,
        is_custom=False,  # Text questions are inherently "custom" but we don't flag them
    )


def ask_scale(question: Question, question_id: int) -> Answer | None:
    """Ask a 1-5 scale rating question."""
    # Build scale choices with optional labels
    low_label, high_label = question.scale_labels or ("", "")

    choices = []
    for i in range(SCALE_MIN, SCALE_MAX + 1):
        if i == SCALE_MIN and low_label:
            title = f"{i} - {low_label}"
        elif i == SCALE_MAX and high_label:
            title = f"{i} - {high_label}"
        else:
            title = str(i)
        choices.append(questionary.Choice(title=title, value=str(i)))

    selected = questionary.select(
        "Select your rating:",
        choices=choices,
        use_shortcuts=True,
        style=QUESTIONARY_STYLE,
    ).ask()

    if selected is None:
        return None

    return Answer(
        question_id=question_id,
        selected_value=selected,
        is_custom=False,
    )


def ask_checkbox(question: Question, question_id: int) -> Answer | None:
    """Ask a checkbox (multi-select) question."""
    choices = build_choices(question)

    selected = questionary.checkbox(
        "Select all that apply:",
        choices=choices,
        style=QUESTIONARY_STYLE,
    ).ask()

    if selected is None:
        return None

    # Handle custom answer if selected
    if "__custom__" in selected:
        custom_answer = questionary.text(
            "Enter your custom option:",
            style=QUESTIONARY_STYLE,
        ).ask()

        if custom_answer is None:
            return None

        # Replace __custom__ with actual custom answer
        selected = [s if s != "__custom__" else custom_answer for s in selected]

        return Answer(
            question_id=question_id,
            selected_value=",".join(selected),
            is_custom=True,
        )

    return Answer(
        question_id=question_id,
        selected_value=",".join(selected),
        is_custom=False,
    )


def ask_question(question: Question, current: int, total: int) -> Answer | None:
    """Ask a single question interactively and return the answer.

    Routes to the appropriate question type handler.
    Note: question.id should be assigned before calling this function.
    If id is None, current index is used as fallback.
    """
    display_question_header(question, current, total)

    # Use question.id if available, otherwise fall back to current index
    question_id = question.id if question.id is not None else current

    # Dispatch to type-specific handler
    handlers = {
        "select": ask_select,
        "confirm": ask_confirm,
        "text": ask_text,
        "scale": ask_scale,
        "checkbox": ask_checkbox,
    }

    handler = handlers.get(question.type, ask_select)
    return handler(question, question_id)


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
