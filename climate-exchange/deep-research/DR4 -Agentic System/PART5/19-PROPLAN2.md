Large datasets: what’s “normal” and what the right strategy is

Big datasets are absolutely normal in agentic systems—but the normal strategy is not “return the whole dataset to the model and hope it reads it.” The standard pattern is:
	1.	Tools compute; models reason.
Put aggregations, joins, ranking, and statistical summaries in the tool layer (DB/query engine), not in the model’s context.
	2.	Return “summary + pointer,” not “rows.”
Tool responses should be small and structured:
	•	row_count, date_range, coverage, top_k, key percentiles
	•	receipt_id / evidence IDs
	•	artifact_ref / dataset_ref (pointer to the full result stored elsewhere)
	3.	Use “index → drill-down” flows.
Make the agent call:
	•	dataset_profile(...) first (returns summary + ref)
	•	then dataset_slice(ref, filters, limit, offset) or dataset_aggregate(ref, metric, group_by)
This converts “giant blob” into a multi-step investigation that fits token limits.
	4.	Enforce token discipline explicitly.
Context windows are finite, and tool definitions + tool outputs contribute to what the model must carry. That’s why OpenAI’s docs emphasize counting/controlling tokens and using context reduction techniques (compaction) when needed.  ￼
	5.	For truly large blobs, use files/retrieval—don’t paste.
The OpenAI platform supports passing content as files and using retrieval mechanisms (e.g., File Search) so you don’t shove giant content directly into the conversational context.  ￼

What’s missing in many brittle implementations (and what your traces scream) is that tools are acting like “dump CSV,” when they should act like query services that return compact evidence + pointers.

⸻

Is “large dataset handling” defined in your deep research PDF?

The PDF you uploaded is strongly aligned with the right direction because it repeatedly pushes toward:
	•	a standard tool response envelope
	•	evidence refs / artifacts
	•	crash inbox artifacts → regression probes
	•	observability via trace/run IDs
	•	and hard gates / verification harness behavior

But it does not fully spell out a concrete “big dataset contract” (e.g ￼ng, slice/aggregate tools). It gestures at the artifact/evidence approach, which is the right foundation—you still need to implement the “summary + pointer + drilldown tools” pattern explicitly.

That’s “more work” beyond the earlier 5-sprint stabilization plan unless you already added it under “tool shaping / artifact refs.”

⸻

Your “Ruthless Teardown” is directionally correct—and yes, planning should explicitly include it

That teardown is valuable because it reframes the problem correctly:
	•	Model non-determinism is not a bug; it’s a fact of life.
	•	Therefore “the model must call finalize_response” is a wish, not an invariant.
	•	World-class systems make finalization code-guaranteed, not model-guaranteed.

Even if you keep an orchestrator agent, a world-class approach is:
	•	Orchestrator decides tools + plan
	•	Tools run
	•	Code always runs a finalizer step (narrator/finalize agent or deterministic reducer), even if the orchestrator “forgets.”
	•	If finalization doesn’t happen, it’s a runtime invariant violation in dev mode and blocks the harness.

Your teardown’s proposed instrumentation like finalize_response_called and “if tools succeeded but finalize wasn’t called → FATAL” is exactly the kind of explicit observability + gating that prevents silent rot.

This is also consistent with the OpenAI platform emphasis on tracing/verification as first-class parts of agentic development.  ￼

⸻

What else from the PDF is not clearly addressed in your sprint plan (and you should still do)

Below are the highest-leverage gaps I would call “world-class fundamentals” that often remain undone after the first stabilization sprint set. These are all themes the PDF emphasizes (or implies) but your earlier 5-sprint plan only partially covers.

1) A true “Tool Contract” that prevents big outputs by design

You already talked about 2KB caps and shaping—but the missing piece is the  ￼:
	•	Every tool returns:
	•	summary (bounded size)
	•	receipt_id (or explicit error envelope)
	•	artifact_ref (pointer to the full dataset)
	•	stats (row counts, date ranges, coverage)
	•	And you provide paired drilldown tools (slice, aggregate, topk, explain) so the agent never needs raw dumps.

This is the real fix for “agent can’t read the tool output.”

2) A “crash → regression” pipeline (crash inbox → new probe automatically)

If a bad run happens in dev/prod, the system should:
	•	capture the trace + evidence bundle + failure class
	•	automatically create a new repro probe fixture
	•	add it to the probe suite so it never regresses again

This is a huge multiplier on engineering effort and is one of the fastest ways world-class teams drive reliability.

3) Release engineering: feature flags + canary + auto-rollback tied to probe suite

Even after stabilization, you will keep changing prompts/tools/models.

World-class teams:
	•	ship behind flags
	•	run a canary slice of traffic or scheduled probe suite
	•	rollback automatically on SLO/probe failure

4) Observability that answers “why” in <5 minutes

Not just “PASS/FAIL”.

You want dashboards/queries for:
	•	failure class distribution (planning leak, missing finalize, tool empty-success, receipt mismatch)
	•	tool health (error rate per connector)
	•	tokens per tool response (or proxy metrics)
	•	latency breakdown (tool time vs model time)
	•	cost per run + per probe

And all of this keyed by run_id / trace_id / group_id so you can click through from “red metric” to “the trace”.

5) Policy-as-code for retries/fallbacks/circuit breakers

Instead of “random retries happen,” define:
	•	bounded retries per tool/error class
	•	fallback model strategy (dev vs prod)
	•	tool circuit breaker when upstream is failing

⸻

“Post-stabilization” plan: what a world-class team does next (deep, implementation-oriented)

Assuming you truly completed the earlier stabilization work (hard gates, status integrity, deterministic grader, fixed recovery/finalization paths, connector wiring), here’s the next 5-sprint sequence I’d hand to coding agents.

⸻

Sprint 6 — Big Data Contract + Artifact-First Tools

Objective: Make it impossible for large datasets to enter model context unbounded.

Deliverables
	1.	New Tool Response Envelope (mandatory)
	•	ok: boolean
	•	summary: string (bounded)
	•	stats: { row_count, date_range, bbox?, units?, … }
	•	receipt_id: string (or error: { code, message })
	•	artifact_ref?: { type, id, uri?, expires_at? }
	2.	Artifact store
	•	Store full result payloads (DB table, blob store, filesystem cache—whatever you already use)
	•	Return only refs to the model
	3.	Drilldown toolset
	•	dataset_profile(ref)
	•	dataset_slice(ref, filters, limit, offset)
	•	dataset_aggregate(ref, group_by, metrics)
	•	dataset_topk(ref, sort_by, k)
	4.	Default limits
	•	Hard default limit=200 rows where relevant
	•	Always return aggregates before raw rows

Acceptance tests
	•	Any tool that can return “lots of rows” demonstrates:
	•	profile works
	•	slice works
	•	aggregate works
	•	summary stays below your size budget
	•	Add a probe that previously caused failures due to volume and verify it passes reliably.

⸻

Sprint 7 — Crash-to-Regression Automation

Objective: Every failure becomes a test within minutes, not a repeated incident.

Deliverables
	1.	Crash Inbox
	•	A directory/DB table that stores failing run bundles: inputs, tool calls, outputs, failure class, trace IDs
	2.	Auto-probe generator
	•	Convert a crash bundle into:
	•	a new probe entry
	•	expected failure class (until fixed)
	•	then flip expectation to PASS once fixed
	3.	Pass^k reliability runs
	•	Nightly: run core probe suite with k=3 (or more)
	•	Track reliability drift over time

Acceptance tests
	•	Trigger one known failure intentionally → it lands in crash inbox → generates a new probe automatically.

⸻

Sprint 8 — Production-Grade Observability + SLOs (Quality, Latency, Cost)

Objective: You can answer “what broke?” and “what changed?” immediately.

Deliverables
	1.	Dashboards:
	•	probe pass rate (PASS/FAIL/FATAL) + pass^k
	•	failure taxonomy histogram
	•	tool health per connector
	•	latency breakdown
	•	tokens + cost per run
	2.	Alerts:
	•	FATAL in canary → stop rollout
	•	tool error rate spikes → circuit breaker triggers
	•	cost anomaly (run cost jumps) → block
	3.	Trace correlation enforced:
	•	run_id/trace_id/group_id always present

Acceptance tests
	•	You can pick any failed run from the dashboard and navigate to:
	•	evidence bundle
	•	tool outputs (by artifact refs)
	•	trace

⸻

Sprint 9 — Release Engineering: Feature Flags + Canary + Auto Rollback

Objective: You can ship changes daily without risking system-wide regressions.

Deliverables
	1.	Feature flags for:
	•	model choice
	•	prompt versions
	•	tool shaping behavior
	•	fallback behaviors (dev strict vs prod degrade)
	2.	Canary flow:
	•	1% traffic (or scheduled canary probes)
	•	promote to 10% / 50% / 100% only if probe suite is green
	3.	Auto rollback:
	•	if probe pass rate < threshold OR FATAL occurs → revert flag set automatically

⸻

Sprint 10 — Agent Platform Hardening

Objective: Make the system maintainable with more tools, more agents, and more people.

Deliverables
	1.	Generated agent inventory
	•	Enumerate all agents, tools, prompts, versions, owners
	•	Build a “what changed?” report from git diffs
	2.	Tool contract test harness
	•	Every tool has:
	•	schema test
	•	error envelope test
	•	output size test
	•	idempotency test (if relevant)
	3.	Runbooks
	•	“If probe fails with X, do Y”
	•	“How to reproduce a run from artifacts”
	•	“How to add a new tool safely”

⸻

When you start “grinding through live API calls”: how to run it like a world-class team

This is the operational playbook I’d give your agents.

1) Start with canary probes, not random user traffic
	•	Run the core probe suite every N minutes (e.g., 15–30)
	•	Add “connector health probes” that only hit tools (no synthesis), to isolate tool outages early

2) Enforce a stop-the-line budget
	•	If FATAL triggers:
	•	automatically switch system to “dev strict block” (or halt canary rollout)
	•	open an incident ticket with trace IDs + failure class + last-good commit SHA

3) Make failures self-serve for engineers

Every failure report should include:
	•	run_id / trace_id / group_id
	•	failure class (taxonomy)
	•	which invariant fired
	•	tool calls list + artifact refs
	•	replay command (one-liner)

4) Convert incidents into probes immediately
	•	“No incident closes until a regression probe exists.”

5) Track reliability as a product metric
	•	pass^k over time (not pass@k)
	•	SLOs per probe tier (L1-L2 must be ~perfect, L5-L6 can be lower early)
	•	cost/run and latency/run budgets

⸻

Pasteable message to your coding agents

If you want something you can drop straight into your coordination channel:

“Team: Post-stabilization roadmap (next 5 sprints). We’re moving from ‘works once’ to ‘operates reliably.’
Sprint 6: Big Data Contract + artifact-first tools (summary + receipt_id + artifact_ref; add dataset_profile/slice/aggregate tools; enforce default limits).
Sprint 7: Crash-to-regression pipeline (crash inbox → auto probe generator; nightly pass^3).
Sprint 8: Observability + SLOs (dashboards for failure taxonomy/tool health/latency/cost; alerts; trace correlation always).
Sprint 9: Release engineering (feature flags + canary + auto rollback tied to probe suite).
Sprint 10: Platform hardening (generated agent inventory; tool contract test harness; runbooks).
Definition of done: any failure is reproducible in 1 command, traceable in <5 min, and becomes a regression test within the day.”

⸻

If you tell me what stack you’re using for artifact storage (Postgres blobs vs S3/Minio vs filesystem) and whether you want the dataset tools backed by SQL or by your existing snapshot store, I can tighten Sprint 6 into very concrete file-by-file tasks.