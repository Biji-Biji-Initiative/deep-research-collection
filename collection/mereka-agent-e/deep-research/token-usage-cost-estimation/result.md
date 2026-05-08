# Agent E token usage, cache efficiency, and pre-run cost estimation

## Executive summary

Agent E already has the core building blocks for cost observability, but they are incomplete for production-grade cost control. The codebase has a `TokenUsage` table, per-run and per-project cost summaries, admin cost reporting, a pre-run assistant endpoint, and budget guards. It also centralizes several prompts with stable hashes and uses both a process-level OpenAI semaphore and a Redis-backed shared token/request bucket to avoid rate-limit storms. Those are strong foundations.

The main gap is that current "cost per run" is only partially measured. Successful structured LLM calls in triage, planning, evaluation, and pre-run assistant flows can be recorded, but the current schema only stores `prompt_tokens`, `completion_tokens`, `cost_usd`, `model`, `prompt_hash`, and timestamps. It does **not** store cached-token breakdowns, provider request IDs, phase/operation metadata, embedding token usage, or estimate-vs-actual metadata. The current cost math is also derived locally from a static pricing table rather than from provider billing fields.

The most important missing-cost risks in the inspected paths are embeddings, retry/fallback attempts, and likely red-team review usage. The vector search and document indexing paths call the embeddings API directly but do not write `TokenUsage` rows. The LLM client returns one usage object for the successful parsed response path, so validation retries and failed batch attempts are not fully represented in the current persistence model. In the visible red-team helper, the returned usage object is discarded, which makes that path at least a strong instrumentation risk and likely a real blind spot.

Prompt caching readiness is mixed. Agent E already puts system prompts before user payloads, which is directionally correct. But OpenAI prompt caching depends on **exact shared prefixes**, works only once prompts are long enough, and benefits when static content is placed before dynamic content. In several evaluation paths, the user payload begins with dynamic applicant- or criterion-specific fields before repeated boilerplate, which reduces the chance that the prompt's earliest shared prefix reaches the cacheable threshold. The app also does not persist `cached_tokens`, so it currently cannot verify whether caching is helping.

My recommendation is a phased rollout. First, fix measurement and pricing so actual usage is complete and trustworthy. Next, add a conservative, explainable estimator endpoint and UI card before run launch. Then optimize prompts, retrieval, batching, and gating so the estimate and the real spend both go down together. That sequence reduces the risk of shipping a polished pre-run cost estimate on top of incomplete underlying data.

## Current token and cost flow

At the data model level, `TokenUsage` is currently a lean ledger: `project_id`, nullable `run_id`, `model`, `prompt_tokens`, `completion_tokens`, `cost_usd`, `prompt_hash`, and `created_at`. That is enough for coarse per-run and per-project summaries, but not enough for cache accounting, phase-level attribution, or estimate-vs-actual analysis. `PipelineRun` already stores useful run-shape metadata such as mode, phase, bundle versions, `run_input_manifest`, and `applicant_snapshot_id`, which can be reused by an estimator.

In the inspected code, the high-confidence write paths for token cost are these: the shared `_record_token_usage()` helper in graph nodes, the worker-side `_record_token_usage()` helper, explicit `TokenUsage` creation in `generate_pre_run_assistant_draft()`, and the documented applicant-evaluation path in `evaluate_applicant_node`. Triaging documents records usage for each successful file classification call. Planning records usage for both evaluation-plan generation and decision-compiler agent generation. The pre-run assistant records usage against the project with `run_id=None`.

The run shapes are also clear. Calibration runs execute `triage -> planning -> approval_gate -> calibration -> finalize`, and calibration evaluates only the first `V2_CALIBRATION_SAMPLE_SIZE` applicants, with the default sample size set to `3`. Full runs execute `evaluation_fanout -> evaluate_applicant -> finalize`, and the fanout emits one subgraph send per applicant loaded from the project database. That means calibration cost is bounded mostly by document count plus three applicant evaluations, while full-run cost scales roughly with applicant count times per-applicant evaluation complexity.

Within applicant evaluation, the code already includes one important optimization: criteria can be evaluated in a single agent-batch call instead of one LLM call per criterion. The batch path gathers evidence for all criteria assigned to that agent, sends one structured batch request, and only falls back to per-criterion calls if that batch request fails. That batching is valuable, because without it the call count would explode with `applicants x criteria`.

Current cost visibility is split across run, project, and admin views. `ObservabilityRepository.run_cost_summary()` aggregates `TokenUsage` by `run_id`, while `project_budget_summary()` aggregates by `project_id` and also computes daily spend and remaining soft/hard budget headroom. Run summaries are built from those observability queries. The admin cost route already exposes summary aggregates by time window, model, and project. The project routes already expose a budget endpoint and the pre-run assistant draft route, but there is no dedicated pre-run run-estimate endpoint yet.

One subtle but important behavior is that `run_id=None` usage is handled differently from run-scoped usage. The pre-run assistant creates `TokenUsage` rows with `run_id=None`, project budget summaries include all project usage, and run summaries filter on a real `run_id`. So pre-run assistant spend is counted against project budgets but excluded from run summaries. That is internally consistent, but the product should make the distinction explicit in the UI and admin reporting.

## Missing instrumentation and data quality gaps

The biggest data-quality problem is that cost is only as complete as the call sites that remember to persist usage. The OpenAI client wrapper enforces concurrency and shared-rate limiting, and its distributed bucket uses a coarse request estimator for throughput control, but it does **not** centrally persist billing usage. That means call-site coverage determines observability completeness. The inspected graph and service paths handle some of that manually, but not all of it.

Embeddings are the clearest hard gap. `EvidenceSearchService._embed()` and `_embed_batch()` call `embeddings.create()`, and `extract_and_index()` uses the batched embedding path to index document chunks, but none of those inspected paths write `TokenUsage` rows. The same is true in the lower-level vector store adapter, which generates embeddings repeatedly during indexing and query generation without visible token persistence. If Agent E's retrieval layer is used heavily, run cost is currently understated.

Retry and fallback accounting is also incomplete. `StructuredLLMClient.complete()` retries structured output parsing internally, but the persisted usage model only captures the usage object returned on the eventual successful path. If a request is retried due to schema issues, or if a batch evaluation fails and the code falls back to per-criterion calls, the failed attempt cost is not fully represented in the current database model. That matters for a production estimator, because retries are not rare edge cases in structured-output systems.

The pricing layer also needs modernization. Current `_cost_usd()` uses a local prefix-match table with input and output rates only. It does not model cached input rates, embedding rates, or tool-specific fees, and one entry is suspiciously stale or misnamed: the code contains `gpt-5.4-nano`, while current OpenAI pricing pages document GPT-5.4 and GPT-5.4 mini, plus current cached-input pricing for supported models. This means `cost_usd` should be treated as an internal estimate rather than a faithful rendering of current provider billing.

Prompt-family attribution is only partial. The prompt registry is well-designed for centrally managed prompts and automatically hashes template text, but some important prompts are inline and unversioned from the registry's perspective. The triage system prompt is still embedded directly in `triage.py`, and generated agent prompts are persisted in `AgentConfig` but the evaluation paths deliberately record `prompt_hash=None` when an agent-specific prompt is used. That weakens prompt-family cost analysis, cache-family analysis, and regression tracking.

The current rate-limit estimator is not a good user-facing cost estimator. `estimate_openai_call()` walks request payloads and approximates token count mostly from text length, with a rough "1 token ~ 4 chars" heuristic plus output-budget additions. The tests confirm it is intended to be broad and protective for shared bucket admission, not precise for billing. OpenAI's own guidance says the reliable pre-flight path is tokenizer-based counting with `tiktoken`, while the "1 token ~ 4 characters" rule is just a rule of thumb. Reusing the current estimator is still useful, but only as a fallback or sanity-check layer.

## Cache readiness assessment

There is good news first: Agent E already tends to send a stable `system` prompt before a dynamic `user` payload, which aligns with OpenAI's recommended prompt-caching structure. Planning, pre-run assistant, criterion evaluation, agent-batch evaluation, and red-team review all follow that basic two-message pattern. That means the repo is not starting from zero.

But it is not actually "cache-optimized" yet. OpenAI prompt caching works on exact shared prefixes, becomes relevant for prompts of at least 1,024 tokens, and is improved when static content is placed before variable content. In `_evaluate_criterion()`, the user message begins with dynamic fields such as criterion name and applicant ID before the reusable scoring instructions. In `_evaluate_agent_batch()`, the user message begins with dynamic applicant-specific fields before reusable instructions and then appends large variable evidence blocks. Those placements reduce the shared prefix across repeated calls, especially when the system prompt itself is not long enough to carry the cached prefix over the 1,024-token boundary.

The application also cannot currently verify cache effectiveness because the schema has no place to store `cached_tokens` or related usage details. OpenAI exposes cached token counts through `usage.prompt_tokens_details.cached_tokens`, and recommends monitoring cached-token ratios directly. Today's `TokenUsage` model has nowhere to persist that. So even if caching is already happening automatically on supported models, the system has no durable evidence of it.

One other nuance matters: Agent E already has an **application-level embedding cache** for repeated embedding texts inside a worker process. That is helpful, but it is not the same thing as provider prompt caching, and it only applies to repeated identical embedding inputs in-process. It does not tell you anything about LLM cached input tokens, and it does not survive across processes or runs.

My assessment is therefore: **cache-capable, but not cache-observable and not yet cache-maximized**. The lowest-risk wins are to persist cache usage fields, hash all prompt families, and reorder evaluation payloads so the largest stable instruction blocks are placed before dynamic IDs and evidence whenever possible.

## Estimator design and data analysis plan

The estimator should be a dedicated service, not a thin wrapper around the Redis rate-limit estimator. I recommend `RunCostEstimatorService`, fed by deterministic run-shape inputs plus historical actuals. The deterministic layer should compute expected call counts by phase from run mode, applicant count, criteria count, agent count, retry mode, and red-team enablement. The statistical layer should pull historical medians and percentiles from `TokenUsage` grouped by run mode, phase/operation, model, and prompt family. The token-counting layer should use tokenizer-based counts for static prompt templates and bounded evidence slices, with the current char/4 estimator retained only as a fallback for unknown payloads.

The estimator response should return, at minimum: estimated input tokens, estimated output tokens, estimated total tokens, estimated cached-input tokens if the model supports it, low/expected/high USD ranges, per-phase call counts, major cost drivers, confidence, and budget-threshold implications. I would compute "expected" from a weighted blend of tokenizer-based prompt math and historical p50 actuals, "low" from a conservative p25/p50 lower envelope, and "high" from p90/p95 actuals plus retry uplift. Until real cached-token fields are persisted, cache savings should be shown as **potential** rather than folded into the base estimate.

For calibration runs, the deterministic part is straightforward because the graph and config bound the sample size. For full runs, the estimator should derive its base from `applicant_count x cost_per_applicant`, then add any fixed planning or run-start overhead that applies to the chosen entry mode. For retry-failed-applicants and single-applicant retry, the estimator should use the applicant count directly and exclude planning/triage if the run is not re-entering those phases.

The current schema already supports useful SQL analysis. The following query gives average run cost and token totals by mode from current data:

```sql
SELECT
  pr.mode,
  COUNT(*) AS runs,
  AVG(run_cost.cost_usd) AS avg_cost_usd,
  AVG(run_cost.prompt_tokens) AS avg_prompt_tokens,
  AVG(run_cost.completion_tokens) AS avg_completion_tokens
FROM pipeline_runs pr
JOIN (
  SELECT
    run_id,
    SUM(cost_usd) AS cost_usd,
    SUM(prompt_tokens) AS prompt_tokens,
    SUM(completion_tokens) AS completion_tokens
  FROM token_usage
  WHERE run_id IS NOT NULL
  GROUP BY run_id
) run_cost ON run_cost.run_id = pr.id
GROUP BY pr.mode
ORDER BY pr.mode;
```

The following query gives p50, p75, and p95 run cost by mode:

```sql
WITH run_cost AS (
  SELECT
    pr.id,
    pr.mode,
    COALESCE(SUM(tu.cost_usd), 0) AS cost_usd
  FROM pipeline_runs pr
  LEFT JOIN token_usage tu ON tu.run_id = pr.id
  GROUP BY pr.id, pr.mode
)
SELECT
  mode,
  percentile_cont(0.50) WITHIN GROUP (ORDER BY cost_usd) AS p50_cost_usd,
  percentile_cont(0.75) WITHIN GROUP (ORDER BY cost_usd) AS p75_cost_usd,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY cost_usd) AS p95_cost_usd
FROM run_cost
GROUP BY mode
ORDER BY mode;
```

Prompt leaderboard query (noting it will undercount inline/agent-specific prompts where `prompt_hash` is null):

```sql
SELECT
  COALESCE(prompt_hash, 'unhashed') AS prompt_family,
  model,
  COUNT(*) AS calls,
  SUM(prompt_tokens) AS prompt_tokens,
  SUM(completion_tokens) AS completion_tokens,
  SUM(cost_usd) AS cost_usd
FROM token_usage
GROUP BY COALESCE(prompt_hash, 'unhashed'), model
ORDER BY cost_usd DESC
LIMIT 50;
```

Once the schema is extended, cache effectiveness should be tracked with `SUM(cached_input_tokens) / NULLIF(SUM(input_tokens), 0)` by phase, model, and prompt family. Estimator accuracy should be reported from a new estimate snapshot table as absolute error, absolute percentage error, and signed bias by mode and estimator version. I recommend making p50 absolute percentage error the primary KPI.

## Backend implementation plan

The backend MVP should add a dedicated endpoint, `POST /api/v1/projects/{project_id}/runs/estimate`, and keep all mutating budget decisions authoritative in the existing run-creation and worker budget guards. The new endpoint should **warn** and explain; it should not replace the existing hard-stop logic in run creation and worker pause flows.

### Schema changes

I recommend these schema changes in a migration, keeping current fields for backward compatibility:

- `provider_request_id`
- `phase`
- `operation`
- `input_tokens`
- `output_tokens`
- `cached_input_tokens`
- `uncached_input_tokens`
- `cache_write_tokens`
- `cache_read_tokens`
- `estimated_input_tokens`
- `estimated_output_tokens`
- `estimated_cost_usd`
- `actual_total_tokens`
- `estimator_version`
- `metadata_json` for provider-specific details

Existing `prompt_tokens` and `completion_tokens` can continue to be populated for compatibility until summaries are migrated to the richer naming.

### Pricing registry

The pricing table should be moved out of `_shared.py` and `v2_run_worker.py` into a single pricing registry module (`src/agente/core/pricing.py`), with tests and a clearly updateable source-of-truth format. That registry should support input, cached-input, output, embedding, and tool-call fees, and should be able to version rates by effective date or model snapshot.

### Instrumentation

Keep `StructuredLLMClient.complete()` responsible for returning a rich usage object and provider request metadata for every successful provider response, and add dedicated usage-recording helpers that all graph/service paths must use. Then explicitly instrument embedding paths in `EvidenceSearchService` and document indexing.

### Phase/operation enums

Introduce explicit `phase` and `operation` enums. Good initial `operation` values: `triage_classify_document`, `planning_generate_plan`, `planning_generate_agents`, `evaluation_agent_batch`, `evaluation_single_criterion`, `evaluation_red_team`, `pre_run_assistant`, `embedding_query`, `embedding_index`.

### Metrics

Add Prometheus series: `agente_estimate_vs_actual_usd`, `agente_estimation_absolute_pct_error`, `agente_cached_input_token_ratio`, `agente_token_usage_total{phase,operation,model}`, `agente_run_estimate_budget_warning_total{threshold}`.

## Frontend, prompt, and rollout plan

The frontend is a Next.js application with React Query, Vitest, and Playwright already in place, which is a good fit for adding a cost-estimate card, threshold warnings, contract tests, and end-to-end coverage around run launch flows.

### Estimate card

The estimate card should appear on the calibration launch surface, the full-run launch surface, retry flows, and any pre-run assistant surface where the action itself can burn tokens. It should show:

- Expected cost and low/expected/high range
- Estimated token totals and call count by phase
- Cache assumptions
- Remaining project budget
- "Why this estimate" breakdown
- Extra confirmation step if estimate crosses soft/hard/daily thresholds

### Prompt optimization

1. Move reusable instructions ahead of dynamic applicant/criterion identifiers inside evaluation user payloads
2. Hash all prompt families, including inline triage prompts and persisted agent prompts
3. Introduce explicit evidence budgets: lower `top_k` from `10` and `8` where quality allows, deduplicate chunks, and cap total evidence characters/tokens per criterion/agent before the model call
4. Gate red-team review to trigger only when confidence is low, evidence provenance is weak, scores are near thresholds, or a manual-review/risk rule fires

### Rollout sequence

1. Ship instrumentation and pricing cleanup first
2. Ship estimator endpoint and UI card in "informational" mode
3. Run estimate-vs-actual tracking for a release window
4. Begin prompt and retrieval optimization behind flags, compare spend and quality against golden evaluation set

## Testing and acceptance criteria

### Test layers

1. **Unit tests**: Pricing lookup, estimator formulas, percentile blending, tokenizer math
2. **Contract tests**: New estimate endpoint response shape
3. **Migration tests**: New `TokenUsage` fields and backward compatibility
4. **Integration tests**: Every successful LLM and embedding phase writes usage rows
5. **Frontend tests**: Estimate card, threshold warnings, estimate-vs-actual rendering

### Acceptance criteria

- Users can see estimated tokens and USD cost before launching runs
- Estimate includes range, confidence, and cost-driver explanation
- UI warns on soft/hard/daily threshold risks before run creation
- Actual runs persist enough detail to calculate cache savings and per-phase cost
- Admins can break down cost by run, project, phase, model, and prompt family
- Estimate-vs-actual error is measured continuously (target: p50 APE below 25% after calibration window)
- Existing budget hard stops remain authoritative even when estimate is optimistic

### Open questions

- Not every frontend endpoint registry file or every direct OpenAI call site was fully inspected; frontend file-path plan is intentionally architectural rather than path-by-path
- Complete red-team caller chain and some retry paths beyond the visible helper logic were not fully inspected
- These are not blockers for MVP design but should be closed during Phase 0 before committing to baseline cost numbers
