
CIE Agent SDK Orchestration Root-Cause Diagnosis and Patch Plan
Executive summary
Your current instability is not “random model behavior” but a control-plane contract mismatch between how the OpenAI Agents SDK actually triggers routing/handoffs (handoffs are tools that must be called) and how the CIE runner implicitly expects “automatic” handoff + recovery to behave. This is amplified by a too-tight shared turn budget in mixed-domain flows, context pollution when handing to the Narrator (tool-loop envelopes and retries), and trace/session fragmentation that makes the system look like “no handoffs happened” in the OpenAI dashboard even when you “recovered” downstream. The fastest path to predictable, production-grade behavior is to adopt the SDK’s Manager pattern (agents-as-tools) for L1/L2/L3 orchestration, while applying a minimal “Pattern A hotfix” in parallel to immediately stop the worst looping/termination failures. 

Findings with evidence
Repo + ref used for evidence: Biji-Biji-Initiative/climate-exchange @ commit 40667cd (branch tip of wx/integration-staged). Biji-Biji-Initiative GitHub

The “10 reasons” critique: alignment and where it’s even worse than it looks
Your “10 reasons the architecture is wrong” is directionally correct, and the SDK docs strongly support the core thrust:

Handoffs are tools; “handoff language” is not a handoff. In the SDK, a handoff is represented as a tool call (e.g., transfer_to_<agent_name>). If the model does not call that transfer tool, no handoff occurs—no matter what it writes in plain text. 
Implication: Any prompt text implying “Turn 3 is automatic” is a direct reliability hazard because it encourages the model to not emit the required transfer tool call.

Input filters are the SDK-native way to prevent “tool loop noise” from contaminating the next agent. The SDK explicitly supports inputFilter on handoff() and ships helpers like “remove all tools from history”. 
Implication: If the Narrator receives the full transcript including retries/TOOL_LOOP_LIMIT envelopes, synthesis quality degrades and termination can become inconsistent (because the Narrator reasons over garbage context).

The SDK strongly endorses two multi-agent patterns—Manager (agents-as-tools) vs Handoffs—and explains why Manager gives you a single enforcement point. 
Implication: For “parallel tool calls then synthesis” (your L3 mixed-domain work), the Manager approach is the more production-bounded pattern.

Where your list is even more revealing:

Your repo already encodes the incident prompts + regression expectations in a corpus (meaning the org has already recognized this as an orchestration/control-plane problem, not “randomness”):
specs/agents/trace_regression_corpus.v1.json includes incident case incident_a28a7d1e with trace id trace_a28a7d1e87dc48b59b3aa5ff7fe2f1e6 and a mixed-domain cyclone + sea level prompt. It explicitly fails closed on max_turns and tool_loop_detected, and requires both tool families (hazard.cyclone* and climate.sea_level*).
Evidence: specs/agents/trace_regression_corpus.v1.json.
docs/runbooks/agentic_trace_grading.md formalizes this as a release gate.
Evidence: docs/runbooks/agentic_trace_grading.md.
Confirmed failure class
Per your non-negotiable triage (“SDK runtime contract misuse vs prompt mismatch vs tooling/state persistence issue”), evidence points to:

SDK runtime contract misuse (primary)
Handoff mechanics misunderstood/under-enforced: a “handoff” only happens when the model calls the transfer_to_* tool; the SDK explicitly defines handoffs as tools.
The system depends on recovery behavior rather than enforcing a single coherent run: your quality probes and trace regression scripts assume that a “clean exit” occurs within bounded turns and without tool_loop_detected warnings; that’s a control-plane invariants problem, not a model problem.
Evidence:
scripts/run-agentic-quality-probes.mjs (strict mode sets breach → fail, and reads termination + route decision fields).
scripts/agentic_trace_regression.mjs and scripts/verify-agentic-trace-grade.sh (fail-closed on the same termination classes).
Prompt / route-policy mismatch (secondary)
The SDK recommends explicitly educating prompts about handoffs using a provided prefix. That’s not the same as teaching “handoff is automatic.” 
Your regression corpus is specifically mixed-domain; the acceptance gates require mixed-domain routing to Mixed Specialist (or equivalent mixed handling) and bounded tool policy.
Tooling / persistence / trace plumbing (tertiary)
The API persistence layer already supports storing openai_trace_id on the run record and in streamed assistant_final events.
Evidence:
apps/api/src/runs/store.ts persists openai_trace_id in finalizeChatRun(...).
apps/api/src/index.ts includes openai_trace_id in assistant_final event data and passes it into finalizeChatRun(...).
However, your incident inputs reference multiple OpenAI trace IDs, and the repo’s official regression corpus currently includes trace_a28... and trace_fb09... but not the trace_2f7e... you mentioned in the prompt—meaning your regression gate is incomplete against the symptoms you’re actively debugging.
Evidence: specs/agents/trace_regression_corpus.v1.json, docs/runbooks/agentic_trace_grading.md.
Turn budgets and loop semantics are enforced in code (good) but misaligned with “handoff + narrator” sequencing (bad)
Tool loop protection exists and is deterministic (per-tool call limits, param-aware dedup cache, bounded retry via failed-signature blocking). This is tested thoroughly.
Evidence: packages/agents/src/slb/run.test.ts (createGuardedExecutor tests for cache hits, TOOL_LOOP_LIMIT, TOOL_RETRY_EXHAUSTED).

Your probe gates codify the production definition of “bounded success.” For the L3 cyclone+sea-level probe, it enforces tool counts, turn counts, and termination class, and it treats tool_loop_detected and max_turns as failures in strict mode.
Evidence: scripts/run-agentic-quality-probes.mjs (thresholding + strict termination grading) and specs/agents/trace_regression_corpus.v1.json.

Key insight: you already have a robust enforcement perimeter; what’s broken is that the current orchestration pattern produces failure modes that your own gates correctly fail.

Trace evidence status (what we can and cannot prove from the repo alone)
From the repo, we can prove the incident IDs and how you intend to grade them, but not the full OpenAI trace timelines (tool calls, handoff events, etc.) for the two traces you named because the raw trace payloads are not stored in the repository.

What we can prove you already have:

A deterministic regression harness that reruns incident prompts and records:
run_id
openai_trace_id
termination_reason
turn/tool/handoff counts
Evidence: scripts/agentic_trace_regression.mjs, docs/runbooks/agentic_trace_grading.md, scripts/verify-agentic-trace-grade.sh.
What remains to do (but is completely unblockable because you already have the scripts):

Run the grader against your live API and collect the artifacts under reports/agentic_quality/trace_grade/ to get the missing trace-to-runtime map for trace_a28... and your additional trace(s).
Evidence path exists by runbook + script design.
Patch plan by priority
This is a “three-lane” plan: a minimal hotfix to stop the bleeding, a structural refactor that aligns with the SDK’s SOTA patterns, and a final hardening layer that makes the system debuggable and regression-resistant.

Immediate stabilization hotfix set
Objective: “Predictable, bounded, production-reliable” without redesigning everything in week one.

Hotfix cluster A: make handoff semantics unambiguous and SDK-native

Remove any Mixed Specialist prompt language that implies narration/handoff is automatic. Replace with explicit instruction: “When finished, you must call transfer_to_CIE_SLB_Narrator.”
Why: SDK handoffs only occur via transfer tool calls. 
Files to change:
packages/agents/src/slb/network.ts (Mixed specialist prompt text)
Any handoff prompt prefixes: incorporate SDK recommended prefix for handoffs in the relevant agent(s). 
Hotfix cluster B: prevent narrator contamination via inputFilter

Wrap Narrator handoff with an input filter that removes tool noise and retries (the SDK ships helpers for this). 
Intended diff direction:
In createSlbNetwork(...) where handoffs: [narrator] exists, change it to handoffs: [handoff(narrator, { inputFilter: removeAllTools })] (JS naming depends on your import; the concept is stable).
Ensure this applies to all specialists handing to Narrator, not just Mixed.
Hotfix cluster C: align turn budget with the actual multi-step workflow

Your own probe defaults assume max turn counts like ~6–8 for L3. Your regression corpus sets max_turn_count: 8 for the cyclone+sea-level incident.
Evidence: specs/agents/trace_regression_corpus.v1.json, scripts/run-agentic-quality-probes.mjs.
Intended diff direction:
Increase the effective maxTurns for the mixed-domain path enough to allow:
tool execution,
optional “gap analysis” tool call (if invoked),
explicit transfer_to_Narrator,
Narrator output.
Keep it bounded: match the corpus limit (8), don’t “open the floodgates.”
Hotfix cluster D: termination semantics—successful runs must not be labeled tool_loop_detected

The acceptance gate is explicit: “No WARN tool_loop_detected for successful completion paths.”
Your scripts already enforce this by failing the probe on tool_loop_detected.
Evidence: scripts/run-agentic-quality-probes.mjs.
Intended diff direction:
Treat “loop guard tripped but we still produced a verified, bounded, narrated answer” as completed_degraded (or similar), and reserve tool_loop_detected for runs that exit without reliable narration.
Rollback plan for hotfix

Gate the new behavior behind existing env switches already present in your repo’s mode handling, and roll back by:
reverting network.ts prompt change,
reverting narrator handoff configuration,
restoring previous maxTurns.
(This is a standard revert, no schema migration needed.)
Structural fix
Objective: eliminate handoff loops and shared-turn fragility by adopting the SDK’s Manager (agents-as-tools) pattern for L1/L2/L3.

This directly aligns with the SDK’s stated production design pattern taxonomy:

“Manager (agents as tools)” keeps conversation control with one orchestrator and invokes specialists as tools. 
Design sketch

Create CIE_SLB_Manager (or repurpose Router+Narrator into one “manager” agent).
Expose each domain specialist via specialist.asTool(...) (JS) / as_tool(...) (Python), giving each:
isolated maxTurns budget,
constrained tool set,
strong structured output (custom output extractor that returns canonical JSON payload). 
The manager:
selects which specialist tools to call (possibly multiple for mixed-domain),
never hands off control,
synthesizes or calls a Narrator-as-tool for final formatting (optional).
Why this resolves your highest-priority failures

Mixed-domain queries stop being a brittle “handoff choreography”—they become “call two specialist tools and join results.”
Shared-turn budget fragility disappears because each specialist tool has a bounded nested budget.
Handoff loops are structurally removed from the primary path.
Trace coherence

The SDK’s tracing model supports nested spans and higher-level traces; the docs explicitly describe tracing around runner runs and how to group multiple runs when needed. 
File-level patch direction

packages/agents/src/slb/network.ts: add an orchestrator agent and switch from “router → specialist → narrator” to “manager → specialist tools → manager synthesis”.
packages/agents/src/slb/run.ts: update the run pipeline so the final output is always produced by the manager run (not a post-hoc recovery pass).
packages/agents/src/slb/run.test.ts + specialist_integration.test.ts: extend tests to assert manager invariants.
Rollback

Keep the old handoff-based orchestration behind CIE_SLB_AGENT_MODE=handoff vs manager, and be able to revert by switching the env flag only.
Production hardening
Objective: make investigations fast and deterministic.

Trace corpus completion

Add your missing trace id(s) (e.g., your prompt’s trace_2f7e...) into specs/agents/trace_regression_corpus.v1.json and update the runbook list so the gate actually covers what you’re seeing.
Evidence of existing mechanism: specs/agents/trace_regression_corpus.v1.json, docs/runbooks/agentic_trace_grading.md.
Run artifact standardization

Persist openai_trace_id and any nested trace references if you keep nested runs. Your persistence layer already supports openai_trace_id at the run level.
Evidence: apps/api/src/runs/store.ts, apps/api/src/index.ts.
Minimal standard (per run):
run_id, session_id, request_id
openai_trace_id (primary)
termination: reason, turn_count, tool_call_count, unique_tool_count
route_decision (and domain classifier hits)
tool calls: tool_name, ok, receipt_id, blob refs (already supported by your event schema)
Test plan and expected outcomes
You requested 8+ tests spanning L1/L2/L3 + pathological runs, with strict assertions.

Unit/integration tests to add
All new tests must assert:

handoff completed or (Manager pattern) “manager finalized output,”
no repeated tool loops beyond policy,
narrator (or manager) finalization occurs,
openai_trace_id is present when OpenAI is actually invoked,
termination classification is consistent with success/failure.
L1 tests

L1 catalog query: ensure at least one tool call, narrator/manager final output, termination=completed.
L1 sea level query: ensure the correct tool family is invoked and sources/receipts are propagated.
L2 tests

L2 rainfall time series: ensure tool call budget stays bounded and the response ends with a verified sources section.
L2 temperature forecast: ensure slow-tool timeouts degrade correctly without looping.
L3 tests

L3 cyclone + sea level synthesis: assert mixed handling uses both tool families and ends within corpus thresholds.
Evidence target: specs/agents/trace_regression_corpus.v1.json.
L3 rainfall + temperature synthesis: same structure, different domains.
Pathological tests

Tool retry storm: simulate repeated invalid-input tool calls and ensure:
you do not mark the run “successful but tool_loop_detected,”
you do mark it degraded/partial in a deterministic way.
Handoff cycle attempt: simulate a model that tries to transfer back-and-forth; assert the cycle detector trips and termination classification is deterministic.
Regression harness extensions
You already have two strong harnesses:

Live probes: node scripts/run-agentic-quality-probes.mjs
Evidence: script exists and emits closure packet + trace table.
Incident regressions: bash scripts/verify-agentic-trace-grade.sh
Evidence: runbook + scripts exist and emit per-case JSON.
Expected gate movements

Before patch:
At least one L3 case fails with termination max_turns or tool_loop_detected (by definition of the incident corpus).
After hotfix:
L3 incident cases converge (or, at worst, become “degraded” but not “failed” in the regression grading).
After Manager migration:
The same cases converge with lower variance and fewer run-to-run drifts in tool counts.
Risk and rollback
Hotfix risks
Prompt text changes can inadvertently change tool selection frequency (models can over-call tools when told “must call transfer tool” unless the prompt is balanced). Mitigation: keep tool constraints in code, not just instructions.
Input filtering may reduce Narrator context too much if you “remove all tools” without adding a compact synthesis context. Mitigation: pass a minimal structured “tool receipts + computed values + key deltas” payload into the Narrator.
Rollback:

revert the handoff wrapping and prompt changes; your existing “deterministic fallback” mode in the API is already a safe escape hatch (useAgentic gating in apps/api/src/index.ts).
Manager-migration risks
Nested agent tools can introduce new failure surfaces (e.g., approvals or nested streaming edge cases). The SDK has active discussion on nested tool behaviors; treat nested approval flows as a risk area. 
Rollback:

ship Manager pattern behind an env flag; keep handoff path intact until the new regression gates are green.
Next actions
Evidence collection command pack
This is the fastest deterministic sequence to pin causality without “rabbit holes”:

Run incident regression gate (captures run_id ↔ openai_trace_id ↔ termination metrics):
bash
Copy
bash scripts/verify-agentic-trace-grade.sh
Evidence: docs/runbooks/agentic_trace_grading.md, scripts/verify-agentic-trace-grade.sh, scripts/agentic_trace_regression.mjs.

Run L1/L2/L3 live probes (captures closure packet + per-probe evidence + trace table):
bash
Copy
node scripts/run-agentic-quality-probes.mjs --strict=true
Evidence: scripts/run-agentic-quality-probes.mjs.

For any failing run_id produced above, pull full run ledger:
bash
Copy
curl -s http://localhost:8090/runs/<RUN_ID> | jq .
Evidence: /runs/:runId route in apps/api/src/index.ts.

Patch assignment-ready bead packet
You already created the epic and child beads (cie-2ej2, cie-1kqn, cie-39am, cie-2rh6, cie-ps0t) in your tracker conversation; the only “upgrade” I’d add is one explicit architecture decision bead:

New task: “Adopt Manager (agents-as-tools) orchestration for L3 mixed-domain”
AC:
Mixed-domain L3 uses manager + 2 specialist tools + manager finalization
No handoff loops possible in that path
Regression corpus passes for incident_a28 and incident_fb09
Verification:
bash scripts/verify-agentic-trace-grade.sh
node scripts/run-agentic-quality-probes.mjs --strict=true
Two high-friction blockers to resolve immediately
Trace corpus mismatch: your prompt mentions trace_2f7e..., but the repo’s official regression corpus includes trace_a28... and trace_fb09.... Add the missing trace case so the regression gate reflects reality.
Evidence: specs/agents/trace_regression_corpus.v1.json, docs/runbooks/agentic_trace_grading.md.

Stop treating “tool loop guard returned an envelope” as “agent looped.” Your tooling already distinguishes this; your termination semantics must match (successful completion cannot still be flagged as tool_loop_detected).
Evidence: loop guard tests in packages/agents/src/slb/run.test.ts and strict failure rules in scripts/run-agentic-quality-probes.mjs.