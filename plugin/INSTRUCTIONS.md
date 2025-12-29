# Itch Plugin Instructions

This file provides guidance for LLMs on how to use the itch tool effectively.

## When to Use Itch

Use the `itch` tool when you want to:
- Understand user preferences or opinions
- Gather input for decision-making
- Explore a topic through Socratic questioning
- Get user feedback on proposed approaches

## Generating Good Questions

When creating questions for itch:

1. **Keep questions focused** - Each question should explore one specific aspect
2. **Provide meaningful choices** - 3-5 choices per question works best
3. **Use clear labels** - Choice labels should be self-explanatory
4. **Include variety** - Mix concrete and abstract options
5. **Enable custom answers** - Set `allows_custom: true` for open-ended exploration

## Example Usage

```json
{
  "topic": "project architecture",
  "questions": [
    {
      "text": "What's your primary concern for this codebase?",
      "choices": [
        { "label": "Performance and speed", "value": "performance" },
        { "label": "Maintainability", "value": "maintainability" },
        { "label": "Security", "value": "security" },
        { "label": "Developer experience", "value": "dx" }
      ],
      "allows_custom": true
    },
    {
      "text": "How do you prefer to handle errors?",
      "choices": [
        { "label": "Fail fast with detailed messages", "value": "fail_fast" },
        { "label": "Graceful degradation", "value": "graceful" },
        { "label": "Retry with backoff", "value": "retry" }
      ]
    }
  ]
}
```

## Interpreting Responses

The response includes:
- `status`: "complete", "cancelled", or "error"
- `answers`: Array of user selections with `question_id`, `selected_value`, and `is_custom`

Use the answers to tailor your subsequent responses to the user's stated preferences.
