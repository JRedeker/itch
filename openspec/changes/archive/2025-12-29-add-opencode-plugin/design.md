# Design: OpenCode Plugin Hybrid Architecture

## Context

OpenCode supports three extension mechanisms:
1. **MCP Servers** - External tools via Model Context Protocol
2. **Plugins** - TypeScript/JavaScript modules with event hooks
3. **Custom Commands** - Slash commands with templated prompts

Itch currently uses MCP (#1) but would benefit from plugin integration (#2) for:
- Simplified installation (npm vs manual MCP config)
- Event hooks (session lifecycle, tool execution feedback)
- Custom commands for common workflows
- Better ecosystem discoverability

### Constraints

- Python runtime required (questionary, rich, MCP SDK)
- Interactive TTY needed for user prompts
- OpenCode plugins run in Bun runtime
- Plugin must spawn subprocess for Python execution

### Research Findings

**Best practices from existing OpenCode plugins:**

1. **opencode-skills** pattern: Uses `Bun.$` for subprocess, Zod for validation, silent prompt injection via SDK
2. **opencode-morph-fast-apply** pattern: External API call, graceful fallback, environment variable config
3. **OpenCode custom tools docs**: Shows Python invocation pattern via `Bun.$\`python3 script.py\``
4. **Commands are NOT auto-installed** from npm packages - they must be manually copied or the plugin must use the tool-based approach instead

## Goals / Non-Goals

**Goals:**
- Enable one-line npm installation
- Provide native `itch` tool via plugin SDK
- Provide `/itch`-like workflow (via documented instructions, not bundled command)
- Hook into session events for UX enhancements
- Maintain backward compatibility with MCP server

**Non-Goals:**
- Rewrite Python logic in TypeScript
- Remove standalone MCP server
- Add new questioning features (separate change)
- Auto-install slash commands (OpenCode doesn't support this)

## Decisions

### Decision 1: Hybrid Architecture (TypeScript wrapper → Python subprocess)

**Choice:** TypeScript plugin spawns `uv run itch` or `itch` subprocess

**Rationale:**
- Reuses existing, tested Python implementation
- Follows pattern from `opencode-morph-fast-apply` (calls external API)
- Avoids duplicating complex questionary/rich logic
- Python MCP server remains usable for non-OpenCode clients

**Alternatives considered:**
1. Pure TypeScript rewrite - High effort, duplicates logic
2. MCP-only - Misses plugin benefits (events, commands, npm)
3. Node child process calling Python - Same as chosen, less elegant

### Decision 2: Python Package Discovery (UPDATED)

**Choice:** Multi-step resolution with clear fallback chain

**Resolution order:**
1. `ITCH_PATH` environment variable (explicit override)
2. `itch` command in PATH (global pip/pipx install)
3. `uv run itch` (uv-based execution)
4. Error with installation instructions

**Rationale:**
- Supports multiple installation methods (pip, pipx, uv)
- Environment variable allows explicit control for development
- Global `itch` command is simplest for end users
- `uv run` works if user cloned the repo

**Implementation:**
```typescript
async function resolveItchCommand(): Promise<string[]> {
  // 1. Explicit override
  if (process.env.ITCH_PATH) {
    return [process.env.ITCH_PATH]
  }
  
  // 2. Check if itch is in PATH
  try {
    await Bun.$`which itch`.quiet()
    return ["itch"]
  } catch {}
  
  // 3. Try uv run
  try {
    await Bun.$`which uv`.quiet()
    return ["uv", "run", "itch"]
  } catch {}
  
  // 4. Error
  throw new Error("itch not found. Install with: pip install itch")
}
```

### Decision 3: Slash Command Approach (UPDATED)

**Choice:** Document command template in README instead of bundling

**Rationale:**
- OpenCode does NOT auto-install commands from npm packages
- Commands must be in `.opencode/command/` or `~/.config/opencode/command/`
- Bundling commands that users must manually copy creates confusion
- Better to document how to create the command

**Documentation approach:**
```markdown
## Optional: Create a slash command

Add to `.opencode/command/itch.md`:

\`\`\`markdown
---
description: Explore a topic through Socratic questioning
---
Generate 3-5 thoughtful Socratic questions about: $ARGUMENTS

Then use the itch tool to present them and collect responses.
Summarize what we learned about the user's perspective.
\`\`\`
```

**Alternative considered:** Use AGENTS.md instructions to guide LLM to use itch tool naturally (no slash command needed).

### Decision 4: Client-Side Validation (NEW)

**Choice:** Validate questions in TypeScript before spawning subprocess

**Rationale:**
- Fail fast with clear error messages
- Avoid spawning Python for obviously invalid input
- Match Python-side validation rules (1-20 questions, 2+ choices)
- Reduce latency for validation errors

**Implementation:**
```typescript
function validateQuestions(questions: Question[]): string | null {
  if (!questions.length) return "At least one question is required"
  if (questions.length > 20) return "Maximum 20 questions allowed"
  
  for (let i = 0; i < questions.length; i++) {
    const q = questions[i]
    if (!q.text?.trim()) return `Question ${i + 1} is missing text`
    if (!q.choices || q.choices.length < 2) {
      return `Question ${i + 1} must have at least 2 choices`
    }
  }
  return null // Valid
}
```

### Decision 5: Plugin Configuration (NEW)

**Choice:** Support configuration via environment variables

**Rationale:**
- Consistent with OpenCode plugin patterns (morph-fast-apply uses env vars)
- No need for complex config file parsing
- Easy to set globally or per-project

**Configuration options:**
| Variable | Default | Description |
|----------|---------|-------------|
| `ITCH_PATH` | (auto-detect) | Path to itch executable |
| `ITCH_TIMEOUT` | `300000` (5 min) | Subprocess timeout in ms |
| `ITCH_DEBUG` | `false` | Enable debug logging |

### Decision 6: npm Package Structure (UPDATED)

**Choice:** Flat structure in `plugin/` directory

**Rationale:**
- Keeps TypeScript plugin isolated from Python source
- Single repo for easier maintenance
- npm package only includes plugin files
- No command/ subdirectory (see Decision 3)

**Package structure:**
```
plugin/
├── package.json       # npm package config
├── index.ts           # Plugin entry point
├── tsconfig.json      # TypeScript config
├── README.md          # Installation instructions
└── INSTRUCTIONS.md    # Optional: LLM guidance for itch usage
```

**package.json files field:**
```json
{
  "files": ["index.ts", "README.md", "INSTRUCTIONS.md"]
}
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Python/itch not installed | Clear error with install instructions (`pip install itch`) |
| Subprocess communication failure | Timeout + structured error response |
| Version mismatch (plugin vs Python) | Version check on startup, warn if mismatched |
| TTY not available | Detect and return error before spawning |
| User expects /itch command | Document in README, provide template |

## Migration Plan

1. **Phase 1:** Create plugin, test locally via symlink
2. **Phase 2:** Publish to npm, update README with install instructions
3. **Phase 3:** Submit to OpenCode ecosystem list

**Rollback:** Plugin is additive; remove from config to disable

## Open Questions (RESOLVED)

1. ~~Should the npm package bundle a pre-built Python binary?~~
   - **Decision:** No. Start simple with pip/uv install requirement.

2. ~~Should we support `bunx opencode-itch` as standalone invocation?~~
   - **Decision:** No. Focus on OpenCode integration only.

3. ~~How are slash commands distributed?~~
   - **Decision:** Document template in README. OpenCode doesn't auto-install commands.

4. ~~How does the plugin find Python itch?~~
   - **Decision:** Multi-step resolution: ITCH_PATH → PATH → uv run → error
