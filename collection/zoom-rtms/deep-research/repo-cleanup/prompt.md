# Research Prompt

**Date**: 2026-04-29
**Repository**: zoom-rtms
**Researcher**: Platform Engineering Team
**Priority**: high

## Research Question

Conduct a deep research pass on the Zoom RTMS repo to identify cleanup opportunities, cost-reduction opportunities, and areas that need attention before the project can be considered healthier and more maintainable.

## Context

The goal is to produce a practical, prioritized cleanup brief that helps the team decide what to fix, what to document, what to defer, and what to remove. The repo has undergone significant architectural evolution and needs a comprehensive audit of remaining technical debt.

## Scope

### Focus Areas
1. Reducing expensive AI / LLM usage
2. Identifying cost-reduction opportunities
3. Improving repo health and maintainability
4. Validating whether current cleanup plans match the repo's actual state
5. Producing clear, evidence-backed recommendations

### Research Questions

1. **What cleanup remains in the repo?**
   - Legacy `meetings` dependencies
   - Compatibility-only control surfaces
   - Deprecated aliases or bridge modules
   - Duplicated service boundaries
   - Stale docs or historical plans still referenced as current
   - Orphaned feature flags or environment variables
   - Old route names, misleading method names, or hidden compatibility behavior
   - TODO/FIXME/temporary comments
   - Code that contradicts the current project direction

2. **Where is expensive AI usage happening?**
   - OpenAI client wrappers, summarization, transcription fallback
   - Ask/search endpoints, artifact generation, prompt bundles
   - Schema extraction, map-reduce flows, dashboard intelligence
   - Backfill jobs, tests or scripts that may hit live AI accidentally
   - Repeated LLM calls where one canonical extraction could be reused
   - Missing cache / dedupe / idempotency around AI calls
   - Missing budget checks, cost telemetry, model routing

3. **What cost controls already exist, and are they enough?**
   - Monthly AI budget constants, alert thresholds, cost dashboards
   - Per-run manifest cost fields, token usage tracking
   - Bundle `cost_limit` policies, max token configuration
   - Retry/backoff behavior around OpenAI failures
   - Feature flags for summary / AI / pack generation

4. **What deterministic generation opportunities remain?**
   - Extract structured truth once, validate it, render deterministic artifacts in code
   - Reserve LLMs for style, synthesis, or communication outputs only when needed

5. **What repo health issues should be cleaned up?**
   - Test coverage gaps, flaky or skipped tests
   - CI/doc validation gaps, outdated scripts
   - Config drift between `.env.example`, schema, docs, and runtime
   - Inconsistent route naming, weak observability

## Expected Deliverables

- [x] Executive summary with overall assessment
- [x] Source-of-truth assessment with contradictions identified
- [x] Highest-priority cleanup findings table
- [x] Expensive AI usage findings with cost risk ratings
- [x] Cost controls and gaps analysis with recommended guardrails
- [x] Deterministic generation opportunities
- [x] Repo health findings
- [x] Prioritized cleanup plan (fix now / document / defer / remove)
- [x] Proposed PR plan with validation and rollback strategies
- [x] Open questions for team decision

## References

- [zoom-rtms repository](https://github.com/Biji-Biji-Initiative/zoom-rtms)
- Repo roadmap: `docs/roadmap/README.md`
- AI model registry: `docs/reference/ai-model-registry.md`
- Config schema: `src/config/schema.ts`
