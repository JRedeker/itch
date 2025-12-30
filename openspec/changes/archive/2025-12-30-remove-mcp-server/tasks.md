# Tasks: Remove MCP Server

## 1. Extract Validation Logic

- [x] 1.1 Create `src/itch/validation.py` with `validate_questions()` and helpers extracted from `server.py`
  - **Verify**: `from itch.validation import validate_questions` works
- [x] 1.2 Add constants: `MAX_QUESTIONS`, `MIN_CHOICES_SELECT`, `MIN_CHOICES_CHECKBOX`, `SCALE_LABELS_LENGTH`
  - **Verify**: Constants match values from `server.py`

## 2. Fix CLI Question Parsing Bug

- [x] 2.1 Update `cli.py` `ask` command to parse `type` field from JSON (default: "select")
  - **Verify**: `echo '{"type":"confirm"}' | jq` style input works
- [x] 2.2 Update `cli.py` `ask` command to parse `scale_labels` field from JSON (convert to tuple)
  - **Verify**: `scale_labels: ["Low", "High"]` converts to `("Low", "High")`
- [x] 2.3 Handle edge case: empty `scale_labels` array treated as None
  - **Verify**: `scale_labels: []` results in `None`

## 3. Unit Tests

- [x] 3.1 Rename `tests/test_server.py` → `tests/test_validation.py`
  - **Verify**: File exists at new path
- [x] 3.2 Update imports from `itch.server` to `itch.validation`
  - **Verify**: `uv run pytest tests/test_validation.py -v` passes
- [x] 3.3 Add `TestCLIQuestionParsing` class to `tests/test_cli.py` (new file)
  - **Verify**: Test class exists with proper structure
- [x] 3.4 Add test `test_parses_type_field` - verifies type is extracted from JSON
  - **Verify**: Test passes with mock subprocess
- [x] 3.5 Add test `test_parses_scale_labels` - verifies scale_labels converted to tuple
  - **Verify**: Test passes with mock subprocess
- [x] 3.6 Add test `test_missing_type_defaults_to_select` - verifies default behavior
  - **Verify**: Test passes
- [x] 3.7 Add test `test_empty_scale_labels_treated_as_none` - edge case
  - **Verify**: Test passes
- [x] 3.8 Add test `test_invalid_json_exits_with_error` - error handling
  - **Verify**: Test verifies exit code 1 and error message

## 4. Integration Tests

- [x] 4.1 Create `tests/test_integration.py` for E2E flows
  - **Verify**: File created with proper imports
- [x] 4.2 Add test `test_cli_ask_all_question_types` - subprocess test with all 5 types
  - **Verify**: Test verifies each type is handled correctly
- [x] 4.3 Add test `test_validation_module_matches_plugin_validation` - parity check
  - **Verify**: Same inputs produce same validation results

## 5. Remove MCP Server

- [x] 5.1 Delete `src/itch/server.py`
  - **Verify**: File no longer exists
- [x] 5.2 Remove `mcp>=1.0.0` from `pyproject.toml` dependencies
  - **Verify**: `grep -q "mcp" pyproject.toml` returns no matches
- [x] 5.3 Remove `itch-server = "itch.server:main"` from `[project.scripts]`
  - **Verify**: `grep -q "itch-server" pyproject.toml` returns no matches
- [x] 5.4 Run `uv sync` to update lockfile
  - **Verify**: `uv.lock` updated, no mcp references

## 6. Update Documentation

- [x] 6.1 Update `openspec/project.md` to remove MCP/FastMCP references
  - **Verify**: No "MCP" or "FastMCP" in project.md
- [x] 6.2 Update `AGENTS.md` architecture section to show plugin-only path
  - **Verify**: Architecture diagram shows single path
- [x] 6.3 Update `README.md` to remove MCP server references
  - **Verify**: No `itch-server` command in README
- [x] 6.4 Add migration section to README for MCP server users
  - **Verify**: Section titled "Migrating from MCP Server" exists

## 7. Verify and Clean Up

- [x] 7.1 Run full test suite: `uv run pytest -v`
  - **Verify**: All tests pass, including new tests (53 passed)
- [x] 7.2 Run linter: `uv run ruff check src/ tests/`
  - **Verify**: No lint errors
- [x] 7.3 Run type checker: `uv run ty check src/`
  - **Verify**: No type errors
- [x] 7.4 Run plugin checks: `cd plugin && npm run check`
  - **Verify**: TypeScript compiles, ESLint passes
- [x] 7.5 Verify `uv run itch demo learning` still works
  - **Verify**: Interactive demo completes successfully
- [x] 7.6 Verify `uv run itch ask` with all question types works
  - **Verify**: Each type (select, confirm, text, scale, checkbox) functions
- [x] 7.7 Verify plugin can spawn CLI successfully
  - **Verify**: Manual test with OpenCode or mock

## 8. Archive Spec

- [x] 8.1 Run `openspec validate remove-mcp-server --strict`
  - **Verify**: Validation passes ✓
- [ ] 8.2 Update spec statuses after implementation approved
- [ ] 8.3 Archive the change: `openspec archive remove-mcp-server --yes`
  - **Verify**: Change moved to `changes/archive/`
