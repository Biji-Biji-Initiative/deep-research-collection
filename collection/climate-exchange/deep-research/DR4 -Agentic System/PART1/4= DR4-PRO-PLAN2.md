Alright — let’s go from “mostly works sometimes” to a systems-engineered, eval-driven, traceable, bounded, production-grade agent platform that squeezes the Agents SDK for everything it’s worth.

I’m going to give you:
	1.	A reference architecture (control-plane / data-plane) aligned with the Agents SDK’s strongest patterns
	2.	A “correct” agent/tool taxonomy so you never confuse tools vs agents vs function calls again
	3.	Hard invariants + contracts that make looping mechanically difficult
	4.	A build plan + attack sequence your coding agents can execute, with validation scaffolding at every layer
	5.	2026 SOTA practices (Anthropic harness/evals thinking + OpenAI SDK primitives)

⸻

1) The non-negotiable architectural choice (SOTA in 2026)

Use “Manager (agents-as-tools)” as the default orchestration

OpenAI’s own Agents SDK guide calls out two production patterns: Manager (agents as tools) and Handoffs — and explicitly notes managers are where you enforce guardrails/rate limits while retaining conversation control.  ￼

For your use case (mixed-domain + 30+ tools + report synthesis), the winning structure is:

Control plane (Orchestrator) owns:
	•	routing/classification
	•	planning
	•	budget enforcement
	•	evidence policy (“receipts-only; no raw dumps”)
	•	final report synthesis
	•	final termination semantics

Data plane (Specialists + dataset tools) owns:
	•	tool calling
	•	domain computations
	•	returning structured results with receipts

This is basically “orchestrator-workers” (Anthropic) but implemented using the SDK’s manager pattern.  ￼

⸻

2) Canonical object model (stop mixing primitives)

Definitions you should standardize internally

These map cleanly to SDK concepts:

Tool (function tool)
	•	A callable capability exposed via JSON schema (Zod strongly recommended).
	•	This is what the model calls.
	•	Must be idempotent, strictly validated, bounded output.
Tools are one of several SDK tool categories (hosted, local built-in, function tools, agents-as-tools, MCP servers, etc.).  ￼

Tool call
	•	One invocation of a tool with args.
	•	Recorded in newItems, trace spans, and your run evidence.

Agent
	•	Model + instructions + (limited) toolset + optional outputType for structured outputs.  ￼

Handoff
	•	A tool that transfers control to another agent inside the same loop, sharing the same run’s turn budget and history.  ￼

Agent as Tool (agent.asTool())
	•	Exposes a sub-agent as a tool, letting the manager stay in control.
	•	You can pass runConfig/runOptions into asTool() to control nested budgets/behavior.  ￼
	•	Advanced options matter: inputBuilder, includeInputSchema, resumeState, streaming nested events, needsApproval, isEnabled.  ￼

Your system should treat:
	•	dataset access = function tools (or MCP tools)
	•	domain reasoning = specialist agents-as-tools
	•	report synthesis = orchestrator agent (structured output)
	•	handoffs = only for user-facing escalations / role switching (rare)

⸻

3) The agent roster you actually want (balanced, scalable, non-garbled)

You said you can make as many agents as needed. True — but world-class systems do not proliferate agents randomly. They form a clean hierarchy:

Tier 0: One Orchestrator to rule them all

CIE_Orchestrator (Manager)
Tools:
	•	specialist tools only (HazardSpecialist.asTool(), etc.)
	•	a small number of workflow/meta tools (store artifact, render report)
	•	optionally a “tool catalog lookup” tool (but usually keep this deterministic)

Output:
	•	ReportSchema (Zod structured output)

Why: the SDK manager pattern is explicitly designed for this.  ￼

Tier 1: Specialists (agents-as-tools)

Keep each specialist narrow, with a tight toolset and a structured output schema.

Recommended minimum set for climate mixed-domain reliability:
	1.	Hazard Specialist
	•	Cyclone tracks, wind fields, rainfall extremes, etc.
	2.	SeaLevel/Coastal Specialist
	•	Tide gauges, SLR projections, storm surge baselines, coastal DEM logic
	3.	Exposure Specialist
	•	Population within buffers, assets, critical infra, admin boundary lookup
	4.	Adaptation/Options Specialist (optional for L2/L3)
	•	Known interventions, cost ranges, feasibility constraints
	5.	Gap & Uncertainty Specialist (optional for L3)
	•	“what we don’t know,” missing datasets, sensitivity requirements

Each returns structured output with:
	•	findings
	•	key numbers
	•	uncertainties
	•	receipt references (not raw data)

Tier 2: Verifier (evaluator) agent-as-tool

This is your “evaluator-optimizer” loop — but bounded to 1 iteration.

CIE_Verifier
	•	no tools (or maybe read-only “receipt index” tool)
	•	output: VerificationResultSchema (pass/fail + actionable defects)

This follows Anthropic’s evaluator-optimizer workflow pattern, but you keep it bounded.  ￼

Tier 3: Rendering / publication is code, not LLM

Report PDFs, citations formatting, storing artifacts: do in code.
Let the model output structured report JSON → renderer turns it into markdown/PDF.

⸻

4) The contracts that eliminate 80% of looping

Looping isn’t “prompt weakness.” It’s a missing contract.

Contract A: Receipt-first tool outputs (mandatory)

All dataset tools must return small, bounded outputs plus receipt_id pointing to stored raw artifact.

This prevents context blowups and removes the incentive for the model to repeatedly query because it “lost” the data.

Contract B: Tool-call ledger (duplicate blocking)

Implement in context a ledger keyed by:
hash(tool_name + canonical_json(args))

Policy:
	•	same signature seen → tool guardrail rejects with “duplicate blocked” + hint to revise args or proceed

This is the cleanest “mechanical” loop breaker.

Why context: Agents SDK context is DI and is forwarded to every tool/guardrail/handoff.  ￼

Contract C: Strict schemas + tool guardrails

Use tool guardrails to:
	•	validate inputs
	•	normalize / coerce obvious mistakes (units, region IDs)
	•	block duplicates (ledger)
	•	enforce tool-specific call limits

Tool guardrails are first-class in the SDK.  ￼

Contract D: Deterministic termination

Use a combination of:
	•	maxTurns safety limit  ￼
	•	errorHandlers.maxTurns to convert max-turn exhaustion into a controlled final output (instead of crashing)  ￼
	•	optionally toolUseBehavior to stop execution when a specific “finalize” tool is called (for function tools)  ￼

⸻

5) How to use Sessions properly (this is where many systems quietly fail)

If you want production reliability, you need real session persistence.

Agents SDK Sessions:
	•	automatically fetch prior items before each run
	•	persist new items after run completes
	•	support resumable HITL flows with RunState
	•	support deterministic merging via sessionInputCallback (trim/dedupe/noise control)  ￼

The SDK provides:
	•	OpenAIConversationsSession for Conversations API
	•	MemorySession for demos/tests (not recommended for production)  ￼
	•	OpenAIResponsesCompactionSession wrapper to shrink history via responses.compact  ￼

World-class pattern for you
	•	Implement a DB-backed Session (your run store is already close)
	•	Use sessionInputCallback to:
	•	keep last N “human messages”
	•	keep last N “specialist outputs”
	•	drop tool spam / duplicate tool outputs
	•	inject a compact “Receipt Index” summary

This gives you stable memory, bounded model-visible context, and fewer tool re-tries.

⸻

6) Tracing and evidence: make causality unbreakable

The SDK supports:
	•	workflowName, traceId, groupId, traceMetadata in RunConfig  ￼
	•	withTrace() to group work under one trace name  ￼
	•	trace spans for agent runs, tool calls, handoffs, guardrails by default  ￼
	•	custom trace processors for exporting traces elsewhere  ￼

World-class move: deterministic trace IDs

Generate traceId from your internal run_id, store both, and pass traceId explicitly.
No more “sometimes missing openai_trace_id.”

Store the right artifacts

From RunResult, persist:
	•	finalOutput (structured)
	•	state (serializable)  ￼
	•	newItems (your ground-truth event log)
	•	rawResponses (optional; huge)
	•	lastResponseId
	•	usage via result.state.usage  ￼
	•	guardrail results (inputGuardrailResults, outputGuardrailResults, tool guardrail results)  ￼

This becomes your canonical run evidence bundle.

⸻

7) Streaming is not a UI nicety — it’s a control mechanism

Streaming gives you:
	•	incremental model output
	•	real-time tool call events
	•	handling HITL interruptions
	•	ability to resume with RunState

SDK streaming yields event objects and supports toTextStream() for convenience.  ￼

For production: stream events into your run evidence store as they arrive.
That makes post-mortems trivial.

⸻

8) The execution pipeline I would build for CIE (highly bounded, highly capable)

This is the “best of both worlds”: workflow predictability + agent flexibility.

Step 1: Classify (structured)

Orchestrator produces RouteDecision:
	•	L-level (L1/L2/L3)
	•	domains involved (hazard, sea-level, exposure, adaptation, gaps)
	•	must-call specialists list
	•	tool risk flags (e.g., high-cost tools, approvals)

Step 2: Plan (structured)

Orchestrator produces ExecutionPlan:
	•	specialist calls (with budgets)
	•	required receipts
	•	stop conditions
	•	what uncertainties must be reported

Step 3: Execute (code-driven)

Your code executes the plan:
	•	call each specialist tool (agent.asTool) with:
	•	maxTurns bounded
	•	includeInputSchema: true to reduce schema mistakes  ￼
	•	optional parallelization (Promise.all) for independent domains (hazard + sea level)

Step 4: Synthesize (structured)

Orchestrator composes:
	•	conclusions
	•	scenario comparisons
	•	a receipt-backed evidence map

Step 5: Verify (bounded evaluator-optimizer)

Call CIE_Verifier.asTool() once:
	•	if pass → finalize
	•	if fail → orchestrator repairs once then finalize
(no infinite revision loops)

This is eval-driven development “inside” the runtime, but bounded.

⸻

9) Eval & harness strategy (2026 SOTA, non-brittle)

Anthropic’s eval guidance is extremely aligned with what you need:
	•	define tasks, run multiple trials, store transcripts/trajectories, grade outputs with deterministic graders where possible, avoid overly rigid path checking, include partial credit, balance positive/negative cases.  ￼

Your eval bank should be “feature_list.json” for the agent

Anthropic’s long-running harness article shows why structured JSON checklists beat markdown as state artifacts (models are less likely to corrupt JSON), and why incremental “feature list” style tracking prevents “declare victory” failures.  ￼

So: create agentic_task_bank.json with entries like:
	•	prompt
	•	expected domains
	•	required specialist calls
	•	required tool families (by tag)
	•	max tool calls
	•	must-have output fields
	•	forbidden termination classes (e.g., tool_loop_detected)
	•	grading rules

Graders (what you should measure)

Deterministic graders:
	•	schema valid
	•	receipts present for every claim cluster
	•	no duplicate tool call signatures
	•	tool calls <= budgets
	•	mixed-domain prompts call >=2 domain specialists
	•	termination class is “complete” or “partial_needs_info” but not “loop”

LLM graders (optional):
	•	clarity, decision usefulness, uncertainty quality
	•	hallucination suspicion (but still verify via receipts)

And run multiple trials per task; agents are stochastic.  ￼

⸻

10) Attack sequence for your coding agents (the “do this in order” plan)

This is how you scaffold validations as you build, so you never chase ghosts.

Phase A — Build the measurement spine first

A1. Add deterministic traceId/groupId/workflowName wiring  ￼
A2. Persist RunResult evidence bundle (state/newItems/usage/etc.)  ￼
A3. Create 8 canonical probe tasks (2 L1, 2 L2, 2 L3, 2 pathological) with multi-trial runs

Success = you can diff runs before/after changes using only artifacts.

Phase B — Tool reliability foundation (kills most loops)

B1. Receipt-first wrapper for every dataset tool
B2. Tool input guardrails (schema + normalization + dedupe ledger)  ￼
B3. Tool timeouts + structured error objects (never throw raw errors back to model)

Success = no tool produces multi-kilobyte blobs into the model context; retries become rare.

Phase C — Swap architecture to manager pattern (the real unlock)

C1. Build Orchestrator agent with structured ReportSchema  ￼
C2. Convert 2 key specialists to asTool() (Hazard + SeaLevel)  ￼
C3. Route + plan + execute pipeline (plan is structured, execution is code-driven)

Success = mixed-domain queries never “accidentally” land in a single domain toolset.

Phase D — Add verifier loop (bounded)

D1. Verifier agent tool that produces structured defects
D2. Single repair attempt max (hard limit)

Success = reports are consistently structured + receipt-backed.

Phase E — Sessions + compaction (production hardening)

E1. Replace ad-hoc memory with a real Session backend  ￼
E2. sessionInputCallback to keep model context clean and deterministic  ￼
E3. compaction wrapper if needed for long threads  ￼

Success = long conversations don’t regress into tool spam / forgetting / retries.

⸻

11) What “using the SDK to its fullest” looks like in practice

Here’s the punch list of SDK features you should actively exploit:
	•	Structured outputs (outputType) everywhere that matters  ￼
	•	Agents-as-tools (asTool) with nested runOptions and includeInputSchema  ￼
	•	Tool guardrails for pre/post validation and duplicate blocking  ￼
	•	callModelInputFilter to redact tool noise and inject receipt index  ￼
	•	toolErrorFormatter so rejections teach the model how to proceed  ￼
	•	Sessions + sessionInputCallback for deterministic memory and merging  ￼
	•	Tracing (withTrace, trace processors, traceId/groupId) for debuggability  ￼
	•	Streaming to capture real-time events + HITL flows cleanly  ￼
	•	Error taxonomy + state recovery via AgentsError.state and RunState  ￼
	•	toolUseBehavior for deterministic stop behaviors on certain tools (function tools)  ￼

⸻

12) The “do not do this again” list (hard-earned traps)
	1.	Don’t use handoffs for internal workflow phases (router → specialist → narrator).
	2.	Don’t run “recovery narrator” in a separate session/run unless you intentionally want separate traces.
	3.	Don’t dump raw tool JSON into prompts — receipts only.
	4.	Don’t allow silent retries of the same tool call signature.
	5.	Don’t give 30+ tools to one agent. Tool surface area is a reliability killer.
	6.	Don’t measure success by “it answered”; measure by trace trajectory invariants and artifact completeness.

⸻

If you want the next step:

Tell me whether your production runtime is primarily:
	•	Responses API + Conversations API, or
	•	your own DB-run-store with custom memory

…and I’ll give you a concrete blueprint for:
	•	the exact Session implementation choice,
	•	the exact schemas (RouteDecision / ExecutionPlan / ReportSchema / ReceiptSchema),
	•	the exact invariants your harness should grade,
	•	and a “coding-agent prompt” that forces disciplined, evidence-first implementation.

No guessing. No rabbits. Just a controlled burn straight to stability.