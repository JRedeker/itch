# Change: Add Multiple Question Types

## Why

Currently Itch only supports **select** (multiple choice) questions. This limits the types of Socratic exploration possible. Users and LLMs need richer question types to:

- Ask yes/no confirmation questions (simpler than full multiple choice)
- Collect free-form text responses for open-ended exploration  
- Gather scaled ratings (1-5) for prioritization and sentiment
- Support checkbox-style multi-select for gathering multiple perspectives

These capabilities exist in the underlying `questionary` library but aren't exposed through Itch.

## What Changes

### New Question Types

| Type | Description | Use Case |
|------|-------------|----------|
| `select` | Multiple choice (existing) | "Which approach resonates most?" |
| `confirm` | Yes/No boolean | "Would you like to explore this further?" |
| `text` | Free-form input | "What concerns do you have about this?" |
| `scale` | 1-5 rating with labels | "How confident are you? (1=Not at all, 5=Very)" |
| `checkbox` | Multi-select | "Which of these apply to your situation?" |

### Model Changes

- Add `type` field to `Question` model with literal type union
- Add `scale_labels` field for scale questions (low/high endpoint labels)
- Update `Answer` model to handle different response types
- Choices become optional (not needed for confirm/text)

### Backward Compatibility

- Default `type` to `"select"` for existing behavior
- Existing questions without `type` field continue to work
- No breaking changes to MCP or CLI interfaces

## Impact

- **Affected specs**: `interactive-questionnaire`
- **Affected code**: 
  - `src/itch/models.py` - Question/Answer models
  - `src/itch/questioner.py` - Rendering logic per type
  - `plugin/index.ts` - TypeScript schemas
  - `tests/` - New test cases
