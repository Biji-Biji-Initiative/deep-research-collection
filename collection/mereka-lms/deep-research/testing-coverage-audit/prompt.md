# Research Prompt

**Date**: 2026-03-12
**Repository**: mereka-lms
**Researcher**: Mereka Team
**Priority**: high

## Research Question

Conduct a comprehensive testing coverage audit for Mereka LMS production readiness with detailed coverage assessment and gap analysis.

## Context

Mereka LMS has E2E tests (Playwright) in tests/e2e/, unit and integration tests in services/purchase-gateway/tests/, and testmaps in specs/testmaps/. The CI workflow runs tests on PRs but coverage enforcement is unclear. This audit will assess testing completeness and identify gaps before public launch.

## Scope

### Primary Files (Must Read)

- `tests/e2e/` - E2E test suite (Playwright)
- `tests/e2e/playwright.config.ts` - Playwright configuration
- `tests/e2e/tests/critical-path.spec.ts` - Critical path E2E tests
- `tests/e2e/tests/smoke-unauthenticated.spec.ts` - Smoke tests
- `tests/e2e/tests/branding-smoke.spec.ts` - Branding tests
- `tests/e2e/tests/selector-dom-audit.spec.ts` - DOM audit tests
- `services/purchase-gateway/tests/` - Purchase gateway tests
- `specs/testmaps/` - Test mapping files (45 files)
- `.github/workflows/ci.yml` - CI workflow configuration

### Secondary Files (Should Review)

- `tests/tutor/` - Tutor-related tests
- `tests/tenants/` - Tenant tests
- `services/purchase-gateway/tests/conftest.py` - Test fixtures
- `specs/ci-cd-pipeline_spec.md` - CI/CD specifications

### Discovery Patterns

- Files matching `**/*.spec.ts` - All Playwright tests
- Files matching `**/test_*.py` - All Python tests
- Files matching `**/*.testmap.yml` - Test mapping files

### Discovery Commands

```bash
# Count all test files by type
find . -name "*.spec.ts" | grep -v node_modules | wc -l
find . -name "test_*.py" | grep -v node_modules | grep -v ".git" | wc -l

# List all E2E tests
ls -la tests/e2e/tests/

# Find test coverage configurations
find . -name "pytest.ini" -o -name "coverage" -type d -o -name ".coverage" | grep -v ".git"

# Check for integration tests
find services/ -path "*/tests/integration*" -name "*.py" | head -20

# List testmaps
ls specs/testmaps/*.testmap.yml | wc -l

# Find unit tests in purchase-gateway
ls -la services/purchase-gateway/tests/unit/
```

## Assessment Points

### 1. E2E Test Coverage

Are critical user journeys covered by E2E tests?

**Why it matters:** E2E tests verify the system works as users expect. Missing critical path coverage means regressions reach production.

**How to evaluate:** Map user journeys to E2E tests, identify gaps, review test quality (assertions, flakiness).

**What good looks like:**
- All critical user journeys covered (login, enroll, complete lesson, payment)
- Stable tests (95%+ pass rate)
- Meaningful assertions

**Red flags:**
- Missing critical paths (payment flow, enrollment)
- Flaky tests
- Tests without assertions
- No cross-browser testing

**Questions to answer:**
- What user journeys are covered by E2E tests?
- Is the payment flow end-to-end tested?
- What's the test pass rate and flakiness index?
- Are there tests for error scenarios?

### 2. Unit Test Coverage

Is unit test coverage adequate for critical services?

**Why it matters:** Unit tests catch bugs early and enable confident refactoring. Low coverage increases regression risk.

**How to evaluate:** Run coverage analysis on purchase-gateway and other services, identify uncovered critical paths.

**What good looks like:**
- >80% coverage for critical services
- All payment logic tested
- Error handling tested
- Edge cases covered

**Red flags:**
- Coverage <60% for critical services
- Payment logic untested
- No error handling tests

**Questions to answer:**
- What's the coverage percentage for purchase-gateway?
- Are Stripe integration flows tested?
- Is error handling tested?
- What code paths are not covered?

### 3. Integration Test Coverage

Are integration tests comprehensive for service interactions?

**Why it matters:** Integration tests catch issues that unit tests miss. They verify services work together correctly.

**How to evaluate:** Review integration test suite, check database integration tests, verify API tests.

**What good looks like:**
- Database integration tests
- API integration tests
- External service mocks
- Test containers for isolation

**Red flags:**
- No integration tests
- Tests share mutable state
- No database tests
- External services not mocked

**Questions to answer:**
- What integration tests exist in purchase-gateway?
- Are database operations tested with real databases?
- Are external APIs (Stripe) mocked or tested against sandbox?
- Do tests clean up after themselves?

### 4. Test Infrastructure Quality

Is test infrastructure robust and maintainable?

**Why it matters:** Poor test infrastructure leads to slow, unreliable tests. Good infrastructure enables fast feedback.

**How to evaluate:** Review Playwright config, check test fixtures, verify CI integration.

**What good looks like:**
- Fast test execution (<5 min for unit, <15 min for E2E)
- Parallel execution
- Proper test data management
- CI integration

**Red flags:**
- Slow tests (>30 min)
- No parallelization
- Shared mutable state
- Manual test execution required

**Questions to answer:**
- How long does the full test suite take?
- Are tests parallelized?
- How is test data managed?
- Are tests run in CI on every PR?

### 5. Test Map Completeness

Are testmaps accurate and complete?

**Why it matters:** Testmaps document test coverage per spec. Incomplete testmaps mean gaps in verification.

**How to evaluate:** Review testmaps in specs/testmaps/, verify they match actual tests, check for missing specs.

**What good looks like:**
- Testmap for every spec
- Accurate test references
- Coverage status documented
- Gaps identified

**Red flags:**
- Specs without testmaps
- Testmaps with stale references
- Missing coverage status

**Questions to answer:**
- How many specs have corresponding testmaps?
- Are testmaps kept in sync with tests?
- What specs are missing testmaps?
- How is testmap accuracy verified?

### 6. CI/CD Test Gates

Are quality gates enforced in CI/CD?

**Why it matters:** Quality gates prevent regressions from reaching production. Unenforced gates are meaningless.

**How to evaluate:** Review CI workflow, check test gate configurations, verify enforcement.

**What good looks like:**
- All tests run on every PR
- Coverage thresholds enforced
- Blocking gates on failure
- No bypass mechanisms

**Red flags:**
- Tests can be skipped
- No coverage thresholds
- Gates can be bypassed
- Failing tests don't block merges

**Questions to answer:**
- What tests run in CI?
- Are coverage thresholds enforced?
- Can tests be bypassed?
- What happens when tests fail?

## Specific Questions to Answer

1. What is the complete inventory of E2E tests and what user journeys do they cover?
2. Is the complete payment flow (browse -> cart -> checkout -> payment -> confirmation) end-to-end tested?
3. What is the unit test coverage percentage for purchase-gateway? What code paths are not covered?
4. What integration tests exist? Are database operations tested with real databases?
5. How many specs have corresponding testmaps? What specs are missing testmaps?
6. What tests run in CI? Are coverage thresholds enforced?
7. What is the test pass rate and flakiness index?
8. What test infrastructure improvements are needed?

## Expected Deliverables

- [ ] E2E test inventory with journey mapping
- [ ] Unit test coverage report
- [ ] Integration test inventory
- [ ] Testmap completeness audit
- [ ] CI configuration analysis
- [ ] Flakiness metrics
- [ ] Test coverage matrix by service and type
- [ ] Critical path coverage assessment
- [ ] Gap analysis with severity ratings
- [ ] Test infrastructure quality assessment
- [ ] CI/CD test gate recommendations
- [ ] Prioritized test improvement roadmap

## References

- Playwright Documentation
- Pytest Coverage Plugin
- Testing Best Practices
- CI/CD Quality Gates
- Open edX Testing Guide
