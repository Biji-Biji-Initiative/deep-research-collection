Below is the mission brief + attack sequence I’d hand to a world‑class agent engineering team to take your CIE orchestration from “probe-and-pray” to predictable, bounded, production-reliable.

It is designed so your coding agents cannot bypass discipline, and every paid run yields durable learning.

I’m going to assume your current baseline matches what you described (Agents SDK JS, Responses API, runSlbChatTurn, tool partitions, chat_run + chat_run_event, openai_trace_id present sometimes). The plan intentionally doesn’t depend on DB refactors—you can prove everything with artifacts first, and only then harden persistence.

⸻

0) The ontology (so you stop mixing concepts)

This is critical—half of “agent systems” bugs are category errors.

Tool (Function Tool)

A callable capability exposed to the model via function calling. Each dataset connector is a tool (or a small family of tools). A tool invocation is one tool call. Tool names must match [a-zA-Z0-9_-]{1,64}.  ￼

Agent

An LLM policy + instructions + access to a toolset. It can call tools, reason, and output. In the Agents SDK, agents can also be wrapped as tools via agent.asTool().  ￼

Agent-as-tool (Pattern B)

A specialist agent becomes a tool that returns structured output to the orchestrator. Nested runs can be configured via asTool() options (input schema inclusion, resume strategy, streaming, etc.).  ￼

Function call vs tool call

Same thing in practice: the model emits a function/tool call item; your runtime executes it. The important distinction is attempted vs executed (guardrails can block). Tool guardrails formalize this.  ￼

Structured outputs

Boundaries where you must enforce schema:
	•	Specialist returns (SpecialistResultSchema)
	•	Orchestrator plan (ExecutionPlanSchema)
	•	Final report (ReportSchema)
	•	Debug artifacts (DebugSchema, ReviewSchema)

(Structured outputs are supported in OpenAI APIs via JSON Schema style response formats; function tool schema strictness exists too.)  ￼

⸻

1) North-star architecture (the one experts would ship)

Goal: eliminate handoff loops and shared-turn-budget fragility by removing “narrator handoff” as a control mechanism. Replace with a manager-orchestrator that owns the final answer.

Runtime flow (Pattern B)
	1.	Orchestrator (Manager Agent) produces a typed plan (what domains, what tools/specialists, what constraints).
	2.	Orchestrator calls specialists as tools (cyclone_specialist.asTool, sea_level_specialist.asTool, etc.).
	3.	Specialists call dataset tools (function tools) and return Receipts + Findings to orchestrator.
	4.	Orchestrator synthesizes final ReportSchema with explicit provenance (receipt IDs).
	5.	No narrator handoff required. No “Turn 3 automatic.” No re-entrant routing loop.

This leverages agent.asTool() exactly the way the SDK intends for nested sub-agents.  ￼

Tracing & trace linkage (non-negotiable)

Every top-level run must set:
	•	workflowName (human readable stable grouping)
	•	traceId (stable per run, stored)
	•	groupId (thread/session id; stable for a user conversation)

These are first-class in RunConfig.  ￼

⸻

2) Stop-the-line invariants (these are laws, not suggestions)

If any invariant fails, the system must downgrade to STOPPED state until reviewed.

Invariant A — “No second probe without review”

A probe is an experiment. You don’t get a second experiment until you have:
	•	a machine review report
	•	a human acknowledgement (two-phase commit)

Invariant B — Evidence integrity

If tools executed but 0 receipts, that is a FATAL defect:
	•	Either tools errored
	•	Or receipt pipeline dropped results
Either way: system must STOP_AND_FIX.

Invariant C — Status truth

If user-facing result is “could not compute” / guard fired / no receipts, DB status can’t be “succeeded”.
Telemetry lying breaks evals and makes you chase ghosts.

Invariant D — Tool naming correctness

All tool names must obey the API restrictions (64 chars; underscore/dash allowed).  ￼

Invariant E — Bounded loops

Tool retries and duplicates must be mechanically bounded (guardrails + ledger), not “discouraged by prompt.”  ￼

⸻

3) Attack sequence (phased plan with gates)

This is written as instructions your agents can execute in order. No phase proceeds without passing gates.

⸻

Phase 1 — Build the “Scientific Instrument” harness (process > code changes)

Objective

Make it impossible to spend money twice without extracting learning from the first run.

Deliverables

(1) ProbeLock state machine
	•	reports/probe_guard/state.json
	•	phases: READY → REVIEW_REQUIRED → ACK_REQUIRED → READY/STOPPED

(2) Review script (machine)
	•	scripts/review-last-probe.mjs
	•	reads:
	•	chat_run + chat_run_event
	•	run artifact directory
	•	outputs:
	•	reports/probe_reviews/review_<run_id>.json
	•	reports/probe_reviews/review_<run_id>.md
	•	emits verdict: PROCEED | STOP_AND_FIX | NEEDS_HUMAN_DECISION

(3) Ack script (human)
	•	scripts/ack-probe.mjs --decision ... --notes ...
	•	writes ack_<run_id>.json
	•	transitions ProbeLock state to READY or STOPPED

(4) Runner hard gate
	•	scripts/run-agentic-hard-probes.mjs refuses to run unless state is READY.

Review checks (beyond “basics”)

Your review script must classify every run into explicit failure classes:

Trace integrity
	•	missing trace_id
	•	missing workflow_name
	•	suspicious fast-fail (<5s, 0 tools) category

Control flow
	•	did orchestrator call specialist-as-tool?
	•	did specialist call dataset tools?

Tool ledger
	•	attempted vs executed
	•	blocked_duplicate vs blocked_budget vs timeouts vs errors

Receipt integrity
	•	receipts present?
	•	tool_results_count matches receipts?

Status integrity
	•	DB status consistent with evidence and verdict?

Gate to exit Phase 1
	•	Runner physically blocks “probe again” unless review+ack exist.
	•	One real probe produces a review JSON with correct verdict classification.

⸻

Phase 2 — Make tools “receipt-safe” and guardrail-bounded

Objective

Turn your 30+ tools into a reliable substrate: predictable I/O, predictable provenance, bounded repetition.

Deliverables

(1) Standard tool result envelope
Every dataset tool returns:

type ToolResult = {
  ok: boolean;
  receipt?: Receipt;
  data?: unknown;
  error?: { code: string; message: string; retryable: boolean };
  meta: { tool_name: string; args_hash: string; elapsed_ms: number };
}

(2) Receipt schema (canonical)
Receipt is your atomic provenance object:
	•	receipt_id
	•	tool_name
	•	query_fingerprint
	•	source_attribution (dataset/version)
	•	time_range
	•	units
	•	confidence
	•	payload_digest (hash, not raw blob)

(3) Tool guardrails
Use input/output tool guardrails to enforce:
	•	name/args schema validity
	•	one-call-per-signature when intended
	•	max payload size / truncation rules
	•	retry budget rules

Guardrails can allow, rejectContent, or throwException (tripwire).  ￼

(4) Tool ledger
A single shared ledger records:
	•	attempts
	•	executions
	•	blocked_duplicate
	•	blocked_budget
	•	errors
	•	timeout
	•	receipt_id mapping

This is what makes “tool loop detected” objectively diagnosable.

Gate to exit Phase 2
	•	In a controlled local test, two tools can execute and produce 2 receipts reliably.
	•	If a tool errors, it produces a structured error; review script classifies correctly.

⸻

Phase 3 — Implement Pattern B runtime (Manager + Specialists as tools)

Objective

Remove handoff-based synthesis fragility and shared turn budget coupling.

Deliverables

(1) Orchestrator agent
	•	Owns final output: ReportSchema
	•	Calls specialists as tools (asTool())
	•	Maintains plan → execute → synthesize discipline

(2) Specialist agents
	•	Each specialist returns SpecialistResultSchema
	•	Includes:
	•	findings list
	•	receipts list
	•	gaps list (“missing data because…”)
	•	recommended follow-up tool calls (optional)

(3) Orchestrator constraints
	•	budgets:
	•	max specialist calls
	•	max dataset tool calls
	•	max retries per args_hash
	•	never calls narrator/handoff
	•	never emits final answer without receipts unless explicitly allowed (policy switch)

(4) Nested run configuration
When wrapping specialists with asTool(), enable:
	•	includeInputSchema for stronger schema adherence
	•	optional nested runConfig override for maxTurns/temperature
	•	optional resumeState strategy if you want continuity in nested runs  ￼

(5) Trace grouping
Use RunConfig.traceId, groupId, workflowName, and attach trace metadata (tier, case id).  ￼

Gate to exit Phase 3

Mixed-domain prompt MUST:
	•	call ≥2 specialists (or a mixed specialist-as-tool) deterministically
	•	call ≥1 dataset tool per required domain
	•	produce a final report with receipts
	•	have bounded tool behavior and no re-entrant routing/handoff loops

⸻

Phase 4 — Evals & regression gates (the compounding advantage)

Objective

Turn failures into test cases and stop regressions before they ship.

This is directly aligned with Anthropic’s “eval-driven development” approach: write unambiguous tasks, reference solutions, balanced sets, and read transcripts.  ￼

Deliverables

(1) agentic_task_bank.json
	•	8 canonical probes minimum:
	•	2 L1
	•	2 L2
	•	2 L3
	•	2 pathological (timeouts, malformed args, partial data)
	•	Each task defines:
	•	user prompt
	•	expected domains
	•	required tool families
	•	required receipts count (min)
	•	disallowed behaviors (duplicate tool spam, “no receipts but success”)

(2) Deterministic graders
	•	Rule-based graders (zero false positives for structural bugs):
	•	NO_RECEIPTS_WHEN_TOOLS_EXECUTED (fatal)
	•	STATUS_MISMATCH (fatal)
	•	MISSING_TRACE_ID (fatal)
	•	MISSING_WORKFLOW_NAME (fatal)
	•	DOMAIN_COVERAGE_INCOMPLETE (fatal for mixed)
	•	TOOL_DUPLICATE_EXECUTED (warn/fatal depending)
	•	LLM judge graders (quality):
	•	clarity
	•	correctness w.r.t receipts
	•	gap explanation quality
	•	citation hygiene

(3) pass^k metric for reliability
For production reliability you want pass^k, not pass@k, because consistency matters (Anthropic explicitly discusses this tradeoff).  ￼

Gate to exit Phase 4
	•	You can run 3 trials per canonical task and hit a target pass^3 threshold for critical workflows.
	•	Failures produce actionable defect labels, not “vibes.”

⸻

Phase 5 — Long-running agent development harness (how your coding agents work)

This is about how your agents write code over days without thrashing—the exact “initializer + incremental coder + artifacts” approach Anthropic describes.  ￼

Deliverables

(1) Initializer routine (one-time)
	•	create:
	•	docs/agentic/feature_list.json (end-to-end feature checks)
	•	docs/agentic/progress.log
	•	docs/agentic/known_failures.md
	•	init.sh for running minimal local e2e checks

(2) Coding agent routine (every session)
	1.	Read progress log + feature list
	2.	Select ONE feature/bug ticket
	3.	Implement smallest diff
	4.	Run tests
	5.	Update progress log
	6.	Commit with descriptive message

This prevents “one-shotting” and “declaring victory too early,” two classic long-horizon failures.  ￼

⸻

4) Team topology (the right number of agents)

You asked “how many agents should we have?” Here’s the expert answer:

Runtime agents (user-facing)
	•	Orchestrator (1)
	•	Specialists (N domains) — but each is an asTool() agent tool
	•	No narrator agent in the control plane (optional: keep a “writer” agent as a tool if you want style separation)

Engineering agents (dev-facing)
	•	Probe Operator (runs probes; cannot bypass ProbeLock)
	•	Trace Reviewer (runs review script; produces root-cause labels)
	•	Tool Contract Engineer (makes tools receipt-safe + guardrailed)
	•	Runtime Architect (Pattern B migration)
	•	Evals Engineer (task bank + graders + CI gate)

Important contrarian constraint: you do not want “tons of agents.” You want few agents + strong skills/contracts. Complexity belongs in tools, schemas, and harnesses—not in proliferating “god agents.”

⸻

5) Exact instructions to give your agents (copy/paste)

Instruction packet for Probe Operator
	1.	You may run exactly one probe when ProbeLock is READY.
	2.	After probe completes, you must run review-last-probe.mjs.
	3.	You must wait for human ack (ack-probe.mjs) before any further probe.
	4.	If verdict is STOP_AND_FIX, you stop immediately and file a defect with:
	•	run_id, trace_id
	•	defect labels
	•	top 3 suspected root causes
	•	pointers to events (seq ranges)

Instruction packet for Trace Reviewer
	1.	Use DB + artifacts only (no new probes).
	2.	Produce:
	•	review JSON + markdown
	•	defect labels chosen from a fixed taxonomy
	3.	Your output must answer:
	•	did tools execute?
	•	did receipts exist?
	•	did status match evidence?
	•	what is the minimal fix surface?

Instruction packet for Tool Contract Engineer
	1.	No tool ships without:
	•	input schema
	•	output schema
	•	receipt emission rules
	•	guardrails (duplicate + payload + retry)
	2.	Every tool error must be structured and classified retryable/non-retryable.
	3.	Tool ledger must reflect attempted vs executed.

Instruction packet for Runtime Architect
	1.	Implement Pattern B:
	•	orchestrator calls specialists as tools via asTool().  ￼
	2.	Remove narrator/handoff from core completion path.
	3.	Ensure RunConfig is set for trace linkage (workflowName, traceId, groupId).  ￼

Instruction packet for Evals Engineer
	1.	Build task bank from real failures (every defect becomes a task).
	2.	Maintain rule-based graders for structural issues.
	3.	Track pass^k for reliability and read transcripts regularly.  ￼

⸻

6) The single highest leverage next step (do this first)

Implement ProbeLock + Review + Ack (Phase 1).
Not because it fixes the underlying bug, but because it guarantees that every subsequent dollar spent produces permanent learning—and forces correctness discipline into the workflow.

Once that exists, the “trace_fb845…” class of failures becomes a crisp label (e.g., TOOLS_EXECUTED_BUT_ZERO_RECEIPTS + STATUS_MISMATCH) instead of an emotional debate.

⸻

If you want, I’ll now define the exact schema set you requested (Zod/JSON Schema):
	•	RouteDecisionSchema
	•	ExecutionPlanSchema
	•	SpecialistResultSchema
	•	ReceiptSchema
	•	ReportSchema
	•	ProbeReviewSchema (for the review gate)

…and the grading rules that catch your current failure modes with near-zero false positives.