# Change: Define Core Specs with Simplified MCP Interface

## Why
The Itch project needs formal specifications for its core capabilities. Additionally, the original two-phase MCP workflow (`itch` → generate questions → `itch_ask`) adds unnecessary complexity. This change establishes all core specs while implementing a streamlined single-call interface where AI agents provide all information upfront.

## What Changes

### New Specifications (3 capabilities)
- **mcp-server**: Single `itch` tool accepting topic + pre-generated questions
- **interactive-questionnaire**: CLI-based question presentation and answer collection
- **socratic-prompts**: Internal prompt templates and example questions (NOT exposed via MCP)

### MCP Interface Simplification
- Single `itch` tool replaces the two-phase `itch` → `itch_ask` workflow
- No MCP prompts exposed (AI agents generate questions independently)
- Comprehensive input validation with clear error messages
- Structured Pydantic-based input/output with auto-conversion from JSON
- Maximum 20 questions per session
- Graceful cancellation with partial results

## Design Decisions

### Single Tool Call Pattern
Following MCP best practices, tools should be self-contained operations. The AI agent prepares all data before calling, and the tool executes the complete operation. This eliminates:
- Multiple round-trips between AI and MCP server
- Intermediate state management
- Potential for partial failures

### FastMCP JSON-to-Pydantic Conversion
FastMCP automatically converts JSON input to Pydantic models. AI agents send JSON; the server receives validated Pydantic objects. This provides:
- Auto-generated JSON schemas for AI agent discovery
- Runtime validation with detailed error messages
- Field descriptions for documentation

### Validation Before Execution
All validation happens before launching the CLI subprocess:
- Fail fast with actionable, indexed error messages
- No wasted subprocess spawning for invalid input
- Clear identification of which question/choice is invalid

### Prompts as Internal Templates Only
The `socratic-prompts` capability provides templates and examples for:
- CLI demo command (predefined questions)
- Reference documentation for AI agents
- NOT exposed as MCP prompts (agents generate questions independently)

### Graceful Cancellation
User can cancel mid-session (Ctrl+C); system returns `status: "cancelled"` with partial results rather than failing completely.

## Impact
- Affected specs: All new (mcp-server, interactive-questionnaire, socratic-prompts)
- Affected code: `src/itch/server.py` (rewrite tool interface), prompts module (keep but don't expose via MCP)
- AI agents must generate questions before calling (no prompts returned from server)

## Supersedes
This change supersedes and incorporates the `add-core-specs` proposal, which is now deleted.
