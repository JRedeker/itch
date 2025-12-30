# Change: Remove MCP Server and Consolidate on OpenCode Plugin

## Why

The project currently has two parallel integration paths that duplicate functionality:
1. **MCP Server** (`server.py`) - For Claude Desktop and generic MCP clients
2. **OpenCode Plugin** (`plugin/index.ts`) - For OpenCode specifically

Both paths spawn the same `itch ask` CLI subprocess and perform nearly identical validation. This duplication:
- Increases maintenance burden (validation logic in two languages)
- Creates potential for inconsistencies between paths
- Adds the `mcp` Python dependency that's only used by one integration

Since the primary use case is OpenCode, we should consolidate on the plugin-only architecture and remove the MCP server component.

## What Changes

- **REMOVED**: `src/itch/server.py` - MCP server implementation
- **REMOVED**: `mcp>=1.0.0` dependency from `pyproject.toml`
- **REMOVED**: `itch-server` entry point from `pyproject.toml`
- **ADDED**: `src/itch/validation.py` - Extracted validation logic (for CLI and tests)
- **ADDED**: `tests/test_cli.py` - Tests for CLI question parsing
- **ADDED**: `tests/test_integration.py` - E2E integration tests
- **MODIFIED**: `src/itch/cli.py` - Parse all question fields (`type`, `scale_labels`)
- **MODIFIED**: `openspec/project.md` - Remove MCP references
- **MODIFIED**: `AGENTS.md`, `README.md` - Update architecture documentation

## Impact

- **Affected specs**: 
  - `mcp-server` (entire spec REMOVED - 6 requirements)
  - `opencode-plugin` (becomes the sole integration path, +1 requirement)
  - `interactive-questionnaire` (CLI bug fix for question types)
- **Affected code**:
  - `src/itch/server.py` (deleted)
  - `src/itch/validation.py` (new, extracted from server.py)
  - `src/itch/cli.py` (bug fix for type/scale_labels parsing)
  - `tests/test_server.py` → `tests/test_validation.py` (renamed)
  - `tests/test_cli.py` (new)
  - `tests/test_integration.py` (new)
  - `pyproject.toml` (dependencies and scripts)
- **Breaking change**: Users relying on `itch-server` command or MCP protocol will need to migrate to the OpenCode plugin

## Acceptance Criteria

1. **Validation logic preserved**: All 417 lines of validation tests pass after extraction
2. **CLI bug fixed**: `type` and `scale_labels` fields are correctly parsed from JSON
3. **No MCP references**: `grep -r "mcp" src/` returns no matches
4. **Tests comprehensive**: Unit tests for CLI parsing, integration tests for E2E flow
5. **Documentation updated**: README includes migration guide for MCP users
6. **All checks pass**: `uv run pytest`, `uv run ruff check`, `uv run ty check`, `npm run check`

## Non-Goals

- Changing the plugin's functionality (it already works correctly)
- Adding new question types or features
- Changing the CLI interface (beyond bug fixes)
- Supporting non-OpenCode MCP clients going forward

## Rollback Plan

If issues are discovered post-implementation:
1. Revert commits to restore `server.py`
2. Restore `mcp` dependency in `pyproject.toml`
3. Restore `itch-server` script entry point
4. `validation.py` can remain as it's additive
