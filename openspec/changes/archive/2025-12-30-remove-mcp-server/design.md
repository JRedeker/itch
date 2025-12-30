# Design: Remove MCP Server

## Context

Itch currently supports two integration paths:

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│   OpenCode Plugin           │     │   MCP Server                │
│   (plugin/index.ts)         │     │   (server.py)               │
│                             │     │                             │
│   spawns → itch CLI ────────┼─────┼── spawns → itch CLI         │
│             (ask command)   │     │             (ask command)   │
└─────────────────────────────┘     └─────────────────────────────┘
```

Both validate input, spawn `itch ask`, and parse JSON output. The duplication exists because:
1. MCP server was the original implementation
2. OpenCode plugin was added for tighter OpenCode integration
3. Both kept for different client compatibility

## Goals

- Single integration path via OpenCode plugin
- Preserve validation logic for CLI and tests
- Fix existing bug in CLI (doesn't parse `type`/`scale_labels`)
- Reduce dependencies (remove `mcp` package)

## Non-Goals

- Supporting non-OpenCode MCP clients
- Changing plugin behavior
- Adding new features

## Decisions

### Decision 1: Extract validation to `validation.py`

**What**: Move `validate_questions()` and helpers from `server.py` to new `src/itch/validation.py`

**Why**: 
- Validation logic is useful for CLI tests
- Keeps the validation patterns established in server.py
- Tests can continue using Python validation without MCP

**Alternatives considered**:
- Remove Python validation entirely (rely on plugin's TypeScript validation): Would break Python tests
- Keep validation in cli.py: Violates single responsibility, makes testing harder

### Decision 2: Fix CLI question parsing

**What**: Update `cli.py` to parse `type` and `scale_labels` from JSON input

**Why**: Current bug - CLI only parses `id`, `text`, `choices`, `allows_custom` but ignores `type` and `scale_labels`, defaulting everything to "select" type

**Current code** (`cli.py:46-53`):
```python
Question(
    id=q.get("id", i + 1),
    text=q["text"],
    choices=[Choice(**c) for c in q.get("choices", [])],
    allows_custom=q.get("allows_custom", True),
    # Missing: type and scale_labels
)
```

**Fixed code**:
```python
Question(
    id=q.get("id", i + 1),
    text=q["text"],
    type=q.get("type", "select"),
    choices=[Choice(**c) for c in q.get("choices", [])],
    allows_custom=q.get("allows_custom", True),
    scale_labels=tuple(q["scale_labels"]) if q.get("scale_labels") else None,
)
```

### Decision 3: Rename test file

**What**: Rename `tests/test_server.py` → `tests/test_validation.py`

**Why**: Tests are for validation logic, not MCP server. Update import from `itch.server` to `itch.validation`.

## Architecture After Change

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenCode Plugin                         │
│   (plugin/index.ts)                                          │
│   - TypeScript validation                                    │
│   - Spawns Python CLI                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Python CLI Layer                         │
│   src/itch/cli.py - Typer CLI (ask, demo, version)          │
│   src/itch/validation.py - Shared validation logic          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Components                          │
│   src/itch/questioner.py + src/itch/models.py               │
└─────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing MCP users | Medium | Document in CHANGELOG, provide migration guide |
| Loss of generic MCP compatibility | Low | OpenCode is the primary use case |
| Reduced test coverage | Low | Validation tests remain, just moved |

## Migration Plan

1. Create `validation.py` with extracted logic
2. Fix CLI to parse all question fields
3. Update tests to import from `validation.py`
4. Remove `server.py` and MCP dependencies
5. Update documentation (AGENTS.md, README.md, project.md)
6. Update openspec specs

## Test Strategy

### Unit Tests

| Test File | Purpose | Key Test Cases |
|-----------|---------|----------------|
| `tests/test_validation.py` | Validation logic | Existing 417 lines, renamed from test_server.py |
| `tests/test_cli.py` | CLI parsing | `test_parses_type_field`, `test_parses_scale_labels`, `test_missing_type_defaults_to_select`, `test_empty_scale_labels_treated_as_none`, `test_invalid_json_exits_with_error` |
| `tests/test_models.py` | Data models | Existing, no changes needed |

### Integration Tests

| Test File | Purpose | Key Test Cases |
|-----------|---------|----------------|
| `tests/test_integration.py` | E2E flows | `test_cli_ask_all_question_types`, `test_validation_module_matches_plugin_validation` |

### Test Verification Matrix

| Component | Unit | Integration | Manual |
|-----------|------|-------------|--------|
| validation.py | ✓ test_validation.py | - | - |
| cli.py type parsing | ✓ test_cli.py | ✓ test_integration.py | - |
| cli.py scale_labels | ✓ test_cli.py | ✓ test_integration.py | - |
| plugin → CLI flow | - | ✓ test_integration.py | ✓ OpenCode test |
| Demo command | - | - | ✓ `itch demo learning` |

### Mocking Strategy

- **CLI tests**: Mock `run_questionnaire()` to avoid interactive prompts
- **Integration tests**: Use `subprocess.run()` with `--json` flag for non-interactive verification
- **Plugin tests**: TypeScript tests mock `Bun.spawn()` for subprocess calls

## Open Questions

None - straightforward extraction and removal.
