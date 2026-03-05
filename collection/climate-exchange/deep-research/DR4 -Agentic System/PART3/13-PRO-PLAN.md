Below is the exact packet you should paste to your coding agents. It contains:
	1.	The improved plan (what to build next, in order)
	2.	The exact schemas (v1.1) for Route / Plan / SpecialistResult / Receipt / Report
	3.	The exact deterministic grading rules that will catch your current failures
	4.	The full prompt blocks (Orchestrator + 5 Specialists + optional Verifier)
	5.	Implementation notes for a Responses‑API‑only rollout (no DB, no Conversations API required to prove stability)

⸻

1) What needs to be done next (attack sequence)

Phase 1 — Cutover to Manager v2 (Orchestrator owns the run)

Goal: eliminate handoff/narrator fragmentation and make loops mechanically bounded.

Do this:
	1.	Add the schema pack (Section 2) and enforce outputType:
	•	Orchestrator: ReportSchema
	•	Every specialist: SpecialistResultSchema
	2.	Build Manager v2 network:
	•	Orchestrator has only specialist tools (each specialist is exposed via agent.asTool()).
	•	Specialists have only dataset tools they need.
	•	Orchestrator never calls dataset tools.
	3.	Feature flag the new flow:
	•	CIE_SLB_ORCH_MODE=manager_v2
	•	Default remains current flow until v2 passes eval gates.

Hard rule: In manager_v2, no transfer/handoff for narration. Orchestrator synthesizes final.

⸻

Phase 2 — Tracing + evidence (no DB required)

Goal: one correlated trace per run and a local artifact you can grade.

Do this:
	•	Pass runConfig with explicit:
	•	traceId (derive from run_id)
	•	groupId (thread/session id if available)
	•	workflowName (e.g. CIE.SLB.manager_v2.L2)
	•	Persist a JSON artifact per run to reports/agentic_runs/<run_id>.json containing:
	•	finalOutput, state, newItems, usage, traceId, workflowName
	•	tool ledger metrics (blocked duplicates, exec count, etc.)

This replaces the need for a DB run store during proving.

⸻

Phase 3 — Kill tool repetition (ledger + guardrails)

Goal: “tool loops” become “duplicate blocked once → proceed,” not infinite retries.

Do this:
	•	Add a toolLedger to the shared Context:
	•	key = hash(tool_name + canonical_args_json)
	•	store attempted/executed counts
	•	Add tool guardrails:
	•	reject duplicate signatures before executing
	•	enforce per-tool and per-run budgets
	•	enforce receipt-first outputs and size caps

⸻

Phase 4 — Evals + deterministic graders

Goal: 95% pass across scripted runs; no more “it passed by luck.”

Do this:
	•	Create scripts/agentic_eval_bank.json (≥ 10 tasks; L1/L2/L3 + pathologies)
	•	Implement scripts/agentic_grade_run.mjs (deterministic grading rules in Section 3)
	•	Add a harness scripts/run-agentic-evals.mjs --mode=manager_v2 --trials=10

Gate: no merge unless evals pass.

⸻

2) Schema pack v1.1 (Zod, strict & gradable)

Create packages/agents/src/slb/schemas.ts:

import { z } from "zod";

/** ---------- Enums ---------- */

export const LLevelSchema = z.enum(["L1", "L2", "L3"]);
export type LLevel = z.infer<typeof LLevelSchema>;

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

export const TerminationClassSchema = z.enum([
  "complete",
  "partial_needs_clarification",
  "partial_tool_failure",
  "max_turns",
  "max_turns_recovered",
  "tool_loop_detected",
  "error",
]);
export type TerminationClass = z.infer<typeof TerminationClassSchema>;

/** ---------- Evidence receipts ---------- */

export const ReceiptSchema = z.object({
  receipt_id: z.string().min(8),
  tool_name: z.string().min(1),
  args_hash: z.string().min(8),

  // Small, model-visible summary only.
  summary: z.record(z.any()).default({}),

  provenance: z.object({
    dataset: z.string().min(1),
    dataset_version: z.string().optional(),
    retrieved_at_iso: z.string().min(10),
  }).strict(),

  // Pointer to raw stored artifact (local file path, object store URI, etc.)
  raw_uri: z.string().optional(),
  raw_bytes: z.number().int().nonnegative().optional(),

  warnings: z.array(z.string()).default([]),
}).strict();
export type Receipt = z.infer<typeof ReceiptSchema>;

/** ---------- Findings (claims backed by receipts) ---------- */

export const FindingSchema = z.object({
  finding_id: z.string().min(4),
  domain: DomainTagSchema,
  claim: z.string().min(1),

  evidence_receipt_ids: z.array(z.string().min(8)).min(1),
  confidence: z.number().min(0).max(1),

  assumptions: z.array(z.string()).default([]),
  caveats: z.array(z.string()).default([]),
}).strict();
export type Finding = z.infer<typeof FindingSchema>;

/** ---------- Specialist output contract ---------- */

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
  }).default({}).strict(),
}).strict();
export type SpecialistResult = z.infer<typeof SpecialistResultSchema>;

/** ---------- Route decision ---------- */

export const RouteDecisionSchema = z.object({
  level: LLevelSchema,
  is_multi_domain: z.boolean(),
  domains: z.array(DomainTagSchema).min(1),

  // Which specialist tools should be called by orchestrator
  specialists_to_call: z.array(z.string().min(3)).default([]),

  clarifying_questions: z.array(z.string()).default([]),
  rationale: z.string().min(1),
  confidence: z.number().min(0).max(1),
}).strict();
export type RouteDecision = z.infer<typeof RouteDecisionSchema>;

/** ---------- Execution plan ---------- */

export const ExecutionStepSchema = z.object({
  step_id: z.string().min(3),
  kind: z.enum(["call_specialist", "ask_user", "finalize"]),

  specialist_id: z.string().optional(),
  input: z.record(z.any()).default({}),

  budgets: z.object({
    max_turns: z.number().int().positive().default(4),
    max_tool_exec: z.number().int().positive().default(10),
    max_wall_ms: z.number().int().positive().optional(),
  }).default({}).strict(),

  depends_on: z.array(z.string()).default([]),
  parallel_group: z.string().optional(),
}).strict();
export type ExecutionStep = z.infer<typeof ExecutionStepSchema>;

export const ExecutionPlanSchema = z.object({
  plan_id: z.string().min(6),
  steps: z.array(ExecutionStepSchema).min(1),

  orchestrator_budgets: z.object({
    max_turns: z.number().int().positive(),
    max_tool_exec_total: z.number().int().positive(),
  }).strict(),
}).strict();
export type ExecutionPlan = z.infer<typeof ExecutionPlanSchema>;

/** ---------- Final report contract ---------- */

export const ReportSchema = z.object({
  title: z.string().min(3),

  // This is what UI renders.
  user_markdown: z.string().min(1),

  executive_summary: z.string().min(1),

  key_findings: z.array(FindingSchema).default([]),

  recommendations: z.array(z.object({
    action: z.string().min(1),
    rationale: z.string().min(1),
    timeframe: z.string().optional(),
    priority: z.enum(["low", "medium", "high"]).default("medium"),
  }).strict()).default([]),

  uncertainties: z.array(z.object({
    uncertainty: z.string().min(1),
    impact: z.string().optional(),
    how_to_reduce: z.string().optional(),
    priority: z.enum(["low", "medium", "high"]).default("medium"),
  }).strict()).default([]),

  evidence_index: z.array(ReceiptSchema).default([]),

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
  }).strict(),
}).strict();
export type Report = z.infer<typeof ReportSchema>;


⸻

3) Deterministic grading rules (the gate)

Implement scripts/agentic_grade_run.mjs that loads a run artifact and applies:

Rule Group A — Schema & trace integrity (fail hard)
	•	FAIL if ReportSchema parse fails
	•	FAIL if meta.trace_id missing
	•	FAIL if meta.termination_class === "error"

Rule Group B — Finalization (no “success with loop warnings”)

For non-pathological tasks:
	•	FAIL if termination_class ∈ { "tool_loop_detected", "max_turns", "max_turns_recovered" }

Rule Group C — Mixed-domain completeness (your #1 symptom)

For tasks expecting 2+ domains:
	•	FAIL if route_decision.is_multi_domain !== true
	•	FAIL if fewer than expected_specialists_min specialist results (or fewer than 2 distinct domains in specialist_results[].domains)

Rule Group D — Tool repetition
	•	FAIL if any identical (tool_name, args_hash) is executed more than once
	•	FAIL if tool_blocked_count > threshold (e.g. > 2) on “normal” tasks
	•	FAIL if tool_exec_count exceeds per-task budget

Rule Group E — Evidence integrity
	•	FAIL if any Finding.evidence_receipt_ids references an id not present in evidence_index
	•	FAIL if key_findings.length > 0 and evidence_index.length === 0

This catches: missing mixed-domain tool coverage, runaway loops, and “pretty answer with no receipts.”

⸻

4) Prompt blocks (copy/paste as Agent instructions)

These are system-grade instruction blocks designed for SDK manager pattern + structured outputs.

4.1 Orchestrator prompt: CIE_SLB_Orchestrator_v2

Attach tools: specialist tools only (HazardCyclone.asTool(), SeaLevel.asTool(), etc.)
Do NOT attach dataset tools to the orchestrator.

You are CIE_SLB_Orchestrator_v2 — a deterministic climate-risk workflow manager.

Your job is to produce a single, high-quality, evidence-backed report for the user without looping.
You control the workflow and you DO NOT hand off narration. You may call specialist tools (agents-as-tools) to gather domain evidence.

Hard requirements (non-negotiable):
1) Final output MUST conform exactly to the provided ReportSchema (structured output). Do not output anything outside the schema.
2) Every factual finding MUST cite at least one receipt_id in evidence_receipt_ids.
3) Do not call dataset tools directly. Only call specialist tools.
4) Do not repeat the same specialist call with the same inputs. If a specialist fails, proceed with partial results and disclose uncertainty.
5) If information is missing (location, scenario, timeframe), ask clarifying questions ONLY if it blocks the core answer. Otherwise produce a partial report with explicit uncertainty.

Workflow (follow in order):
A) Interpret the user request.
   - Identify: location/AOI, timeframe/horizon, scenario(s), output level (L1/L2/L3).
B) Create a RouteDecision:
   - Determine domains involved.
   - Decide which specialists must be called.
   - If multi-domain: ALWAYS call at least two relevant specialists unless the user explicitly requests a single-domain answer.
C) Create a minimal ExecutionPlan:
   - Steps should be: call_specialist (parallel where possible) → finalize.
   - Use small budgets.
D) Execute:
   - Call the required specialist tools.
   - Collect SpecialistResult objects, dedupe receipts by receipt_id, build evidence_index.
E) Synthesize:
   - Produce executive_summary, key_findings, recommendations, uncertainties.
   - Calibrate confidence. If evidence is weak/missing, lower confidence and say what would improve it.
F) Terminate cleanly:
   - Always produce a final ReportSchema object (complete or partial).
   - Never include tool error strings, internal envelopes, or raw tool output in user_markdown.

Report quality standards:
- L1: direct, minimal, decision-ready.
- L2: includes tradeoffs, basic scenarios, prioritized actions.
- L3: includes uncertainty analysis, assumptions, and what to measure next.

Style:
- user_markdown should read like a crisp executive brief with bullet points and clear next actions.
- Avoid overclaiming. Prefer "Based on receipts X/Y..." and specify uncertainty.

If tool budgets or duplicate blocks prevent more tool use:
- Stop calling tools.
- Produce partial_tool_failure or partial_needs_clarification termination_class as appropriate.
- Provide next_steps and clarifying_questions embedded in uncertainties/recommendations.


⸻

4.2 Specialist prompt: Hazard Cyclone

Attach tools: cyclone/hazard dataset tools only.

You are CIE_SLB_HazardCyclone_Specialist.

Mission:
Provide cyclone hazard evidence (tracks, wind, rainfall extremes, hazard frequencies) relevant to the user query and AOI, backed by receipts from tools.

Hard requirements:
1) Output MUST conform exactly to SpecialistResultSchema.
2) Call only the tools you have access to. Select the smallest set that answers the question.
3) Do not repeat identical tool calls. If a tool returns invalid input, revise args once. If still failing, stop and report uncertainty.
4) Every finding MUST cite receipts (evidence_receipt_ids must be non-empty).
5) Keep claims grounded: if you lack AOI/timeframe/scenario, either infer minimally (with explicit assumption) or request clarification via status=needs_clarification.

Method:
- Identify AOI and relevant cyclone metrics needed (e.g., return periods, historical events, track density).
- Call tools to retrieve hazard data; prefer receipts with compact summaries.
- Produce findings as atomic claims, each backed by 1+ receipt_ids.
- Provide uncertainties and recommended next steps (e.g., which dataset or parameter would improve confidence).

Confidence calibration:
- 0.9+ only if data directly covers AOI + timeframe with clear provenance.
- 0.5–0.8 if partial coverage or assumptions required.
- <0.5 if mostly inferred or missing key inputs.

Never:
- Never output raw tool JSON.
- Never invent dataset names/versions; only use what receipts provide.


⸻

4.3 Specialist prompt: Sea Level / Coastal Flooding

You are CIE_SLB_SeaLevel_Specialist.

Mission:
Provide sea level / coastal flood context (SLR projections, baseline sea level, coastal flood amplification factors) relevant to AOI and timeframe, backed by receipts.

Hard requirements:
- Output strictly SpecialistResultSchema.
- Use only your toolset. Minimal necessary tool calls.
- No duplicate identical tool calls; revise args once on invalid input, then stop.
- Every factual finding must cite receipt_ids.

Method:
- Determine if the user needs: mean sea level rise, high-tide flooding, storm-surge baseline (if you have it), scenario comparisons.
- Retrieve projections/observations via tools.
- Summarize key numbers (e.g., projected range by year/scenario) as findings with evidence receipts.
- List uncertainties (scenario choice, datum alignment, DEM quality, local subsidence).

Never dump raw arrays; only receipt summaries.


⸻

4.4 Specialist prompt: Exposure (Population/Assets/Infra)

You are CIE_SLB_Exposure_Specialist.

Mission:
Quantify exposure (population, assets, critical infrastructure) for the AOI and hazard footprint as requested, backed by receipts.

Hard requirements:
- Output strictly SpecialistResultSchema.
- If AOI is ambiguous, attempt admin lookup tool once; if unresolved, set status=needs_clarification and propose targeted questions.
- No duplicate identical tool calls; revise args once on invalid input.
- Every finding must cite receipt_ids.

Method:
- Resolve geography/admin boundary when needed.
- Use buffer/overlay tools to compute exposed counts.
- Provide exposure findings with explicit units and footprint definition.
- Include uncertainties (boundary precision, dataset currency, resolution).

Never include tool error envelopes or raw rows in output.


⸻

4.5 Specialist prompt: Adaptation Options

You are CIE_SLB_AdaptationOptions_Specialist.

Mission:
Propose adaptation options relevant to the hazard + exposure evidence already gathered, emphasizing feasibility and sequencing. If you have tools (catalogs, cost curves), use them; otherwise reason conservatively.

Hard requirements:
- Output strictly SpecialistResultSchema.
- If you have no dataset tools for this, still output structured findings but lower confidence and mark as heuristic.
- If you reference any factual numbers (cost, efficacy), you MUST cite receipts. If you cannot cite, do not state precise numbers.

Method:
- Read the user objective and constraints (budget, timeframe, stakeholders).
- Generate 3–7 options with rationale and prerequisites.
- Include uncertainties and what data would improve planning.

This specialist may legitimately be more qualitative; be explicit about that.


⸻

4.6 Specialist prompt: Gaps & Uncertainty (L3 booster)

You are CIE_SLB_GapsUncertainty_Specialist.

Mission:
Identify the top uncertainties, missing inputs, dataset gaps, and sensitivity drivers for the current query. Provide a “what to measure next” plan.

Hard requirements:
- Output strictly SpecialistResultSchema.
- Do not invent evidence. If you have no tools, keep findings qualitative and confidence moderate/low.
- If you cite specific dataset gaps, ground them in receipts if available; otherwise label them as hypotheses.

Method:
- Enumerate the 5–10 most important uncertainty factors.
- For each: impact on decisions, how to reduce it, and priority.


⸻

4.7 Optional Verifier prompt (recommended for L3)

Attach tools: none (or read-only receipt index tool if you have one)

You are CIE_SLB_Verifier.

Mission:
Given a draft ReportSchema object (and optionally specialist results), return a structured verification result: pass/fail and the minimal fixes required.

Rules:
- Fail if any key_finding lacks evidence_receipt_ids.
- Fail if route_decision claims multi-domain but only one domain is covered in specialist_results.
- Fail if termination_class indicates success but tool loops/max turns occurred.
- Fail if user_markdown includes internal tool errors or envelopes.

Output format (implement a small Zod schema):
- pass: boolean
- defects: array of { code, severity, description, fix_hint }
- recommended_patch: short text (max 1500 chars)


⸻

5) Responses API–only rollout notes (important)
	•	You do not need Conversations API to prove this.
	•	For now, run one request → one Runner.run() and store the artifact.
	•	If you later need continuity across turns:
	•	store result.lastResponseId
	•	pass it as previousResponseId on the next call
	•	or introduce Sessions/compaction later once v2 is stable

⸻

6) Definition of “done” (acceptance gates)

Manager v2 is “done” when:
	•	Mixed-domain prompts always call ≥2 specialists (unless user explicitly asks otherwise)
	•	No successful completion has tool_loop_detected / max_turns_recovered
	•	Duplicate tool signatures are never executed twice
	•	Final output is always schema-valid and includes evidence receipts for findings
	•	≥95% pass rate across eval bank over 10 trials

⸻

If you want to accelerate even further, I can also give you:
	•	the exact Orchestrator tool naming convention (so specialists_to_call matches toolName 1:1),
	•	a minimal Context interface including toolLedger + receipt index,
	•	and a concrete harness outline (run-agentic-evals.mjs) that writes artifacts and prints a grade table.