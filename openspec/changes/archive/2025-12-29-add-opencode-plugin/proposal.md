# Change: Add OpenCode Plugin for Hybrid MCP Integration

## Why

Itch currently functions as a standalone MCP server, which works but has limitations:
1. Users must manually configure MCP server startup commands
2. No access to OpenCode's event system (session lifecycle, tool execution)
3. No native npm distribution for the OpenCode ecosystem
4. Cannot provide custom slash commands or enhanced UX

Creating an OpenCode plugin wrapper enables:
- One-line installation via npm
- Native integration with OpenCode's event hooks
- Custom commands (e.g., `/itch machine-learning`)
- Better error handling and user feedback
- Participation in the OpenCode ecosystem

## What Changes

### New Capability: `opencode-plugin`
- TypeScript plugin that wraps the Python MCP server
- Exposes `itch` tool using `@opencode-ai/plugin` SDK
- Provides slash commands for common workflows
- Hooks into session events for enhanced UX

### Architectural Pattern
- **Hybrid approach**: TypeScript plugin shell → Python runtime
- Plugin spawns `uv run itch` subprocess for actual execution
- Follows patterns from existing plugins (morph-fast-apply, helicone-session)

### Distribution
- npm package: `opencode-itch`
- Local development via symlink
- GitHub repository with npm publishing workflow

## Impact

- **Affected specs**: None modified (additive change)
- **New files**:
  - `plugin/` directory with TypeScript source
  - `package.json` for npm package
  - GitHub Actions for publishing
- **Dependencies**: `@opencode-ai/plugin`, `bun-types`

## Non-Goals

- Rewriting the core Python logic in TypeScript
- Removing MCP server support (remains for non-OpenCode clients)
- Adding new questioning capabilities (separate change)
