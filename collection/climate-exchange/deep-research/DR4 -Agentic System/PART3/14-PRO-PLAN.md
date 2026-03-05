Below is the Implementation Pack v2.0 to paste to your coding agents. It gives the exact tool naming convention, a minimal context + toolLedger design, and a complete eval harness + grader outline that writes artifacts and prints a score table.

Everything is designed for Responses API + Agents SDK, with bounded execution, no handoff loops, and receipt‑first evidence.

⸻

0) Non-negotiable rule before writing code

Stop shipping “behavioral” changes without a grader gate.
Anything that changes routing / turn budgets / tool dedupe must come with:
	•	a run artifact (reports/agentic_runs/*.json)
	•	a deterministic grade (PASS/FAIL + reasons)
	•	a small eval bank that reproduces the known failures

This is the only way out of rabbit holes.

⸻

1) Tool naming convention (exact, enforceable)

1.1 The constraint (don’t fight the platform)

Function tool names must be <= 64 chars and only include letters, numbers, underscores, and dashes. (No dots, no spaces.)  ￼

That means any existing tool names like exposure.population_within_buffer are a liability unless you’re already normalizing them before they hit the API.

1.2 The standard

We will use lower_snake_case, and prefix namespaces, all within 64 chars:
	•	Specialists (agents-as-tools): slb_spec_<domain>
Examples:
	•	slb_spec_mixed
	•	slb_spec_hazard_cyclone
	•	slb_spec_sea_level
	•	slb_spec_exposure
	•	slb_spec_adaptation
	•	slb_spec_gaps_uncertainty
	•	Dataset tools (function tools inside specialists): slb_data_<family>_<action>
Examples:
	•	slb_data_exposure_population_within_buffer
	•	slb_data_geo_admin_lookup
	•	slb_data_hazard_cyclone_tracks
	•	Utility tools: slb_util_<verb>
Examples:
	•	slb_util_gap_analysis (if it’s truly deterministic / non-LLM)

1.3 ToolNameRegistry (single source of truth)

Create a registry module (don’t scatter names across prompts).

File: packages/agents/src/slb/tool_registry.ts

import { createHash } from "node:crypto";

export const TOOL_NAME_RE = /^[A-Za-z0-9_-]{1,64}$/;

/**
 * Convert legacy / internal IDs (may contain dots) into an API-safe function tool name.
 * - Only [A-Za-z0-9_-]
 * - Max length 64
 * - Deterministic
 */
export function toSafeToolName(input: string): string {
  // Replace illegal chars with underscore
  let base = input.replace(/[^A-Za-z0-9_-]+/g, "_");

  // Ensure non-empty
  if (!base.length) base = "tool";

  // If too long, truncate + append stable hash suffix
  if (base.length > 64) {
    const hash = createHash("sha256").update(input).digest("hex").slice(0, 10);
    base = `${base.slice(0, 53)}_${hash}`; // 53 + 1 + 10 = 64
  }

  // Enforce regex
  if (!TOOL_NAME_RE.test(base)) {
    // Final fallback (should not happen)
    const hash = createHash("sha256").update(input).digest("hex").slice(0, 24);
    base = `tool_${hash}`; // <= 64
  }

  return base;
}

/** Hard fail in CI if any tool name is invalid. */
export function assertValidToolName(name: string) {
  if (!TOOL_NAME_RE.test(name)) {
    throw new Error(`Invalid tool name "${name}". Must match ${TOOL_NAME_RE}`);
  }
}

1.4 Specialist tool names must match RouteDecision.specialists_to_call 1:1

This is critical. No mapping logic inside prompts.

File: packages/agents/src/slb/specialist_ids.ts

export const SPECIALIST_TOOLNAMES = {
  mixed: "slb_spec_mixed",
  hazard_cyclone: "slb_spec_hazard_cyclone",
  sea_level: "slb_spec_sea_level",
  exposure: "slb_spec_exposure",
  adaptation: "slb_spec_adaptation",
  gaps_uncertainty: "slb_spec_gaps_uncertainty",
} as const;

export type SpecialistToolName =
  typeof SPECIALIST_TOOLNAMES[keyof typeof SPECIALIST_TOOLNAMES];


⸻

2) Specialist-as-tool input contract (so calls are structured + consistent)

Agents-as-tools default to a single input parameter, but the SDK supports structured inputs via inputBuilder + includeInputSchema.  ￼

2.1 Define the schema once

File: packages/agents/src/slb/specialist_tool_args.ts

import { z } from "zod";

export const SpecialistCallArgsSchema = z.object({
  run_id: z.string().min(4),
  level: z.enum(["L1", "L2", "L3"]),
  user_query: z.string().min(1),

  // optional but strongly preferred
  aoi: z
    .object({
      kind: z.enum(["admin", "bbox", "point", "poly"]),
      label: z.string().optional(),
      admin: z.object({ country: z.string().optional(), name: z.string().optional() }).optional(),
      bbox: z.tuple([z.number(), z.number(), z.number(), z.number()]).optional(), // [minLon,minLat,maxLon,maxLat]
      point: z.object({ lon: z.number(), lat: z.number() }).optional(),
      poly_geojson: z.any().optional(),
    })
    .optional(),

  timeframe: z
    .object({
      baseline: z.string().optional(), // e.g. "1995-2014"
      horizon_years: z.array(z.number().int()).optional(), // e.g. [2030,2050,2100]
    })
    .optional(),

  scenarios: z.array(z.string()).optional(), // e.g. SSPs/RCPs if relevant
  constraints: z.array(z.string()).optional(), // e.g. "no paid data", "coastal only"

  // to support receipt reuse across specialists (optional)
  known_receipt_ids: z.array(z.string()).optional(),
});

export type SpecialistCallArgs = z.infer<typeof SpecialistCallArgsSchema>;

2.2 Use includeInputSchema to improve reliability

When building each specialist tool, use:
	•	toolName: SPECIALIST_TOOLNAMES.<...>
	•	includeInputSchema: true
	•	inputBuilder to feed structured args as a compact prompt block

This is directly supported by the Agents SDK docs.  ￼

⸻

3) Minimal Context interface (toolLedger + receipt store + artifact store)

This is the “no more looping” control plane.

3.1 Data structures

File: packages/agents/src/slb/context.ts

import { createHash } from "node:crypto";

export type ToolCallDisposition =
  | "executed"
  | "blocked_duplicate"
  | "blocked_budget"
  | "error";

export interface ToolLedgerEntry {
  tool_name: string;
  args_hash: string;

  attempts: number;              // how many times model tried
  executed: number;              // how many times we executed (should be 0 or 1)
  disposition: ToolCallDisposition;

  first_attempt_iso: string;
  last_attempt_iso: string;

  // optional: link to receipt if executed
  receipt_id?: string;
  error_code?: string;
  error_message?: string;
}

export interface SlbBudgets {
  max_tool_exec_total: number;   // hard cap for entire run
  max_tool_exec_per_tool: number; // usually 1
  max_tool_attempts_per_signature: number; // usually 2 (1 retry allowed)
  max_receipt_raw_bytes: number; // cap raw payload persistence
}

export interface SlbRunContext {
  run_id: string;
  trace_id: string;
  group_id: string;
  workflow_name: string;

  created_at_iso: string;

  budgets: SlbBudgets;

  // Ledger keyed by tool_name + args_hash
  toolLedger: Map<string, ToolLedgerEntry>;

  // Receipts keyed by receipt_id
  receipts: Map<string, any>;

  // Artifact root for this run (local FS for now)
  artifact_dir: string;

  // Aggregate counters (for quick grading)
  tool_exec_count: number;
  tool_blocked_count: number;
  tool_error_count: number;
}

/** Canonical JSON stringify with stable key order. */
export function canonicalJson(value: any): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((k) => JSON.stringify(k) + ":" + canonicalJson(value[k])).join(",")}}`;
}

/** Hash tool args deterministically so duplicate calls can be detected. */
export function hashArgs(args: unknown): string {
  const canon = canonicalJson(args);
  return createHash("sha256").update(canon).digest("hex").slice(0, 32);
}

/** Ledger key (tool + args signature). */
export function ledgerKey(toolName: string, argsHash: string): string {
  return `${toolName}:${argsHash}`;
}

3.2 Why this works
	•	You can block repeats before execution.
	•	You can allow one retry (e.g. schema mismatch), but after that it’s blocked.
	•	The ledger becomes your single source of truth for “loop vs normal retry”.

⸻

4) Tool guardrails (SOTA: stop loops at the tool boundary)

Agents SDK supports tool guardrails that can allow/reject/throw.  ￼

Design principle:

The model is allowed to attempt a tool call multiple times, but execution is bounded and duplicates are rejected with an informative message.

4.1 Attach guardrails to every dataset tool (inside specialists)

Pseudo‑pattern (adapt to your actual tool factory):

import { tool } from "@openai/agents";
import { z } from "zod";
import { hashArgs, ledgerKey } from "./context";

// Example dataset tool
export const populationWithinBuffer = tool({
  name: "slb_data_exposure_population_within_buffer",
  description: "Return population within a radius/buffer around an AOI.",
  parameters: z.object({
    aoi: z.any(),
    radius_km: z.number().positive(),
    year: z.number().int().optional(),
  }),

  // Tool guardrails: block duplicates / budget overruns before execute
  inputGuardrails: [
    async ({ context, toolCall }) => {
      // toolCall.arguments is JSON string according to SDK
      const args = JSON.parse(toolCall.arguments);
      const argsHash = hashArgs(args);
      const key = ledgerKey(toolCall.name, argsHash);

      const now = new Date().toISOString();
      const entry = context.toolLedger.get(key);

      // 1) Duplicate execution block (one-call-per-signature)
      if (entry?.executed >= 1) {
        context.tool_blocked_count++;
        return {
          type: "rejectContent",
          message: `Duplicate tool call blocked: ${toolCall.name} (args_hash=${argsHash}). Use existing receipt_id=${entry.receipt_id}.`,
        };
      }

      // 2) Budget block
      if (context.tool_exec_count >= context.budgets.max_tool_exec_total) {
        context.tool_blocked_count++;
        return {
          type: "rejectContent",
          message: `Tool budget reached. Stop calling tools and proceed with partial synthesis.`,
        };
      }

      // 3) Track attempts
      context.toolLedger.set(key, {
        tool_name: toolCall.name,
        args_hash: argsHash,
        attempts: (entry?.attempts ?? 0) + 1,
        executed: entry?.executed ?? 0,
        disposition: "executed",
        first_attempt_iso: entry?.first_attempt_iso ?? now,
        last_attempt_iso: now,
      });

      // Optional: prevent infinite retries
      const attempts = (entry?.attempts ?? 0) + 1;
      if (attempts > context.budgets.max_tool_attempts_per_signature) {
        context.tool_blocked_count++;
        return {
          type: "rejectContent",
          message: `Too many attempts for this tool signature. Stop retrying and proceed.`,
        };
      }

      return { type: "allow" };
    },
  ],

  async execute(args, runCtx) {
    // Normal tool execution
    const result = await yourPopulationQuery(args);

    // Write raw artifact to disk and return receipt summary only
    // (receipt creation shown in your SpecialistResultSchema design)
    return result;
  },
});

This guardrail approach is directly aligned with SDK tool guardrail semantics (allow/reject/throw).  ￼

⸻

5) Tracing + runConfig standard (Responses-only compatible)

RunConfig supports:
	•	traceId, groupId, workflowName
	•	global model settings override
	•	input/output guardrails
	•	callModelInputFilter hooks  ￼

Also you can chain turns using previousResponseId (Responses-only, no Conversations required).  ￼

5.1 Deterministic trace IDs

Use stable trace IDs for artifacts (so you can correlate run artifacts to traces):

import { createHash } from "node:crypto";

export function deriveTraceId(runId: string) {
  // "trace_" + 32 hex chars
  const h = createHash("sha256").update(runId).digest("hex").slice(0, 32);
  return `trace_${h}`;
}

5.2 workflowName taxonomy (so traces are searchable)

Use:
CIE.SLB.manager_v2.<L1|L2|L3>.<case_id>

⸻

6) Eval bank + harness (writes artifacts + prints score table)

6.1 Eval bank format

File: scripts/agentic_eval_bank.json

{
  "version": "2026-02-20",
  "cases": [
    {
      "case_id": "mix_cyclone_sea_level_001",
      "level": "L2",
      "prompt": "Assess cyclone risk AND sea-level rise implications for Honiara (Solomon Islands) by 2050. Provide prioritized actions.",
      "expect": {
        "is_multi_domain": true,
        "must_include_domains": ["hazard_cyclone", "sea_level"],
        "must_call_specialist": ["slb_spec_mixed"],
        "max_tool_exec": 12
      }
    },
    {
      "case_id": "single_cyclone_001",
      "level": "L1",
      "prompt": "Cyclone hazard snapshot for Honiara. Keep it brief and evidence-backed.",
      "expect": {
        "is_multi_domain": false,
        "must_include_domains": ["hazard_cyclone"],
        "max_tool_exec": 6
      }
    }
  ]
}

6.2 Harness script (complete outline)

File: scripts/run-agentic-evals.mjs

This version assumes you hit your local API (most robust because it tests full wiring). Your agents should adapt endpoint/payload to your actual API routes.

#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const argv = process.argv.slice(2);

// Minimal CLI parsing
function getArg(name, def) {
  const idx = argv.indexOf(`--${name}`);
  if (idx === -1) return def;
  return argv[idx + 1] ?? def;
}

const baseUrl = getArg("base-url", "http://localhost:8787"); // adjust
const outDir = getArg("out-dir", "reports/agentic_runs");
const trials = Number(getArg("trials", "3"));
const mode = getArg("mode", "manager_v2");
const bankPath = getArg("bank", "scripts/agentic_eval_bank.json");

fs.mkdirSync(outDir, { recursive: true });

function deriveTraceId(runId) {
  const h = crypto.createHash("sha256").update(runId).digest("hex").slice(0, 32);
  return `trace_${h}`;
}

async function callApi({ runId, traceId, level, prompt }) {
  // Adapt this payload to match your /chat contract.
  const res = await fetch(`${baseUrl}/chat`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      // optional: force your server to use manager_v2
      "x-cie-agentic-mode": mode,
      "x-cie-run-id": runId,
      "x-cie-trace-id": traceId
    },
    body: JSON.stringify({
      message: prompt,
      level,
      // include mode also in body if your API expects it
      mode
    })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return await res.json();
}

function gradeArtifact(artifact, expect) {
  // Minimal deterministic grader (you will replace with full grader file).
  const defects = [];

  // A: trace/run integrity
  if (!artifact?.meta?.trace_id) defects.push("MISSING_TRACE_ID");
  if (!artifact?.meta?.run_id) defects.push("MISSING_RUN_ID");

  // B: termination
  const term = artifact?.meta?.termination_class;
  if (["error"].includes(term)) defects.push(`TERMINATION_${term}`);

  // C: mixed-domain expectations
  if (expect?.is_multi_domain === true) {
    if (artifact?.route_decision?.is_multi_domain !== true) defects.push("NOT_MULTI_DOMAIN");
  }

  // D: tool budgets
  const toolExec = artifact?.meta?.tool_exec_count ?? 0;
  if (expect?.max_tool_exec != null && toolExec > expect.max_tool_exec) {
    defects.push(`TOOL_BUDGET_EXCEEDED_${toolExec}>${expect.max_tool_exec}`);
  }

  // E: required domains
  const domains = new Set();
  for (const fr of artifact?.key_findings ?? []) {
    if (fr?.domain) domains.add(fr.domain);
  }
  for (const d of expect?.must_include_domains ?? []) {
    if (!domains.has(d)) defects.push(`MISSING_DOMAIN_${d}`);
  }

  // required specialist calls (if you include specialist_results)
  const specIds = new Set((artifact?.specialist_results ?? []).map((s) => s.specialist_id));
  for (const s of expect?.must_call_specialist ?? []) {
    if (!specIds.has(s)) defects.push(`MISSING_SPECIALIST_${s}`);
  }

  const pass = defects.length === 0;
  return { pass, defects };
}

async function main() {
  const bank = JSON.parse(fs.readFileSync(bankPath, "utf8"));
  const results = [];

  for (const c of bank.cases) {
    for (let t = 1; t <= trials; t++) {
      const runId = `${c.case_id}__t${t}__${Date.now()}`;
      const traceId = deriveTraceId(runId);

      const started = Date.now();
      let apiJson;
      let artifactPath;

      try {
        apiJson = await callApi({
          runId,
          traceId,
          level: c.level,
          prompt: c.prompt
        });

        // IMPORTANT:
        // Your API should return final report JSON (ReportSchema) under some field.
        // Adjust accordingly:
        const artifact = apiJson.report ?? apiJson.final ?? apiJson;

        artifactPath = path.join(outDir, `${runId}.json`);
        fs.writeFileSync(artifactPath, JSON.stringify(artifact, null, 2), "utf8");

        const grade = gradeArtifact(artifact, c.expect);

        results.push({
          case_id: c.case_id,
          trial: t,
          run_id: runId,
          trace_id: traceId,
          ms: Date.now() - started,
          pass: grade.pass,
          defects: grade.defects,
          artifactPath
        });
      } catch (err) {
        results.push({
          case_id: c.case_id,
          trial: t,
          run_id: runId,
          trace_id: traceId,
          ms: Date.now() - started,
          pass: false,
          defects: ["HARNESS_ERROR", String(err?.message ?? err)],
          artifactPath
        });
      }
    }
  }

  // Print score table
  const byCase = new Map();
  for (const r of results) {
    const arr = byCase.get(r.case_id) ?? [];
    arr.push(r);
    byCase.set(r.case_id, arr);
  }

  console.log("\n=== AGENTIC EVAL RESULTS ===");
  for (const [caseId, arr] of byCase.entries()) {
    const passCount = arr.filter((x) => x.pass).length;
    console.log(`${caseId}: ${passCount}/${arr.length} PASS`);
    for (const r of arr) {
      console.log(
        `  t${r.trial} ${r.pass ? "PASS" : "FAIL"} ${r.ms}ms defects=${r.defects.join(",")} artifact=${r.artifactPath ?? "n/a"}`
      );
    }
  }

  // Write summary JSON
  fs.writeFileSync(
    path.join(outDir, `eval_summary_${Date.now()}.json`),
    JSON.stringify({ mode, trials, results }, null, 2),
    "utf8"
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});


⸻

7) Full grader (the real gate)

Your quick harness grader above is intentionally shallow.
Now add the real deterministic grader implementing the rules I specified earlier (schema validity, evidence integrity, duplication, mixed routing, termination classes).

Key addition: tool repetition check
You can compute from:
	•	artifact.meta.tool_exec_count
	•	ledger lines if you persist them
	•	or artifact.specialist_results[].metrics totals

⸻

8) SOTA “no loop” mechanics you should explicitly use in Agents SDK

These are the SDK-native levers that matter most for your situation:
	1.	Tool guardrails to reject duplicates & over-budget calls (pre-execution).  ￼
	2.	RunConfig tracing: set traceId, groupId, workflowName, and (optionally) modelSettings overrides.  ￼
	3.	Agents-as-tools: use agent.asTool() plus includeInputSchema for structured calls.  ￼
	4.	Prevent infinite loops: SDK resets toolChoice and supports toolUseBehavior as additional control for function tools.  ￼
	5.	Responses-only continuity: chain with previousResponseId if you later need multi-turn without Conversations API.  ￼

⸻

9) Attack sequence for your coding agents (assignment-ready)

Agent A — Tool registry + naming

Deliverable: tool_registry.ts + a CI check that asserts all tool names match the allowed regex.
Gate: build fails if any tool violates ^[A-Za-z0-9_-]{1,64}$.  ￼

Agent B — Context + toolLedger

Deliverable: context.ts + integration points where tools can read/update ledger.
Gate: every dataset tool execution increments ledger + counters.

Agent C — Tool guardrails rollout (top 10 tools first)

Deliverable: guardrails added to top tool families (geo/admin lookup, exposure buffer, cyclone hazard fetch, sea-level fetch).
Gate: duplicate tool signatures never execute twice; duplicates are rejected with a useful message.  ￼

Agent D — Eval harness + artifacts

Deliverable: agentic_eval_bank.json + run-agentic-evals.mjs producing reports/agentic_runs/*.json and summary table.

Agent E — Deterministic grader

Deliverable: agentic_grade_run.mjs + integrate into harness (fail build if <95% pass).

Agent F — Manager v2 wiring (specialists-as-tools + receipts)

Deliverable: orchestrator uses specialist tools; specialists emit SpecialistResultSchema; orchestrator emits ReportSchema.

⸻

10) One more critical nuance (don’t get tricked again)

If you use Structured Outputs for the orchestrator, the run can end as soon as the model emits valid schema—even if it didn’t call tools. So you must either:
	•	make tool calls unavoidable via orchestration logic + eval gates, or
	•	structure the flow into plan → execute → synth phases

We can decide which once your harness is running, because the harness will tell you immediately whether “schema-first hallucination” is happening.

⸻

If you want, I’ll now write the full grader spec (actual code) that implements all the deterministic checks from the earlier message (including exact duplicate detection and evidence index referential integrity), so your agents can drop it in and immediately start getting PASS/FAIL with actionable defect codes.