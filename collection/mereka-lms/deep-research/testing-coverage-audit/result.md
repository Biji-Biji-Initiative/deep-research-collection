# Research Results

**Research Topic**: Testing Coverage Audit for Mereka LMS Production Readiness
**Date Conducted**: 2026-03-12
**Date Completed**: 2026-03-12

## Executive Summary

Mereka LMS has **strong "spec-to-evidence" governance** (testmaps, spec linting, spec coverage dashboards, and a large suite of verification scripts) and a **release-blocking post-deploy E2E gate** that checks five core user paths (Login, Enroll, Video, Forum, Certificate).

However, the repository's **test coverage posture for production readiness is uneven**:
- **Payment flow E2E coverage is absent** (explicitly out-of-scope for the post-deploy gate due to Oscar deprecation)
- The **purchase-gateway service has a meaningful unit/integration-style test suite**, but **it is not clearly executed nor coverage-enforced by the main PR CI job**
- The "Python test coverage" job uses a repo-root pytest configuration that defaults collection to `tests/` and is additionally **non-blocking** due to `continue-on-error`

**Critical production-readiness risks:**
- No end-to-end verification of the purchase/payment confirmation journey
- No CI gate that guarantees purchase-gateway tests run (or meet coverage thresholds)
- Limited true database-backed integration testing for purchase-gateway (tests largely use mocked `AsyncSession`)

---

## Testing Landscape and Current Inventory

### What Exists Today

The repo's "testing" spans multiple layers:

| Layer | Location | Description |
|-------|----------|-------------|
| Playwright E2E | `tests/e2e/` | Configured via `playwright.config.ts` |
| Purchase Gateway Tests | `services/purchase-gateway/tests/` | Unit and integration tests with `conftest.py` |
| Repo-root Python Tests | `tests/` | Configuration/fixture packs, tenant validation |
| Tutor Verification | `tests/tutor/` | Shell-based tests |
| Testmaps | `specs/testmaps/` | Curated testmaps (45 files) |
| Generated Testmaps | `specs/_generated/testmaps/` | Generated from `@covers` annotations |

### Core Playwright Spec Files

| Spec File | Purpose |
|-----------|---------|
| `tests/e2e/tests/critical-path.spec.ts` | Release-critical learner experience |
| `tests/e2e/tests/smoke-unauthenticated.spec.ts` | Public/unauthenticated surfaces |
| `tests/e2e/tests/branding-smoke.spec.ts` | Branding markers and theme assets |
| `tests/e2e/tests/selector-dom-audit.spec.ts` | Anti-regression contract for DOM selectors |

---

## Coverage Matrix Snapshot

| Area / Component | E2E (Playwright) | Unit Tests | Integration Tests | DB-Backed Tests | Spec/Testmap |
|------------------|------------------|------------|-------------------|-----------------|--------------|
| Core learner UX (login/dashboard/course/video/forum/cert) | **Yes** (post-deploy gate) | N/A | N/A | N/A | Yes |
| Purchase gateway (checkout/webhooks/fulfillment/admin) | **No** | **Yes** | **Yes** (endpoint-driven) | **No** (mocked AsyncSession) | Yes |
| Tutor config / patches | No | Shell tests | N/A | N/A | Yes |
| Multi-tenant tenant-spec parsing | No | Yes | N/A | N/A | Yes |

---

## End-to-End Test Coverage Assessment

### E2E Test Inventory and Journey Mapping

| Spec File | User Journeys Covered |
|-----------|----------------------|
| `critical-path.spec.ts` | Login, Enroll, Video playback, Forum rendering, Certificate rendering |
| `smoke-unauthenticated.spec.ts` | Public surfaces, basic reachability, branding shell |
| `branding-smoke.spec.ts` | Branding markers, theme assets, cross-browser verification |
| `selector-dom-audit.spec.ts` | DOM selector stability contract |

### Is the Complete Payment Flow End-to-End Tested?

**No** - There is **no evidence** that the full commerce journey (browse → cart → checkout → payment → confirmation) is covered by the production E2E gate or by the current Playwright "critical path" definition.

**Evidence:**
- Post-Deploy E2E Gate explicitly verifies five paths (Login, Enroll, Video, Forum, Certificate)
- **Oscar ecommerce is deprecated** and therefore not included in the critical path suite
- Purchase-gateway verification scripts exist (`verify-purchase-gateway*.sh`) but are not equivalent to a "learner-level" E2E purchase journey

**Production-readiness implication:** If Learner purchase is a production capability, the absence of a real payment E2E is a **high-severity gap** because it is exactly the type of cross-system regression (routing ↔ LMS ↔ purchase-gateway ↔ Stripe ↔ confirmation ↔ entitlement) that unit tests cannot fully protect.

---

## Purchase-Gateway Unit and Integration Testing Coverage

### What is Covered by Tests Today

| Test Area | File | Coverage |
|-----------|------|----------|
| Checkout route behavior | `tests/unit/test_checkout_route.py` | Unit tests |
| Rate limiting | `tests/unit/test_rate_limit.py` | Unit tests |
| Webhooks/fulfillment/admin | `tests/unit/` | Multiple test files |
| Checkout flow (endpoint-driving) | `tests/integration/test_checkout_flow.py` | Integration tests |

### Stripe Integration Testing

**Yes, but primarily via mocks:**
- Checkout flow tests patch `stripe` calls and validate API returns checkout URL/session ID
- Integration tests still mock Stripe and use dependency overrides
- **Not validated:** Real Stripe sandbox behavior, event signing, webhook delivery characteristics, idempotency at API boundary

### Are Database Operations Tested with Real Databases?

**No** - Database operations are **not exercised against a real database**:
- Tests override `get_db` and yield mocked `AsyncSession` objects
- Test infrastructure uses in-process ASGI transport (`httpx.ASGITransport(app=app)`)
- Keeps persistence and data integrity outside the test's scope

**Untested risks:**
- SQLAlchemy model constraints and migrations correctness
- Transaction behavior (commit ordering, rollbacks)
- Concurrency/race conditions around webhooks and fulfillment
- Real DB performance characteristics or serialization issues

### Unit Test Coverage Percentage

A numerical **coverage percentage cannot be determined from the repo state alone**:
- No committed coverage reports for purchase-gateway found
- PR CI coverage job is configured at repo root and is non-blocking
- Main repo-root pytest configuration collects tests from `tests/`, implying `services/purchase-gateway/tests/` may not run

**Current status:**
- **Not measured** as a required/visible gate
- **Not enforceable** (repo-root coverage job is explicitly non-blocking via `continue-on-error`)

---

## Testmap Completeness and Accuracy Audit

### Spec Coverage Statistics (as of 2026-02-18)

| Metric | Value |
|--------|-------|
| Total Specs | 38 |
| Acceptance Criteria | 976 |
| Overall Coverage | ~80.7% |
| Deployment-Critical Specs | 7/7 GREEN (≥80%) |

### Two Parallel Testmap Systems

| System | Location | Source |
|--------|----------|--------|
| Curated Testmaps | `specs/testmaps/…` | Manual curation, CI scorecards |
| Generated Testmaps | `specs/_generated/testmaps/…` | `@covers` annotations + verification entries |

### Testmap Accuracy Risk

The generation approach (`discover_testmap.py`) infers verification commands from file paths and defaults to `pytest <file>` for `.py` files. This can create "automation evidence" that is effectively an import/collection check rather than a functional test.

**Resulting risk:** Testmaps may be "complete" as a mapping artifact while overstating real executable test coverage.

### Key Takeaways

- Spec/testmap governance appears operationally mature
- But **spec coverage ≠ executable regression safety** unless referenced tests are:
  - (a) real tests
  - (b) run as blocking gates in relevant pipelines

---

## CI/CD Test Gates and Enforcement Analysis

### What Tests Run in CI on PRs?

| Job | Tests Run | Blocking? |
|-----|-----------|-----------|
| Static Validation | Verification scripts, spec coverage (`--fail-under 80`) | Yes |
| Tutor Configuration Tests | `tests/tutor/*.sh` suite | Yes |
| Python test coverage | `pytest --cov=. --cov-fail-under=40 -q` | **No** (`continue-on-error: true`) |
| Security scans | Various static checks | Yes |

### Coverage Thresholds

| Type | Threshold | Enforced? |
|------|-----------|-----------|
| Code coverage | 40% | **No** (non-blocking) |
| Spec coverage | 80% | **Yes** |

### Do E2E Tests Run on PRs?

**No** - PR CI does not run the full Playwright suite as a gate:
- Runs scripts like `verify-e2e-framework.sh` (wiring/structure checks)
- Actual release-blocking E2E happens in **post-deploy E2E gate** workflow
- Runs Playwright against live deployment and blocks release completion

**Production-readiness implication:** Bugs in critical learner flows can be detected only **after deployment**, which is a late feedback loop.

---

## Flakiness and Infrastructure Quality

### Pass Rate and Flakiness

| Aspect | Status |
|--------|--------|
| Flake quarantine registry | Present (`verification/baselines/FLAKE_QUARANTINE.yml`) |
| Tests currently quarantined | None |
| Computed flakiness index | Not included in repo artifacts |
| Reliability targets | "workflow success rate > 95%" stated as goal |

### Infrastructure Quality Observations

**Strengths:**
- Playwright supports cross-browser execution via environment toggles
- Post-deploy gate designed as release blocker with 30-minute timeout
- In-process ASGITransport client fixture for fast endpoint-level tests

**Gaps:**
- DB-backed integration tests not evidenced
- Integration tests override DB dependencies with mocked sessions

---

## Gap Analysis with Severity Ratings

### Severity Scale
- **P0**: Release blocker
- **P1**: High
- **P2**: Medium
- **P3**: Low

| Priority | Gap | Impact |
|----------|-----|--------|
| **P0** | No end-to-end payment flow testing | Cross-system regression risk for purchase journey |
| **P0** | Purchase-gateway tests not part of PR CI gating | Regressions can merge without test execution |
| **P1** | Code coverage gate non-blocking and low (40%) | Weak guardrail for production readiness |
| **P1** | Lack of real DB integration tests for purchase-gateway | Migrations, constraints, transactions unverified |
| **P2** | Spec coverage may overstate executable confidence | Generated testmaps may reference non-test modules |
| **P2** | No automated flakiness index in-repo | Metrics are policy/targets, not measured values |

---

## Prioritized Test Improvement Roadmap

### Immediate (P0/P1 - Before Next Production Release)

| Action | Details | Effort |
|--------|---------|--------|
| Add dedicated CI job for purchase-gateway | `cd services/purchase-gateway && pytest ...` with coverage report | Medium |
| Make purchase-gateway coverage blocking | Start with realistic floor, ratchet upward | Low |
| Establish payment confirmation E2E | Staging/sandbox Stripe environment | High |

### Near-term (P1/P2 - Next Sprint)

| Action | Details | Effort |
|--------|---------|--------|
| Introduce DB-backed integration tests | Containerized Postgres, run migrations in-test | Medium |
| Promote staging/preview E2E lane | Run `critical-path.spec.ts` on PRs for learner-facing changes | Medium |

### Medium-term (P2/P3 - Within a Quarter)

| Action | Details | Effort |
|--------|---------|--------|
| Validate testmap references | Ensure "automated" references point to runnable tests | Low |
| Add flake index artifact | "% of runs with retries/quarantine" in certification scorecard | Medium |

---

## Production Readiness Conclusion

### Strengths

- **Mature operational/spec governance**
- **Real release-blocking post-deploy E2E gate** for core learner flows
- Strong spec coverage tooling (80.7% overall, 7/7 deployment-critical specs GREEN)

### Critical Weaknesses

| Weakness | Risk Level |
|----------|------------|
| Missing payment journey E2E coverage | Critical |
| Non-blocking and incomplete purchase-gateway test execution in PR CI | Critical |
| Lack of DB-realistic integration testing for purchase-gateway | High |

### Bottom Line

Addressing the three critical items above would provide the **largest immediate improvement in regression safety per engineering hour invested**.

---

## Test Coverage Score

| Score | 6.5/10 |
|-------|--------|

**Rationale:** Strong governance and release gates, but critical gaps in payment E2E coverage and CI enforcement for purchase-gateway tests.

---

## References

- Playwright Configuration (`tests/e2e/playwright.config.ts`)
- CI Workflow (`.github/workflows/ci.yml`)
- Post-Deploy E2E Workflow (`.github/workflows/post-deploy-e2e.yml`)
- Purchase Gateway Tests (`services/purchase-gateway/tests/`)
- Spec Coverage Dashboard
- Testmap Registry (`specs/testmaps/`, `specs/_generated/testmaps/`)
- Flake Quarantine Registry (`verification/baselines/FLAKE_QUARANTINE.yml`)

## Appendix

### E2E Test Inventory

```
tests/e2e/tests/
├── critical-path.spec.ts        # 5 core learner journeys
├── smoke-unauthenticated.spec.ts # Public surface tests
├── branding-smoke.spec.ts       # Theme/branding verification
└── selector-dom-audit.spec.ts   # DOM selector contract
```

### Purchase-Gateway Test Structure

```
services/purchase-gateway/tests/
├── conftest.py                  # ASGI client fixtures
├── unit/
│   ├── test_checkout_route.py
│   ├── test_rate_limit.py
│   └── ...
└── integration/
    └── test_checkout_flow.py    # Endpoint tests (mocked DB)
```

### CI Coverage Configuration

```yaml
# Current (non-blocking)
- name: Python test coverage
  run: pytest --cov=. --cov-fail-under=40 -q
  continue-on-error: true  # Not enforced!
```

### Recommended CI Addition

```yaml
# Proposed (blocking)
- name: Purchase Gateway Tests
  run: |
    cd services/purchase-gateway
    pytest --cov=. --cov-fail-under=60 --cov-report=xml
  working-directory: services/purchase-gateway
```
