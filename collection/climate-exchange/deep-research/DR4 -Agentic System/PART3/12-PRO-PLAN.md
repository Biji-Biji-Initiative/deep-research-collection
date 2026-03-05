You’re in the “good news / bad news” zone:
	•	Good news: your direction (manager/orchestrator + specialists-as-tools + strict schemas + deterministic trace IDs + receipt-first tools + bounded budgets) is exactly the SOTA path for your symptom set.
	•	Bad news: to get “predictable, bounded, production‑reliable,” you must make a control-plane cutover. Stabilizing the current handoff+recovery-narrator approach will always be fragile.

Below is what you should paste to your coding agents as the next execution order, plus the exact schema pack and a grading spec that will catch your current failures with near-zero false positives.

⸻

Mission for the coding agents

Objective

Deliver CIE SLB Manager v2: a Responses-API-first, SDK-native orchestration that:
	1.	routes mixed-domain deterministically
	2.	calls tools without repetition/loops
	3.	always finalizes with a single, structured report object
	4.	produces one correlated trace per run (no “mystery narrator trace”)
	5.	is regressible via an eval bank + deterministic graders

Primary constraints
	•	Prefer Agents SDK mechanics over prompt hacks.
	•	No “hope-based” fixes: every change must have a failing test/eval before, and pass after.

⸻

What we know about your current state (only what agents need)
	1.	You’re already using Agents SDK (@openai/agents + @openai/agents-core 0.4.11).
	2.	Current flow is Responses API via Runner.run(...) (not Conversations API).
	3.	Mixed routing exists, but tool surfaces are partitioned per specialist, so misrouting → missing datasets.
	4.	Narration is fragmented:
	•	sometimes handoff to narrator
	•	sometimes recovery/fallback narrator runs in a new MemorySession (creating separate traces)
	5.	You have loop handling/guarded tool execution already, but the semantics of “tool loop detected” vs “blocked duplicate” are conflated.

⸻

What needs to be done next (the exact attack sequence)

Phase 1 — Build the “Manager v2” orchestration under a feature flag

Goal: Orchestrator retains control; specialists are called via agent.asTool(); narrator handoff removed from core path.

Task 1.1 Add schema pack and enforce structured outputs everywhere
	•	Create packages/agents/src/slb/schemas.ts (or similar) containing:
	•	RouteDecisionSchema
	•	ExecutionPlanSchema
	•	SpecialistResultSchema
	•	ReceiptSchema
	•	ReportSchema
	•	All specialist agents must define outputType: SpecialistResultSchema.
	•	Orchestrator must define outputType: ReportSchema.

Why: structured outputs are how you prevent “inconsistent termination semantics” and allow deterministic grading.

Task 1.2 Create “CIE_SLB_Orchestrator_v2” using specialists-as-tools
	•	Implement a new network factory (e.g. createSlbNetworkV2() in packages/agents/src/slb/network.ts) that returns:
	•	orchestratorV2: Agent<Context, Report>
	•	specialist agents (hazard / sea level / exposure / etc.) exposed as tools using agent.asTool()

Use asTool() advanced options intentionally:
	•	includeInputSchema: true to reduce schema mistakes in nested calls  ￼
	•	pass nested runOptions/runConfig to bound specialist turns  ￼
	•	optional onStream to bubble nested events up into your evidence recorder  ￼

Task 1.3 Wire runSlbChatTurn to choose “manager_v2” mode
	•	Add an env or config flag:
	•	CIE_SLB_ORCH_MODE=manager_v2 (new)
	•	default keeps current behavior until v2 proves stable
	•	In packages/agents/src/slb/run.ts, branch the selection to use orchestratorV2 when flag is on.

Task 1.4 Remove narrator handoff from core completion
	•	In manager_v2:
	•	No transfer_to_* for narration
	•	Orchestrator produces final report itself (or optionally calls a writer agent as a tool, not a handoff)

This eliminates the entire “handoff loop / narrator trace fragmentation” class.

⸻

Phase 2 — Deterministic tracing & evidence capture (no DB required)

Goal: Every run has a single, correlated trace ID and a local evidence artifact you can grade.

Task 2.1 Set traceId, groupId, workflowName explicitly in RunConfig

In your Runner.run(...) call, pass runConfig with:
	•	traceId (deterministic from your internal run_id)
	•	groupId (thread/session id; OK to be “unknown” early)
	•	workflowName (e.g., CIE.SLB.L2.manager_v2)

RunConfig supports these fields  ￼

Also decide if you want:
	•	traceIncludeSensitiveData: false in prod (spans exist, payload removed)  ￼

Task 2.2 Record the full trajectory to disk (temporary store)

Until DB run store is solid:
	•	write a JSON artifact per run to reports/agentic_runs/<run_id>.json
	•	include:
	•	finalOutput
	•	state (serializable)
	•	newItems
	•	tool ledger metrics (below)
	•	usage if present
	•	traceId, workflowName

This becomes your “single source of truth” for evals.

⸻

Phase 3 — Tool repetition becomes mechanically impossible

Goal: “repeated tool loops” become “blocked duplicate attempts,” not runaway runs.

Task 3.1 Implement a tool-call ledger in Agent Context

Agents SDK context is DI passed to tools/guardrails/handoffs  ￼

Add to your context:
	•	toolLedger: Map<string, { firstSeenAt, countAttempted, countExecuted }>
	•	toolBudgets: { maxTotalToolExec, maxPerToolExec, maxPerSpecialistExec }
	•	receiptsIndex: Map<receipt_id, Receipt>

Ledger key = stable hash of:
tool_name + canonical_json(args)

Task 3.2 Enforce tool ledger with tool guardrails

Tool guardrails can reject tool calls before execution and can replace outputs after execution  ￼

Implement:
	•	Input guardrail (per tool):
	•	canonicalize args
	•	if signature already executed → rejectContent (“Duplicate blocked; change args or proceed”)  ￼
	•	if tool budget exceeded → rejectContent with next-step guidance
	•	Output guardrail (per tool):
	•	enforce “receipt-first” (see below)
	•	enforce max output size
	•	strip raw arrays/large payloads

Task 3.3 Standardize “receipt-first” outputs for dataset tools

All dataset tools must return:
	•	small summary
	•	receipt_id
	•	provenance fields
	•	pointer to stored raw (raw_uri or file path)

Never dump raw data arrays into model-visible content.

⸻

Phase 4 — Eval bank + deterministic graders (your new quality gate)

Goal: you can prove “loop-free + mixed-domain complete + finalization consistent” at scale.

Task 4.1 Create an eval bank JSON

scripts/agentic_eval_bank.json with ≥ 10 cases:
	•	2× L1 single-domain
	•	2× L2 mixed-domain
	•	2× L3 deep reasoning (requires uncertainties/gaps)
	•	2× tool failure pathologies (invalid input, timeout)
	•	2× routing ambiguities

Each case includes:
	•	prompt
	•	expected_domains[]
	•	expected_specialists_min (e.g. 2 for cyclone+sea level)
	•	tool budgets
	•	allowed termination classes

Task 4.2 Add deterministic graders (no LLM grader required for core gating)

Write scripts/agentic_grade_run.mjs which loads a run artifact and returns:
	•	pass: boolean
	•	score: 0..100
	•	fail_reasons[]
	•	metrics

Use the grading rules below.

Task 4.3 Add CI gate

node scripts/run-agentic-evals.mjs --mode=manager_v2 --trials=10 --fail-fast

Pass criteria:
	•	≥ 95% pass on non-pathological tasks
	•	100% schema-valid outputs
	•	0% “tool_loop_detected” on successful completions

⸻

Exact schema pack (Zod, implementation-ready)

Create packages/agents/src/slb/schemas.ts:

import { z } from "zod";

/**
 * Core enums
 */
export const LLevelSchema = z.enum(["L1", "L2", "L3"]);
export type LLevel = z.infer<typeof LLevelSchema>;

// Keep domain tags broad; you can refine later without breaking contracts.
export const DomainTagSchema = z.enum([
  "hazard_cyclone",
  "hazard_rainfall",
  "hazard_heat",
  "sea_level",
  "storm_surge",
  "coastal_flooding",
  "exposure_population",
  "exposure_assets",
  "admin_geography",
  "adaptation_options",
  "uncertainty_gaps",
  "meta",
]);
export type DomainTag = z.infer<typeof DomainTagSchema>;

/**
 * Termination classes (map your existing ones into this set)
 */
export const TerminationClassSchema = z.enum([
  "complete",
  "partial_needs_clarification",
  "partial_tool_failure",
  "max_turns",
  "tool_loop_detected",
  "error",
]);
export type TerminationClass = z.infer<typeof TerminationClassSchema>;

/**
 * Receipt-first evidence object produced by tools (and referenced by findings).
 */
export const ReceiptSchema = z.object({
  receipt_id: z.string().min(8),
  tool_name: z.string().min(1),
  args_hash: z.string().min(8),

  // Small model-visible summary only.
  summary: z.record(z.any()).default({}),

  provenance: z.object({
    dataset: z.string().min(1),
    dataset_version: z.string().optional(),
    retrieved_at_iso: z.string().min(10),
  }),

  // Pointer to raw stored artifact (file path, object store URI, etc.).
  raw_uri: z.string().optional(),
  raw_bytes: z.number().int().nonnegative().optional(),

  warnings: z.array(z.string()).default([]),
});
export type Receipt = z.infer<typeof ReceiptSchema>;

/**
 * A single factual claim backed by receipts.
 * This is the unit your graders should reason over.
 */
export const FindingSchema = z.object({
  finding_id: z.string().min(4),
  domain: DomainTagSchema,
  claim: z.string().min(1),

  // Must be non-empty if claim is factual.
  evidence_receipt_ids: z.array(z.string().min(8)).min(1),

  // Calibrated confidence; allow 0..1
  confidence: z.number().min(0).max(1),

  assumptions: z.array(z.string()).default([]),
  caveats: z.array(z.string()).default([]),
});
export type Finding = z.infer<typeof FindingSchema>;

/**
 * Specialist output contract.
 * Must be returned by every specialist agent tool.
 */
export const SpecialistResultSchema = z.object({
  specialist_id: z.string().min(3),
  domains: z.array(DomainTagSchema).min(1),

  status: z.enum(["ok", "partial", "needs_clarification", "error"]),
  executive_summary: z.string().min(1),

  findings: z.array(FindingSchema).default([]),
  receipts: z.array(ReceiptSchema).default([]),

  uncertainties: z.array(z.string()).default([]),
  recommended_next_steps: z.array(z.string()).default([]),

  metrics: z.object({
    tool_exec_count: z.number().int().nonnegative().default(0),
    tool_blocked_duplicate_count: z.number().int().nonnegative().default(0),
    tool_blocked_budget_count: z.number().int().nonnegative().default(0),
    tool_error_count: z.number().int().nonnegative().default(0),
  }).default({}),
});
export type SpecialistResult = z.infer<typeof SpecialistResultSchema>;

/**
 * Route decision: produced by Orchestrator early (or by a classifier tool).
 */
export const RouteDecisionSchema = z.object({
  level: LLevelSchema,
  is_multi_domain: z.boolean(),
  domains: z.array(DomainTagSchema).min(1),

  // Specialists to consult as tools; Orchestrator stays in control.
  specialists_to_call: z.array(z.string().min(3)).default([]),

  clarifying_questions: z.array(z.string()).default([]),
  rationale: z.string().min(1),
  confidence: z.number().min(0).max(1),
});
export type RouteDecision = z.infer<typeof RouteDecisionSchema>;

/**
 * Execution plan: Orchestrator declares intended calls + budgets (then code executes).
 * Keep this small and evaluable.
 */
export const ExecutionStepSchema = z.object({
  step_id: z.string().min(3),
  kind: z.enum(["call_specialist", "ask_user", "finalize"]),

  specialist_id: z.string().optional(), // required for call_specialist
  input: z.record(z.any()).default({}),

  budgets: z.object({
    max_turns: z.number().int().positive().default(4),
    max_tool_exec: z.number().int().positive().default(10),
    max_wall_ms: z.number().int().positive().optional(),
  }).default({}),

  depends_on: z.array(z.string()).default([]),
  parallel_group: z.string().optional(),
});
export type ExecutionStep = z.infer<typeof ExecutionStepSchema>;

export const ExecutionPlanSchema = z.object({
  plan_id: z.string().min(6),
  steps: z.array(ExecutionStepSchema).min(1),

  orchestrator_budgets: z.object({
    max_turns: z.number().int().positive(),
    max_tool_exec_total: z.number().int().positive(),
  }),
});
export type ExecutionPlan = z.infer<typeof ExecutionPlanSchema>;

/**
 * Final report output schema: stable, renderable, gradable.
 */
export const ReportSchema = z.object({
  title: z.string().min(3),

  // For immediate UX. Render this directly.
  user_markdown: z.string().min(1),

  executive_summary: z.string().min(1),

  // For decision quality; keep structured.
  key_findings: z.array(FindingSchema).default([]),
  recommendations: z.array(z.object({
    action: z.string().min(1),
    rationale: z.string().min(1),
    timeframe: z.string().optional(),
    priority: z.enum(["low", "medium", "high"]).default("medium"),
  })).default([]),

  uncertainties: z.array(z.object({
    uncertainty: z.string().min(1),
    impact: z.string().optional(),
    how_to_reduce: z.string().optional(),
    priority: z.enum(["low", "medium", "high"]).default("medium"),
  })).default([]),

  evidence_index: z.array(ReceiptSchema).default([]),

  // Debuggable internals (optional to show user; always saved to artifact)
  route_decision: RouteDecisionSchema.optional(),
  execution_plan: ExecutionPlanSchema.optional(),
  specialist_results: z.array(SpecialistResultSchema).default([]),

  meta: z.object({
    run_id: z.string().min(4),
    trace_id: z.string().min(8),
    workflow_name: z.string().min(3),

    termination_class: TerminationClassSchema,
    turn_count: z.number().int().nonnegative(),
    tool_exec_count: z.number().int().nonnegative(),
    tool_blocked_count: z.number().int().nonnegative(),

    created_at_iso: z.string().min(10),
  }),
});
export type Report = z.infer<typeof ReportSchema>;


⸻

Deterministic grading rules (near-zero false positives)

Implement scripts/agentic_grade_run.mjs with these rules. All are deterministic (no LLM graders needed to catch your current failures).

1) Output validity
	•	Fail if ReportSchema.safeParse(finalOutput).success === false
	•	Fail if meta.trace_id missing or doesn’t match your expected trace ID format
	•	Fail if meta.run_id missing

2) Finalization + termination correctness

For non-pathological tasks:
	•	Fail if termination_class ∈ { "tool_loop_detected", "max_turns", "error" }
	•	Fail if user_markdown contains any of:
	•	TOOL_LOOP_LIMIT
	•	ERR_INVALID_INPUT
	•	TOOL_RETRY_EXHAUSTED
(these should never leak into user output in a clean system)

3) Mixed-domain completeness (the core issue)

For tasks marked expected_domains.length >= 2:
	•	Fail if route_decision.is_multi_domain !== true
	•	Fail if route_decision.domains doesn’t include all expected_domains (allow small mapping table)
	•	Fail if specialist_results covers fewer than 2 distinct domains (or fewer than expected_specialists_min)
	•	coverage = union of specialist_results[].domains

4) Tool repetition / loops

From run artifact newItems (or your tool ledger metrics):
	•	Fail if any tool signature executed more than once with identical args_hash
	•	Fail if tool_blocked_duplicate_count exceeds threshold (e.g., > 2) on a normal task
	•	Fail if tool_exec_count exceeds the per-task budget

5) Evidence integrity (receipts)
	•	Fail if any Finding.evidence_receipt_ids contains an id not present in evidence_index
	•	Fail if key_findings.length > 0 and evidence_index.length === 0

This catches “report looks good but has no evidence” and “missing dataset coverage” immediately.

⸻

Responses API: do we need Conversations API?

Not for proving stability.

Use Responses API + SDK Runner per request. Later, if you want long-lived threads without building your own store:
	•	adopt Sessions and/or a compaction decorator like OpenAIResponsesCompactionSession, which triggers responses.compact as history grows  ￼

But that’s Phase 2 productization — not required for the manager_v2 cutover.

⸻

What to tell your agents to do today

If you want a crisp “do this next” list to paste into a coding agent:
	1.	Implement the schema pack exactly as above and wire outputType into orchestrator + specialists.
	2.	Create manager_v2 network: orchestrator + specialists as tools (with includeInputSchema: true).  ￼
	3.	Feature flag wiring in run.ts to select manager_v2.
	4.	Explicit RunConfig tracing: set traceId, groupId, workflowName.  ￼
	5.	Tool guardrails + ledger: reject duplicate tool signatures before execution.  ￼
	6.	Receipt-first tool outputs: no raw JSON arrays into model context.
	7.	Eval bank + graders: implement the deterministic grader rules and run 10 trials per task.
	8.	Only then: tune budgets and remove old narrator recovery paths once v2 passes ≥95%.

⸻

If you want, I can also provide a single “Orchestrator instruction block” (the exact system prompt for manager_v2) that’s optimized for:
	•	routing → plan → execute → synthesize
	•	strict schema compliance
	•	no tool retries unless args change
	•	explicit fallback behavior (partial reports with clarifying questions)

Just say: “give orchestrator prompt + specialist prompts.”