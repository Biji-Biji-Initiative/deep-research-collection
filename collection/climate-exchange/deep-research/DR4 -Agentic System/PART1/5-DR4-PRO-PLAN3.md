Perfect — staying 100% on the Responses API is totally compatible with a world‑class Agents SDK system. In fact, the SDK is designed for exactly this: you can get stable orchestration, bounded tool use, eval-grade trajectories, and deterministic termination without adopting Conversations API or a DB run store yet.

Below is the “expert‑tier” blueprint I’d hand to a senior coding agent team to execute.

⸻

0) The two strategic moves that unlock reliability

Move 1: Treat “handoffs” as UI/role transitions only

For your core workflow (router → specialists → narrator), do not use handoffs as the primary mechanism.

Instead, use:
	•	One Orchestrator agent that owns the conversation + final output
	•	Specialists as tools (agent.asTool()), called by the Orchestrator
	•	Dataset tools only inside specialists (not on the Orchestrator)

This is the SDK’s “manager / agents-as-tools” pattern, and it’s the cleanest way to enforce budgets and stop loops by construction.  ￼

Move 2: Use “receipt-first” + ledger-based tool gating

Most tool loops are context failures disguised as “agent behavior.”

Your system must enforce:
	•	bounded tool outputs (no giant JSON into model context)
	•	duplicate tool call blocking (same tool+args signature cannot re-run)

This is not prompt hardening — it’s runtime physics.

⸻

1) Responses API–first: how to do multi-turn without Conversations API or a DB

You have 3 escalating options, all supported by the SDK:

Option A: Single-turn runs only (fastest to prove stability)

For your initial hardening + eval suite, run each probe as one runner.run(). You don’t need a session at all.

This is usually enough to validate the loop/termination/tool policy correctness.

Option B: “previousResponseId chaining” (minimal state, still 100% Responses)

The runner.run() options include:
	•	previousResponseId — continue from a previous Responses call without creating a conversation (Responses API only)  ￼
	•	and the SDK gives you result.lastResponseId to store for the next turn  ￼

So you can implement multi-turn by storing just:
	•	lastResponseId
	•	your own run_id/trace_id

No DB “run store” required — you can keep this in memory or a file while proving things.

Option C: Sessions + Responses compaction (still Responses API; best “no DB” middle ground)

Agents SDK Sessions give you persistent memory through a Session interface. It ships with MemorySession, and you can plug in a file-backed session quickly.  ￼

Then, because you’re using Responses models, you can wrap your session with OpenAIResponsesCompactionSession, which triggers responses.compact as history grows.  ￼

Important nuance: the docs explicitly warn to avoid pairing OpenAIResponsesCompactionSession with OpenAIConversationsSession because they use different memory flows.  ￼

When to consider Conversations API

Only when you specifically want server-managed thread memory via conversationId (“Reuse a server-side conversation”), which is available when you use Responses + Conversations API together.  ￼

For your current goal (“prove stability before DB”), I’d start with Option A/B, then graduate to Option C.

⸻

2) World-class architecture for CIE (what to build)

2.1 The agent topology you want (clean, scalable, non-garbled)

A) One Orchestrator (the only agent that “speaks” to the user)

Responsibilities
	•	classify intent + L1/L2/L3 level
	•	choose which specialists to consult
	•	enforce budgets
	•	maintain receipts index
	•	synthesize final structured report

Tools
	•	specialist tools only (HazardSpecialist.asTool(), etc.)
	•	minimal workflow tools (render report, persist artifact)
	•	optional: “tool catalog” lookup (only if tool count explodes)

Output
	•	ReportSchema (Zod) structured output for deterministic downstream use

B) Specialists as tools (agents-as-tools)

Each specialist:
	•	has a narrow toolset (only the dataset tools it needs)
	•	returns a structured domain result with receipt references
	•	has a small nested maxTurns budget

Use agent.asTool() options aggressively:
	•	includeInputSchema to reduce schema mistakes in nested runs  ￼
	•	needsApproval for expensive/side-effect-y tools  ￼
	•	onStream to stream nested events upward for observability  ￼
	•	runConfig/runOptions to set nested budgets and trace metadata  ￼

C) Dataset tools (function tools)

Dataset tools should be:
	•	strictly validated (Zod)
	•	idempotent
	•	bounded output (receipt-first)
	•	protected by tool guardrails (reject duplicates, cap output, validate args)

Tool guardrails are first-class in the SDK and run on every tool invocation.  ￼

⸻

2.2 The orchestration pipeline (bounded & deterministic)

Orchestrator does:
	1.	Classify (structured)
	2.	Plan (structured)
	3.	Execute (code-driven calling specialist tools, possibly parallel)
	4.	Synthesize (structured final report)
	5.	Optional Verify (bounded evaluator pass)

This is basically Anthropic’s “orchestrator-workers” + “evaluator-optimizer” patterns, but implemented with SDK primitives (agents-as-tools + structured outputs + guardrails).  ￼

⸻

3) Loop elimination: do it with SDK-native mechanics, not vibes

3.1 Understand what the SDK loop is

The SDK run loop is explicitly:
	1.	call model
	2.	inspect response: final output / handoff / tool calls
	3.	on tool calls: execute tools, append results, run model again
	4.	throw MaxTurnsExceededError when maxTurns reached  ￼

So “looping” is usually:
	•	tool calls repeating
	•	or handoffs bouncing
	•	or the model never producing final output

3.2 Use the SDK’s built-in loop dampening

The Agents guide notes that after a tool call, the SDK resets toolChoice back to auto to prevent repeated forced-tool loops, and you can control stopping behavior via toolUseBehavior.  ￼

Practical use in CIE
	•	Keep the default toolUseBehavior for specialists (“run_llm_again”) so they can interpret tool results.
	•	Use custom stopping logic only when you have a tool whose output should be treated as final (rare for you).

3.3 Hard anti-loop stack (you should implement all 4)

Layer A — Explicit budgets
	•	Orchestrator maxTurns as the safety ceiling
	•	specialist nested budgets via asTool({ runOptions/runConfig })  ￼

Layer B — Tool-call ledger (duplicate signature blocking)

In shared context:
	•	hash (toolName + canonicalArgsJson)
	•	if seen → reject pre-execution (guardrail) with guidance
	•	allow second call only if args changed in a meaningful way

Layer C — Tool guardrails (before/after execution)

Use tool guardrails to reject duplicates and enforce bounded output.  ￼

Layer D — ErrorHandlers for deterministic termination

Instead of throwing at maxTurns, convert it into a controlled final output using errorHandlers.maxTurns.  ￼

⸻

4) Maximum “Agents SDK leverage”: the 7 hooks you should actively use

These are the power tools that separate toy agent systems from production systems:

4.1 traceId + groupId + workflowName

Set these per run so your traces are always correlatable:
	•	workflowName shows in Traces dashboard  ￼
	•	traceId/groupId can be manually specified  ￼

World-class move: deterministically derive traceId from your internal run_id.

4.2 traceIncludeSensitiveData

You can exclude LLM/tool I/O from traces while keeping spans, for privacy/PII.  ￼

4.3 withTrace() for higher-level workflows

Tracing guide: SDK traces runs, tool calls, guardrails, handoffs by default, and you can group multi-run flows with withTrace() and/or custom trace processors.  ￼

4.4 callModelInputFilter

This is where you enforce “receipt-first” context:
	•	drop tool spam
	•	inject receipt index
	•	inject dynamic system guidance

The SDK explicitly supports mutating input items + optional instructions right before model call.  ￼

4.5 sessionInputCallback

If/when you adopt Sessions, this is your deterministic merge policy for history + new input.  ￼

4.6 toolErrorFormatter

This is underrated: when you reject tool calls (duplicates, invalid args), the model needs a useful rejection message. SDK lets you customize these approval-rejection messages.  ￼

4.7 Streaming events as your “trajectory recorder”

Streaming guide: stream: true returns an async iterable of event objects (raw model events + run items + agent updates).  ￼

Even if you don’t stream to UI, stream to your evidence sink.

⸻

5) “Prove it first” plan (no DB run store required)

You said: DB run store later once we prove things. Perfect. Here’s the proof harness:

5.1 Define a JSON task bank (feature-list style, eval-driven)

Anthropic’s long-running harness work shows using structured JSON checklists reduces model “corruption” versus markdown and prevents premature victory.  ￼

Create: scripts/agentic_eval_bank.json
Each task includes:
	•	prompt
	•	expected specialists (set)
	•	required tool families/tags
	•	max tool calls
	•	forbidden termination classes
	•	required output fields in ReportSchema

5.2 Run multi-trial, store full trajectories

Anthropic’s eval post emphasizes “transcripts/trajectories” as the complete record of a trial including tool calls and intermediate results.  ￼

Your harness should save:
	•	traceId, groupId, workflowName
	•	streamed events (or RunResult.newItems)
	•	finalOutput
	•	usage
	•	lastResponseId

5.3 Grade outputs, not brittle paths

Anthropic explicitly warns that grading “specific steps like tool calls in the right order” is too rigid; better to grade what was produced.  ￼

So your graders should be:
	•	deterministic schema checks
	•	receipt presence checks
	•	tool duplication checks
	•	termination class checks
	•	domain coverage checks (specialists called)

⸻

6) The exact “attack sequence” I’d give your coding agents

This is written like an internal strike plan.

Phase 1 — Observability spine (must come first)

Goal: every run is debuggable, correlatable, and reproducible.

Implement:
	•	deterministic traceId/groupId/workflowName in runConfig  ￼
	•	capture RunResult.newItems, finalOutput, usage, lastResponseId  ￼
	•	enable streaming in the harness (stream: true) and record events  ￼
	•	add a custom trace processor (optional) to also write spans to local JSON  ￼

Exit criteria
	•	you can reconstruct the full story of a run from artifacts alone

Phase 2 — Tool contract hardening (where loops die)

Implement a shared tool wrapper + tool guardrails:
	•	input validation + normalization
	•	duplicate blocking (ledger)
	•	output size cap + receipt storage
	•	timeouts

Tool guardrails are designed for exactly this.  ￼

Exit criteria
	•	no dataset tool ever dumps huge payloads into the model context
	•	duplicate calls are blocked with helpful guidance

Phase 3 — Migrate to Orchestrator + specialists-as-tools

Implement Orchestrator with:
	•	ReportSchema outputType
	•	calls to specialist tools via asTool() with nested budgets and includeInputSchema  ￼
	•	parallel specialist calls where independent (hazard + sea level)
	•	callModelInputFilter that injects a clean “Receipt Index” and strips tool spam  ￼
	•	errorHandlers.maxTurns that converts maxTurns into a controlled partial output  ￼

Exit criteria
	•	mixed-domain prompts always produce multi-specialist coverage (by plan, not luck)
	•	no handoff loop class exists in normal workflow

Phase 4 — Bounded verifier (optional but very high ROI for L3)

Add a Verifier agent-as-tool:
	•	grades the report object against a rubric
	•	returns structured defects
	•	Orchestrator may do one repair pass maximum

This matches evaluator-optimizer but stays bounded.  ￼

Exit criteria
	•	L3 reports become consistently “boardroom quality” with stable structure

Phase 5 — Sessions/compaction (only once core is solid)

If you need persistent multi-turn memory:
	•	implement file-backed session or minimal store
	•	wrap with OpenAIResponsesCompactionSession for automatic responses.compact  ￼

Avoid mixing this with Conversations session.  ￼

⸻

7) Copy/paste instructions for your coding agent (tight, uncompromising)

Use this verbatim as the “system-style” instruction for your implementation agent:

Coding Agent Mission Brief
	1.	Implement Orchestrator + specialists-as-tools architecture on Responses API. No handoff-based orchestration except explicit UI escalation.
	2.	Add tool guardrails + ledger duplicate blocking + receipt-first output contracts for all dataset tools.
	3.	Add deterministic trace correlation via traceId/groupId/workflowName, and persist full run trajectories.
	4.	Build an eval harness with a JSON task bank, multi-trial runs, and graders that validate output+receipts rather than brittle tool-order.
	5.	No behavior changes land without a failing regression test + after/before artifact proof.

SDK features to use
	•	asTool() options: includeInputSchema, runOptions/runConfig, needsApproval, onStream  ￼
	•	callModelInputFilter, toolErrorFormatter, errorHandlers.maxTurns  ￼
	•	Streaming events via stream: true  ￼
	•	Tool guardrails on all function tools  ￼
	•	Tracing with traceId/groupId/workflowName, optional traceIncludeSensitiveData  ￼
	•	Use previousResponseId chaining if multi-turn is needed; persist lastResponseId.  ￼

⸻

If you want, I’ll go one level deeper still:

I can propose the exact schemas (RouteDecisionSchema / ExecutionPlanSchema / SpecialistResultSchema / ReceiptSchema / ReportSchema) and the exact grading rules that will catch your current failures (handoff loops, tool retries, missing mixed-domain coverage) with near-zero false positives.

Just say “give me the schema pack + grader spec”, and I’ll produce it as implementation-ready Zod + JSON task bank format.