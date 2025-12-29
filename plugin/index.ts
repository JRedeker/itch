/**
 * OpenCode Plugin for Itch - Socratic Questioning Tool
 *
 * This plugin provides the `itch` tool for interactive Socratic questioning.
 * It spawns the Python `itch` CLI as a subprocess to handle the actual
 * user interaction via questionary.
 */

import type { Plugin } from "@opencode-ai/plugin";
import { tool } from "@opencode-ai/plugin";

const z = tool.schema;

// =============================================================================
// Configuration
// =============================================================================

const PLUGIN_VERSION = "0.2.0";
const DEFAULT_TIMEOUT_MS = 300_000; // 5 minutes
const MIN_CHOICES_SELECT = 2;
const MIN_CHOICES_CHECKBOX = 1;
const MAX_QUESTIONS = 20;

interface Config {
  timeout: number;
  debug: boolean;
  itchPath?: string;
}

function loadConfig(): Config {
  const timeout = parseInt(process.env.ITCH_TIMEOUT ?? "", 10);
  return {
    timeout: Number.isNaN(timeout) ? DEFAULT_TIMEOUT_MS : timeout,
    debug: process.env.ITCH_DEBUG === "true",
    itchPath: process.env.ITCH_PATH,
  };
}

function debugLog(config: Config, ...args: unknown[]): void {
  if (config.debug) {
    console.log("[itch-plugin]", ...args);
  }
}

// =============================================================================
// Zod Schemas (matching Python models in src/itch/models.py)
// =============================================================================

const QuestionTypeSchema = z.enum(["select", "confirm", "text", "scale", "checkbox"]);

const ChoiceSchema = z.object({
  label: z.string().describe("Display text shown to user"),
  value: z.string().describe("Identifier returned when this choice is selected"),
});

const QuestionSchema = z.object({
  id: z
    .number()
    .int()
    .positive()
    .optional()
    .describe("Question ID (auto-assigned if not provided)"),
  text: z.string().min(1).describe("The question text to display"),
  type: QuestionTypeSchema.default("select").describe(
    "Question type: select (multiple choice), confirm (yes/no), text (free-form), scale (1-5), checkbox (multi-select)"
  ),
  choices: z
    .array(ChoiceSchema)
    .optional()
    .describe("List of answer choices (required for select/checkbox types)"),
  allows_custom: z
    .boolean()
    .default(true)
    .describe("Whether to show 'Other' option for custom answers (select/checkbox only)"),
  scale_labels: z
    .tuple([z.string(), z.string()])
    .optional()
    .describe("Labels for scale endpoints, e.g., ['Not at all', 'Completely']"),
});

// Type definitions
type QuestionType = "select" | "confirm" | "text" | "scale" | "checkbox";

interface Choice {
  label: string;
  value: string;
}

interface Question {
  id?: number;
  text: string;
  type?: QuestionType;
  choices?: Choice[];
  allows_custom?: boolean;
  scale_labels?: [string, string];
}

// Response types (matching Python ItchResponse)
interface Answer {
  question_id: number;
  selected_value: string;
  is_custom: boolean;
}

interface ItchResponse {
  status: "complete" | "cancelled" | "error";
  topic: string;
  questions: Question[];
  answers: Answer[];
  error?: string;
}

// BunShell type (simplified for our use case)
type BunShell = (
  strings: TemplateStringsArray,
  ...values: unknown[]
) => { quiet(): Promise<unknown> };

// =============================================================================
// Client-Side Validation
// =============================================================================

/**
 * Validates questions before spawning the Python subprocess.
 * Returns null if valid, or an error message string if invalid.
 */
function validateQuestions(questions: Question[]): string | null {
  if (!questions.length) {
    return "At least one question is required";
  }

  if (questions.length > MAX_QUESTIONS) {
    return `Maximum ${MAX_QUESTIONS} questions allowed`;
  }

  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];
    const qType = q.type ?? "select";

    if (!q.text.trim()) {
      return `Question ${i + 1} is missing text`;
    }

    // Type-specific validation
    if (qType === "select") {
      const choices = q.choices ?? [];
      if (choices.length < MIN_CHOICES_SELECT) {
        return `Question ${i + 1}: Select questions require at least ${MIN_CHOICES_SELECT} choices`;
      }
      for (let j = 0; j < choices.length; j++) {
        const c = choices[j];
        if (!c.label.trim()) {
          return `Question ${i + 1}, choice ${j + 1} is missing a label`;
        }
        if (!c.value.trim()) {
          return `Question ${i + 1}, choice ${j + 1} is missing a value`;
        }
      }
    } else if (qType === "checkbox") {
      const choices = q.choices ?? [];
      if (choices.length < MIN_CHOICES_CHECKBOX) {
        return `Question ${i + 1}: Checkbox questions require at least ${MIN_CHOICES_CHECKBOX} choice`;
      }
      for (let j = 0; j < choices.length; j++) {
        const c = choices[j];
        if (!c.label.trim()) {
          return `Question ${i + 1}, choice ${j + 1} is missing a label`;
        }
        if (!c.value.trim()) {
          return `Question ${i + 1}, choice ${j + 1} is missing a value`;
        }
      }
    } else if (qType === "scale") {
      // scale_labels is optional but if provided must have 2 elements (enforced by Zod tuple)
      // No additional validation needed here
    }
    // confirm and text types don't require choices
  }

  return null; // Valid
}

// =============================================================================
// Python Package Discovery
// =============================================================================

/**
 * Resolves the command to run itch CLI.
 * Resolution order:
 * 1. ITCH_PATH environment variable (explicit override)
 * 2. `itch` command in PATH (global pip/pipx install)
 * 3. `uv run itch` (uv-based execution)
 * 4. Error with installation instructions
 */
async function resolveItchCommand(
  config: Config,
  $: BunShell
): Promise<string[]> {
  // 1. Explicit override via environment variable
  if (config.itchPath) {
    debugLog(config, `Using ITCH_PATH: ${config.itchPath}`);
    return [config.itchPath];
  }

  // 2. Check if itch is in PATH
  try {
    await $`which itch`.quiet();
    debugLog(config, "Found itch in PATH");
    return ["itch"];
  } catch {
    // Not found in PATH, continue
  }

  // 3. Try uv run
  try {
    await $`which uv`.quiet();
    debugLog(config, "Using uv run itch");
    return ["uv", "run", "itch"];
  } catch {
    // uv not available either
  }

  // 4. Error with installation instructions
  throw new Error(
    "itch not found. Install with one of:\n" +
      "  pip install itch\n" +
      "  pipx install itch\n" +
      "  uv pip install itch\n" +
      "Or set ITCH_PATH environment variable to the itch executable."
  );
}

// =============================================================================
// Subprocess Execution
// =============================================================================

/**
 * Executes the itch CLI with the given topic and questions.
 */
async function executeItch(
  config: Config,
  $: BunShell,
  topic: string,
  questions: Question[]
): Promise<ItchResponse> {
  const cmd = await resolveItchCommand(config, $);
  const questionsJson = JSON.stringify(questions);

  debugLog(config, `Executing: ${cmd.join(" ")} ask --topic "${topic}" --questions '...'`);

  try {
    // Build the command based on the resolved path
    const args = ["ask", "--topic", topic, "--questions", questionsJson, "--json"];

    const proc = Bun.spawn([...cmd, ...args], {
      stdout: "pipe",
      stderr: "pipe",
      stdin: "inherit", // Allow interactive input
    });

    // Set up timeout
    const timeoutId = setTimeout(() => {
      proc.kill();
    }, config.timeout);

    let exitCode: number;
    try {
      exitCode = await proc.exited;
      clearTimeout(timeoutId);
    } catch {
      clearTimeout(timeoutId);
      throw new Error(`Subprocess timed out after ${config.timeout}ms`);
    }

    const stdout = (await new Response(proc.stdout).text()).trim();
    const stderr = (await new Response(proc.stderr).text()).trim();

    debugLog(config, `Exit code: ${exitCode}`);
    debugLog(config, `stdout: ${stdout}`);
    if (stderr) debugLog(config, `stderr: ${stderr}`);

    // Handle user cancellation (Ctrl+C)
    if (exitCode === 130) {
      return {
        status: "cancelled",
        topic,
        questions,
        answers: [],
        error: "Session cancelled by user",
      };
    }

    // Handle other non-zero exit codes
    if (exitCode !== 0) {
      // Check for TTY errors
      if (stderr.includes("questionary") || stderr.includes("tty") || stderr.includes("terminal")) {
        return {
          status: "error",
          topic,
          questions,
          answers: [],
          error:
            "Interactive mode requires a TTY. This tool cannot run in non-interactive environments.",
        };
      }

      return {
        status: "error",
        topic,
        questions,
        answers: [],
        error: stderr || `Process exited with code ${exitCode}`,
      };
    }

    // Parse JSON response
    try {
      // The CLI outputs an array of answers directly
      const answers = JSON.parse(stdout) as Answer[];
      return {
        status: "complete",
        topic,
        questions,
        answers,
      };
    } catch {
      return {
        status: "error",
        topic,
        questions,
        answers: [],
        error: `Invalid JSON response from itch CLI: ${stdout.slice(0, 200)}`,
      };
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      status: "error",
      topic,
      questions,
      answers: [],
      error: message,
    };
  }
}

// =============================================================================
// Plugin Export
// =============================================================================

const ItchPlugin: Plugin = (ctx) => {
  const config = loadConfig();

  debugLog(config, `Initializing itch plugin v${PLUGIN_VERSION}`);
  debugLog(config, `Config: timeout=${config.timeout}ms, debug=${config.debug}`);

  return Promise.resolve({
    tool: {
      itch: tool({
        description:
          "Present Socratic questions to the user interactively and collect their answers. " +
          "Supports multiple question types: select (multiple choice), confirm (yes/no), text (free-form), scale (1-5 rating), checkbox (multi-select). " +
          "Use this to explore topics, gather preferences, or guide decision-making through thoughtful inquiry.",
        args: {
          topic: z.string().min(1).describe("The topic being explored through questioning"),
          questions: z
            .array(QuestionSchema)
            .min(1)
            .max(MAX_QUESTIONS)
            .describe(
              `Array of questions to ask (1-${MAX_QUESTIONS}). Each question has 'text' and optional 'type' (defaults to 'select'). ` +
              "Types: select (needs 2+ choices), confirm (yes/no), text (free-form), scale (1-5), checkbox (needs 1+ choices)."
            ),
        },
        async execute(args) {
          debugLog(config, `itch tool called with topic: ${args.topic}`);

          const questions = args.questions as Question[];

          // Client-side validation
          const validationError = validateQuestions(questions);
          if (validationError) {
            const response: ItchResponse = {
              status: "error",
              topic: args.topic,
              questions,
              answers: [],
              error: validationError,
            };
            return JSON.stringify(response, null, 2);
          }

          // Auto-assign IDs if not provided, ensure type defaults
          const questionsWithDefaults = questions.map((q, i) => ({
            ...q,
            id: q.id ?? i + 1,
            type: q.type ?? "select",
          }));

          // Execute the Python CLI
          const response = await executeItch(
            config,
            ctx.$ as unknown as BunShell,
            args.topic,
            questionsWithDefaults
          );

          debugLog(config, `Response status: ${response.status}`);
          return JSON.stringify(response, null, 2);
        },
      }),
    },
  });
};

export default ItchPlugin;
