---
description: Explore a topic through Socratic questioning
---
Explore through Socratic questioning: $ARGUMENTS

## Instructions

First, determine if the argument matches an OpenSpec change proposal:

1. Run `openspec list` to check for active changes
2. If `$ARGUMENTS` matches a change name (e.g., "add-feature-x"), this is an **OpenSpec mode** request
3. Otherwise, this is a **general topic** request

---

### OpenSpec Mode (if argument matches a change name)

Run `openspec show $ARGUMENTS` to get the proposal details.

Generate 3-5 Socratic questions focused on:
- Clarifying requirements or ambiguities in the proposal
- Validating design decisions and trade-offs
- Identifying potential risks or edge cases
- Understanding user priorities for implementation
- Confirming scope boundaries (what's in vs out)

Example question themes:
- "Which aspect of this change is most important to get right?"
- "What would make you consider this implementation successful?"
- "Are there any constraints or concerns not captured in the proposal?"

---

### General Topic Mode (default)

Generate 3-5 thoughtful Socratic questions to explore the topic.

Guidelines:
- Each question should probe a different aspect
- Provide 3-4 meaningful choices per question
- Include a mix of concrete and reflective options
- Use clear, concise language

---

## Execution

After generating questions, use the `itch` tool to present them interactively.

Once you receive the user's answers:
- Summarize what you learned about their perspective
- For OpenSpec mode: note any clarifications or decisions that should update the proposal
- Suggest concrete next steps based on their responses
