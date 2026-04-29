# Agent-E Repo Cleanup Research Report

## Executive Summary

- The biggest immediate cost problem is **incomplete cost attribution**: the repo persists `TokenUsage` for successful structured LLM completions, but the main embedding paths are outside that ledger, and failed parse/self-repair attempts are not persisted as usage. That means some of the most frequent and expensive AI work is only partially visible in budget summaries and dashboards.

- The **budget guardrail story is materially better than before, but still fragmented**. The dev proof shows run-scope and daily-scope alerting working after follow-up fixes, yet the runtime still mixes project-level hard budgets, per-run hard budgets, and multiple pause/override paths in a way that is easy to misunderstand and hard to verify. In particular, `PipelineRun.run_hard_budget_usd` exists, but the main execution paths inspected still compare against `Project.hard_budget_usd` in key places.

- The repo still carries **duplicate or overlapping orchestration surfaces**. There is a LangGraph executor bridge in `src/agente/graph/executor.py`, a separate V2 worker orchestration surface in `src/agente/workers/v2_run_worker.py`, and config still exposes legacy/fallback flags such as `V2_USE_LANGGRAPH` and `V2_ALLOW_BOOTSTRAP_LANGGRAPH_FALLBACK`. That directly contradicts one internal handover note that says the dual-path cleanup was already finished, which means code and docs are out of sync.

- The repo already contains some good cost-control primitives: a per-process OpenAI semaphore, a shared Redis rate bucket, batched chunk embeddings during document indexing, and an embedding cache for repeated evidence queries. Those are strong foundations, but they are not yet paired with stage-aware budgeting, full usage accounting, or result caching.

- The highest-leverage cleanup items are not cosmetic. They are: **wire true per-run enforcement to the actual execution path, account for every AI call including embeddings and failed retries, remove duplicate orchestration surfaces, and split or quarantine the large legacy vector/embedding layer**. Those changes reduce both spend and operational ambiguity.

- The most important production-readiness unknowns are still around **auth-disabled dev proof, concurrent resume/advisory-lock behavior, SSE replay completeness, and Postgres/RLS behavior hidden by SQLite-heavy tests**. The cost proof explicitly says live Authentik-token proof was not completed because dev runs with `V2_SKIP_AUTH=true`, and the lifecycle handover still calls out concurrent resume safety and SQLite masking as unresolved risks.

## Highest-Impact Cleanup Backlog

| Priority | Area | Finding | Evidence | Recommendation | Impact | Effort | Risk |
|---|---|---|---|---|---|---|---|
| P0 | AI cost accounting | Embedding calls and some failed LLM attempts are not fully reflected in `TokenUsage`; budget summaries therefore underreport true AI spend. | `TokenUsage` only stores prompt/completion/cost rows from `_record_token_usage`; embeddings are made in `vector_search` and indexing flows outside that path. | Introduce a single AI usage recorder for **responses + embeddings + retries + parse failures**; add stage/applicant/provider metadata. | Very high | M | Med |
| P0 | Budget enforcement | Per-run budget semantics are inconsistent: DB schema has `run_hard_budget_usd`, helper `check_run_cost()` exists, but create/execute paths inspected rely on project hard budget in important branches. | `PipelineRun.run_hard_budget_usd` exists; `check_run_cost()` exists; `RunsService` imports `check_daily_cost`; executor/worker compare against `Project.hard_budget_usd`; budget override mutates project budgets. | Make one source of truth: **run cap = `run_hard_budget_usd`**, project cap = cumulative org/project guard, daily cap = run-creation guard. Remove mixed comparisons. | Very high | M | High |
| P0 | Retry multiplication | Structured output self-repair, tenacity transport retries, SDK retries, applicant retries, and resume flows can multiply expensive calls; successful parse attempts are counted, but failed parse attempts are not durably attributed. | `StructuredLLMClient.complete()` performs self-correction; `_call_api()` does tenacity retries; SDK max retries are configured in the client wrapper; applicant retry settings are configurable. | Bound self-repair to one retry on expensive paths, persist usage per attempt, and surface retry counts in receipts/metrics. | Very high | M | Med |
| P0 | Runtime duplication | LangGraph execution exists in both `graph/executor.py` and `workers/v2_run_worker.py`, while config still exposes bootstrap/fallback flags and legacy bridges. | Dual execution files plus legacy flags remain; docs say removal already happened. | Collapse to one execution surface and delete or quarantine the other after end-to-end verification. | Very high | L | High |
| P1 | Model tiering | Model choice is global in `StructuredLLMClient`; `AgentConfig.model` exists in schema but the main evaluation path uses `config.LLM_MODEL` rather than per-stage or per-agent model selection. | `AgentConfig.model` exists; `StructuredLLMClient` always calls `config.LLM_MODEL`; evaluation code passes prompt/temperature, not model. | Wire model selection by stage: cheap triage/planning/extraction, premium only where justified. | High | M | Med |
| P1 | Dead or stale vector surfaces | `EmbeddingService` appears unused in-repo, and large parts of `VectorStoreAdapter` look like older program-details/applicant-embedding infrastructure rather than the V2 graph runtime. | Search hits only surface `EmbeddingService` in its own file; `store_program_details` is only found in `embedding_service.py` and `vector_store.py`. | Confirm no external caller depends on them, then remove or move behind `legacy/`. Keep only `_WeaviateCollectionAdapter` if still needed. | High | M | Med |
| P1 | Config sprawl | `config.py` is a large god-module with duplicate env declarations, auth/debug flags, runtime guards, fallback flags, and compatibility behaviors all mixed together. | `config.py` contains duplicated `V2_ALLOW_BOOTSTRAP_LANGGRAPH_FALLBACK`, both `SKIP_AUTH` and `V2_SKIP_AUTH`, and broad runtime-validation logic. | Split config into `ai.py`, `runtime.py`, `auth.py`, `ops.py`; remove retired flags after migration. | High | M | Low |
| P1 | Stale docs | Internal docs disagree with live code/config, especially around dual-path removal and active flags. | Handover says `V2_USE_LANGGRAPH` was removed; dev audit and cost proof still show it present and true; config still defines it. | Add a "canonical current runtime" doc and archive or mark contradictory handover notes as historical. | High | S | Low |
| P2 | Metrics drift | `llm_cost_usd_total` is defined, but the in-repo search surfaced the metric definition and dashboard/rule references rather than an emitter path. | Search only found metric declaration and observability assets. | Either emit it from the unified AI usage recorder or delete it from dashboards/rules. | Medium | S | Low |
| P2 | CSV ingestion cost | Multi-row CSV triage embeds each applicant row one-by-one with `_embed()` instead of batching with `_embed_batch()`. | Row loop in `triage.py` calls `search._embed(row_text)` for each created applicant; `vector_search.py` already has `_embed_batch()`. | Batch row embeddings and skip LLM triage for clearly structured CSV imports when deterministic parsing is enough. | Medium | S | Low |

## Expensive AI Usage Audit

The repo's AI spend comes from four main categories: document triage, document indexing embeddings, planning, and evaluation. The evaluation path is the dominant multiplier because it stacks applicant fanout, criterion/agent loops, evidence-query embeddings, optional red-team review, and retries. The code already tries to reduce this with batch-per-agent evaluation and query-embedding caching, but it does not yet pair that with durable per-attempt accounting or reusable result caching.

| Path | Trigger | Model/provider | Estimated cost multiplier | Current guardrails | Cleanup and cost opportunity |
|---|---|---|---|---|---|
| Document triage | Fresh runs with uploaded docs | Global `LLM_MODEL` via `StructuredLLMClient` / OpenAI-compatible provider | Roughly **1 LLM call per document** | Preview is capped at 2,000 chars; rate bucket + semaphore exist. | Cache triage by document checksum; bypass LLM for obvious CSV/TSV and known file classes. |
| Single-document indexing | Triage identifies applicant document and calls `extract_and_index()` | `EMBEDDING_MODEL` via batched embeddings | Roughly **chunks per document** | Uses `_embed_batch()` and idempotent delete-before-reindex in vector layer. | Skip re-index when checksum/object key unchanged; persist embedding usage and cost. |
| Multi-row CSV indexing | Triage marks CSV as applicant data | `EMBEDDING_MODEL` | Roughly **1 embedding call per row**, currently unbatched | Duplicate-email/name skips exist, but embeddings are still one-by-one. | Replace per-row `_embed()` with `_embed_batch()`, and do deterministic CSV classification before LLM where possible. |
| Planning | Fresh calibration path | Global `LLM_MODEL` | Typically **1 planning pass** plus any self-repair/retry | Standard LLM retry stack only. Handover note confirms planning is LLM-generated. | Introduce manifest-hash caching and cheaper planning model tier. |
| Calibration evaluation | Calibration run sample | Global `LLM_MODEL` + `EMBEDDING_MODEL` | Roughly **sample size x criteria/agents**, plus optional red-team pass | Default calibration sample is 3 in config; query embeddings are cached; some criteria can be batched per agent. | Add preflight estimate before run start; disable red-team in smoke mode unless explicitly enabled. |
| Full evaluation | Full run fanout over all applicants | Global `LLM_MODEL` + `EMBEDDING_MODEL` | Roughly **applicant count x criteria/agents x retries** | Fanout/concurrency configs, OpenAI semaphore, rate bucket, and agent-batch path exist. | Add budget-aware fanout, stop/skip unchanged applicants, and persist cost by applicant/node. |
| Red-team review | Only when red-team agent config exists | Global `LLM_MODEL` | **+1 extra LLM call per applicant** | Non-fatal if it fails, but still adds cost when enabled. | Make red-team opt-in per run mode or confidence threshold. |
| Self-repair and retries | Parse failures, transient transport failures, applicant retry loops | Same as above | Worst case multiplies a single logical call across several attempts | SDK retries, tenacity, self-correction, plus applicant retry count are all bounded. | Count every attempt, store retry metadata, and cap expensive self-repair harder than cheap stages. |
| Live proof and provider tests | Manual proof scripts and provider-certification cases | Real provider, not mock, unless env changed | Manual but potentially expensive and quota-sensitive | Mock provider exists; cost proof explicitly stopped reruns when preflight returned `insufficient_quota`. | Force opt-in markers/tags for any test that can spend live tokens. |

Two especially important cost-reduction opportunities stand out. First, the repo already stores `checksum_sha256` on documents and `prompt_hash` on token rows, but the execution paths inspected do not use those fields to skip unchanged AI work or replay cached outputs. Second, `AgentConfig.model` exists but the runtime still routes structured completions through one global model, so the repo cannot currently use a cheaper tier for triage/planning and reserve premium inference for borderline scoring or red-team review.

## Cost Guardrail Assessment

The repo has real guardrail components, and the latest dev proof shows meaningful progress. There is schema support for project soft/hard budgets, per-run hard budgets, and daily hard budgets; there are repository-level cost summaries; there are dedicated guard functions for run and daily caps; and there is a Prometheus counter for cap breaches whose labelsets are now pre-initialized to support `increase()`-based alerting. The dev proof explicitly records successful run-scope and daily-scope alert firing after fixing multiprocess export and zero-baseline initialization.

What is working is mostly **project-level cumulative guardrails and observability**, not a clean end-to-end per-run regime. `RunsService.create_run()` blocks new work when project hard budget or daily budget is already exceeded, and the LangGraph executor now does a pre-execution hard-budget check before graph invocation. But the inspected execution paths still mix project-level fields and run-level fields in ways that make the mental model harder than it needs to be. `create_run()` writes `run_hard_budget_usd`; the DB schema has a dedicated column for it; and `check_run_cost()` is implemented. Yet the main execution guard examined in `graph/executor.py` uses project cumulative cost against `Project.hard_budget_usd`, and `budget_override_resume()` mutates project-wide limits rather than resuming against a run-scoped override.

There is also a precision and attribution issue. Budget summaries aggregate only by project and run, while `TokenUsage` stores only model, prompt tokens, completion tokens, cost, and prompt hash. That means the repo cannot answer questions like "which applicant," "which node," "which provider," or "which retry pass" caused the breach. For a system whose dominant runtime cost comes from high-multiplier evaluation fanout, that attribution gap will become the main cleanup bottleneck the moment spend starts drifting upward.

The proof gaps are clear in the repo itself. The latest cost proof says live Authentik-token proof is still not proven because dev runs with `V2_SKIP_AUTH=true`, and provider preflight failures (`insufficient_quota`) prevented rerunning the fully LLM-backed proof in some cases. That does not invalidate the existing proof; it does mean the team should treat auth-enabled budget behavior and quota-exhaustion behavior as still requiring production-like verification.

| Scope | What exists | What has proof | What is still fragile or unproven | Recommended cleanup |
|---|---|---|---|---|
| Project hard budget | Create-time block and executor precheck | Proven in dev as visible pause/rejection behavior. | Mixed with run semantics; override path changes project budget. | Separate project cap from run cap in code and API. |
| Run hard budget | Schema field and helper exist | Unit-level helper exists. | Main runtime path inspected does not present a clean single run-budget enforcement story. | Make `run_hard_budget_usd` the enforced run budget at execution checkpoints. |
| Daily hard budget | Guard function and project setting field exist | Proven in dev through public APIs and alerting. | Only blocks new runs; no mid-run daily-budget logic. | Decide whether daily cap is create-time only or also a mid-run tripwire. |
| Metrics and alerts | `cost_cap_exceeded_total`, Prometheus rules, dashboards | Run and daily alerts proven after multiprocess and zero-baseline fixes. | Some metrics drift remains; `llm_cost_usd_total` appears undeployed in code paths inspected. | Wire unused metrics or delete them. |
| Auth-protected behavior | OIDC config, RBAC, route guards | Repo has auth scaffolding. | Live auth-enabled cost proof is explicitly unproven in dev. | Add one auth-on staging proof before production. |

## Dead Code and Legacy Surface Inventory

The repo's biggest cleanup signal is not just "old files exist." It is that **code, configuration, and docs still disagree about what the canonical runtime is**. That is exactly the kind of ambiguity that drives accidental spend and maintenance drag.

| Candidate | Location | Why it may be dead or stale | Safe to remove | Required proof before removal |
|---|---|---|---|---|
| Legacy bootstrap / fallback flags | `src/agente/config.py`, `src/agente/workers/v2_run_worker.py` | Config still defines `V2_USE_LANGGRAPH` and bootstrap fallback behavior even though internal handover says dual-path cleanup removed them. | Needs tests before removal | One passing end-to-end lifecycle run on the surviving path, including resume and budget pause. |
| Duplicate graph-execution surface | `src/agente/graph/executor.py`, `src/agente/workers/v2_run_worker.py` | Both execute LangGraph and apply overlapping budget/state logic. | Needs migration window | Decide canonical executor, then prove parity on retries, pause/resume, failure handling, and metrics. |
| `EmbeddingService` | `src/agente/services/embedding_service.py` | In-repo search only surfaced the class in its own file; no active call sites were found in the inspected repo. | Likely safe after owner check | Confirm no external jobs or scripts import it. |
| Program-details vector storage surface | `src/agente/services/vector_store.py` | Large parts of `VectorStoreAdapter` appear to support older program-details/applicant-embedding flows, while the active graph runtime uses `EvidenceSearchService` plus `_WeaviateCollectionAdapter`. | Needs owner decision | Trace imports and keep only shared adapter pieces still used by V2. |
| Duplicate approval flows | `RunsService.resume_run()`, `RunsService.approve_run()`, `budget_override_resume()` | The repo now has plan-approve, resume-approve, and budget-override-resume flows, which increases operator/API complexity. | Should remain but be simplified or documented | Decide whether approve and resume stay split or are collapsed behind one explicit workflow contract. |
| Stale runtime docs | `docs/casse/HANDOVER_NOTE.md` and related notes | The handover claims some removals already happened, but current config/dev proof still show the relevant flags live. | Safe to update now | Mark historical docs as historical and nominate one canonical runtime/status doc. |
| Unused cost metric | `src/agente/core/metrics.py` | Search surfaced definition/dashboard references, but not a clear emitter path in the code reviewed. | Safe to remove or implement | Pick one: wire it from unified AI usage accounting, or delete it from observability assets. |

## Test Gap Analysis

The repo has meaningful unit coverage around guard helpers and some contract coverage around cost endpoints. It also has provider-certification work that checks usage-shape integrity, which is valuable because the app depends on provider usage fields to build token/cost records safely. But those tests stop short of proving that the application itself records **all** AI spend under failure, retry, embedding, and resume conditions.

| Critical behavior | Existing coverage | Gap | Recommended test | Cost impact |
|---|---|---|---|---|
| Per-run and daily budget enforcement | Unit tests for `check_run_cost()` and `check_daily_cost()`; dev proof for run/daily alerting. | No tight E2E proof that **runtime execution** enforces `run_hard_budget_usd` consistently in graph path. | One app-level lifecycle test that seeds run budget, triggers graph execution, and proves pause/override/resume against the actual executor. | High |
| LLM call counting and attribution | Provider-certification T08 validates usage field shape. | No app-level assertion for parse-failure attempts, embedding calls, cancellations, or retries landing in durable cost records. | Add tests that deliberately force parse failure and assert all attempts plus embeddings are recorded. | Very high |
| SSE reconnect and replay | Live/frontend SSE specs and docs exist. | Internal handover still lists reconnect gaps; current dev proof focuses more on cost than replay correctness. | Add backend-level replay/cursor test and one auth-on browser test with `Last-Event-ID`. | Medium |
| Concurrent resume/advisory lock safety | Executor acquires advisory lock; handover names load testing as unresolved. | No evidence in the reviewed repo of a true concurrent stress test. | Run a targeted concurrency test that fires many resumes against one paused run and asserts one winner, clean losers. | Medium |
| Vector-store outage behavior | Dev audit explicitly marks Weaviate connectivity as a runtime risk. | No inspected test proving graceful degradation on indexing/search failure. | Add failure-injection tests for Weaviate unavailability during triage and evaluation. | High |
| Auth and RBAC under real runtime settings | Auth config and RBAC e2e surfaces exist. | Dev proofs run with `V2_SKIP_AUTH=true`; cost proof says live auth-enabled proof remains unproven. | One staging-only proof with skip-auth disabled. | High |
| Expensive live-AI test isolation | Mock provider exists; live provider-cert tests and live proof scripts also exist. | The repo needs stronger guarantees that live-AI specs cannot run accidentally in CI. | Gate all live-AI tests behind explicit marker/env and fail fast if not opted in. | Very high |
| SQLite masking Postgres/RLS behavior | Handovers and tests show SQLite-based coverage is common. | SQLite will not surface advisory lock, RLS, or some concurrency semantics. | Add a small Postgres-only contract suite for resume, idempotency, and budget events. | Medium |

## Recommended Cleanup Plan

### Phase One: Immediate cost/risk controls

| Action | Owner suggestion | Estimated effort | Files likely touched | Acceptance criteria |
|---|---|---:|---|---|
| Unify AI usage recording across responses, embeddings, retries, and parse failures | Backend platform | 1-2 weeks | `src/agente/graph/llm.py`, `src/agente/graph/vector_search.py`, `src/agente/graph/nodes/_shared.py`, `src/agente/services/v2/document_extraction.py`, `src/agente/db/models.py` | Every AI attempt produces durable usage rows with provider/model/stage metadata; dashboards and summaries include embeddings. |
| Make run-budget enforcement actually use `run_hard_budget_usd` in the execution path | Backend platform | 1 week | `src/agente/services/v2/cost_guard.py`, `src/agente/services/v2/runs_service.py`, `src/agente/graph/executor.py`, `src/agente/workers/v2_run_worker.py` | One E2E test proves per-run pause/resume against real executor semantics; project vs run vs daily caps are documented and non-overlapping. |
| Force live-AI tests to be explicit opt-in only | QA / DevEx | 2-3 days | Live proof scripts, provider-cert harness, frontend live e2e configs | CI cannot spend live tokens unless a dedicated env/marker is supplied; default test env uses mock provider. |

### Phase Two: Remove confusing legacy/dead surfaces

| Action | Owner suggestion | Estimated effort | Files likely touched | Acceptance criteria |
|---|---|---:|---|---|
| Collapse duplicate LangGraph execution surfaces to one canonical path | Backend platform | 2 weeks | `src/agente/graph/executor.py`, `src/agente/workers/v2_run_worker.py`, related dispatch code and route callers | One runtime path remains; duplicate budget/state logic is deleted; lifecycle and retry tests pass. |
| Remove or quarantine `EmbeddingService` and legacy vector-store program-details code | Backend platform | 3-5 days | `src/agente/services/embedding_service.py`, `src/agente/services/vector_store.py`, `src/agente/services/__init__.py` | In-repo import scan is clean; retained adapter surface is minimal and documented. |
| Simplify approval workflows | Product backend owner | 3-5 days | `src/agente/services/v2/runs_service.py`, route layer, API docs | One clear plan-approval workflow and one clear budget-override workflow; docs match UI and API behavior. |

### Phase Three: Improve tests and proof

| Action | Owner suggestion | Estimated effort | Files likely touched | Acceptance criteria |
|---|---|---:|---|---|
| Add app-level cost-accounting tests for failed parse, embeddings, and retries | QA / Backend | 1 week | `tests/services/v2`, `tests/graph`, provider-test helpers | Failing parse attempts and embedding-heavy flows produce expected usage rows and counters. |
| Add Postgres-only concurrency suite | QA / Platform | 1 week | `tests/e2e` or dedicated integration suite | Concurrent resume/advisory-lock behavior is proven on Postgres, not just SQLite. |
| Add vector-store outage and auth-on staging proofs | Platform / QA | 1 week | Runtime integration tests, staging proof scripts | One reproducible proof for Weaviate failure and one for auth-enabled run approval/budget flow. |

### Phase Four: Documentation and runbook alignment

| Action | Owner suggestion | Estimated effort | Files likely touched | Acceptance criteria |
|---|---|---:|---|---|
| Replace contradictory historical notes with a canonical runtime-status doc | Tech lead | 2-3 days | `docs/casse/HANDOVER_NOTE.md`, `reports/dev-truth-audit.md`, architecture/governance docs | One "current runtime truth" page exists; historical docs are marked historical. |
| Split `config.py` and retire legacy flags deliberately | Backend platform | 1 week | `src/agente/config.py`, startup validation, Helm/env docs | No duplicate flag declarations; deprecated flags have explicit removal timeline or are gone. |
| Align dashboards and emitted metrics | SRE / Platform | 2-3 days | `src/agente/core/metrics.py`, dashboards, alert rules | Every metric on the cost dashboard is actually emitted; dead metrics are removed. |

## Open Questions

The highest-confidence findings are based on the selected repo, its current code, and repo-local proof/docs. Anything that depends on external infra state should be treated as "repo-supported, runtime-dependent," not as a blind guarantee.

Questions that need explicit team decisions:

- Should **project hard budget** and **run hard budget** both remain first-class concepts, or should one be demoted to a derived control? The code currently suggests both, but the execution path is not cleanly separated.

- Is the older worker surface in `v2_run_worker.py` still required for any queueing/deployment path, or can it now be treated as retirement work?

- Does the team want **per-agent/per-stage model selection** as an explicit product capability, or is a global model acceptable for this release? The schema suggests model selection was intended.

- Which live-AI proofs are acceptable in CI versus manual/staging-only? The repo now has both mock-provider and live-provider surfaces, and that needs a hard rule.

## Final Recommendation

The five cleanup actions that should become tickets immediately are these:

1. **Implement a unified AI usage ledger** that records responses, embeddings, retries, parse failures, and applicant/node/provider attribution in one place. This is the single most important spend-control improvement because it fixes both visibility and budgeting.

2. **Refactor budget enforcement around one explicit policy model**: project budget, run budget, and daily budget should each have a single source of truth, with the executor path enforcing the same semantics that the API advertises.

3. **Delete or retire the duplicate orchestration surface** after one parity test suite passes. Keeping both `graph/executor.py` and `workers/v2_run_worker.py` alive is avoidable maintenance risk.

4. **Wire real model tiering and low-cost shortcuts**: use cheaper models for triage/planning/basic extraction, batch CSV row embeddings, and skip unchanged re-indexing/evaluation work using hashes.

5. **Replace contradictory historical docs with one canonical runtime document** and immediately mark the old handover notes as historical. At the moment, the repo itself makes it too easy to believe cleanup already happened when the code still shows otherwise.
