There are several high‑leverage items in that PDF that your 5‑sprint “Stop‑the‑line → runtime → wiring → grader → prompts” plan doesn’t fully cover yet. They’re mostly the things that make the system self-policing once you start “grinding” live API calls (so you don’t regress back into silent garbage again).

Below is what’s still not clearly addressed (or only partially addressed) relative to the PDF, and what to tell your coding agents to implement next.

⸻

1) Crash evidence → regression tests → CI gating pipeline

The PDF calls out a mechanical bridge from “runtime evidence” to “regression tests” to “CI gating” as the missing piece in most orgs. It specifically points at your .ntm/human_inbox/*_agent_crashed.md artifacts and says these should become structured fixtures/tests that fail until fixed.  ￼ ￼

What to implement:
	•	An ingestion script that parses every crash inbox entry into canonical JSON.
	•	Auto-generate “regression fixtures” (prompt + environment + last known run/trace IDs + expected failure_class).
	•	Wire these regressions into CI so new crashes automatically become failing tests until addressed.

This is not the same as adding eval-gate rules; it’s an “incident → test” conveyor belt.

⸻

2) Mandatory run/trace contract: {run_id, trace_id, group_id} everywhere

The PDF’s “definition of done” requires every externally-visible run to return and persist run_id + trace_id + group_id, and to propagate them across services.  ￼ ￼

It also requires every tool call and handoff to record structured linkage (tool_call_id, idempotency_key, evidence_refs, etc.).  ￼

Why this is still a gap vs your plan:
Your plan talks about graders + evidence bundles, but not the strict propagation contract and CI fail conditions for missing IDs. The PDF explicitly says runtime verification harness should fail CI when trace/run IDs are missing.  ￼ ￼

⸻

3) A single failure-envelope schema across API + worker + probes

Your plan addresses “status integrity” and “eval-gate outcome checks”, but the PDF goes further: every failure must conform to a single schema and be surfaced consistently everywhere.  ￼

It defines an explicit tool error envelope contract too (failure_class, retryable, blame, safe_message).  ￼

What’s missing:
A uniform “FailureEnvelope v1” contract that:
	•	is emitted by tools, runtime, probe harness, and API responses
	•	supports deterministic classification (so your graders/gates don’t depend on fuzzy string matching)

This directly prevents the “partial is normal” mindset by making every failure legible and categorizable.

⸻

4) Tool idempotency keys as a first-class invariant

The PDF demands idempotency keys derived from (run_id, step_id, tool_name, canonical_args_hash) for every tool call.  ￼

And it explicitly requires contract tests verifying idempotency behavior: “same key → no duplicate side effects.”  ￼

Why it matters for your current pain:
Once you start aggressive live probing (and retries), lack of idempotency makes it impossible to distinguish:
	•	“agent retried safely” vs
	•	“agent duplicated actions / produced inconsistent evidence”

⸻

5) Loop detection & stagnation protection (handoffs + repeated tool signatures)

Your plan has “tool repetition” checks in the grader, but the PDF explicitly requires handoff loop protection and stagnation metrics, with a regression test derived from a handoff-loop postmortem.  ￼ ￼

What to implement:
	•	Cross-run + intra-run loop detectors:
	•	repeated handoff edges
	•	repeated tool-call signatures
	•	stagnation (“no new evidence added”)
	•	A classified failure envelope: loop_prevented
	•	A synthetic regression that used to loop and now terminates bounded.

This is a core “agentic OS” protection—separate from answer-quality gating.

⸻

6) Feature flags + canary rollout mechanics for new behaviors

Your plan mentions hardening; the PDF mandates feature flags (default OFF) and a canary rollout sequence (internal → 1–5% → 25% → 100% only if thresholds remain green).  ￼ ￼

It even names suggested flags:
	•	agentsdk_runner_v2
	•	tool_guardrails_strict
	•	handoff_loop_protection
	•	trace_export_external  ￼

This is the post-implementation control plane you’ll want once you start grinding live calls.

⸻

7) Monitoring dashboards keyed by workflow_name/trace_id/run_id

Your plan has grading, but the PDF requires ops-grade dashboards:
	•	success rate and failure class trends
	•	“handoff loop prevented” events
	•	tool latency/error rate per tool
	•	model fallback rate + reason
	•	trace completeness (% of runs with trace IDs + exported spans)  ￼

This is how a world-class team keeps “we’re fine” from becoming another 14/14 mirage.

⸻

8) Evidence release automation

Your plan doesn’t explicitly include expanding the evidence release workflow, but the PDF does: publish run/eval summaries, trace links, tool schema inventory, regression catalog, crash trend charts.  ￼ ￼

This matters because it turns “trust us” into “here’s the evidence bundle”.

⸻

9) Machine-generated agent inventory (called out as “the missing piece to implement first”)

The PDF explicitly says: generate an agent inventory on every CI run:
	•	agent_inventory.files.json
	•	agent_inventory.symbols.json
	•	agent_inventory.deps.json  ￼

If you don’t do this, future analysis and maintenance drift back into guesswork.

⸻

10) Explicit 4-role agent operating model (Orchestrator / Tool Executor / Verifier / Recovery)

Your plan is largely “single pipeline with specialists + narrator + grader”. The PDF proposes a more “OS-like” separation:
	•	Orchestrator: bounded steps, loop limits, evidence growth rules
	•	Tool Executor: JSON-only outputs, idempotency keys, attaches evidence IDs
	•	Verifier: pass/fail + missing evidence list (actionable)
	•	Recovery: classifies failures, proposes smallest fix, generates regressions  ￼

Even if you don’t literally create four separate agents, the missing part is enforcing these behaviors/contracts in your current architecture.

⸻

11) Retry-layer separation + “background mode” for non-interactive probes

Your plan talks about runtime fixes, but the PDF wants strict separation:
	•	SDK/model retries (timeouts, 5xx, 429) with a per-run time budget
	•	tool retries with idempotency awareness
	•	workflow retries (Temporal) with explicit activity timeouts + retry policy  ￼ ￼

And it explicitly calls out using background mode for long tasks/probes.  ￼

That’s critical once you start high-volume probing and need predictable behavior under rate limits.

⸻

How this ties to the “large datasets” problem

The PDF doesn’t give a single “big dataset cookbook”, but it does define the key mechanism you need to handle big datasets safely:
	•	Tool Executor must return structured outputs and evidence IDs, not uncontrolled blobs.  ￼
	•	Tool registry contract is schema’d and designed for deterministic grading (so output must be shapeable).  ￼

The “normal” world-class strategy for big datasets in agent systems:
	1.	Tools never return the full dataset into the model context.
	2.	Tools return:
	•	a small summary (row count, date range, key aggregates),
	•	an artifact pointer/handle (receipt_id / dataset_id),
	•	and next-step affordances (e.g., “call tool again with filters/pagination/cursors”).
	3.	If analysis is heavy, do it inside the tool (compute aggregates), not in the LLM.

So: the doc implies the solution via contracts; your missing implementation is making your connectors and tool shaping enforce “summary + evidence refs” universally.

⸻

What to tell your coding agents: the “not yet covered” backlog

If your 5-sprint plan is already underway, add this as the next post-stabilization tranche (in roughly this priority order):
	1.	Crash→Regression pipeline (crash inbox ingestion + auto failing tests + CI gating).  ￼ ￼
	2.	Run/Trace contract + CI fail on missing IDs (run_id/trace_id/group_id + propagation + runtime harness).  ￼ ￼
	3.	FailureEnvelope v1 + tool error envelope standardization (failure_class/retryable/blame/safe_message).  ￼ ￼
	4.	Idempotency keys + contract tests.  ￼ ￼
	5.	Handoff loop & stagnation protection + regression.  ￼ ￼
	6.	Feature flags + canary rollout.  ￼ ￼
	7.	Dashboards + evidence release automation.  ￼ ￼
	8.	Machine-generated agent inventory (so future planning/debugging is “exact by construction”).  ￼

⸻
