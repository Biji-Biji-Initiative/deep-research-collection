# Zoom RTMS Repo Cleanup Research Brief

## Executive Summary

The repo's cleanup work is no longer mostly about broad structural uncertainty. The current codebase already has a clear canonical roadmap and a fairly well-governed doc structure, but the remaining drag is concentrated in four places: compatibility-only meeting control surfaces that are still on the runtime path, extra LLM calls that should be eliminated or downgraded, cost-control modules that exist but are not actually enforced in the main pipeline, and stale scripts/docs that no longer match the current manifest and AI configuration contracts.

The biggest near-term savings opportunity is straightforward: keep one canonical LLM extraction pass, then deterministically render downstream artifacts. Right now, `summary_json`, `summary_md`, and `actions_csv` are separate generation paths, which means the repo is still paying for multiple AI transformations over material that is already structured after the first pass. That is the highest-confidence cost reduction available from the code inspected.

The existing cost architecture is directionally good but operationally incomplete. There is a canonical model registry, a bundle-level `cost_limit`, a budget module, analytics that read `runs.cost_microusd`, retry/circuit-breaker behavior around the OpenAI client, and explicit live-test opt-ins. But the monthly budget guard appears to be isolated in telemetry/tests rather than wired into the active pipeline, and pricing/model references are currently drifting across modules. That means the repo can report some cost numbers without being able to reliably prevent or explain a spike.

My overall recommendation is to treat cleanup as one focused program with three concrete goals: make downstream artifacts deterministic, wire hard budget enforcement into every runtime and operator-triggered AI path, and remove or quarantine stale compatibility/script surfaces that can still confuse engineers or accidentally spend money. The roadmap already points in that direction; the repo state suggests the team is close, but not finished.

## Source-of-Truth Assessment

The repo does have a usable source-of-truth hierarchy. `docs/roadmap/README.md` explicitly names the Meeting OS Closeout Roadmap as the canonical execution plan for the rewrite and the Meeting Admin Compatibility Removal Roadmap as the canonical follow-on cleanup plan. It also explicitly marks older execution docs as historical. That governance is a strength, not a weakness.

In practice, the best current source-of-truth set is: the roadmap index and closeout docs for program intent, `src/config/schema.ts` and `src/config/index.ts` for runtime configuration truth, and `src/ai/models.ts` plus `docs/reference/ai-model-registry.md` for the intended AI model contract. The AI registry doc even states that if docs and code differ, code is authoritative.

The main contradictions are not in the roadmap layer; they are in configuration and operational docs. `.env.example` and `docs/platform-guide/configuration.md` still describe the AI setup primarily in legacy `OPENAI_*` terms, while runtime code has already moved to a shared `AI_*` contract with `OPENAI_*` as fallback. The platform guide also says `ALLOW_UNAUTH_WEBHOOKS` defaults true in development, while the runtime config sets the unauthenticated-webhooks default to false and treats bypass as opt-in. That drift is exactly the kind of repo-health issue that creates operator mistakes.

A second useful reality check: the "bounded compatibility-only residual" described by the roadmap is real. The runtime still imports `legacyMeetingControlService` from `dashboardMeetingCommandService`, so the compatibility cleanup plan is not hypothetical. At the same time, one legacy area has progressed further than the repo narrative might suggest: `_legacy.ts` is already not mounted from the dashboard route index, which means it is now reference-only dead code and can move from "careful migration" to "delete/archive."

## Highest-Priority Cleanup Findings

| Priority | Area | Finding | Evidence | Impact | Recommendation |
|---|---|---|---|---|---|
| P0 | AI artifact generation | `summary_json`, `summary_md`, and `actions_csv` are still separate AI generation paths rather than one extraction followed by deterministic rendering. | `src/os/artifacts/builtins/summary-json.ts`, `summary-md.ts`, `actions-csv.ts`. | High recurring AI cost and duplicated failure surface. | Keep `summary_json` as the canonical LLM extraction; render markdown and CSV in code. |
| P0 | Budget enforcement | The budget module exists, but repo search shows `checkBudgetBeforeGeneration` only in telemetry/docs/tests, not the active runtime pipeline. | `src/os/telemetry/budget.ts` plus search hits only in telemetry/index/README/tests. | High. Costs can be observed but not reliably blocked. | Wire budget checks into generate, ask, backfill, and regeneration paths with fail-closed behavior. |
| P0 | Stale operator CLI | `src/os/cli/regen-artifact.ts` appears out of contract with current `ManifestV2`: it references old-style fields like `runId`, `outputs`, and `transcript`, while the current manifest shape uses `run.id`, `artifacts`, and `inputs.transcript`. | `src/os/cli/regen-artifact.ts` vs `src/os/manifest/manifest.ts` and `manifest.schema.json`. | High. This script is both misleading and capable of direct AI spend. | Quarantine immediately: either refactor to current contracts or remove from supported tooling. |
| P1 | Compatibility control surface | `dashboardMeetingCommandService` still relies on `legacyMeetingControlService` for ACL, visibility, and auto-open mutations. | `src/os/policy/dashboardMeetingCommandService.ts`, `src/os/policy/legacyMeetingControlService.ts`. | Medium-high. It is bounded debt, but still hot-path debt. | Keep this as an explicit cleanup PR set, not a vague "later" item. |
| P1 | Dead legacy route code | `src/app/routes/dashboard/_legacy.ts` still contains `/api/slo` and old cost endpoints, but `src/app/routes/dashboard/index.ts` says the legacy mount was removed. | `_legacy.ts` and route index. | Medium. It adds confusion without runtime value. | Delete or move to a clearly archived path. |
| P1 | Config/documentation drift | Runtime supports `AI_*` precedence and defaults unauthenticated webhooks to false, but `.env.example` and the configuration guide still center legacy `OPENAI_*` flows and describe different defaults. | `.env.example`, configuration guide, config schema/index. | Medium. Increases operator error and migration confusion. | Update docs/examples to the runtime contract now. |
| P2 | Duplicate service boundaries | `packages/core` contains parallel AI/generation abstractions that do not appear to be used by app runtime code beyond package exports/tests. | `packages/core/src/ai/generators/summaryJson.ts`, `packages/core/src/pipeline/stages/generate.ts`, search for `createSummaryJsonGenerator`. | Medium-low, but it raises maintenance overhead and model-contract drift risk. | Decide whether `packages/core` is strategic; if not, archive or collapse duplicate logic. |

## Expensive AI Usage Findings

| Priority | Path | Pattern | Cost Risk | Recommendation | Validation |
|---|---|---|---|---|---|
| High | `src/os/artifacts/builtins/summary-json.ts` | Canonical structured extraction uses an LLM and is the right place for the one "truth extraction" pass. | High, but justified | Keep it, but make it the only extraction pass and aggressively reuse its output. | Compare downstream artifacts before/after renderer refactor for semantic parity. |
| High | `src/os/artifacts/builtins/summary-md.ts` | Second LLM pass converts already-structured summary data into markdown. | High | Replace with deterministic markdown templates generated from `summary_json`. | Golden-file tests on existing summary markdown outputs. |
| High | `src/os/artifacts/builtins/actions-csv.ts` | LLM-generated CSV from structured summary/action context. | High | Replace with deterministic CSV serialization from canonical action items. | Snapshot CSV tests using known `summary_json` fixtures. |
| High | `src/os/cli/regen-artifact.ts` | Direct OpenAI calls with transcript payloads, local cost math, and outdated manifest assumptions. | High | Refactor behind shared runtime wrapper with budget/cost telemetry, or archive. | Run against one known manifest fixture after contract update. |
| High | `scripts/backfill-local.ts` | Bulk summarization path with concurrency and only local cost estimates using `gpt-4o`-era assumptions. | High | Default to dry-run, enforce shared budget checks, and route through the same cost recorder as normal pipeline runs. | Dry-run plus one-meeting live validation under explicit budget cap. |
| Medium | `src/os/intelligence/dashboardSearchService.ts` | "Ask" endpoint synthesizes answers with an LLM over retrieved meeting/action/decision context. | Medium | Add cheaper-model routing for simple questions, stronger rate limits, and cost attribution per request. | A/B on answer quality and token usage using current dashboard tests. |
| Medium | `src/os/pipeline/stages/transcribe.ts` | Whisper STT fallback is available when higher-priority transcript sources are missing; cost is a real but opaque fallback spend. | Medium | Make fallback conditions stricter and persist STT cost into run telemetry. | Long-media test with fallback path and cost persistence assertions. |
| Medium | `src/os/pipeline/stages/generate.ts` | Generation stage still hard-codes legacy model usage instead of fully routing through the canonical model-role registry. | Medium-high | Replace ad hoc model strings with `MODELS.standard` / `MODELS.premium` routing and one shared pricing source. | Manifest/model/cost integration test covering selected bundles. |

## Cost Controls and Deterministic Opportunities

**Existing controls.** The repo already has several legitimate cost-control building blocks: a canonical model registry and pricing table, bundle-level `cost_limit` declarations, a runtime budget module, analytics that aggregate `runs.cost_microusd`, a configurable `OPENAI_MAX_ASK_TOKENS`, retry plus circuit-breaker behavior in the OpenAI wrapper, and explicit live-test opt-ins via `VITE_LIVE` and `OPENAI_LIVE`. These are good foundations and show the repo is not starting from zero.

**Missing or weak controls.** The biggest gap is enforcement. The budget checker is not clearly connected to the active generate path, so budget policy appears advisory rather than fail-closed. Cost telemetry is also too coarse for debugging a spike: analytics aggregate run cost by model, but that is not the same as attributing spend to artifact type, endpoint, or operator script. There is also pricing drift between the canonical AI model registry and the telemetry cost tracker, which undermines confidence in cost reporting. Finally, operator-triggered paths such as `backfill-local.ts` and `regen-artifact.ts` either roll their own cost behavior or bypass the normal runtime controls altogether.

**Recommended guardrails.** First, require every LLM call to go through one metered wrapper that records model, input/output tokens, artifact or endpoint name, and cost. Second, use one canonical pricing source only. Third, enforce three budget levels: per-call caps, per-run caps, and daily/monthly budget caps; all three should be able to block or downgrade work rather than merely log it. Fourth, apply the same rules to operator CLIs and backfill/replay paths, not just web-triggered paths. Fifth, make non-production default to `AI_PROVIDER=mock` unless a live flag is explicitly set. These recommendations are an engineering inference from the current mismatch between strong cost intent and incomplete runtime wiring.

**Deterministic generation opportunities.**

| Artifact / Flow | Current State | Recommendation | Expected Cost Impact |
|---|---|---|---|
| `summary_json` | Should remain LLM-generated; this is the canonical extraction layer. | Keep as the one extraction pass; add stronger caching/reuse guarantees. | Medium savings downstream, not by deleting this call itself. |
| `summary_md` | Currently LLM-generated from already-structured content. | Should become deterministic. | High |
| `actions_csv` | Currently LLM-generated even though CSV is a deterministic rendering target. | Should become deterministic. | High |
| Follow-up email artifacts | Stylistic communication output; currently one of the cleaner uses for LLMs. | Should remain LLM-generated, but only from canonical structured inputs and with lower-cost default models where acceptable. | Medium |
| Dashboard ask responses | LLM synthesis over retrieved context, not a core artifact. | Unclear; keep LLM for free-form questions, but avoid invoking it for obvious lookup-only queries. | Medium |
| Manifests, analytics aggregates, routing outputs | Already deterministic by design. | Keep deterministic and do not regress. | Protects against cost creep |

## Repo Health Findings

| Area | Finding | Recommendation |
|---|---|---|
| Runtime/config hygiene | `policy-engine.ts` still reads ClickUp list IDs from `process.env`, bypassing normalized config patterns in `src/config/index.ts`. | Move all env access behind `CONFIG` and add a drift test. |
| Dead code | `_legacy.ts` is retained but unmounted. | Delete or archive immediately. |
| Stale tooling | `regen-artifact.ts` appears contract-stale; `backfill-local.ts` still contains TODO-level upload behavior and outdated cost assumptions. | Either modernize and support them, or archive them and remove from normal operator guidance. |
| Documentation drift | `.env.example` and the configuration guide lag runtime behavior on AI contract and webhook defaults. | Update docs in the same PR as config/AI cleanup to stop new drift from reappearing. |
| Duplicate implementation footprint | `packages/core` mirrors generation/AI concepts that are easy to drift away from `src/os` runtime implementations. | Decide whether package extraction is active. If not, reduce duplicated surfaces. |
| Positive governance signal | Historical execution docs are explicitly labeled historical, which reduces accidental execution from stale plans. | Preserve this governance discipline while shrinking stale runtime/doc surfaces. |

## Cleanup Plan and Proposed PR Plan

**Fix now.** Convert `summary_md` and `actions_csv` to deterministic renderers. Wire the budget module into the generate path, dashboard ask path, and operator-triggered AI paths. Quarantine or refactor `regen-artifact.ts`. Update config/docs to the shared `AI_*` contract and current webhook defaults. Replace hard-coded or duplicated model/pricing references with the canonical registry.

**Document.** Explicitly document that the remaining meeting-control compatibility layer is intentional debt with bounded scope, and document which AI paths are allowed to run live in non-prod only by explicit flag. Also document the rule that downstream artifacts must be deterministic whenever the repo already has canonical structured inputs.

**Defer intentionally.** If `packages/core` is still a real extraction effort, keep it but add a clear owner and drift policy. If not, do not spend cleanup energy on making both `packages/core` and `src/os` equally polished; collapse one of them. Also defer broader historical-doc grooming beyond the canonical roadmap/docs mismatch items, because the repo already marks many old docs responsibly.

**Remove or archive.** Remove `_legacy.ts` from active repo surfaces, and archive unsupported operator tools that are contract-stale rather than allowing them to look usable. If `backfill-local.ts` is no longer a supported workflow, archive it too; if it is supported, it belongs under the same guardrails as the production pipeline.

**Proposed PR plan.**

| Title | Scope | Affected files | Risk class | Validation command | Rollback plan |
|---|---|---|---|---|---|
| Make downstream artifacts deterministic | Replace LLM use in markdown/CSV renderers with code templates/serializers | `src/os/artifacts/builtins/summary-md.ts`, `src/os/artifacts/builtins/actions-csv.ts`, related tests | Medium | `npx vitest run test/**/*.test.ts --reporter=dot` with targeted snapshots added for summary/CSV outputs | Re-enable previous generators behind a temporary feature flag if formatting regressions appear |
| Enforce AI budgets in every runtime path | Wire budget checks and shared metering into generate, ask, backfill, and regeneration | `src/os/telemetry/budget.ts`, `src/os/pipeline/stages/generate.ts`, `src/os/intelligence/dashboardSearchService.ts`, `scripts/backfill-local.ts`, `src/os/cli/regen-artifact.ts` | High | `npx vitest run test/budget.test.ts test/intelligence/dashboardSearchService.test.ts test/**/*.test.ts` | Keep report-only logging mode behind a flag for one release if fail-closed behavior is too disruptive |
| Unify model and pricing references | Remove hard-coded/duplicated pricing/model tables and use canonical registry everywhere | `src/ai/models.ts`, `src/os/telemetry/cost-tracker.ts`, `src/os/pipeline/stages/generate.ts`, `src/os/cli/regen-artifact.ts` | Medium | `npx vitest run test/ai-provider-resolution.test.ts test/**/*.test.ts` | Restore previous pricing table if historical-cost rendering breaks, then patch with converter |
| Delete dead dashboard legacy route | Remove reference-only V1 route file and update any docs that still imply it is live | `src/app/routes/dashboard/_legacy.ts`, dashboard docs if needed | Low | `npx vitest run test/**/*.test.ts` plus a targeted route smoke test | Reintroduce file from git history if any forgotten route dependency exists |
| Fix config/doc drift | Align `.env.example` and config docs with runtime `AI_*` contract and current webhook defaults | `.env.example`, `docs/platform-guide/configuration.md`, possibly `docs/reference/ai-model-registry.md` | Low | Run the repo's docs validation workflow and `npx vitest run test/config.test.ts test/regression/config-validation.test.ts` | Revert docs-only changes if operator rollout requires phased wording instead |

## Open Questions

The highest-confidence findings above are based on the repo files inspected directly, not an exhaustive audit of every prompt bundle or every artifact generator. The deterministic-opportunity list is therefore strong for the fetched generators, but not a full inventory of every possible downstream renderer.

Two strategic questions should be answered before doing deeper cleanup. First, is `packages/core` an active extraction/public-package effort or just a partial mirror of runtime code? Second, are `backfill-local.ts` and `regen-artifact.ts` still supported operator workflows, or are they effectively abandoned? The right action differs sharply depending on those answers.

Production usage data was not inspected, so spend share across dashboard "ask," STT fallback, artifact generation, or operator-triggered scripts cannot be quantified. The prioritization of cost savings is based on code-path duplication and guardrail gaps, not on observed billing telemetry. That means the direction is high confidence, while the exact dollar ranking still needs one production cost sample.
