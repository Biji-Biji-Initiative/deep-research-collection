You’re not crazy — what you’re fighting is an architecture that’s structurally incentivized to loop. The fastest path to “predictable, bounded, production‑reliable” in 2026 is to stop treating multi-agent orchestration as a conversational relay race (handoffs) and instead treat it like a control plane (orchestrator/manager) driving a data plane (specialists + dataset tools).

Below is a world‑class implementation plan that a strong OpenAI/Anthropic-style agent team would execute. It’s aligned to the current OpenAI Agents SDK mechanics: manager pattern (agents-as-tools), withTrace, structured outputs, tool schemas, guardrails, and run-level budgets.  ￼

⸻

1) Correct mental model (stop mixing primitives)

If you internalize only one thing:

Handoffs are for “who should talk next.”
Agent-as-tool is for “do work, return results.”

What is what (Agents SDK-aligned)
	•	Tool / function tool: a callable capability exposed to the model (via JSON schema). In JS/TS SDK you typically build these with tool() and Zod schemas. Best practice: one responsibility per tool + strict validation.  ￼
	•	Tool call: an item produced by the model that triggers tool execution; the runner loop executes tool calls then re-runs the model.  ￼
	•	Agent: model + instructions + toolset + optional output schema (structured output).  ￼
	•	Handoff: a tool (transfer_to_<agent_name>) that switches the active agent inside the same agent loop and shares the same maxTurns budget and accumulated history.  ￼
	•	Agent as Tool (agent.asTool()): exposes an entire agent as a callable tool, so the calling agent stays in control (no handoff). SDK wraps it as a function tool and runs the sub-agent when called; you can pass runConfig/runOptions.  ￼
	•	Structured outputs: define outputType (Zod/JSON schema) so you get parsed/validated finalOutput reliably.  ￼
	•	Tracing: each run() is traced; if you do multiple runs and want one trace, wrap in withTrace().  ￼

Why your current architecture loops

Because handoffs + shared turn counters + “narrator recovery runs” + tool noise is an unstable combo:
	•	The runner loop is literally: model → inspect → (handoff/tool) → model again → … until maxTurns, then MaxTurnsExceededError.  ￼
	•	Handoff “works” only if the model actually calls the transfer tool; writing “handoff language” in text does nothing.  ￼

So you want to remove handoff as the primary orchestration mechanism. Keep handoff only for rare UI-driven escalations (“human review”, “switch to chat mode”, “handoff to support agent”), not for internal workflow phases.

⸻

2) Target architecture (the world-class version)

North Star: “CIE Agentic Control Plane” (Manager + Specialist Tools + Dataset Tools)

Think Kubernetes:
	•	Orchestrator = control plane (decides what to do, enforces budgets, owns final output)
	•	Specialists = internal services (called as tools, return structured results)
	•	Dataset tools = data plane (strict schemas, small outputs, receipts)

Sequence diagram (stable, bounded)

User Query
   |
   v
[Orchestrator Agent]  (single owner of the conversation + final answer)
   |--(1) classify intent + domains + L-level (structured output)
   |--(2) build plan (structured output: which specialists, which datasets, what horizons)
   |--(3) execute plan:
   |      - call specialist tools (agent.asTool) with bounded budgets
   |      - specialists call dataset tools (strict, receipt-based)
   |--(4) synthesize final report (Orchestrator produces finalOutput schema)
   |
   v
Final response + evidence map + run_id + trace_id

Key properties (why this works)
	•	No re-entrant router loops: orchestrator never “hands off back” to router.
	•	Budgets are explicit: orchestrator has its own maxTurns; each specialist tool run can have its own maxTurns because it’s a nested run/tool.  ￼
	•	Tool repetition is enforceable via a shared ledger + tool guardrails (see below).
	•	Trace readability: wrap the entire request in withTrace() and set workflowName/traceId/groupId deterministically.  ￼
	•	Outputs are deterministic: you define schemas for specialist outputs + final report outputType.  ￼

⸻

3) Tooling design best practices for 30+ tools (don’t drown the model)

You’re right that “each dataset is a tool” is often correct — but only if you also do tool surface area management.

Tool taxonomy (recommended)
	1.	Dataset tools (read-only)
	•	Each tool should map to one dataset or one coherent API (cyclone tracks, sea level projections, exposure grid, admin boundaries, etc.)
	•	MUST return: small response + receipt_id (pointer to stored raw)
	2.	Compute tools (pure functions)
	•	Buffering, interpolation, unit conversion, scenario alignment
	3.	Workflow tools
	•	“build_evidence_bundle”, “write_report_pdf”, “store_run_artifact”
	4.	Meta tools
	•	“tool_catalog.search” (optional) to reduce selection load when tool count grows

Golden rule: Don’t give 30+ tools to one agent. Give:
	•	Orchestrator: specialist tools + a few meta/workflow tools
	•	Each specialist: only the dataset tools it truly needs

This matches the SDK’s “agents as tools” approach for collaboration without handing off.  ￼

Tool contract: “Receipt-first outputs”

If tool output is big, your system will eventually fail from context overflow. The fix is structural:

Tool output should be small and reference the full artifact stored server-side.

Example return shape (pattern, not exact):

{
  "ok": true,
  "receipt_id": "rcpt_...",
  "summary": { "key_numbers": [...], "geo": "...", "time_horizon": "..." },
  "provenance": { "dataset": "...", "version": "...", "queried_at": "..." },
  "warnings": ["..."],
  "raw_stored_at": "s3://.../run_id/.../tool_call_id.json"
}

This single move eliminates a huge fraction of tool loops + narrator overflow issues.

Tool input validation (must be strict)

Use strict Zod schemas where possible. This is literally called out as best practice.  ￼
Also add timeouts to bound worst-case behavior.  ￼

⸻

4) Loop prevention the “real” way (not prompt nagging)

Looping is rarely “the model is dumb.” It’s almost always:
	•	ambiguous tool affordances,
	•	invalid schema inputs,
	•	non-idempotent tools,
	•	noisy tool errors,
	•	or missing deterministic stopping rules.

The 4-layer anti-loop stack

Layer A — Runtime budget boundaries (SDK-native)
	•	Use maxTurns at orchestrator level (safety limit).  ￼
	•	Use nested budgets for specialist tool runs via agent.asTool({ runOptions/runConfig... }).  ￼
	•	Add errorHandlers for maxTurns to force a controlled finalization path (no “crash and retry”).  ￼

Layer B — Tool-call ledger (hard stop on duplicates)
Implement a shared ledger in context:
	•	Key = stable hash of (tool_name, canonical_json(args))
	•	Policy:
	•	same signature: block and return a clear “duplicate call blocked” message
	•	allow second call only if args materially changed

This turns “tool loops” into one blocked attempt + forced progress.

Layer C — Tool guardrails (reject before executing)
Use tool input guardrails to:
	•	normalize inputs (admin name → id, units normalization),
	•	reject impossible ranges,
	•	reject duplicates (ledger check),
	•	enforce tool-specific budgets.

Guardrail results are surfaced in run results and can be logged/persisted.  ￼

Layer D — Control tool use behavior (stop pathological patterns)
The SDK supports tool use behavior controls and describes how resetting toolChoice prevents infinite loops, plus custom stopping behavior.  ￼
In practice for your system:
	•	Don’t globally force tools on every step.
	•	Instead:
	•	In specialists, “tool-first then summarize” with explicit budgets
	•	Custom stop condition: if tool calls exceed N or duplicate-block events exceed M → stop and return partial with “needs clarification”.

⸻

5) Structured outputs: where you must use them

Use structured outputs for:
	1.	Router/classifier output (domains, L-level, output format, required datasets)
	2.	Specialist outputs (domain findings + receipts + uncertainties)
	3.	Final report object (so UI + storage are deterministic)

Agents SDK will parse Zod outputType automatically and return typed finalOutput.  ￼

Recommended final output schema (pragmatic + evaluable)

Your Orchestrator should output something like:
	•	answer_summary
	•	assumptions
	•	data_used[] (tool receipts)
	•	findings[] (each with domain tag + confidence)
	•	uncertainties[]
	•	recommendations[]
	•	next_actions[]
	•	run_links: { run_id, trace_id }

This becomes your “report contract” and makes regressions measurable.

⸻

6) Tracing + evidence: make it impossible to lose causality

You want “traceability persistence” to be solved structurally, not as best-effort logging.

SOTA trace correlation approach

Instead of “extract openai_trace_id after the fact”, set it.

RunConfig supports specifying traceId and groupId, plus workflowName.  ￼
And trace IDs must follow trace_<32_alphanumeric>.  ￼

So:
	•	Generate traceId deterministically from your internal run_id
	•	Set groupId = conversation/thread id (or workspace session id)
	•	Set workflowName = "CIE Agentic: L1" / "L2" / "L3"

Now your DB never needs to “guess” which OpenAI trace belongs to which run.

Single-trace, multi-step flows

If you still do multiple run() calls inside one API request (e.g., “draft then verify then rewrite”), wrap the whole thing in withTrace() so it’s one trace.  ￼

Persist run evidence using SDK-native artifacts

The Results guide exposes:
	•	newItems (including tool calls, tool outputs, handoff call items if any)
	•	serializable state
	•	aggregated usage metrics state.usage  ￼

This is exactly what your run store should persist as the canonical evidence bundle.

⸻

7) Implementation plan (attackable by a coding agent)

This is the “do this in order” plan, with explicit success criteria at each step.

Phase 0 — Lock a reproducible baseline

Goal: you can reproduce failures deterministically before touching behavior.

Actions
	•	Add 3 deterministic probe prompts (one each L1/L2/L3) with stable seeds/settings.
	•	Ensure your probe runner stores:
	•	run_id
	•	trace_id (or at minimum exported trace)
	•	tool ledger stats (total calls, blocked duplicates, timeouts)
	•	termination class

Success looks like
	•	“cyclone + sea level” prompt reproduces the loop/handoff issue in ≥1 scripted run.
	•	Your evidence artifact contains newItems and state so you can audit tool calls.  ￼

⸻

Phase 1 — Immediate stabilization without redesign (optional but often worth it)

Goal: stop the bleeding while you migrate.

Actions
	•	Stop “narrator in separate run/session” behavior.
	•	If you must run multiple agents, at least wrap them under withTrace() so traces are grouped.  ￼
	•	If you keep handoffs temporarily:
	•	enforce that transfer happens via tool call (and remove any prompt text implying “automatic handoff”). Handoffs are tools.  ￼
	•	add narrator handoff inputFilter: removeAllTools to prevent tool-noise poisoning.  ￼
	•	Implement receipt-first tool outputs (cap tool output size).
	•	Add tool timeoutMs + error_as_result for graceful continuation.  ￼

Success looks like
	•	Narrator output is consistently produced in the same end-to-end trace view.
	•	Context overflow errors disappear because tool results are compact.

⸻

Phase 2 — Canonical architecture migration (the real fix)

Goal: Replace handoff-based orchestration with manager pattern + agents-as-tools.

Agents guide explicitly documents the “manager pattern (agents as tools)” and calls out it’s used in production apps.  ￼

Actions
	1.	Create Orchestrator Agent (the only “talking” agent)
	•	Has:
	•	specialist tools (agent.asTool())
	•	minimal workflow/meta tools
	•	Has outputType = ReportSchema (Zod)
	2.	Convert each specialist into an Agent Tool
	•	specialist.asTool({ toolName, toolDescription, runOptions: { maxTurns: specialistTurns }, ... })  ￼
	•	Specialists return structured domain objects (Zod outputType)
	3.	Remove router handoffs
	•	Routing becomes a structured classification step produced by orchestrator (or a tiny “Classifier agent tool” called by orchestrator).
	4.	Centralize budgets + loop control
	•	tool-call ledger in context
	•	per-specialist tool call caps
	•	“duplicate call blocked” guardrail behavior
	5.	Orchestrator synthesis
	•	orchestrator produces final report output (not a separate narrator run)

Success looks like
	•	Mixed-domain prompts trigger multiple specialist tool calls (not misrouted to a single domain).
	•	No more “handoff loop” class of failures because you’re not handing off for core orchestration.
	•	Termination is deterministic: orchestrator always returns a final structured report (or a controlled partial + questions).

⸻

Phase 3 — Production hardening (non-negotiables for reliability)

Actions
	•	Add callModelInputFilter to aggressively filter tool noise from the model input when necessary.  ￼
	•	Add run-level workflowName, deterministic traceId, and groupId.  ￼
	•	Add evaluation harness + regression gates (below).

⸻

8) Validation scaffolding (what “success” looks like at each layer)

This is how you teach your agents (and your CI) what “good” is.

Layer 1 — Tool contract tests (per tool)

For each of your 30+ tools:
	•	schema validation test (Zod)
	•	timeout test
	•	“returns receipt-first output” test (size cap)
	•	error mode test (returns structured error, not thrown exception)

Layer 2 — Specialist tests (per agent-tool)
	•	Given a deterministic prompt + mocked tool responses:
	•	specialist returns valid structured output
	•	tool calls ≤ budget
	•	no duplicate tool signatures
	•	produces receipts[]

Layer 3 — Orchestrator tests (end-to-end, mocked tools)

You asked for 8+ tests; here’s the set I’d enforce:
	•	L1 (2 tests)
	1.	single-domain cyclone quick answer
	2.	single-domain sea-level quick answer
	•	L2 (2 tests)
3) cyclone + sea level mixed-domain synthesis
4) rainfall + school infrastructure adaptation
	•	L3 (2 tests)
5) mixed-domain + gap/uncertainty section required
6) multi-scenario comparison with explicit assumptions
	•	Pathological (2 tests)
7) tool returns invalid input error once → no retries, controlled partial
8) tool timeout → fallback data path or “needs clarification” with evidence

Assertions (system-level)
	•	finalOutput exists and matches schema  ￼
	•	newItems includes tool call outputs and no handoff call items in normal path  ￼
	•	trace_id persisted and linked to run_id (ideally deterministic)
	•	tool_loop_detected classification absent for success paths (or downgraded to “blocked duplicate attempt” but not failure)
	•	tool call signature duplicates == 0 (or ≤ 1 if you intentionally allow a second call with changed args)

⸻

9) “Attack sequence” for your coding agents (who does what, in what order)

If I had multiple strong coding agents, I’d run them like an incident response team with parallel lanes:

Lane A — Control Plane migration (highest leverage)

Owner: “Orchestrator Architect” agent
	•	Build orchestrator agent + schemas
	•	Convert 1–2 specialists to asTool first (cyclone + sea level)
	•	Prove mixed-domain reliability early

Lane B — Tool contract + receipts + loop guard

Owner: “Tool Systems Engineer” agent
	•	Implement receipt-first output wrapper
	•	Add tool timeouts + strict schemas  ￼
	•	Add ledger-based duplicate blocking + tool input guardrails

Lane C — Trace + evidence store (causality guarantee)

Owner: “Observability Engineer” agent
	•	Deterministic traceId/groupId + workflowName  ￼
	•	Persist newItems, state, usage  ￼
	•	Update runbooks with “how to debug one run end-to-end”

Lane D — Regression harness + gates

Owner: “Eval/QA Engineer” agent
	•	Build 8-test suite above
	•	Add scripted probe runner gating (95% pass requirement)
	•	Add trace grading report artifact

The non-negotiable ordering rule

No lane merges a behavioral change until:
	1.	Baseline failure reproduced and stored (Phase 0)
	2.	New test asserts the failure
	3.	Patch makes test pass
	4.	Trace evidence shows the intended control flow

That’s how you stop rabbit holes.

⸻

10) A concrete SDK-aligned scaffold (so your coding agent can start clean)

This is intentionally “skeleton-level” — it tells your agent exactly what to build, without locking you into your current file layout.

Orchestrator pattern checklist
	•	ReportSchema (Zod) for final output  ￼
	•	RouteDecisionSchema (domains, L-level, required specialists)
	•	Each specialist has outputType (Zod)
	•	Each specialist is exposed via specialist.asTool({ toolName, ... })  ￼
	•	Orchestrator has only specialist tools + minimal workflow tools
	•	Entire request wrapped in withTrace("CIE Agentic", ...)  ￼
	•	RunConfig sets workflowName, traceId, groupId  ￼
	•	Tool outputs are receipt-first (small)
	•	Ledger prevents duplicates
	•	ErrorHandlers convert maxTurns into controlled output  ￼

⸻

One contrarian insight (worth adopting)

Most teams try to “fix looping” by making the model more careful.

Top teams do the opposite:
	•	assume the model will sometimes be careless,
	•	then design a runtime that makes carelessness cheap and bounded.

That means:
	•	strict schemas,
	•	receipts,
	•	ledgers,
	•	budgets,
	•	deterministic orchestration.

Prompts become the last line of defense, not the first.

⸻

Next actions (agent-assignment ready)
	1.	Declare the North Star: “Manager pattern only for core workflows; handoffs only for user-visible control transfers.”  ￼
	2.	Implement Phase 0: deterministic probe prompts + evidence bundle persistence (newItems, state, usage).  ￼
	3.	Pick two mixed-domain specialists first (cyclone + sea level) and migrate them to asTool() to prove the architecture.  ￼
	4.	Receipt-first tool wrapper across all dataset tools (size caps + raw stored).
	5.	Add the 8-test harness and block merges until it’s green.

If you want, I can also write the exact “coding-agent prompt” you should feed your implementation agent so it executes this plan as a disciplined systems engineer (including a step-by-step command pack and a verification checklist for each diff).