
World-class implementation plan for a production-reliable CIE Agents SDK system
Executive summary
Your codebase already contains the right ingredients for state-of-the-art agent reliability: typed tools with Zod schemas, a guarded executor with dedupe + per-tool budgets, explicit termination metadata, trace regression scripts, and (critically) a gated Pattern B (“orchestrator + specialists as tools”) implementation that aligns with how the OpenAI Agents SDK is designed to avoid handoff/turn-budget pathologies. The fastest path to “predictable, bounded, production-reliable” is to: (1) make Pattern B the default, (2) remove or fully contain out-of-band narrator recovery runs (which currently fragment traces and undermine termination semantics), and (3) institutionalize eval-driven development with hard convergence gates that match your real contract (no “passes” that are actually masked max-turn exits). This plan includes an attack sequence that your coding agents can execute with tight validation scaffolds and rollback controls, while keeping you fully on the Responses API. 

Current-state reality check from your repo
The SDK mechanics you must design around
OpenAI’s Agents SDK Runner.run() is an explicit loop with three outcomes per turn: final output, handoff (a tool call that switches agents), or tool calls; it throws MaxTurnsExceededError when maxTurns is hit. That means: handoffs consume turns, and any architecture relying on “a specialist will do X then handoff then narrator will speak” is mechanically sensitive to turn budgets and retries. 

The SDK also explicitly supports the alternative that solves this class of problem: agents as tools (agent.asTool()), where an orchestrator remains in control and calls specialist agents as tool invocations, with isolated run configs available per tool run (including turn budgets and schema inclusion). 

Where your implementation is already aligned
You already implemented the crucial building blocks:

Tool definitions are typed (Zod schemas) and structured to produce receipts/provenance and artifacts. (This matches best practice: tools must be easy for models to call and return “decision-grade” outputs.) 
Guarded tool execution exists (dedupe and loop controls), which is baseline SOTA for preventing pathological repeats.
Trace regression and quality probes exist as first-class scripts, and your runbooks explicitly describe “fail-closed” gates for loops/regressions.
This is strongly aligned with modern agent engineering practice: reliability comes from harness discipline + eval gates, not prompt tweaks. 

Where your implementation is still structurally fragile
Even with recent improvements, you still have two architecture-level liabilities that will keep causing “rabbit holes” until removed:

Out-of-band narrator recovery runs: you still spin up separate runner.run() calls in isolated MemorySessions for specialist recovery/fallback. That necessarily makes tracing and causal reconstruction harder because you’ve now created multiple runs/traces for what users perceive as one request. OpenAI’s tracing docs explicitly call out that multi-run grouping requires explicit trace grouping or single-workflow tracing. 

Termination semantics can be misleading: any system that treats max-turn exits as “completed” (or otherwise masks true termination) will produce false positives in your probes and will destroy debugging signal. Evaluations only work if the harness faithfully measures what happened. 

North-star architecture design for CIE
Design goal
Make the system behave like a bounded, inspectable compiler pipeline:

Classify → Acquire → Analyze → Synthesize → Verify → Emit

The orchestrator is the compiler driver. Specialists are deterministic “passes” that return structured receipts and intermediate artifacts. The narrator is a formatting/synthesis pass that must not be able to re-open acquisition.

This maps directly onto the OpenAI Agents SDK’s strengths:

Use one controlling orchestrator run per request.
Use specialists as tools for isolated budgets and predictable sub-behavior. 
Use handoffs only for true ownership transfer (rare), not for routine “do analysis then narrate” flows. 
Concrete agent topology for your use case
You do not win by having dozens of agents. You win by having a small number of agents with extremely clear contracts plus a “skills”/playbook layer.

A world-class topology for CIE with 30+ tools:

CIE Orchestrator (primary agent)
Responsibilities:

Understand user intent (L1/L2/L3).
Choose which “skills” to run.
Call specialist agents-as-tools to produce intermediate receipts.
Produce final structured output (report + sources + caveats + artifacts pointers).
Enforce budgets and phase-locking (“acquire” vs “synthesize”).
Domain Specialist Agents (as tools) — small set, not one per dataset
Recommended domains given your existing tools:

Hazards: cyclone corridor / hotspots / disaster history / earthquakes / tsunami / volcano / wildfire.
Ocean & coastal: sea level + waves + SST + coral stress.
Hydroclimate: rainfall + temperature + reanalysis/projections.
Exposure & admin: admin boundaries, population exposure, facilities.
Interventions: IATI search, gap analysis, quadrant analysis.
Each specialist’s job is: turn user intent into one bounded batch of tool calls, then return a structured “evidence packet” (not prose).

Narrator / Report Composer (optional)

If you keep a narrator, run it as an agent tool invoked by the orchestrator, fed only the evidence packet.
It must have zero dataset tools, only formatting.
This is consistent with: (a) OpenAI’s recommended primitives (agent tools, run configs, handoff filters), and (b) Anthropic’s production practice: reliability comes from clear role boundaries and harness enforcement, not “god agents.” 

The “skills layer” that makes this SOTA
Instead of relying on the orchestrator to re-invent plans per prompt, create Skills as explicit, versioned workflows:

skill.cyclone_risk_profile(region, years)
skill.sea_level_trend(station_id, range)
skill.mixed_cyclone_plus_sea_level(location, horizon)
skill.risk_coverage_quadrant(admin_level, hazard)
skill.gap_analysis(admin_level, hazards)
Implementation options (choose one, but be consistent):

Skills as code (deterministic): a normal TS function that executes a tool plan with strict budgets and returns a standard evidence packet.
Skills as specialist agents-as-tools: keep the flexibility of an LLM inside each skill, but strongly bound it with maxTurns, tool availability, and output schemas. 
For your reliability goals, “skills as code” is the gold standard for repeatability. Use LLM specialists only where the planning space actually matters.

Implementation plan with a tight attack sequence
Guiding principle
Every step must be:

orthogonal
feature-flagged
paired with a measurable validation
rollbackable in minutes
This is eval-driven development for agents, applied to orchestration. 

Patch tiering
Tier zero stabilization
Goal: stop the bleeding, make behavior bounded and diagnosable today.

Make Pattern B the default path

Flip the default so orchestrator+specialists-as-tools is the standard, and Pattern A is behind an explicit env var.
Rationale: Pattern B eliminates the core class of shared-turn/handoff-budget failures by design. 
Eliminate out-of-band narrator recovery for the normal path
Your best option is one of:

(Preferred) Put narrator inside Pattern B as an agent tool (narrator.asTool) called by the orchestrator.
Or: make the orchestrator itself produce final narration and remove narrator entirely.
Rationale: Your biggest observability pain (“no handoffs”) is often a symptom of the model not calling transfer tools and/or you running narration separately. You want one causal spine per request. 

Stop masking termination

If a run hits maxTurns or tool-loop abort, that must surface as such in termination.reason.
If you choose to treat “specialist hit budget but orchestrator still produced solid answer” as acceptable, introduce a separate explicit state: e.g. completed_degraded (or keep your max_turns_recovered but never label it “completed”).
Rationale: eval gates become meaningless if the harness cannot trust termination labels.

Narrator input must be filtered and bounded

Use SDK handoff/tool input filters to remove tool noise or massive payloads.
Never pass raw full JSON arrays into narrator prompts; pass a compact evidence packet with pointers (artifact URIs, blob refs, receipt IDs).
Input filters are a first-class concept in the SDK. 
Tier one reliability hardening
Goal: make “looping” mechanically impossible (not just unlikely).

Phase-lock tool availability

Introduce a run-context field like context.phase = "acquire" | "synthesize".
Enforce in the executor: dataset tools return a hard “phase_locked” error outside acquire phase.
In Pattern B, this is clean: orchestrator sets phase transitions and tools become unavailable.
Global tool budget + per-domain quota Per-run:

max_total_tool_calls
max_unique_tools
max_failed_tool_calls
max_blocked_tool_calls (you already have a version of this)
This prevents the “6 different tools, each once, repeated forever” pattern that defeats per-tool limits.

Tool result contract enforcement You already defined a proof contract shape. Make it enforceable at runtime:

Validate every tool result.
On violation, convert to { ok:false, error:{code:"ERR_TOOL_CONTRACT_VIOLATION"} }.
Make the orchestrator treat that as a data gap and stop acquisition, not retry.
This aligns with tool best practices: tools must have stable contracts and clear failure modes so models don’t thrash. 

Tier two quality & scale
Goal: move from “works for our probes” to “production-grade under real distribution shift”.

Eval suite as a product artifact Treat your scripts as a “first-class test harness,” not utility scripts:

Convert the probe corpus into versioned fixtures.
Add a dedicated “pathology suite” (mixed-domain, ambiguous, tool failures, missing dataset, huge outputs).
Add LLM-judge graders only where necessary; prefer deterministic graders (receipt present, sources present, termination labels, tool budgets, etc.). 
Trace + artifact model Ensure each run yields:

one trace id (or one group id) that is the spine
a stable run_id
a manifest pointer to artifacts and receipts
a replay pointer
Tracing is already first-class in the SDK; exploit it the way it was intended. 

How to guide your coding agents through the attack sequence
This is the “teach success” layer: each step defines output + verification.

Step zero
“Freeze the contract” doc:

Define L1/L2/L3 formally:
L1: discovery or single lookup.
L2: single domain analysis.
L3: multi-source synthesis (≥2 domains).
Define a required output schema for orchestrator responses:
answer_markdown
sources[] with receipt IDs
artifacts[]
termination{...}
diagnostics{route, tool_ledger, budgets}
Why: Clear success criteria turns “it feels better” into checkable invariants. 

Step one
Enable and validate Pattern B in staging:

Change default config: Pattern B on; Pattern A behind flag.
Run:
agentic quality probes
trace regression corpus
Success definition:

Mixed-domain L3 always calls the two expected tool families (cyclone + sea level).
termination.reason === "completed" for canonical probes.
No tool loop warnings.
Trace shows one coherent run with nested tool calls.
This step directly operationalizes the SDK’s recommended “agents as tools” approach. 

Step two
Remove narrator out-of-band recovery (or collapse it into orchestrator)

Implementation choices:

Orchestrator generates final narrative itself, or
Orchestrator calls narrator as a tool (nested) with strict input schema and strict maxTurns.
Success definition:

There is never a “parallel invisible trace” for the same user request.
openai_trace_id corresponds to the observed run and includes nested spans/events in one place. 
Step three
Tool phase-lock + budgets

Add:

context.phase
global budgets
fail-fast contract violations
Success definition:

Attempted tool calls in synth phase are blocked with an explicit error once, then the orchestrator must synthesize (no retries).
No repeated tool calls with identical args.
This follows modern “harness discipline” (don’t rely on prompts to do budget enforcement). 

Step four
Evals become the release gate

Add two suites:

Capability suite: L1/L2/L3 across representative user intents.
Pathology suite: ambiguous prompts, mixed prompts, tool error injection, missing provenance, big output.
Each suite should output:

pass/fail
termination classification
tool ledger summary
trace id
Anthropic’s eval guidance is clear: capture real failures, make tasks unambiguous, and run them continuously. 

Best-practice clarifications for your team
What is a tool vs a function call vs an agent
Tool (Agents SDK concept): a callable capability exposed to the model with a name, JSON schema, and executor. In your system, tools should represent data access or deterministic analyses (datasets, transforms, aggregations). 
Function call (Responses API representation): the serialized event type that records a tool invocation and its output. The Agents SDK abstracts this but the ordering constraints still matter (hence your filtering logic). 
Agent: an LLM policy (instructions + available tools + optional handoffs/output schema). Agents are not “magic”; they are components in a harness. 
Should each dataset be a tool
High-standard guidance:

Make each dataset access path callable as a tool when:
It has a stable schema
It has a stable provenance model
It returns bounded outputs or uses artifacts/pointers for bulk data
Do not make every micro-operation a tool if it creates combinatorial planning noise.
Prefer a two-layer structure:
Dataset tools (retrieve / summarize / artifact)
Analysis tools (compute derived metrics deterministically)
This is consistent with “writing effective tools” guidance: tool design and naming/namespace discipline is what prevents tool chaos at 30–300 tools. 

When you need structured outputs
Use structured outputs when the result becomes an input to your system (not just something a human reads):

Orchestrator final output should be strongly typed (so your UI and eval harness can trust it).
Specialist outputs should be strongly typed as evidence packets.
Narration can be markdown, but should attach sources deterministically.
This reduces ambiguity and makes eval grading deterministic. 

Risk and rollback
Top risks
Turning on Pattern B by default might surface hidden assumptions in existing specialist prompts (because the orchestrator becomes responsible for synthesis and the specialists become “evidence producers”).
If your eval harness currently treats “maxTurnsExceeded but narrator recovered” as pass, tightening semantics will look like regressions at first (they’re actually truth coming back).
Rollback pattern
Keep Pattern A behind CIE_ORCHESTRATOR_PATTERN=A (or unset), but never iterate on it again except to keep it compatible.
Keep a single “big red switch” env var to revert orchestration architecture without code rollback.
This is the same operational posture used for high-risk agent loop changes: safe default, fast rollback. 

Next actions that are agent-assignment-ready
Orchestration lead: Make Pattern B the default; remove out-of-band narrator recovery; ensure single causal spine per request. Validate via probes and trace regression. 
Tooling lead: Implement global budgets + phase-locking + runtime tool-contract enforcement; produce a tool design guide (“how to add a dataset tool without breaking the system”). 
Evals lead: Convert probes + trace regression into a proper eval suite with pathology cases and deterministic graders; make it the merge gate. 
Observability lead: Ensure workflowName, trace metadata, and trace grouping are coherent and stable for each run; eliminate “missing handoffs” as an observability artifact, not a debugging mystery. 