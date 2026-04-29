# Research Prompt

**Date**: 2026-04-29
**Repository**: mereka-agent-e
**Researcher**: Platform Engineering Team
**Priority**: high

## Research Question

Identify what else needs to be cleaned up in the Agent-E repo, with special attention to reducing expensive AI/LLM usage, finding cost-reduction opportunities, removing dead code and stale compatibility layers, and improving overall project health, maintainability, reliability, and production readiness.

## Context

Agent-E is an AI-driven system for automating qualitative evaluation of program applications. The project has been migrating toward a V2 API-first architecture and LangGraph-based runtime. Existing internal research has already flagged several important areas:

- Large AI agent/runtime files and decomposition opportunities
- LLM API reliability, token accounting, retry/rate-limit behavior, and cost monitoring
- V1/V2 coexistence and legacy compatibility surface area
- Test coverage gaps, especially around real lifecycle, SSE, auth, concurrency, and budget enforcement
- Type safety, documentation, and production-readiness issues
- Budget guardrails that are partially or recently proven in dev, but still need cleanup-oriented review

## Scope

### 1. Expensive AI Usage Patterns
- All paths triggering LLM, embedding, retrieval, or AI-agent execution
- OpenAI/AI provider calls, embeddings, vector indexing
- Applicant fanout multiplication of LLM calls
- Calibration, retries, reprocessing, resume, or full runs duplicating AI work
- Token usage accounting across success, failure, retry, cancellation, partial completion
- Prompt/context construction with unbounded content
- Cache vs recompute behavior
- Model selection (cheap vs expensive) configuration
- Dry-run, preview, validation, smoke, or test paths accidentally using live AI

### 2. Cost Guardrails and Observability
- Per-run soft/hard budget behavior
- Daily budget behavior
- Budget approval/resume flow
- Metric emission for run and daily budget breaches
- Token/cost attribution by project, run, applicant, node, and provider
- Provider preflight and quota exhaustion behavior
- Auth-disabled dev proof gaps
- Multiprocess metrics reliability

### 3. Dead Code, Legacy Paths, and Cleanup Opportunities
- Removed/obsolete flags in code, docs, tests, CI, Helm, or scripts
- Legacy runtime paths, bootstrap paths, compatibility harnesses, fallback logic
- Dead models, fields, schemas, env vars, scripts, migrations, or docs
- Duplicate execution paths and approval/resume/budget override flows
- Mock-only pathways hiding production behavior
- SQLite test fallbacks hiding Postgres/RLS/concurrency bugs
- Stale docs describing removed runtime behavior

### 4. Project Health and Maintainability
- Large files/modules needing splitting
- Circular imports or unclear module boundaries
- Services or graph nodes with too many responsibilities
- Missing or weak tests on critical paths
- Type safety gaps
- CI quality gates
- Helm/Kubernetes/deployment drift
- Observability docs vs actual implementation

### 5. Reliability and Production-Readiness Risks
- Retry loops around LLM calls, parsing, structured output repair, document indexing, fanout
- Circuit breakers, rate limiting, backoff
- Cancellation, partial failure, resume/idempotency behavior
- Concurrent resume or approval safety
- SSE reconnect/event replay behavior
- Vector store outage behavior
- Stuck-run recovery
- Alerting for cost, queue backlog, worker failure, provider failure

## Expected Deliverables

- [x] Executive summary with top findings
- [x] Highest-impact cleanup backlog (prioritized P0-P3)
- [x] Expensive AI usage audit with cost multipliers and guardrails
- [x] Cost guardrail assessment (working / unproven / fragile)
- [x] Dead code and legacy surface inventory
- [x] Test gap analysis with recommended tests
- [x] Phased cleanup plan with effort estimates and acceptance criteria
- [x] Open questions for team decision
- [x] Top 5 immediate ticket recommendations

## References

- [mereka-agent-e repository](https://github.com/Biji-Biji-Initiative/mereka-agent-e)
- Internal handover notes: `docs/casse/HANDOVER_NOTE.md`
- Dev truth audit: `reports/dev-truth-audit.md`
- Cost proof documentation from prior dev cycles
