# Research Prompt

**Date**: 2026-05-08
**Repository**: mereka-agent-e
**Researcher**: Platform Engineering Team
**Priority**: high

## Research Question

Investigate Agent E token usage, prompt/cache efficiency, and pre-run cost estimation. Understand how many tokens Agent E burns per run, whether prompts and cache usage are optimized, and whether the UI can show the expected token/cost burn before a user launches calibration or full evaluation.

## Context

Gurpreet asked us to understand cost-per-run behavior and propose an implementation plan that lets users see estimated token usage and estimated USD cost before starting a run, while also improving actual token/cost efficiency through prompt optimization and prompt caching. This is a production-facing cost, UX, observability, and reliability task.

## Scope

### Relevant Repo Areas
1. **OpenAI client and rate limiting**: `src/agente/core/openai_client.py`, `src/agente/core/openai_rate_limiter.py`
2. **Token/cost persistence and pricing**: `src/agente/db/models.py` (TokenUsage), `src/agente/graph/nodes/_shared.py` (_MODEL_PRICING, _cost_usd, _record_token_usage), `src/agente/workers/v2_run_worker.py`
3. **Existing cost visibility**: `src/agente/api/v1/routes/cost_admin.py`, `src/agente/api/v1/routes/projects.py` (budget, pre-run-draft endpoints)
4. **Prompt and graph execution**: `src/agente/graph/prompts.py`, `src/agente/graph/llm.py`, `src/agente/graph/nodes/`

### Research Questions
- **Current usage and cost-per-run**: All TokenUsage write paths, per-phase token generation, pricing accuracy, cost scaling factors, missing usage rows
- **Cache effectiveness**: Prompt caching readiness, stable prefix ordering, cached token storage, cache effectiveness metrics
- **Token optimization opportunities**: Largest/most frequent prompts, evidence context reduction, model tiering by phase, retry reuse, deterministic fallbacks
- **Cost estimator requirements**: Pre-run estimation of tokens/cost/ranges, budget threshold warnings, support for calibration/full/retry/single-applicant modes

## Expected Deliverables

- [x] Executive summary with cost flow assessment
- [x] Current token and cost flow map
- [x] Missing instrumentation and data quality gaps
- [x] Cache readiness assessment
- [x] Estimator design and data analysis plan with SQL queries
- [x] Backend implementation plan (RunCostEstimatorService, schema extensions, pricing registry)
- [x] Frontend implementation plan (estimate card, threshold warnings)
- [x] Prompt/cache optimization plan
- [x] Testing plan and acceptance criteria
- [x] Phased rollout plan (instrumentation -> estimator MVP -> optimization -> calibration loop)

## References

- [mereka-agent-e repository](https://github.com/Biji-Biji-Initiative/mereka-agent-e)
- OpenAI prompt caching documentation
- OpenAI pricing documentation
- Existing cost admin routes: `src/agente/api/v1/routes/cost_admin.py`
- Existing budget endpoints: `src/agente/api/v1/routes/projects.py`
