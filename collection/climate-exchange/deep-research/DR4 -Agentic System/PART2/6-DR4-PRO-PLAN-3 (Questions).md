You’re right: without the codebase + runtime artifacts, any “world‑class plan” risks becoming a beautiful hallucination.

So here’s the exact discovery questionnaire I’d run as a senior systems architect before locking architecture + patch plan. If your agents bring back clear answers + file:line evidence + trace evidence, I can turn this into an implementation-ready blueprint (schemas, tool ledger rules, eval harness, and migration steps) with almost no ambiguity.

I’m going to give you:
	•	A. Minimum Evidence Pack (must-have) — the 20% that unlocks 80% of the plan
	•	B. Deep Evidence Pack (SOTA hardening) — what experts gather to make it bulletproof
	•	C. “Bring-back format” — exactly how your agents should report findings
	•	D. Command pack — how they can extract it quickly on wx/integration-staged

⸻

A) Minimum Evidence Pack v1 (must-have)

If you answer these 15–20 items with file:line + “what happens at runtime,” I can finalize the plan confidently.

A1) Runtime + SDK contract (what you actually run)
	1.	Agents SDK version & OpenAI client version
	•	package.json / lockfile evidence
	•	Any wrappers around the SDK
	2.	Which models are used where
	•	Orchestrator/router model name
	•	Specialist model name(s)
	•	Tool-call heavy model settings (temperature, reasoning effort, etc.)
	•	Evidence: where these are set in code (file:line)
	3.	Responses API lifecycle
	•	Are you doing single-run per request?
	•	Or using previousResponseId chaining?
	•	Or any Sessions abstraction right now?
	•	Evidence: file:line where previousResponseId is set (if at all), and where you store lastResponseId
	4.	Streaming
	•	Are you running stream: true? If yes: where do events go?
	•	Evidence: file:line in API handler and scripts

Why this matters: determines whether we can do full trajectory capture + deterministic continuation without Conversations API.

⸻

A2) Control graph (the actual orchestration topology)
	5.	“Who calls whom” sequence
	•	Map the control flow as it exists today:
	•	API route → runSlbChatTurn / runner → router → specialist → narrator (or recovery narrator) → final
	•	Evidence: call sites and functions in:
	•	packages/agents/src/slb/run.ts
	•	packages/agents/src/slb/network.ts
	•	apps/api/src/index.ts (or wherever requests enter)
	6.	Do you currently use handoffs for narration?
	•	If yes: confirm where handoffs are registered + if any inputFilter exists
	•	If no: confirm narrator is invoked via a separate runner.run() and whether it uses same session/trace config
	•	Evidence: file:line

Why this matters: decides whether you’re suffering from “handoff contract misuse” vs “prompt mismatch” vs “separate-run trace fragmentation.”

⸻

A3) Turn budgets + loop guards (the core of your pain)
	7.	List all turn budgets and what enforces them
	•	MAX_TURNS
	•	SPECIALIST_MAX_TURNS
	•	Any per-agent maxTurns
	•	Any retry loop counters
	•	Any timeouts
	•	Evidence: all definitions + where applied (file:line)
	8.	How termination is classified
	•	Where do you decide completed vs max_turns vs tool_loop_detected vs max_turns_recovered?
	•	Is it derived from SDK errors (MaxTurnsExceededError) or prompt heuristics?
	•	Evidence: file:line in run.ts and any shared types/enums
	9.	Tool-loop guard behavior
	•	What exactly triggers “tool loop detected”?
	•	Does it count:
	•	repeated tool calls?
	•	repeated tool attempts (blocked)?
	•	repeated tool errors?
	•	Evidence: code path + data tracked

Why this matters: distinguishes “normal blocked retry patterns” from “pathological loops,” and tells us what to change mechanically.

⸻

A4) Routing determinism + mixed-domain policy
	10.	How mixed-domain is detected

	•	What features/signals are used?
	•	Is it LLM-based classification, heuristic-based, or both?
	•	Evidence: fastRouteSpecialist / routing logic (file:line)

	11.	What happens on ambiguity

	•	When signals disagree, do you pick a single-domain specialist or force mixed?
	•	Is there a “force mixed” switch?
	•	Evidence: route-by-signals code + config flags

	12.	Tool surface per specialist

	•	For each specialist: which tool families are available?
	•	Evidence: tool lists in network.ts (or tool registry)

Why this matters: if routing is wrong even 10% of the time, you’ll keep seeing “half the datasets never got called,” which looks like agent stupidity but is a tool-surface design bug.

⸻

A5) Tool contract realities (the other half of looping)
	13.	For your top 10 most-used tools, provide:

	•	tool name (exact string)
	•	input schema (Zod/JSON schema)
	•	output shape
	•	typical failure modes (ERR_INVALID_INPUT etc.)
	•	idempotency / side effects
	•	average payload sizes (roughly)
	•	Evidence: tool definitions in:
	•	apps/api/src/tools/**
	•	packages/agents/src/tools/**

	14.	Do you have receipt storage today?

	•	Are tool results dumped into prompts as raw JSON?
	•	Any truncation?
	•	Evidence: where tool results are appended to context / prompts

	15.	Tool namespace consistency

	•	Are tool names identical across:
	•	router prompts / specialist prompts
	•	tool registry
	•	executor layer
	•	Evidence: show mapping tables or enums

Why this matters: repeated “invalid input” + giant JSON + name mismatches are the #1 drivers of repeated calls and runaway turns.

⸻

A6) Trace correlation (to stop guessing)
	16.	Where do you set or extract trace IDs?

	•	Do you set traceId / workflowName / groupId explicitly?
	•	Or only extract openai_trace_id afterward?
	•	Evidence: code that sets runConfig, and code that persists run evidence:
	•	apps/api/src/runs/store.ts
	•	apps/api/src/runs/index.ts
	•	apps/api/src/index.ts

	17.	For each failure trace (trace_a28…, trace_2f7…)

	•	Provide a short timeline:
	•	routing decision
	•	specialist selected
	•	tool calls (and whether blocked)
	•	any handoff events
	•	termination reason
	•	Evidence: output from scripts/agentic_trace_regression.mjs and any internal logs

Why this matters: we need to prove which hypothesis is dominant: contract misuse vs prompt mismatch vs state/tooling.

⸻

B) Deep Evidence Pack v2 (SOTA hardening)

Once we have A, these unlock “highest standard” hardening (the stuff teams at OpenAI/Anthropic do for production).

B1) Multi-turn product requirements (Responses API vs Conversations API)
	18.	Do you need:

	•	long-lived threads across days/weeks?
	•	server-managed conversation state?
	•	cross-device continuity?
	•	auditability / replay?

If yes, we may recommend Conversations API or SDK Sessions; if no, previousResponseId + local store may be enough.

B2) Cost / latency / concurrency constraints
	19.	Max latency per L1/L2/L3 target
	20.	Concurrency expectations (QPS)
	21.	Rate limits hitting tools / external APIs
	22.	Any tools that are “expensive” and need approvals

These shape budgets, parallelism, and “needsApproval” patterns.

B3) Output correctness standard (what “report quality” means)
	23.	What must appear in a report:

	•	citations format?
	•	evidence table?
	•	confidence levels?
	•	uncertainty section?
	•	“gap analysis” requirements?

	24.	Which outputs must be structured vs freeform text?

This drives schema design: ReportSchema, SpecialistResultSchema, ReceiptSchema.

B4) Existing evals/harness + how you want to gate
	25.	What currently exists in:

	•	scripts/run-agentic-quality-probes.mjs
	•	scripts/agentic_trace_regression.mjs
	•	docs/runbooks/agentic_trace_grading.md

	26.	What constitutes “pass” today? Where are false positives?

We’ll use this to design a robust eval bank + graders.

⸻

C) What your agents should bring back (format that avoids chaos)

Ask your agents to return one Markdown evidence packet like this:

Evidence Packet Template
	1.	System Map (sequence diagram)
	•	bullet steps + function names
	•	file:line evidence per step
	2.	Budgets & Termination Table
	•	each budget: name, value, where enforced, what error triggers
	•	each termination class: where set, when triggered
	3.	Routing Determinism Report
	•	routing decision logic with conditions
	•	10 probe prompts → selected specialist outcomes (actual)
	4.	Tool Catalog Slice (top 10 tools)
	•	name, schema, output size, typical error, idempotency, ownership
	5.	Trace Timelines for the two trace IDs
	•	turn-by-turn with tool calls + blocked tool calls highlighted
	•	where trace_id gets lost (if it does)
	6.	Risks / Unknowns
	•	anything they couldn’t confirm with code evidence

Every claim must have path:lineStart-lineEnd references and (if applicable) trace evidence.

⸻

D) Command pack (your agents can run these now)

Run these on wx/integration-staged to generate the evidence packet quickly:

D1) Locate orchestration entrypoints

cd /home/gurpreet/projects/standalone/climate-exchange
rg -n "runSlbChatTurn|runChatTurn|new Runner\\(|runner\\.run\\(|previousResponseId|stream:\\s*true" apps packages scripts

D2) Extract budgets + termination paths

rg -n "MAX_TURNS|SPECIALIST_MAX_TURNS|maxTurns|MaxTurnsExceeded|tool_loop_detected|max_turns_recovered|termination" packages/agents/src/slb/run.ts packages/agents/src/slb/types.ts
sed -n '1,220p' packages/agents/src/slb/run.ts

D3) Routing logic & mixed-domain signals

rg -n "fastRouteSpecialist|routeBySignals|isMixed|multi-domain|Mixed_Specialist|force.*mixed" packages/agents/src/slb/network.ts packages/agents/src/slb/run.ts

D4) Narrator execution + session usage

rg -n "narrator|MemorySession|newId\\(\"recovery|handoff\\(|transfer_to_" packages/agents/src/slb/run.ts packages/agents/src/slb/network.ts

D5) Tool inventory (names + schemas)

rg -n "export const.*tool|tool\\(|z\\.object\\(|inputSchema|outputSchema|name:\\s*\"|toolName" apps/api/src/tools packages/agents/src/tools

D6) Trace persistence plumbing

rg -n "openai_trace_id|traceId|groupId|workflowName|traceIncludeSensitiveData|run_id|runs/store|runs/index" apps/api/src/runs apps/api/src/index.ts packages/agents/src/slb/run.ts

D7) Run harness artifacts

ls -la scripts | rg "agentic|probe|trace"
node scripts/agentic_trace_regression.mjs --help


⸻

The “10 questions that most change the plan” (if you only answer a few)

If you want maximal leverage with minimal effort, answer these first:
	1.	Is narrator synthesis inside the same runner.run() loop or a second run? (file:line)
	2.	Do you use handoffs for narration or just run narrator separately? (file:line)
	3.	Exact values + enforcement points for MAX_TURNS and SPECIALIST_MAX_TURNS (file:line)
	4.	What exactly triggers tool_loop_detected? (file:line)
	5.	How mixed-domain routing is computed (signals, thresholds, LLM vs heuristic) (file:line)
	6.	Tool surface per specialist (which tools are hidden from which agent) (file:line)
	7.	Top 5 tools that commonly error + their error patterns (schemas + logs)
	8.	Do tool outputs exceed context limits or get dumped raw? (file:line)
	9.	Do you set traceId/workflowName explicitly or just extract after? (file:line)
	10.	Do you do multi-turn via previousResponseId chaining today? (file:line)

With just those, we can lock the architecture migration + anti-loop mechanics precisely.

⸻

One pushback (because you said “systems engineering is pivotal”)

If your agents come back with opinions (“I think it loops because…”) instead of file-level evidence and trace timelines, you’ll keep looping as a team.

So enforce this rule:

“No hypothesis is allowed unless it has a file:line anchor and a trace/event anchor.”

⸻

If you want, I can also give you a one-page “research agent brief” you can paste into FoggyRiver/RoseWolf/etc that forces them to return the evidence packet in exactly the format above (with line ranges, minimal prose, and zero speculation).


## Audience
- Intended readers: engineering and operations collaborators.


## Change Log
- 2026-02-20: Added required doc sections for lint compliance.


## How to Use
1. Read this document end to end.
2. Follow the commands/process in sequence.


## Prerequisites
- Repository checkout and standard local toolchain available.


## Troubleshooting
- If verification fails, capture command output and resolve prerequisites first.
