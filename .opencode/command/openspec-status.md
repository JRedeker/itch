---
agent: general
description: Show detailed task progress for an OpenSpec change with validation.
---

# OpenSpec Task Status

The user wants to see the current implementation status. If a change ID is provided, show that change. Otherwise, detect the active change or ask.

<ChangeId>
  $ARGUMENTS
</ChangeId>

## Purpose

This command helps agents and users:
1. See exactly where they are in implementing a change
2. Identify skipped or missed tasks
3. Know what task to work on next
4. Detect incomplete or out-of-order work

## Steps

### 1. Determine the Active Change

1. If a change ID is provided in `<ChangeId>`, use it (trim whitespace).
2. Otherwise, run `openspec list` to see active changes.
3. If only ONE change is in progress (not 100% complete), use that automatically.
4. If multiple changes exist, ask the user which one to show status for.
5. If no changes exist, inform the user there are no active changes.

### 2. Gather Task Data

1. Read `openspec/changes/<id>/tasks.md` to get the full task list.
2. Parse all tasks using this pattern:
   - `- [x]` = completed
   - `- [ ]` = incomplete
   - Task IDs like `1.1.1`, `2.3.4` indicate hierarchy
3. Run `openspec list` to get the CLI's task count for validation.

### 3. Analyze Task Progress

Perform these checks:
1. **Sequence Violations**: Are there incomplete tasks BEFORE completed ones? (skipped tasks)
2. **Current Position**: What is the first incomplete task? (next task to work on)
3. **Phase Progress**: Which phases/sections are complete vs in-progress?
4. **Completion Status**: Overall percentage and counts

### 4. Generate Status Report

Output a visual status report in this format:

```
OpenSpec Task Status: {change-id}
════════════════════════════════════════════════════════════

Progress: {completed}/{total} tasks ({percent}%)
[████████████░░░░░░░░] 

Current Task: {task-id} {task-description}
  Phase: {phase-name}
  
{if sequence_violations}
⚠️  SKIPPED TASKS DETECTED
────────────────────────────────────────────────────────────
The following tasks were skipped and should be addressed:
  • {task-id}: {task-description}
  • {task-id}: {task-description}
{/if}

Phase Summary
────────────────────────────────────────────────────────────
  ✓ Phase 1: {name}                    {x}/{y} tasks
  ◉ Phase 2: {name} (in progress)      {x}/{y} tasks  
  ○ Phase 3: {name}                    {x}/{y} tasks

Next Steps
────────────────────────────────────────────────────────────
  1. {if skipped} Complete skipped task {task-id} first
  2. {else} Work on task {task-id}: {description}
  3. Mark task complete with `- [x]` when done
  4. Run `/openspec-status` again to verify progress

════════════════════════════════════════════════════════════
```

## Visual Standards

- **Progress Bar**: █ for filled, ░ for empty (20 chars total)
- **Phase Status**: ✓ complete, ◉ in progress, ○ not started
- **Warnings**: ⚠️ for skipped tasks or issues
- **Borders**: Use Unicode box drawing: ═ ─

## Validation Rules

### Sequence Violation Detection
A sequence violation occurs when:
- A task with ID `X.Y.Z` is marked `[x]` (complete)
- But an earlier task `X.Y.W` (where W < Z) is still `[ ]` (incomplete)

Example violation:
```markdown
- [ ] 1.1.1 First task     ← SKIPPED (violation!)
- [x] 1.1.2 Second task    ← Completed out of order
- [ ] 1.1.3 Third task
```

### Phase Detection
Phases are detected by:
- `## N. Phase Name` headers (e.g., `## 1. Core Implementation`)
- `### N.N Sub-section` headers

## Guardrails

- **Read-only**: This command only reads and reports; it does not modify files.
- **Accurate Counts**: Cross-reference with `openspec list` output to ensure counts match.
- **Actionable Output**: Always end with clear "Next Steps" guidance.
- **No Assumptions**: If task structure is unclear, show raw data and ask for clarification.

## Example Output

```
OpenSpec Task Status: enhance-ebay-listing-generation
════════════════════════════════════════════════════════════

Progress: 95/119 tasks (80%)
[████████████████░░░░] 

Current Task: 3.1.7 Integration test: verify URL opens eBay correctly
  Phase: Phase 3: Enhanced Pre-fill URL

Phase Summary
────────────────────────────────────────────────────────────
  ✓ Phase 1: Core Item Specifics Module     18/18 tasks
  ✓ Phase 2: SEO Keywords                   12/12 tasks
  ◉ Phase 3: Enhanced Pre-fill URL (current) 6/7 tasks  
  ✓ Phase 4: File Exchange Export           14/14 tasks
  ○ Phase 5: TUI Integration                45/68 tasks

Next Steps
────────────────────────────────────────────────────────────
  1. Complete task 3.1.7: Integration test: verify URL opens eBay correctly
  2. Mark task complete: change `- [ ]` to `- [x]` in tasks.md
  3. Run `/openspec-status` to verify and see next task

════════════════════════════════════════════════════════════
```

## Reference

- Use `openspec list` to see all active changes with task counts
- Use `openspec show <id>` for full change details
- Use `openspec show <id> --json` for machine-readable output
- See `openspec/AGENTS.md` for workflow conventions
