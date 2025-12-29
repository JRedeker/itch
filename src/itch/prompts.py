"""Socratic questioning prompts and templates.

NOTE: These templates are for INTERNAL USE ONLY (CLI demo command).
They are NOT exposed via MCP - AI agents generate questions independently.
"""

SOCRATIC_SYSTEM_PROMPT = """You are a Socratic questioner. Your role is to help users explore topics deeply through thoughtful, probing questions.

When given a topic, generate questions that:
1. Start with fundamental concepts and progressively go deeper
2. Challenge assumptions and encourage critical thinking
3. Connect ideas to broader concepts or real-world applications
4. Are open-ended but can be answered with provided choices
5. Build upon each other to create a coherent exploration

For each question, provide 3-4 meaningful multiple choice options that represent different perspectives or levels of understanding."""

QUESTION_GENERATION_PROMPT = """Generate {max_questions} Socratic questions about the topic: "{topic}"

For each question, provide:
1. The question text
2. 3-4 multiple choice answers that represent different perspectives or levels of understanding

Format your response as JSON with this structure:
{{
  "questions": [
    {{
      "id": 1,
      "text": "The question text",
      "choices": [
        {{"label": "Choice A", "value": "a"}},
        {{"label": "Choice B", "value": "b"}},
        {{"label": "Choice C", "value": "c"}}
      ]
    }}
  ]
}}

Focus on questions that:
- Start simple and progressively become more nuanced
- Explore different dimensions of the topic
- Encourage reflection and critical thinking
- Have choices that represent genuinely different viewpoints"""


def get_question_generation_prompt(topic: str, max_questions: int) -> str:
    """Generate the prompt for creating Socratic questions."""
    return QUESTION_GENERATION_PROMPT.format(topic=topic, max_questions=max_questions)


# Example questions for demonstration/fallback
EXAMPLE_QUESTIONS = {
    "learning": [
        {
            "id": 1,
            "text": "What do you believe is the primary purpose of learning?",
            "choices": [
                {"label": "To acquire skills for career advancement", "value": "career"},
                {"label": "To understand the world around us", "value": "understanding"},
                {"label": "To grow as a person and expand perspectives", "value": "growth"},
                {"label": "To solve practical problems in daily life", "value": "practical"},
            ],
        },
        {
            "id": 2,
            "text": "How do you typically approach learning something new?",
            "choices": [
                {
                    "label": "I prefer structured courses with clear progression",
                    "value": "structured",
                },
                {"label": "I learn by doing and experimenting", "value": "hands-on"},
                {"label": "I seek out experts and mentors to guide me", "value": "mentored"},
                {"label": "I explore freely and follow my curiosity", "value": "exploratory"},
            ],
        },
        {
            "id": 3,
            "text": "When you encounter difficulty in learning, what is your usual response?",
            "choices": [
                {"label": "I persist and try harder with the same approach", "value": "persist"},
                {"label": "I step back and try a different method", "value": "adapt"},
                {"label": "I seek help from others", "value": "collaborate"},
                {"label": "I take a break and return with fresh eyes", "value": "pause"},
            ],
        },
    ],
}
