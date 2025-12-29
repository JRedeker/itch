# Tasks: Define Core Specs with Simplified MCP Interface

## 1. Remove Two-Phase Components
- [x] 1.1 Remove old `itch` tool (session initialization that returned prompts)
- [x] 1.2 Remove `socratic_questions` MCP prompt decorator
- [x] 1.3 Remove unused MCP-related imports from server.py

## 2. Implement Unified `itch` Tool
- [x] 2.1 Rename `itch_ask` to `itch` as the primary tool
- [x] 2.2 Update tool signature: `topic: str`, `questions: list[Question]`
- [x] 2.3 Add Pydantic Field descriptions to all parameters for schema generation
- [x] 2.4 Note: FastMCP auto-converts JSON input to Pydantic models

## 3. Input Validation
- [x] 3.1 Validate topic is non-empty (strip whitespace)
- [x] 3.2 Validate questions list has 1-20 items
- [x] 3.3 Validate each question has non-empty text
- [x] 3.4 Validate each question has at least 2 choices
- [x] 3.5 Validate each choice has non-empty label and value
- [x] 3.6 Validate no duplicate question IDs (if provided)
- [x] 3.7 Auto-assign sequential IDs (1, 2, 3...) for questions without explicit IDs
- [x] 3.8 Return structured error responses with field/index identification

## 4. Output Structure
- [x] 4.1 Define ItchResponse Pydantic model with status, topic, questions, answers
- [x] 4.2 Echo back questions array in successful response
- [x] 4.3 Return `status: "cancelled"` for user interruption (Ctrl+C)
- [x] 4.4 Include partial answers array on cancellation

## 5. Server Metadata
- [x] 5.1 Update FastMCP instructions to describe single-call workflow
- [x] 5.2 Update tool docstring with JSON example showing expected structure
- [x] 5.3 Ensure no MCP prompts are exposed (remove @mcp.prompt decorators)

## 6. Keep Prompts Module (Internal Use)
- [x] 6.1 Keep `src/itch/prompts.py` for CLI demo command
- [x] 6.2 Keep EXAMPLE_QUESTIONS for `itch demo` command
- [x] 6.3 Document that prompts are internal templates, not MCP-exposed

## 7. Testing
- [x] 7.1 Test successful session with valid input (1-20 questions)
- [x] 7.2 Test validation: empty topic returns error
- [x] 7.3 Test validation: empty questions list returns error
- [x] 7.4 Test validation: >20 questions returns error
- [x] 7.5 Test validation: question with <2 choices returns error
- [x] 7.6 Test validation: missing text/label/value returns indexed error
- [x] 7.7 Test validation: duplicate IDs returns error
- [x] 7.8 Test auto-ID assignment when IDs not provided
- [x] 7.9 Test custom answer flow (allows_custom true/false)
- [x] 7.10 Test user cancellation returns partial results with "cancelled" status
- [x] 7.11 Test 5-minute timeout handling

## 8. Documentation
- [x] 8.1 Update README with single-call usage example
- [x] 8.2 Add example JSON structure for questions input
- [x] 8.3 Document that AI agents must generate questions before calling
