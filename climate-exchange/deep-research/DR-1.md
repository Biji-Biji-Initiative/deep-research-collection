# DR-1: CIE-SLB-V1 Production-Readiness Review (Trust Core + Runtime Truth)

## Audience

Engineering agents and maintainers hardening CIE into a production trust system (runtime truth first).

## Prerequisites

- Ability to run local gates: `make check-fast`, `make verify-runtime-required`, `make verify-ci`
- Familiarity with verified-mode invariants (receipt-gated truth) and SSE stream contract
- Access to deployment logs and live endpoints (for validation)

## How to Use

1. Treat **P0 gaps** as certification blockers (green gates must not be possible while the system is broken).
2. For each gap, create or update a bead with:
   - explicit invariants
   - deterministic failure injection
   - a release-blocking gate target
3. Validate improvements against:
   - local runtime gates
   - live site probes (saved runs health, artifact fetchability)

## Troubleshooting

- If a runtime gate is “green but suspect”, add a **negative (sabotage) test** that must fail.
- If verify runs are flaky/slow, split into PR-fast vs nightly-deep and keep PR gates hermetic.
- If verified-mode behavior seems ambiguous, resolve it in spec and enforce via validator + smoke test.

## Change Log

| Date | Change |
|------|--------|
| 2026-02-15 | Initial DR-1 drafted from reviewer findings and ongoing hardening work |


## Executive Summary

This report summarizes the highest-risk production-readiness gaps found during a trust-first audit. The emphasis is: **runtime truth > docs**. Any condition that allows “green gates while broken” is treated as a P0 issue.

## What’s Already Strong

- Formal certification spine: scorecard + verification strategy matrix that prefers runtime evidence over grep-only proofs.
- Evidence pack concept: hashed artifacts with semantic verification of results (not just log capture).
- CI gate design intent: infra bootstrap + migrations + canary + runtime harness with time budgets.

## P0 Gaps (Certification Blockers)

### 1) Verified-mode leak (fail-open sequencing)

**Risk:** user-visible “final” content emitted or persisted before evidence verification completes.

**World-class invariant:**
- In verified mode, no `assistant_final` is emitted or persisted unless evidence verification is OK.

**Required proof:**
- deterministic failure injection to force evidence verification failure
- negative runtime test: failure => no `assistant_final` emitted; stream terminates with structured error (`debug_id` present)

### 2) SSE truncation contract mismatch (blob pointer)

**Risk:** large payload paths break under load; streaming becomes nondeterministic or unverifiable.

**World-class invariant:**
- if truncation happens: `tool_result_truncated: true` and a pointer to the full payload (canonical field name), preserving receipt/artifact pointers

**Required proof:**
- synthetic that forces truncation, asserts the exact pointer field + preserved provenance

### 3) Receipt signing trust fails open (dev fallback key)

**Risk:** misconfigured production can still “verify” receipts using a publicly guessable dev key.

**World-class invariant:**
- production/verified contexts refuse to start or refuse to sign unless key policy is satisfied
- verifier never accepts dev fallback outside explicitly labeled demo modes

**Required proof:**
- key policy gate in CI and/or release certification
- negative test: missing/unsafe key => contract failure

### 4) Run replay “smoke” passes without asserting correctness

**Risk:** replay can be broken while required-runtime gate is green.

**World-class invariant:**
- replay tests are assertion-backed, include negative case, and verify the stable error envelope

### 5) /health is not truthful for readiness

**Risk:** “ok:true degraded” masks dependency outages, causing canaries to proceed in broken states.

**World-class invariant:**
- separate liveness vs readiness semantics
- readiness fails closed when Postgres/MinIO/Redis are not usable (bounded-time probes)

## P1 Gaps (Trust Completeness)

- Receipt layering and derivability (tool + answer + run receipts; `event_log_hash`).
- Audit-grade provenance fields carried end-to-end (dataset identity hashes/etags, license metadata, pin identity where applicable).
- Verified-mode streaming should not leak “final truth” prior to verification; if streaming deltas exist, they must be labeled unverified until verified.

## Recommended Sequencing (High-Leverage)

1. Replace replay smoke with contract-grade assertions + negative test.
2. Enforce receipt signing key policy by environment; forbid dev fallback.
3. Add truncation synthetic enforcing the blob pointer contract.
4. Make verified-mode sequencing provably fail-closed (stream + persist paths).
5. Make readiness probes truthful and wire gates to readiness.

## Validation on Live Site

Minimum live probes for “not embarrassing” production posture:

- `GET /health` (or `/ready`) must reflect dependency truth
- saved run library runs: status `succeeded` + `ledger_validation.ok:true`
- artifact URIs must be public, fetchable, and must not contain `localhost` or private IPs
