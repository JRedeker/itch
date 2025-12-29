"""Typer CLI for Itch - Interactive Socratic questioning."""

import json
import sys
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from itch.models import Choice, Question
from itch.questioner import display_summary, run_questionnaire

app = typer.Typer(
    name="itch",
    help="Socratic questioning tool for AI agents - explore topics through guided inquiry.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def ask(
    topic: Annotated[str, typer.Option("--topic", "-t", help="The topic being explored")],
    questions: Annotated[
        str, typer.Option("--questions", "-q", help="JSON string of questions to ask")
    ],
    output_json: Annotated[
        bool, typer.Option("--json", "-j", help="Output answers as JSON")
    ] = True,
) -> None:
    """Ask questions interactively and collect user answers.

    This command is typically called by the MCP server to run the interactive
    questioning session.
    """
    try:
        questions_data = json.loads(questions)
        if isinstance(questions_data, dict) and "questions" in questions_data:
            questions_data = questions_data["questions"]

        question_models = [
            Question(
                id=q.get("id", i + 1),
                text=q["text"],
                choices=[Choice(**c) for c in q.get("choices", [])],
                allows_custom=q.get("allows_custom", True),
            )
            for i, q in enumerate(questions_data)
        ]

        answers = run_questionnaire(question_models)

        if output_json:
            # Output JSON for the MCP server to parse
            print(json.dumps([a.model_dump() for a in answers]))
        else:
            display_summary(topic, question_models, answers)

    except json.JSONDecodeError as e:
        typer.echo(f"Error parsing questions JSON: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def demo(
    topic: Annotated[str, typer.Argument(help="Topic to explore with demo questions")] = "learning",
    max_questions: Annotated[int, typer.Option("--max", "-m", help="Maximum questions to ask")] = 3,
) -> None:
    """Run a demo session with example questions.

    This is useful for testing the interactive interface without needing
    an AI to generate questions.
    """
    from itch.prompts import EXAMPLE_QUESTIONS

    console.print(
        Panel(
            f"[bold]Demo: Exploring '{topic}'[/bold]\n\n"
            "This demo uses pre-defined questions to showcase the interactive experience.",
            border_style="cyan",
        )
    )

    # Use example questions or generate simple ones
    if topic.lower() in EXAMPLE_QUESTIONS:
        questions_data = EXAMPLE_QUESTIONS[topic.lower()][:max_questions]
    else:
        # Generate simple fallback questions
        questions_data = [
            {
                "id": 1,
                "text": f"What aspect of '{topic}' interests you most?",
                "choices": [
                    {"label": "The fundamentals and basics", "value": "basics"},
                    {"label": "Advanced concepts", "value": "advanced"},
                    {"label": "Practical applications", "value": "practical"},
                    {"label": "Historical context", "value": "history"},
                ],
            },
            {
                "id": 2,
                "text": f"How would you describe your current understanding of '{topic}'?",
                "choices": [
                    {"label": "Complete beginner", "value": "beginner"},
                    {"label": "Some familiarity", "value": "familiar"},
                    {"label": "Intermediate knowledge", "value": "intermediate"},
                    {"label": "Expert level", "value": "expert"},
                ],
            },
            {
                "id": 3,
                "text": f"What would make exploring '{topic}' most valuable to you?",
                "choices": [
                    {"label": "Clear explanations of concepts", "value": "clarity"},
                    {"label": "Hands-on examples", "value": "examples"},
                    {"label": "Connections to other ideas", "value": "connections"},
                    {"label": "Challenging my assumptions", "value": "challenge"},
                ],
            },
        ][:max_questions]

    question_models = [
        Question(
            id=q["id"],
            text=q["text"],
            choices=[Choice(**c) for c in q["choices"]],
            allows_custom=True,
        )
        for q in questions_data
    ]

    answers = run_questionnaire(question_models)
    display_summary(topic, question_models, answers)


@app.command()
def version() -> None:
    """Show the version of Itch."""
    from itch import __version__

    console.print(f"Itch version {__version__}")


@app.callback()
def main() -> None:
    """Itch - Socratic questioning tool for AI agents.

    This CLI provides interactive questioning capabilities that AI agents
    can use to explore topics with users through the Socratic method.
    """
    pass


if __name__ == "__main__":
    app()
